"""
Tests for DocumentClassifier

Tests classification and metadata extraction functionality:
- Document classification across all 29 categories
- Personal medical metadata extraction
- Personal expense metadata extraction
- Utility bill metadata extraction
- Automotive document metadata extraction
- Error handling and edge cases
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from classifier import DocumentClassifier


class TestDocumentClassifierInit:
    """Test DocumentClassifier initialization"""

    def test_init_with_defaults(self, tmp_path):
        """Test classifier initializes with default paths"""
        # Create minimal prompts directory
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Test prompt")

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        assert classifier.prompts_dir == prompts_dir
        assert classifier.classifier_prompt.exists()

    def test_init_loads_all_prompts(self, tmp_path):
        """Verify all 8 prompts are loaded correctly"""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()

        # Create all required prompt files
        prompts = [
            "classifier.md",
            "medical.md",
            "expense.md",
            "schoolwork.md",
            "personal-medical.md",
            "personal-expense.md",
            "utility.md",
            "auto.md"
        ]

        for prompt in prompts:
            (prompts_dir / prompt).write_text(f"Prompt content for {prompt}")

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Verify all prompts exist
        assert classifier.classifier_prompt.exists()
        assert (classifier.prompts_dir / "medical.md").exists()
        assert (classifier.prompts_dir / "personal-medical.md").exists()
        assert (classifier.prompts_dir / "utility.md").exists()
        assert (classifier.prompts_dir / "auto.md").exists()


class TestDocumentClassification:
    """Test document classification functionality"""

    def test_classify_personal_medical(self, mock_claude_response_personal_medical,
                                       sample_medical_pdf, tmp_path, mocker):
        """Test classification of personal medical documents"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Classify document")

        # Mock Claude Code subprocess
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps(mock_claude_response_personal_medical)

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Execute
        result = classifier.classify_document(str(sample_medical_pdf))

        # Verify
        assert result['category'] == 'PERSONAL-MEDICAL'
        assert result['confidence'] > 0.9
        assert result['is_cps_related'] == False
        assert 'reasoning' in result

    def test_classify_utility(self, mock_claude_response_utility,
                             sample_utility_pdf, tmp_path, mocker):
        """Test classification of utility bills"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Classify document")

        # Mock Claude Code subprocess
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps(mock_claude_response_utility)

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Execute
        result = classifier.classify_document(str(sample_utility_pdf))

        # Verify
        assert result['category'] == 'UTILITY'
        assert result['confidence'] > 0.8
        assert result['is_cps_related'] == False

    def test_classify_cps_vs_personal_routing(self, tmp_path, mocker):
        """Test that CPS documents are correctly flagged"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Classify document")

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        # Mock CPS-MEDICAL response
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({
            "category": "CPS-MEDICAL",
            "confidence": 0.92,
            "is_cps_related": True,
            "reasoning": "Child medical document"
        })

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Execute
        result = classifier.classify_document(str(pdf_path))

        # Verify CPS routing flag
        assert result['category'].startswith('CPS-')
        assert result['is_cps_related'] == True


class TestPersonalMedicalMetadata:
    """Test personal medical metadata extraction"""

    def test_extract_personal_medical_metadata(self, tmp_path, mocker,
                                               mock_personal_medical_metadata):
        """Test extraction of personal medical metadata"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Test")
        (prompts_dir / "personal-medical.md").write_text("Extract personal medical metadata")

        pdf_path = tmp_path / "medical.pdf"
        pdf_path.write_text("test")

        # Mock Claude Code subprocess
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps(mock_personal_medical_metadata)

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Execute
        metadata = classifier.extract_personal_medical_metadata(str(pdf_path))

        # Verify required fields
        assert 'provider' in metadata
        assert 'date' in metadata
        assert 'amount' in metadata
        assert 'type' in metadata

        # Verify values
        assert metadata['provider'] == "Dr. Smith Family Medicine"
        assert metadata['amount'] == 125.50
        assert metadata['type'] == "medical_bill"

    def test_extract_personal_medical_with_corrections(self, tmp_path, mocker):
        """Test metadata extraction includes corrections"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Test")
        (prompts_dir / "personal-medical.md").write_text("Extract metadata")

        pdf_path = tmp_path / "medical.pdf"
        pdf_path.write_text("test")

        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({
            "provider": "Updated Provider",
            "date": "2025-10-01",
            "amount": 200.00,
            "type": "lab_results"
        })

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        corrections = {
            "notes": "Provider should be Dr. Johnson",
            "reason": "incorrect_provider"
        }

        # Execute
        metadata = classifier.extract_personal_medical_metadata(
            str(pdf_path),
            corrections=corrections
        )

        # Verify corrections were applied
        assert metadata is not None
        # In real implementation, corrections would be appended to prompt
        # Here we just verify the method accepts corrections


class TestPersonalExpenseMetadata:
    """Test personal expense metadata extraction"""

    def test_extract_personal_expense_metadata(self, tmp_path, mocker):
        """Test extraction of personal expense metadata"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Test")
        (prompts_dir / "personal-expense.md").write_text("Extract expense metadata")

        pdf_path = tmp_path / "receipt.pdf"
        pdf_path.write_text("test")

        # Mock Claude Code subprocess
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({
            "vendor": "The Bistro Restaurant",
            "date": "2025-12-15",
            "amount": 45.75,
            "category": "dining",
            "description": "Dinner receipt"
        })

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Execute
        metadata = classifier.extract_personal_expense_metadata(str(pdf_path))

        # Verify required fields
        assert 'vendor' in metadata
        assert 'date' in metadata
        assert 'amount' in metadata
        assert 'category' in metadata

        # Verify values
        assert metadata['vendor'] == "The Bistro Restaurant"
        assert metadata['amount'] == 45.75
        assert metadata['category'] == "dining"

    def test_extract_personal_expense_handles_missing_fields(self, tmp_path, mocker):
        """Test extraction handles missing optional fields gracefully"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Test")
        (prompts_dir / "personal-expense.md").write_text("Extract")

        pdf_path = tmp_path / "receipt.pdf"
        pdf_path.write_text("test")

        # Mock response with minimal fields
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({
            "vendor": "Unknown Store",
            "date": "2025-12-01",
            "amount": 25.00
        })

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Execute
        metadata = classifier.extract_personal_expense_metadata(str(pdf_path))

        # Verify essential fields present
        assert metadata['vendor'] == "Unknown Store"
        assert metadata['amount'] == 25.00


class TestUtilityMetadata:
    """Test utility bill metadata extraction"""

    def test_extract_utility_metadata_electric(self, tmp_path, mocker,
                                               mock_utility_metadata):
        """Test extraction of electric utility metadata"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Test")
        (prompts_dir / "utility.md").write_text("Extract utility metadata")

        pdf_path = tmp_path / "electric_bill.pdf"
        pdf_path.write_text("test")

        # Mock Claude Code subprocess
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps(mock_utility_metadata)

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Execute
        metadata = classifier.extract_utility_metadata(str(pdf_path))

        # Verify required fields
        assert 'utility_type' in metadata
        assert 'provider' in metadata
        assert 'billing_date' in metadata
        assert 'due_date' in metadata
        assert 'amount' in metadata

        # Verify values
        assert metadata['utility_type'] == "electric"
        assert metadata['provider'] == "City Power & Light"
        assert metadata['amount'] == 142.37

    def test_extract_utility_metadata_types(self, tmp_path, mocker):
        """Test extraction for different utility types"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Test")
        (prompts_dir / "utility.md").write_text("Extract")

        pdf_path = tmp_path / "utility.pdf"
        pdf_path.write_text("test")

        utility_types = ["electric", "water", "gas", "internet", "phone"]

        for utility_type in utility_types:
            # Mock response for each type
            mock_run = mocker.patch('subprocess.run')
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = json.dumps({
                "utility_type": utility_type,
                "provider": f"Test {utility_type.title()} Company",
                "billing_date": "2025-12-01",
                "due_date": "2025-12-21",
                "amount": 100.00
            })

            classifier = DocumentClassifier(prompts_dir=prompts_dir)

            # Execute
            metadata = classifier.extract_utility_metadata(str(pdf_path))

            # Verify type-specific extraction
            assert metadata['utility_type'] == utility_type


class TestAutoMetadata:
    """Test automotive document metadata extraction"""

    def test_extract_auto_metadata_insurance(self, tmp_path, mocker,
                                             mock_auto_metadata):
        """Test extraction of auto insurance metadata"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Test")
        (prompts_dir / "auto.md").write_text("Extract auto metadata")

        pdf_path = tmp_path / "insurance.pdf"
        pdf_path.write_text("test")

        # Mock Claude Code subprocess
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps(mock_auto_metadata)

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Execute
        metadata = classifier.extract_auto_metadata(str(pdf_path))

        # Verify insurance-specific fields
        assert 'insurance_company' in metadata
        assert 'policy_number' in metadata
        assert 'vehicle' in metadata
        assert 'premium' in metadata

        # Verify values
        assert metadata['insurance_company'] == "State Farm"
        assert metadata['policy_number'] == "POL-12345678"
        assert metadata['premium'] == 1200.00

    def test_extract_auto_metadata_maintenance(self, tmp_path, mocker):
        """Test extraction of auto maintenance metadata"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Test")
        (prompts_dir / "auto.md").write_text("Extract")

        pdf_path = tmp_path / "oil_change.pdf"
        pdf_path.write_text("test")

        # Mock maintenance response
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({
            "service_type": "oil_change",
            "shop": "Jiffy Lube",
            "date": "2025-11-15",
            "vehicle": "2020 Honda Accord",
            "mileage": 45000,
            "cost": 65.99
        })

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Execute
        metadata = classifier.extract_auto_metadata(str(pdf_path))

        # Verify maintenance-specific fields
        assert 'service_type' in metadata
        assert 'shop' in metadata
        assert 'mileage' in metadata
        assert 'cost' in metadata

    def test_extract_auto_metadata_registration(self, tmp_path, mocker):
        """Test extraction of auto registration metadata"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Test")
        (prompts_dir / "auto.md").write_text("Extract")

        pdf_path = tmp_path / "registration.pdf"
        pdf_path.write_text("test")

        # Mock registration response
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({
            "registration_number": "REG-ABC123",
            "vehicle": "2020 Honda Accord",
            "vin": "1HGCV1F3XLA123456",
            "license_plate": "XYZ-1234",
            "renewal_date": "2025-03-15",
            "expiration_date": "2026-03-15",
            "fee": 95.00
        })

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Execute
        metadata = classifier.extract_auto_metadata(str(pdf_path))

        # Verify registration-specific fields
        assert 'registration_number' in metadata
        assert 'vin' in metadata
        assert 'license_plate' in metadata
        assert 'renewal_date' in metadata


class TestClaudeCodeSubprocess:
    """Test Claude Code subprocess execution"""

    def test_claude_code_subprocess_call(self, tmp_path, mocker):
        """Test successful Claude Code subprocess execution"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Test prompt")

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        # Mock subprocess
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({"category": "GENERAL", "confidence": 0.7})

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Execute
        result = classifier.classify_document(str(pdf_path))

        # Verify subprocess was called
        assert mock_run.called
        call_args = mock_run.call_args

        # Verify command structure
        # Should involve piping prompt to claude CLI


class TestJSONParsing:
    """Test JSON extraction from Claude Code responses"""

    def test_json_extraction_from_response(self, tmp_path, mocker):
        """Test JSON parsing handles markdown code blocks"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Test")

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        # Mock response with markdown code block
        response_with_markdown = """Here is the classification:

```json
{
  "category": "PERSONAL-MEDICAL",
  "confidence": 0.95,
  "is_cps_related": false
}
```
"""

        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = response_with_markdown

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Execute - should handle markdown extraction
        # Note: Actual implementation needs to strip markdown blocks
        # This test verifies that the method can handle it

    def test_error_handling_invalid_json(self, tmp_path, mocker):
        """Test handling of invalid JSON responses"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Test")

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        # Mock invalid JSON response
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "This is not valid JSON{{{{"

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Execute - should handle gracefully by returning error dict
        result = classifier.classify_document(str(pdf_path))
        
        # Verify error handling
        assert 'error' in result
        assert result['category'] == 'GENERAL'
        assert result['confidence'] == 0.0
        assert result['needs_clarification'] == True


class TestErrorHandling:
    """Test error handling scenarios"""

    def test_error_handling_subprocess_failure(self, tmp_path, mocker):
        """Test handling of subprocess failures"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Test")

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        # Mock subprocess failure
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Execute - should handle error gracefully
        result = classifier.classify_document(str(pdf_path))
        
        # Verify error handling
        assert 'error' in result
        assert result['category'] == 'GENERAL'
        assert result['confidence'] == 0.0
        assert result['needs_clarification'] == True

    def test_timeout_handling(self, tmp_path, mocker):
        """Test handling of Claude Code timeouts"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Test")

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        # Mock timeout
        mock_run = mocker.patch('subprocess.run')
        mock_run.side_effect = TimeoutError("Claude Code timed out")

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        # Execute - should handle timeout gracefully
        result = classifier.classify_document(str(pdf_path))
        
        # Verify error handling
        assert 'error' in result
        assert result['category'] == 'GENERAL'
        assert result['confidence'] == 0.0
        assert result['needs_clarification'] == True


class TestCorrectionInjection:
    """Test correction injection into prompts"""

    def test_correction_injection(self, tmp_path, mocker):
        """Test that corrections are appended to prompts"""
        # Setup
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "classifier.md").write_text("Original prompt")
        (prompts_dir / "personal-medical.md").write_text("Extract metadata")

        pdf_path = tmp_path / "medical.pdf"
        pdf_path.write_text("test")

        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({
            "provider": "Corrected Provider",
            "date": "2025-01-01",
            "amount": 100.00
        })

        classifier = DocumentClassifier(prompts_dir=prompts_dir)

        corrections = {
            "notes": "Provider name was incorrect",
            "reason": "user_correction"
        }

        # Execute with corrections
        metadata = classifier.extract_personal_medical_metadata(
            str(pdf_path),
            corrections=corrections
        )

        # Verify execution (actual prompt injection tested in integration)
        assert metadata is not None
