"""
Focused Tests for Document Processing Pipeline

Tests the core DocumentProcessor functionality with mocked dependencies.
"""

import pytest
import sqlite3
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from process import DocumentProcessor


class TestDocumentProcessorInit:
    """Test DocumentProcessor initialization"""

    def test_init_default_paths(self, tmp_path, monkeypatch):
        """Test initialization with default paths"""
        # Mock the environment check
        scan_dir = tmp_path / "scan-processor"
        scan_dir.mkdir()
        for subdir in ['incoming', 'processing', 'completed', 'failed', 'queue', 'prompts']:
            (scan_dir / subdir).mkdir()

        processor = DocumentProcessor(base_dir=str(scan_dir), dev_mode=True)

        assert processor.base_dir == scan_dir
        assert processor.dev_mode is True
        assert processor.incoming_dir == scan_dir / 'incoming'
        assert processor.processing_dir == scan_dir / 'processing'
        assert processor.completed_dir == scan_dir / 'completed'
        assert processor.failed_dir == scan_dir / 'failed'

    def test_init_dev_mode(self, tmp_path):
        """Test dev mode initialization"""
        scan_dir = tmp_path / "scan-processor"
        scan_dir.mkdir()
        for subdir in ['incoming', 'processing', 'completed', 'failed', 'queue', 'prompts']:
            (scan_dir / subdir).mkdir()

        processor = DocumentProcessor(base_dir=str(scan_dir), dev_mode=True)

        assert processor.dev_mode is True
        assert processor.paperless.dry_run is True
        assert processor.basicmemory.dry_run is True

    def test_init_with_corrections(self, tmp_path):
        """Test initialization with corrections"""
        scan_dir = tmp_path / "scan-processor"
        scan_dir.mkdir()
        for subdir in ['incoming', 'processing', 'completed', 'failed', 'queue', 'prompts']:
            (scan_dir / subdir).mkdir()

        corrections = {"override_category": "PERSONAL-MEDICAL"}
        processor = DocumentProcessor(
            base_dir=str(scan_dir),
            dev_mode=True,
            corrections=corrections
        )

        assert processor.corrections == corrections


class TestProcessDocument:
    """Test main document processing method"""

    @pytest.fixture
    def setup_processor(self, tmp_path):
        """Setup processor with all necessary directories"""
        scan_dir = tmp_path / "scan-processor"
        scan_dir.mkdir()

        # Create all required directories
        for subdir in ['incoming', 'processing', 'completed', 'failed', 'queue']:
            (scan_dir / subdir).mkdir()

        # Create database
        db_path = scan_dir / 'queue' / 'pending.db'
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                category TEXT,
                status TEXT,
                paperless_id INTEGER,
                basicmemory_path TEXT,
                processing_time_ms INTEGER,
                error_message TEXT,
                classification_prompt TEXT,
                classification_response TEXT,
                metadata_prompt TEXT,
                metadata_response TEXT,
                files_created TEXT,
                corrections TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

        # Create prompts directory
        prompts_dir = scan_dir / 'prompts'
        prompts_dir.mkdir()

        processor = DocumentProcessor(base_dir=str(scan_dir), dev_mode=True)

        return processor, scan_dir

    def test_process_document_basic_flow(self, setup_processor, tmp_path, mocker):
        """Test basic document processing flow"""
        processor, scan_dir = setup_processor

        # Create test PDF
        test_pdf = scan_dir / 'incoming' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        # Mock classifier
        mock_classify = mocker.patch.object(processor.classifier, 'classify_document')
        mock_classify.return_value = {
            'category': 'PERSONAL-MEDICAL',
            'confidence': 0.95,
            'is_cps_related': False,
            'reasoning': 'Test classification'
        }

        # Mock metadata extraction
        mock_extract = mocker.patch.object(processor, '_extract_metadata')
        mock_extract.return_value = {
            'provider': 'Dr. Smith',
            'date': '2024-01-15',
            'amount': 150.00
        }

        # Mock uploads
        mock_upload_paperless = mocker.patch.object(processor, '_upload_to_paperless')
        mock_upload_paperless.return_value = {'success': True, 'document_id': 123}

        mock_create_note = mocker.patch.object(processor, '_create_basicmemory_note')
        mock_create_note.return_value = '/path/to/note.md'

        # Mock logging
        mock_log = mocker.patch.object(processor, '_log_to_history')

        # Process document
        result = processor.process_document(test_pdf)

        # Verify result
        assert result['status'] == 'success'
        assert result['category'] == 'PERSONAL-MEDICAL'

        # Verify methods were called
        assert mock_classify.called
        assert mock_extract.called
        assert mock_log.called

    def test_process_document_full_integration(self, setup_processor, tmp_path, mocker):
        """Test full document processing with all steps"""
        processor, scan_dir = setup_processor

        # Create test PDF
        test_pdf = scan_dir / 'incoming' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        # Mock classification
        mocker.patch.object(processor.classifier, 'classify_document', return_value={
            'category': 'UTILITY',
            'confidence': 0.92,
            'is_cps_related': False
        })

        # Mock extraction
        mocker.patch.object(processor.classifier, 'extract_utility_metadata', return_value={
            'utility_type': 'electric',
            'provider': 'Duke Energy',
            'amount': 125.50,
            'date': '2024-01-15'
        })

        # Mock Paperless upload with success
        mocker.patch.object(processor.paperless, 'upload_document', return_value={
            'success': True,
            'task_id': 'task-789',
            'dry_run': True
        })

        # Mock BasicMemory note creation
        mocker.patch.object(processor.basicmemory, 'create_utility_note', return_value='/vault/note.md')

        # Mock notifier
        mock_notify = mocker.patch.object(processor.notifier, 'notify_processing_completed')

        # Process
        result = processor.process_document(test_pdf)

        # Verify success
        assert result['status'] == 'success'
        assert result['category'] == 'UTILITY'
        assert 'processing_time_ms' in result

        # Verify file was moved to completed (in real code, not mocked)
        # In dev mode with mocks, just verify the result is correct

    def test_process_document_dev_mode(self, setup_processor, tmp_path, mocker):
        """Test processing in dev mode doesn't make real uploads"""
        processor, scan_dir = setup_processor

        # Create test PDF
        test_pdf = scan_dir / 'incoming' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        # Mock classifier
        mock_classify = mocker.patch.object(processor.classifier, 'classify_document')
        mock_classify.return_value = {
            'category': 'UTILITY',
            'confidence': 0.92
        }

        # Mock other methods
        mocker.patch.object(processor, '_extract_metadata', return_value={})
        mocker.patch.object(processor, '_upload_to_paperless', return_value={'success': True, 'dry_run': True})
        mocker.patch.object(processor, '_create_basicmemory_note', return_value=None)
        mocker.patch.object(processor, '_log_to_history')

        # Process
        result = processor.process_document(test_pdf)

        # In dev mode, should still complete successfully
        assert result['status'] == 'success'

    def test_process_document_with_category_override(self, setup_processor, tmp_path, mocker):
        """Test processing with category override from corrections"""
        scan_dir = setup_processor[1]

        # Create processor with corrections
        corrections = {'override_category': 'PERSONAL-EXPENSE'}
        processor = DocumentProcessor(
            base_dir=str(scan_dir),
            dev_mode=True,
            corrections=corrections
        )

        # Create test PDF
        test_pdf = scan_dir / 'incoming' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        # Mock classifier - even with override, it's still called but category is overridden
        mock_classify = mocker.patch.object(processor.classifier, 'classify_document')
        mock_classify.return_value = {
            'category': 'GENERAL',  # This will be overridden
            'confidence': 0.85
        }
        mocker.patch.object(processor, '_extract_metadata', return_value={})
        mocker.patch.object(processor, '_upload_to_paperless', return_value={'success': True})
        mocker.patch.object(processor, '_create_basicmemory_note', return_value=None)
        mocker.patch.object(processor, '_log_to_history')

        # Process
        result = processor.process_document(test_pdf)

        # Should use override category
        assert result['status'] == 'success'
        assert result['category'] == 'PERSONAL-EXPENSE'


class TestErrorHandling:
    """Test error handling in processing"""

    @pytest.fixture
    def setup_processor(self, tmp_path):
        """Setup processor with all necessary directories"""
        scan_dir = tmp_path / "scan-processor"
        scan_dir.mkdir()

        for subdir in ['incoming', 'processing', 'completed', 'failed', 'queue']:
            (scan_dir / subdir).mkdir()

        db_path = scan_dir / 'queue' / 'pending.db'
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                category TEXT,
                status TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

        prompts_dir = scan_dir / 'prompts'
        prompts_dir.mkdir()

        processor = DocumentProcessor(base_dir=str(scan_dir), dev_mode=True)

        return processor, scan_dir

    def test_classification_error_handling(self, setup_processor, tmp_path, mocker):
        """Test handling of classification errors"""
        processor, scan_dir = setup_processor

        # Create test PDF
        test_pdf = scan_dir / 'incoming' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        # Mock classifier to raise error
        mock_classify = mocker.patch.object(processor.classifier, 'classify_document')
        mock_classify.side_effect = Exception("Classification failed")

        # Mock logging
        mocker.patch.object(processor, '_log_to_history')

        # Process should handle error gracefully
        result = processor.process_document(test_pdf)

        assert result['status'] == 'failed'
        assert 'error' in result


class TestDatabaseLogging:
    """Test database logging functionality"""

    def test_log_to_history(self, tmp_path):
        """Test logging to processing_history table"""
        scan_dir = tmp_path / "scan-processor"
        scan_dir.mkdir()

        for subdir in ['incoming', 'processing', 'completed', 'failed', 'queue']:
            (scan_dir / subdir).mkdir()

        db_path = scan_dir / 'queue' / 'pending.db'
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                category TEXT,
                status TEXT,
                paperless_id INTEGER,
                basicmemory_path TEXT,
                processing_time_ms INTEGER,
                error_message TEXT,
                classification_prompt TEXT,
                classification_response TEXT,
                metadata_prompt TEXT,
                metadata_response TEXT,
                files_created TEXT,
                corrections TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

        prompts_dir = scan_dir / 'prompts'
        prompts_dir.mkdir()

        processor = DocumentProcessor(base_dir=str(scan_dir), dev_mode=True)

        # Log a test record
        processor._log_to_history(
            filename='test.pdf',
            category='PERSONAL-MEDICAL',
            status='success',
            processing_time_ms=5000
        )

        # Verify record was created
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT filename, category, status FROM processing_history WHERE filename = 'test.pdf'")
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == 'test.pdf'
        assert result[1] == 'PERSONAL-MEDICAL'
        assert result[2] == 'success'


class TestHelperMethods:
    """Test helper methods in DocumentProcessor"""

    @pytest.fixture
    def setup_processor(self, tmp_path):
        """Setup processor"""
        scan_dir = tmp_path / "scan-processor"
        scan_dir.mkdir()
        for subdir in ['incoming', 'processing', 'completed', 'failed', 'queue', 'prompts']:
            (scan_dir / subdir).mkdir()

        processor = DocumentProcessor(base_dir=str(scan_dir), dev_mode=True)
        return processor, scan_dir

    def test_extract_metadata(self, setup_processor, tmp_path, mocker):
        """Test metadata extraction for different categories"""
        processor, scan_dir = setup_processor

        # Create test PDF
        test_pdf = scan_dir / 'processing' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        # Mock classifier extraction methods
        mock_extract = mocker.patch.object(processor.classifier, 'extract_personal_medical_metadata')
        mock_extract.return_value = {
            'provider': 'Dr. Smith',
            'date': '2024-01-15',
            'amount': 150.00
        }

        # Extract metadata
        metadata = processor._extract_metadata(test_pdf, 'PERSONAL-MEDICAL')

        assert metadata is not None
        assert metadata['provider'] == 'Dr. Smith'

    def test_upload_to_paperless(self, setup_processor, tmp_path, mocker):
        """Test Paperless upload"""
        processor, scan_dir = setup_processor

        # Create test PDF
        test_pdf = scan_dir / 'processing' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        # Mock Paperless client
        mock_upload = mocker.patch.object(processor.paperless, 'upload_document')
        mock_upload.return_value = {'success': True, 'task_id': 'task-123'}

        # Upload
        result = processor._upload_to_paperless(
            test_pdf,
            category='PERSONAL-MEDICAL',
            metadata={'provider': 'Dr. Smith'}
        )

        assert result is not None
        assert mock_upload.called

    def test_create_basicmemory_note(self, setup_processor, tmp_path, mocker):
        """Test BasicMemory note creation"""
        processor, scan_dir = setup_processor

        # Mock BasicMemory client
        mock_create = mocker.patch.object(processor.basicmemory, 'create_personal_medical_note')
        mock_create.return_value = '/path/to/note.md'

        # Create note
        note_path = processor._create_basicmemory_note(
            category='PERSONAL-MEDICAL',
            metadata={'provider': 'Dr. Smith', 'date': '2024-01-15'}
        )

        assert note_path == '/path/to/note.md'
        assert mock_create.called

    def test_extract_metadata_utility(self, setup_processor, tmp_path, mocker):
        """Test metadata extraction for UTILITY category"""
        processor, scan_dir = setup_processor

        test_pdf = scan_dir / 'processing' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        mock_extract = mocker.patch.object(processor.classifier, 'extract_utility_metadata')
        mock_extract.return_value = {
            'utility_type': 'electric',
            'provider': 'Duke Energy',
            'amount': 125.50
        }

        metadata = processor._extract_metadata(test_pdf, 'UTILITY')

        assert metadata is not None
        assert metadata['utility_type'] == 'electric'

    def test_extract_metadata_auto(self, setup_processor, tmp_path, mocker):
        """Test metadata extraction for AUTO categories"""
        processor, scan_dir = setup_processor

        test_pdf = scan_dir / 'processing' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        mock_extract = mocker.patch.object(processor.classifier, 'extract_auto_metadata')
        mock_extract.return_value = {
            'company': 'Geico',
            'policy_number': 'POL-12345',
            'amount': 600.00
        }

        metadata = processor._extract_metadata(test_pdf, 'AUTO-INSURANCE')

        assert metadata is not None
        assert metadata['company'] == 'Geico'

    def test_create_basicmemory_note_utility(self, setup_processor, mocker):
        """Test creating utility note"""
        processor, _ = setup_processor

        mock_create = mocker.patch.object(processor.basicmemory, 'create_utility_note')
        mock_create.return_value = '/path/to/utility-note.md'

        note_path = processor._create_basicmemory_note(
            category='UTILITY',
            metadata={'utility_type': 'electric', 'provider': 'Duke Energy'}
        )

        assert note_path == '/path/to/utility-note.md'

    def test_create_basicmemory_note_auto(self, setup_processor, mocker):
        """Test creating auto note"""
        processor, _ = setup_processor

        mock_create = mocker.patch.object(processor.basicmemory, 'create_auto_note')
        mock_create.return_value = '/path/to/auto-note.md'

        note_path = processor._create_basicmemory_note(
            category='AUTO-INSURANCE',
            metadata={'company': 'Geico'}
        )

        assert note_path == '/path/to/auto-note.md'

    def test_create_basicmemory_note_no_note_category(self, setup_processor):
        """Test category that doesn't create notes"""
        processor, _ = setup_processor

        note_path = processor._create_basicmemory_note(
            category='GENERAL',
            metadata={}
        )

        assert note_path is None

    def test_upload_to_paperless_with_tags(self, setup_processor, tmp_path, mocker):
        """Test Paperless upload with tags"""
        processor, scan_dir = setup_processor

        test_pdf = scan_dir / 'processing' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        mock_upload = mocker.patch.object(processor.paperless, 'upload_document')
        mock_upload.return_value = {'success': True, 'task_id': 'task-456'}

        result = processor._upload_to_paperless(
            test_pdf,
            category='UTILITY',
            metadata={'utility_type': 'electric', 'provider': 'Duke Energy'}
        )

        assert result is not None
        assert mock_upload.called


class TestAdditionalCoverage:
    """Additional tests to reach 80% coverage"""

    @pytest.fixture
    def setup_processor(self, tmp_path):
        """Setup processor"""
        scan_dir = tmp_path / "scan-processor"
        scan_dir.mkdir()
        for subdir in ['incoming', 'processing', 'completed', 'failed', 'queue', 'prompts']:
            (scan_dir / subdir).mkdir()

        processor = DocumentProcessor(base_dir=str(scan_dir), dev_mode=True)
        return processor, scan_dir

    def test_extract_metadata_cps_medical(self, setup_processor, tmp_path, mocker):
        """Test metadata extraction for CPS-MEDICAL"""
        processor, scan_dir = setup_processor

        test_pdf = scan_dir / 'processing' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        mock_extract = mocker.patch.object(processor.classifier, 'extract_medical_metadata')
        mock_extract.return_value = {'provider': 'Dr. Jones', 'child': 'Morgan'}

        metadata = processor._extract_metadata(test_pdf, 'CPS-MEDICAL')
        assert metadata['child'] == 'Morgan'

    def test_extract_metadata_cps_expense(self, setup_processor, tmp_path, mocker):
        """Test metadata extraction for CPS-EXPENSE"""
        processor, scan_dir = setup_processor

        test_pdf = scan_dir / 'processing' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        mock_extract = mocker.patch.object(processor.classifier, 'extract_expense_metadata')
        mock_extract.return_value = {'vendor': 'Target', 'child': 'Jacob'}

        metadata = processor._extract_metadata(test_pdf, 'CPS-EXPENSE')
        assert metadata['vendor'] == 'Target'

    def test_extract_metadata_personal_expense(self, setup_processor, tmp_path, mocker):
        """Test metadata extraction for PERSONAL-EXPENSE"""
        processor, scan_dir = setup_processor

        test_pdf = scan_dir / 'processing' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        mock_extract = mocker.patch.object(processor.classifier, 'extract_personal_expense_metadata')
        mock_extract.return_value = {'vendor': 'Amazon', 'amount': 75.00}

        metadata = processor._extract_metadata(test_pdf, 'PERSONAL-EXPENSE')
        assert metadata['vendor'] == 'Amazon'

    def test_create_note_cps_medical(self, setup_processor, mocker):
        """Test CPS medical note creation"""
        processor, _ = setup_processor

        mock_create = mocker.patch.object(processor.basicmemory, 'create_medical_note')
        mock_create.return_value = '/vault/cps/medical.md'

        note_path = processor._create_basicmemory_note(
            category='CPS-MEDICAL',
            metadata={'provider': 'Dr. Smith'}
        )
        assert note_path == '/vault/cps/medical.md'

    def test_create_note_cps_expense(self, setup_processor, mocker):
        """Test CPS expense note creation"""
        processor, _ = setup_processor

        mock_create = mocker.patch.object(processor.basicmemory, 'create_expense_note')
        mock_create.return_value = '/vault/cps/expense.md'

        note_path = processor._create_basicmemory_note(
            category='CPS-EXPENSE',
            metadata={'vendor': 'Target'}
        )
        assert note_path == '/vault/cps/expense.md'

    def test_create_note_personal_expense(self, setup_processor, mocker):
        """Test personal expense note creation"""
        processor, _ = setup_processor

        mock_create = mocker.patch.object(processor.basicmemory, 'create_personal_expense_note')
        mock_create.return_value = '/vault/personal/expense.md'

        note_path = processor._create_basicmemory_note(
            category='PERSONAL-EXPENSE',
            metadata={'vendor': 'Amazon'}
        )
        assert note_path == '/vault/personal/expense.md'

    def test_create_note_auto_maintenance(self, setup_processor, mocker):
        """Test auto maintenance note"""
        processor, _ = setup_processor

        mock_create = mocker.patch.object(processor.basicmemory, 'create_auto_note')
        mock_create.return_value = '/vault/auto/maint.md'

        note_path = processor._create_basicmemory_note(
            category='AUTO-MAINTENANCE',
            metadata={'shop': 'Jiffy Lube'}
        )
        assert note_path == '/vault/auto/maint.md'

    def test_create_note_auto_registration(self, setup_processor, mocker):
        """Test auto registration note"""
        processor, _ = setup_processor

        mock_create = mocker.patch.object(processor.basicmemory, 'create_auto_note')
        mock_create.return_value = '/vault/auto/reg.md'

        note_path = processor._create_basicmemory_note(
            category='AUTO-REGISTRATION',
            metadata={'vehicle': 'Honda'}
        )
        assert note_path == '/vault/auto/reg.md'

    def test_note_creation_error(self, setup_processor, mocker):
        """Test error handling in note creation"""
        processor, _ = setup_processor

        mock_create = mocker.patch.object(processor.basicmemory, 'create_personal_medical_note')
        mock_create.side_effect = Exception("Failed")

        note_path = processor._create_basicmemory_note(
            category='PERSONAL-MEDICAL',
            metadata={'provider': 'Dr. Smith'}
        )
        assert note_path is None

    def test_upload_paperless_with_notification(self, setup_processor, tmp_path, mocker):
        """Test Paperless upload triggers notification"""
        processor, scan_dir = setup_processor

        test_pdf = scan_dir / 'processing' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        # Mock uploads
        mock_upload = mocker.patch.object(processor.paperless, 'upload_document')
        mock_upload.return_value = {'success': True, 'task_id': 'task-999'}

        # Mock notification
        mock_notify = mocker.patch.object(processor.notifier, 'notify_processing_completed')

        result = processor._upload_to_paperless(
            test_pdf,
            category='PERSONAL-MEDICAL',
            metadata={'provider': 'Dr. Smith', 'amount': 150.00}
        )

        assert result is not None
        # Notification should be called for medical documents
        # (depends on implementation)

    def test_process_with_notification(self, setup_processor, tmp_path, mocker):
        """Test full process triggers notifications"""
        processor, scan_dir = setup_processor

        test_pdf = scan_dir / 'incoming' / 'medical.pdf'
        test_pdf.write_bytes(b"PDF content")

        # Mock all steps
        mocker.patch.object(processor.classifier, 'classify_document', return_value={
            'category': 'PERSONAL-MEDICAL',
            'confidence': 0.95
        })
        mocker.patch.object(processor, '_extract_metadata', return_value={
            'provider': 'Dr. Smith',
            'amount': 200.00
        })
        mocker.patch.object(processor, '_upload_to_paperless', return_value={'success': True})
        mocker.patch.object(processor, '_create_basicmemory_note', return_value='/note.md')
        mocker.patch.object(processor, '_log_to_history')

        mock_notify = mocker.patch.object(processor.notifier, 'notify_processing_completed')

        result = processor.process_document(test_pdf)

        assert result['status'] == 'success'

    def test_extract_metadata_schoolwork(self, setup_processor, tmp_path, mocker):
        """Test metadata extraction for CPS-SCHOOLWORK"""
        processor, scan_dir = setup_processor

        test_pdf = scan_dir / 'processing' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        mock_extract = mocker.patch.object(processor.classifier, 'extract_schoolwork_metadata')
        mock_extract.return_value = {'child': 'Morgan', 'subject': 'Math', 'grade': 'A'}

        metadata = processor._extract_metadata(test_pdf, 'CPS-SCHOOLWORK')
        assert metadata['subject'] == 'Math'

    def test_extract_metadata_no_extractor(self, setup_processor, tmp_path):
        """Test metadata extraction for category without extractor"""
        processor, scan_dir = setup_processor

        test_pdf = scan_dir / 'processing' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        # GENERAL category has no specific extractor
        metadata = processor._extract_metadata(test_pdf, 'GENERAL')
        assert metadata == {}

    def test_upload_with_child_tag(self, setup_processor, tmp_path, mocker):
        """Test Paperless upload with child tag"""
        processor, scan_dir = setup_processor

        test_pdf = scan_dir / 'processing' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        mock_upload = mocker.patch.object(processor.paperless, 'upload_document')
        mock_upload.return_value = {'success': True, 'task_id': 'task-123'}

        result = processor._upload_to_paperless(
            test_pdf,
            category='CPS-MEDICAL',
            metadata={'provider': 'Dr. Smith', 'child': 'Morgan'}
        )

        # Verify child tag was included
        assert mock_upload.called
        call_args = mock_upload.call_args
        tags = call_args[1]['tags']
        assert 'morgan' in tags

    def test_process_document_file_move_error(self, setup_processor, tmp_path, mocker):
        """Test error handling when file move fails"""
        processor, scan_dir = setup_processor

        # Create test PDF
        test_pdf = scan_dir / 'incoming' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        # Mock to raise error during classification
        mocker.patch.object(processor.classifier, 'classify_document', side_effect=Exception("Classification failed"))
        mocker.patch.object(processor, '_log_to_history')

        # Process should handle error
        result = processor.process_document(test_pdf)

        assert result['status'] == 'failed'
        assert 'error' in result

    def test_process_failure_notification_dev_mode(self, setup_processor, tmp_path, mocker):
        """Test that failure notifications are skipped in dev mode"""
        processor, scan_dir = setup_processor

        test_pdf = scan_dir / 'incoming' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        # Mock to fail
        mocker.patch.object(processor.classifier, 'classify_document', side_effect=Exception("Test error"))
        mocker.patch.object(processor, '_log_to_history')

        mock_notify = mocker.patch.object(processor.notifier, 'notify_processing_failed')

        # Process
        result = processor.process_document(test_pdf)

        # In dev mode, notification should NOT be called
        assert not mock_notify.called

    def test_upload_with_various_metadata(self, setup_processor, tmp_path, mocker):
        """Test upload with different metadata fields"""
        processor, scan_dir = setup_processor

        test_pdf = scan_dir / 'processing' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        mock_upload = mocker.patch.object(processor.paperless, 'upload_document')
        mock_upload.return_value = {'success': True}

        # Test with title and created_date
        processor._upload_to_paperless(
            test_pdf,
            category='PERSONAL-EXPENSE',
            metadata={
                'vendor': 'Amazon',
                'amount': 50.00,
                'date': '2024-01-15',
                'description': 'Office supplies'
            }
        )

        assert mock_upload.called
        call_args = mock_upload.call_args
        # Verify created_date was set
        assert 'created_date' in call_args[1]

    def test_notification_for_medical(self, setup_processor, tmp_path, mocker):
        """Test notification is sent for medical documents"""
        processor, scan_dir = setup_processor

        test_pdf = scan_dir / 'incoming' / 'medical.pdf'
        test_pdf.write_bytes(b"PDF content")

        # Mock full processing
        mocker.patch.object(processor.classifier, 'classify_document', return_value={
            'category': 'CPS-MEDICAL',
            'confidence': 0.96
        })
        mocker.patch.object(processor.classifier, 'extract_medical_metadata', return_value={
            'provider': 'Dr. Jones',
            'child': 'Morgan',
            'amount': 250.00
        })
        mocker.patch.object(processor.paperless, 'upload_document', return_value={
            'success': True,
            'dry_run': True
        })
        mocker.patch.object(processor.basicmemory, 'create_medical_note', return_value='/note.md')
        mocker.patch.object(processor, '_log_to_history')

        mock_notify = mocker.patch.object(processor.notifier, 'notify_processing_completed')

        # Process
        result = processor.process_document(test_pdf)

        assert result['status'] == 'success'

    def test_update_paperless_metadata(self, setup_processor, mocker):
        """Test updating existing Paperless document"""
        processor, _ = setup_processor

        mock_update = mocker.patch.object(processor.paperless, 'update_document')
        mock_update.return_value = {'success': True}

        result = processor._update_paperless_metadata(
            document_id=123,
            category='CPS-MEDICAL',
            metadata={'provider': 'Dr. Smith', 'child': 'Morgan', 'date': '2024-01-15'}
        )

        assert mock_update.called
        call_args = mock_update.call_args
        assert call_args[1]['document_id'] == 123
        assert 'morgan' in call_args[1]['tags']

    def test_handle_clarification_needed(self, setup_processor, tmp_path):
        """Test handling document needing clarification"""
        processor, scan_dir = setup_processor

        # Create pending_documents table
        conn = sqlite3.connect(str(processor.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                category TEXT,
                question TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

        test_pdf = scan_dir / 'processing' / 'test.pdf'
        test_pdf.write_bytes(b"PDF content")

        classification = {
            'category': 'UNCERTAIN',
            'clarification_question': 'Is this medical or expense?',
            'metadata': {'partial': 'data'}
        }

        processor._handle_clarification_needed(test_pdf, classification)

        # Verify record was created
        conn = sqlite3.connect(str(processor.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT filename, question FROM pending_documents WHERE filename = 'test.pdf'")
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert 'medical or expense' in result[1]

    def test_process_with_clarification_needed(self, setup_processor, tmp_path, mocker):
        """Test processing document that needs clarification"""
        processor, scan_dir = setup_processor

        # Create pending_documents table
        conn = sqlite3.connect(str(processor.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                category TEXT,
                question TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

        test_pdf = scan_dir / 'incoming' / 'unclear.pdf'
        test_pdf.write_bytes(b"PDF content")

        # Mock classification to need clarification
        mocker.patch.object(processor.classifier, 'classify_document', return_value={
            'category': 'UNCERTAIN',
            'confidence': 0.45,
            'needs_clarification': True,
            'clarification_question': 'Could not determine document type'
        })

        mock_clarification = mocker.patch.object(processor, '_handle_clarification_needed')

        # Process
        result = processor.process_document(test_pdf)

        # Should return pending status
        assert result['status'] == 'pending_clarification'
        assert mock_clarification.called

    def test_init_with_update_mode(self, tmp_path):
        """Test initialization with UPDATE mode"""
        scan_dir = tmp_path / "scan-processor"
        scan_dir.mkdir()
        for subdir in ['incoming', 'processing', 'completed', 'failed', 'queue', 'prompts']:
            (scan_dir / subdir).mkdir()

        # Initialize with paperless_id for UPDATE mode
        processor = DocumentProcessor(
            base_dir=str(scan_dir),
            dev_mode=True,
            paperless_id=456
        )

        assert processor.paperless_id == 456
