"""
Pytest configuration and fixtures for scan-processor test suite

Provides reusable fixtures for testing:
- Mock Claude Code CLI responses
- Temporary vault directories
- Sample PDF documents
- Test databases
- Mock objects for classifier and BasicMemory
"""

import pytest
import json
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import sys
import os

# Add scripts directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


# ========== Claude Code Mock Responses ==========

@pytest.fixture
def mock_claude_response_personal_medical():
    """Mock Claude Code CLI response for PERSONAL-MEDICAL classification"""
    return {
        "category": "PERSONAL-MEDICAL",
        "confidence": 0.95,
        "is_cps_related": False,
        "reasoning": "This is a personal medical document containing healthcare information."
    }


@pytest.fixture
def mock_claude_response_cps_medical():
    """Mock Claude Code CLI response for CPS-MEDICAL classification"""
    return {
        "category": "CPS-MEDICAL",
        "confidence": 0.92,
        "is_cps_related": True,
        "reasoning": "This document relates to a child's medical care and should be tracked in the co-parenting system."
    }


@pytest.fixture
def mock_claude_response_utility():
    """Mock Claude Code CLI response for UTILITY classification"""
    return {
        "category": "UTILITY",
        "confidence": 0.88,
        "is_cps_related": False,
        "reasoning": "This is a utility bill for household services."
    }


@pytest.fixture
def mock_claude_response_auto():
    """Mock Claude Code CLI response for AUTO-* classification"""
    return {
        "category": "AUTO-INSURANCE",
        "confidence": 0.90,
        "is_cps_related": False,
        "reasoning": "This is an auto insurance document."
    }


@pytest.fixture
def mock_personal_medical_metadata():
    """Mock metadata extraction for personal medical documents"""
    return {
        "provider": "Dr. Smith Family Medicine",
        "date": "2025-09-15",
        "amount": 125.50,
        "type": "medical_bill",
        "description": "Office visit and lab work"
    }


@pytest.fixture
def mock_utility_metadata():
    """Mock metadata extraction for utility bills"""
    return {
        "utility_type": "electric",
        "provider": "City Power & Light",
        "billing_date": "2025-12-01",
        "due_date": "2025-12-21",
        "amount": 142.37,
        "account_number": "1234567890"
    }


@pytest.fixture
def mock_auto_metadata():
    """Mock metadata extraction for auto documents"""
    return {
        "insurance_company": "State Farm",
        "policy_number": "POL-12345678",
        "vehicle": "2020 Honda Accord",
        "effective_date": "2025-01-01",
        "expiration_date": "2026-01-01",
        "premium": 1200.00
    }


# ========== Vault Directory Fixtures ==========

@pytest.fixture
def temp_vault_dirs(tmp_path):
    """Create temporary vault directories for testing

    Returns:
        tuple: (cps_vault_path, personal_vault_path)
    """
    cps_vault = tmp_path / "CoparentingSystem"
    personal_vault = tmp_path / "Personal"

    # Create CPS vault structure
    (cps_vault / "60-medical" / "morgan").mkdir(parents=True)
    (cps_vault / "60-medical" / "jacob").mkdir(parents=True)
    (cps_vault / "40-expenses").mkdir(parents=True)

    # Create Personal vault structure
    (personal_vault / "Medical").mkdir(parents=True)
    (personal_vault / "Expenses").mkdir(parents=True)
    (personal_vault / "Utilities").mkdir(parents=True)
    (personal_vault / "Auto" / "Insurance").mkdir(parents=True)
    (personal_vault / "Auto" / "Maintenance").mkdir(parents=True)
    (personal_vault / "Auto" / "Registration").mkdir(parents=True)

    return cps_vault, personal_vault


@pytest.fixture
def cps_vault(temp_vault_dirs):
    """Return just the CPS vault directory"""
    return temp_vault_dirs[0]


@pytest.fixture
def personal_vault(temp_vault_dirs):
    """Return just the Personal vault directory"""
    return temp_vault_dirs[1]


# ========== PDF Document Fixtures ==========

@pytest.fixture
def sample_pdf(tmp_path):
    """Create a simple test PDF

    Returns:
        Path: Path to generated PDF file
    """
    pdf_path = tmp_path / "test_document.pdf"

    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    # Add some text content
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Test Medical Document")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 150, "Patient: John Doe")
    c.drawString(100, height - 170, "Date: 2025-09-15")
    c.drawString(100, height - 190, "Amount: $125.50")

    c.save()

    return pdf_path


@pytest.fixture
def sample_medical_pdf(tmp_path):
    """Create a medical document PDF"""
    pdf_path = tmp_path / "medical_bill.pdf"

    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Dr. Smith Family Medicine")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 130, "Medical Bill")
    c.drawString(100, height - 160, "Patient: Jane Smith")
    c.drawString(100, height - 180, "Date of Service: 2025-09-15")
    c.drawString(100, height - 200, "Total: $125.50")

    c.save()

    return pdf_path


@pytest.fixture
def sample_utility_pdf(tmp_path):
    """Create a utility bill PDF"""
    pdf_path = tmp_path / "electric_bill.pdf"

    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "City Power & Light")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 130, "ELECTRIC BILL")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 160, "Billing Date: 2025-12-01")
    c.drawString(100, height - 180, "Due Date: 2025-12-21")
    c.drawString(100, height - 200, "Amount Due: $142.37")
    c.drawString(100, height - 220, "kWh Used: 850")

    c.save()

    return pdf_path


# ========== Database Fixtures ==========

@pytest.fixture
def test_database(tmp_path):
    """Create temporary test database with schema

    Returns:
        Path: Path to test database file
    """
    db_path = tmp_path / "test.db"

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create processing_history table
    cursor.execute('''
        CREATE TABLE processing_history (
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
    ''')

    # Create pending_documents table
    cursor.execute('''
        CREATE TABLE pending_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            category TEXT,
            question TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create claude_code_logs table
    cursor.execute('''
        CREATE TABLE claude_code_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            prompt_type TEXT,
            prompt_file TEXT,
            prompt_content TEXT,
            response_content TEXT,
            confidence REAL,
            success INTEGER,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def populated_database(test_database):
    """Database with some test data

    Returns:
        Path: Path to database with test records
    """
    conn = sqlite3.connect(str(test_database))
    cursor = conn.cursor()

    # Add some test processing history
    cursor.execute('''
        INSERT INTO processing_history
        (filename, category, status, classification_prompt, classification_response)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        'test_medical.pdf',
        'PERSONAL-MEDICAL',
        'success',
        'Classification prompt...',
        '{"category": "PERSONAL-MEDICAL", "confidence": 0.95}'
    ))

    cursor.execute('''
        INSERT INTO processing_history
        (filename, category, status, classification_prompt, classification_response)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        'test_utility.pdf',
        'UTILITY',
        'success',
        'Classification prompt...',
        '{"category": "UTILITY", "confidence": 0.88}'
    ))

    conn.commit()
    conn.close()

    return test_database


# ========== Mock Subprocess Fixtures ==========

@pytest.fixture
def mock_claude_code_success(mocker):
    """Mock successful Claude Code CLI subprocess call

    Returns a successful JSON response for classification
    """
    def mock_subprocess_run(*args, **kwargs):
        class CompletedProcess:
            returncode = 0
            stdout = json.dumps({
                "category": "PERSONAL-MEDICAL",
                "confidence": 0.95,
                "is_cps_related": False,
                "reasoning": "Test classification"
            })
        return CompletedProcess()

    return mocker.patch('subprocess.run', side_effect=mock_subprocess_run)


@pytest.fixture
def mock_claude_code_failure(mocker):
    """Mock failed Claude Code CLI subprocess call"""
    def mock_subprocess_run(*args, **kwargs):
        class CompletedProcess:
            returncode = 1
            stdout = ""
        return CompletedProcess()

    return mocker.patch('subprocess.run', side_effect=mock_subprocess_run)


# ========== Classifier Fixtures ==========

@pytest.fixture
def mock_classifier(mocker, tmp_path):
    """Mock DocumentClassifier for testing

    Returns:
        MagicMock: Mocked classifier with common methods
    """
    from unittest.mock import MagicMock

    classifier = MagicMock()

    # Mock classification
    classifier.classify.return_value = {
        "category": "PERSONAL-MEDICAL",
        "confidence": 0.95,
        "is_cps_related": False,
        "reasoning": "Test classification"
    }

    # Mock metadata extraction
    classifier.extract_metadata.return_value = {
        "provider": "Dr. Smith",
        "date": "2025-09-15",
        "amount": 125.50,
        "type": "medical_bill"
    }

    return classifier


@pytest.fixture
def real_classifier(tmp_path):
    """Create a real DocumentClassifier instance for integration tests

    Uses temporary directories for prompts and database
    """
    from classifier import DocumentClassifier

    # Create temporary prompts directory
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()

    # Create basic classifier prompt
    (prompts_dir / "classifier.md").write_text(
        "Classify this document into one of the supported categories."
    )

    db_path = tmp_path / "test.db"

    return DocumentClassifier(prompts_dir=prompts_dir, db_path=db_path)


# ========== BasicMemory Fixtures ==========

@pytest.fixture
def mock_basicmemory(mocker, temp_vault_dirs):
    """Mock BasicMemoryNoteCreator for testing

    Returns:
        MagicMock: Mocked note creator
    """
    from unittest.mock import MagicMock

    note_creator = MagicMock()
    cps_vault, personal_vault = temp_vault_dirs

    # Mock note creation methods
    note_creator.create_personal_medical_note.return_value = personal_vault / "Medical" / "2025-09-15-test-note.md"
    note_creator.create_personal_expense_note.return_value = personal_vault / "Expenses" / "2025-09-15-test-expense.md"
    note_creator.create_utility_note.return_value = personal_vault / "Utilities" / "2025-12-01-electric-bill.md"
    note_creator.create_auto_note.return_value = personal_vault / "Auto" / "Insurance" / "2025-01-01-policy.md"

    return note_creator


@pytest.fixture
def real_basicmemory(temp_vault_dirs):
    """Create a real BasicMemoryNoteCreator instance for integration tests"""
    from basicmemory import BasicMemoryNoteCreator

    cps_vault, personal_vault = temp_vault_dirs

    return BasicMemoryNoteCreator(
        cps_path=cps_vault,
        personal_path=personal_vault,
        dry_run=False
    )


# ========== Sample Data Fixtures ==========

@pytest.fixture
def sample_categories():
    """List of all supported document categories"""
    return [
        # CPS categories
        "CPS-MEDICAL",
        "CPS-EXPENSE",
        "CPS-SCHOOLWORK",
        "CPS-CUSTODY",
        "CPS-COMMUNICATION",
        "CPS-LEGAL",
        # Personal categories
        "PERSONAL-MEDICAL",
        "PERSONAL-EXPENSE",
        "UTILITY",
        "AUTO-INSURANCE",
        "AUTO-MAINTENANCE",
        "AUTO-REGISTRATION",
        "RECEIPT",
        "INVOICE",
        "TAX-DOCUMENT",
        "BANK-STATEMENT",
        "INVESTMENT",
        "PRESCRIPTION",
        "INSURANCE",
        "MORTGAGE",
        "LEASE",
        "HOME-MAINTENANCE",
        "PROPERTY-TAX",
        "CONTRACT",
        "LEGAL-DOCUMENT",
        "TRAVEL-BOOKING",
        "TRAVEL-RECEIPT",
        "GENERAL",
        "REFERENCE"
    ]


@pytest.fixture
def sample_corrections():
    """Sample correction data for re-processing tests"""
    return {
        "category_override": "PERSONAL-MEDICAL",
        "additional_context": "This is actually a personal medical bill, not CPS-related",
        "reason": "incorrect_category"
    }


# ========== Utility Fixtures ==========

@pytest.fixture
def mock_paperless_client(mocker):
    """Mock Paperless API client"""
    from unittest.mock import MagicMock

    client = MagicMock()
    client.upload_document.return_value = {
        "id": 12345,
        "status": "success"
    }

    return client


@pytest.fixture
def mock_notification_handler(mocker):
    """Mock Pushover notification handler"""
    from unittest.mock import MagicMock

    handler = MagicMock()
    handler.send.return_value = True

    return handler


@pytest.fixture
def capture_stdout(mocker):
    """Capture stdout for testing print statements"""
    from io import StringIO

    captured_output = StringIO()
    mocker.patch('sys.stdout', captured_output)

    return captured_output
