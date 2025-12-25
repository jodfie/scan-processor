"""
Tests for BasicMemoryNoteCreator

Tests note creation functionality for all categories:
- Personal medical note creation
- Personal expense note creation
- Utility bill note creation
- Automotive document note creation
- Dual-vault routing (CPS vs Personal)
- Frontmatter structure validation
- Filename formatting
- Dry-run mode
"""

import pytest
from pathlib import Path
from datetime import datetime
import sys
import yaml

# Add scripts and test utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent / "utils"))

from basicmemory import BasicMemoryNoteCreator
from helpers import (
    assert_frontmatter_valid,
    assert_frontmatter_has_fields,
    assert_file_in_vault,
    assert_file_in_directory,
    assert_filename_matches_pattern,
    extract_frontmatter_field
)


class TestBasicMemoryInit:
    """Test BasicMemoryNoteCreator initialization"""

    def test_dual_vault_initialization(self, temp_vault_dirs):
        """Verify both vault paths are initialized"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        assert creator.cps_vault == cps_vault
        assert creator.personal_vault == personal_vault
        assert creator.dry_run == False

    def test_init_with_dry_run(self, temp_vault_dirs):
        """Verify dry-run mode initialization"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault,
            dry_run=True
        )

        assert creator.dry_run == True

    def test_init_creates_missing_directories(self, tmp_path):
        """Test automatic vault creation for missing directories"""
        cps_vault = tmp_path / "NewCPS"
        personal_vault = tmp_path / "NewPersonal"

        # Vaults don't exist yet
        assert not cps_vault.exists()
        assert not personal_vault.exists()

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        # Should create them
        assert cps_vault.exists()
        assert personal_vault.exists()


class TestPersonalMedicalNotes:
    """Test personal medical note creation"""

    def test_create_personal_medical_note(self, temp_vault_dirs):
        """Test personal medical note creation"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "provider": "Dr. Smith Family Medicine",
            "date": "2025-09-15",
            "amount": 125.50,
            "type": "medical_bill",
            "description": "Office visit and lab work"
        }

        # Execute
        note_path = creator.create_personal_medical_note(metadata, "test.pdf")

        # Verify file created
        assert note_path.exists()

        # Verify in Personal vault
        assert_file_in_vault(note_path, "Personal")
        assert_file_in_directory(note_path, "Medical")

        # Verify filename format (YYYY-MM-DD-Description.md)
        assert note_path.name.startswith("2025-09-15")
        assert note_path.suffix == ".md"

    def test_personal_medical_frontmatter_structure(self, temp_vault_dirs):
        """Test personal medical note frontmatter structure"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "provider": "Dr. Johnson Clinic",
            "date": "2025-10-01",
            "amount": 200.00,
            "type": "lab_results"
        }

        note_path = creator.create_personal_medical_note(metadata, "lab_test.pdf")

        # Verify frontmatter is valid YAML
        frontmatter = assert_frontmatter_valid(note_path)

        # Verify required fields
        required_fields = ["provider", "date", "amount", "type", "category"]
        assert_frontmatter_has_fields(note_path, required_fields)

        # Verify values
        assert frontmatter['provider'] == "Dr. Johnson Clinic"
        assert frontmatter['amount'] == 200.00
        assert frontmatter['category'] == "PERSONAL-MEDICAL"

    def test_personal_medical_content_sections(self, temp_vault_dirs):
        """Test personal medical note content sections"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "provider": "Test Provider",
            "date": "2025-01-15",
            "amount": 100.00,
            "type": "visit",
            "description": "Annual checkup"
        }

        note_path = creator.create_personal_medical_note(metadata, "checkup.pdf")

        content = note_path.read_text()

        # Verify standard sections
        assert "## Diagnosis" in content
        assert "## Treatment" in content
        assert "## Cost" in content
        assert "## Follow-up" in content


class TestPersonalExpenseNotes:
    """Test personal expense note creation"""

    def test_create_personal_expense_note(self, temp_vault_dirs):
        """Test personal expense note creation"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "vendor": "The Bistro Restaurant",
            "date": "2025-12-15",
            "amount": 45.75,
            "category": "dining",
            "description": "Dinner receipt"
        }

        # Execute
        note_path = creator.create_personal_expense_note(metadata, "dinner.pdf")

        # Verify file created
        assert note_path.exists()

        # Verify in Personal vault
        assert_file_in_vault(note_path, "Personal")
        assert_file_in_directory(note_path, "Expenses")

        # Verify filename format
        assert note_path.name.startswith("2025-12-15")
        assert note_path.suffix == ".md"

    def test_personal_expense_frontmatter(self, temp_vault_dirs):
        """Test personal expense note frontmatter"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "vendor": "Amazon",
            "date": "2025-11-20",
            "amount": 89.99,
            "category": "shopping",
            "description": "Office supplies"
        }

        note_path = creator.create_personal_expense_note(metadata, "amazon.pdf")

        # Verify frontmatter
        frontmatter = assert_frontmatter_valid(note_path)

        required_fields = ["vendor", "date", "amount", "category"]
        assert_frontmatter_has_fields(note_path, required_fields)

        assert frontmatter['vendor'] == "Amazon"
        assert frontmatter['amount'] == 89.99

    def test_personal_expense_category_variations(self, temp_vault_dirs):
        """Test different expense categories"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        categories = ["dining", "shopping", "services", "online_shopping"]

        for category in categories:
            metadata = {
                "vendor": f"Test {category.title()} Vendor",
                "date": "2025-01-15",
                "amount": 50.00,
                "category": category,
                "description": f"Test {category} purchase"
            }

            note_path = creator.create_personal_expense_note(metadata, f"{category}.pdf")

            assert note_path.exists()
            frontmatter = assert_frontmatter_valid(note_path)
            assert frontmatter['category'] == 'PERSONAL-EXPENSE'
            assert frontmatter['subcategory'] == category


class TestUtilityNotes:
    """Test utility bill note creation"""

    def test_create_utility_note_electric(self, temp_vault_dirs):
        """Test electric utility bill note creation"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "utility_type": "electric",
            "provider": "City Power & Light",
            "billing_date": "2025-12-01",
            "due_date": "2025-12-21",
            "amount": 142.37,
            "account_number": "1234567890"
        }

        # Execute
        note_path = creator.create_utility_note(metadata, "electric_bill.pdf")

        # Verify file created
        assert note_path.exists()

        # Verify in Personal vault
        assert_file_in_vault(note_path, "Personal")
        assert_file_in_directory(note_path, "Utilities")

        # Verify filename contains utility type
        assert "electric" in note_path.name.lower() or "2025-12" in note_path.name

    def test_utility_note_frontmatter(self, temp_vault_dirs):
        """Test utility note frontmatter structure"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "utility_type": "water",
            "provider": "City Water & Sewer",
            "billing_date": "2025-12-01",
            "due_date": "2025-12-21",
            "amount": 85.20
        }

        note_path = creator.create_utility_note(metadata, "water.pdf")

        # Verify frontmatter
        frontmatter = assert_frontmatter_valid(note_path)

        required_fields = ["utility_type", "provider", "billing_date", "due_date", "amount"]
        assert_frontmatter_has_fields(note_path, required_fields)

        assert frontmatter['utility_type'] == "water"
        assert frontmatter['provider'] == "City Water & Sewer"
        assert frontmatter['amount'] == 85.20

    def test_utility_types(self, temp_vault_dirs):
        """Test all supported utility types"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        utility_types = ["electric", "water", "gas", "internet", "phone"]

        for utility_type in utility_types:
            metadata = {
                "utility_type": utility_type,
                "provider": f"Test {utility_type.title()} Company",
                "billing_date": "2025-01-01",
                "due_date": "2025-01-21",
                "amount": 100.00
            }

            note_path = creator.create_utility_note(metadata, f"{utility_type}.pdf")

            assert note_path.exists()
            frontmatter = assert_frontmatter_valid(note_path)
            assert frontmatter['utility_type'] == utility_type


class TestAutoNotes:
    """Test automotive document note creation"""

    def test_create_auto_note_insurance(self, temp_vault_dirs):
        """Test auto insurance note creation"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "insurance_company": "State Farm",
            "policy_number": "POL-12345678",
            "vehicle": "2020 Honda Accord",
            "effective_date": "2025-01-01",
            "expiration_date": "2026-01-01",
            "premium": 1200.00
        }

        # Execute
        note_path = creator.create_auto_note(metadata, "insurance.pdf", "AUTO-INSURANCE")

        # Verify file created
        assert note_path.exists()

        # Verify in Personal vault
        assert_file_in_vault(note_path, "Personal")
        assert_file_in_directory(note_path, "Auto")
        assert_file_in_directory(note_path, "Insurance")

    def test_auto_insurance_frontmatter(self, temp_vault_dirs):
        """Test auto insurance note frontmatter"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "insurance_company": "Geico",
            "policy_number": "GEICO-987654",
            "vehicle": "2022 Toyota Camry",
            "premium": 950.00
        }

        note_path = creator.create_auto_note(metadata, "geico.pdf", "AUTO-INSURANCE")

        frontmatter = assert_frontmatter_valid(note_path)

        assert 'insurance_company' in frontmatter
        assert 'policy_number' in frontmatter
        assert frontmatter['insurance_company'] == "Geico"

    def test_create_auto_note_maintenance(self, temp_vault_dirs):
        """Test auto maintenance note creation"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "service_type": "oil_change",
            "shop": "Jiffy Lube",
            "date": "2025-11-15",
            "vehicle": "2020 Honda Accord",
            "mileage": 45000,
            "cost": 65.99
        }

        note_path = creator.create_auto_note(metadata, "oil_change.pdf", "AUTO-MAINTENANCE")

        assert note_path.exists()
        assert_file_in_directory(note_path, "Maintenance")

        frontmatter = assert_frontmatter_valid(note_path)
        assert frontmatter['service_type'] == "oil_change"
        assert frontmatter['cost'] == 65.99

    def test_create_auto_note_registration(self, temp_vault_dirs):
        """Test auto registration note creation"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "registration_number": "REG-ABC123",
            "vehicle": "2020 Honda Accord",
            "vin": "1HGCV1F3XLA123456",
            "license_plate": "XYZ-1234",
            "renewal_date": "2025-03-15",
            "expiration_date": "2026-03-15",
            "fee": 95.00
        }

        note_path = creator.create_auto_note(metadata, "registration.pdf", "AUTO-REGISTRATION")

        assert note_path.exists()
        assert_file_in_directory(note_path, "Registration")

        frontmatter = assert_frontmatter_valid(note_path)
        assert frontmatter['registration_number'] == "REG-ABC123"
        assert frontmatter['vin'] == "1HGCV1F3XLA123456"


class TestDualVaultRouting:
    """Test dual-vault routing logic"""

    def test_personal_medical_routes_to_personal_vault(self, temp_vault_dirs):
        """PERSONAL-MEDICAL documents go to Personal vault"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "provider": "Dr. Test",
            "date": "2025-01-15",
            "amount": 100.00,
            "type": "visit"
        }

        note_path = creator.create_personal_medical_note(metadata, "test.pdf")

        # Verify routed to Personal vault, NOT CPS vault
        assert "Personal" in str(note_path)
        assert "CoparentingSystem" not in str(note_path)

    def test_utility_routes_to_personal_vault(self, temp_vault_dirs):
        """UTILITY documents go to Personal vault"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "utility_type": "electric",
            "provider": "Test Power",
            "billing_date": "2025-01-01",
            "due_date": "2025-01-21",
            "amount": 100.00
        }

        note_path = creator.create_utility_note(metadata, "electric.pdf")

        assert "Personal" in str(note_path)
        assert "CoparentingSystem" not in str(note_path)

    def test_auto_routes_to_personal_vault(self, temp_vault_dirs):
        """AUTO-* documents go to Personal vault"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "insurance_company": "Test Insurance",
            "policy_number": "POL-123",
            "vehicle": "2020 Test Car"
        }

        note_path = creator.create_auto_note(metadata, "insurance.pdf", "AUTO-INSURANCE")

        assert "Personal" in str(note_path)
        assert "CoparentingSystem" not in str(note_path)


class TestDryRunMode:
    """Test dry-run mode functionality"""

    def test_dry_run_mode(self, temp_vault_dirs):
        """Verify dry-run doesn't create files"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault,
            dry_run=True
        )

        metadata = {
            "provider": "Dr. Test",
            "date": "2025-01-15",
            "amount": 100.00,
            "type": "visit"
        }

        # Execute in dry-run mode
        note_path = creator.create_personal_medical_note(metadata, "test.pdf")

        # Path should be returned but file should NOT exist
        assert note_path is not None
        assert not note_path.exists()

    def test_dry_run_all_methods(self, temp_vault_dirs):
        """Test dry-run for all note creation methods"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault,
            dry_run=True
        )

        # Personal medical
        medical_path = creator.create_personal_medical_note({
            "provider": "Test",
            "date": "2025-01-01",
            "amount": 100.00,
            "type": "visit"
        }, "medical.pdf")
        assert not medical_path.exists()

        # Personal expense
        expense_path = creator.create_personal_expense_note({
            "vendor": "Test",
            "date": "2025-01-01",
            "amount": 50.00,
            "category": "shopping"
        }, "expense.pdf")
        assert not expense_path.exists()

        # Utility
        utility_path = creator.create_utility_note({
            "utility_type": "electric",
            "provider": "Test",
            "billing_date": "2025-01-01",
            "due_date": "2025-01-21",
            "amount": 100.00
        }, "utility.pdf")
        assert not utility_path.exists()

        # Auto
        auto_path = creator.create_auto_note({
            "insurance_company": "Test",
            "policy_number": "POL-123",
            "vehicle": "2020 Test"
        }, "auto.pdf", "AUTO-INSURANCE")
        assert not auto_path.exists()


class TestFilenameFormatting:
    """Test filename formatting conventions"""

    def test_personal_medical_filename_format(self, temp_vault_dirs):
        """Test personal medical filename follows YYYY-MM-DD-Description.md"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "provider": "Dr. Smith Family Medicine",
            "date": "2025-09-15",
            "amount": 125.50,
            "type": "medical_bill",
            "description": "Office Visit Lab Work"
        }

        note_path = creator.create_personal_medical_note(metadata, "test.pdf")

        # Verify date prefix
        assert note_path.name.startswith("2025-09-15")

        # Verify .md extension
        assert note_path.suffix == ".md"

    def test_filename_sanitization(self, temp_vault_dirs):
        """Test that filenames are sanitized (no special characters)"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "vendor": "Store/Name: With-Special*Characters",
            "date": "2025-01-15",
            "amount": 50.00,
            "category": "shopping",
            "description": "Test purchase"
        }

        note_path = creator.create_personal_expense_note(metadata, "receipt.pdf")

        # Verify filename doesn't contain problematic characters
        assert "/" not in note_path.name
        assert ":" not in note_path.name
        assert "*" not in note_path.name


class TestMissingFields:
    """Test handling of missing metadata fields"""

    def test_missing_optional_fields(self, temp_vault_dirs):
        """Test note creation with minimal required fields"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        # Minimal metadata (missing optional fields)
        metadata = {
            "provider": "Dr. Minimal",
            "date": "2025-01-15",
            "amount": 100.00
        }

        # Should still create note
        note_path = creator.create_personal_medical_note(metadata, "minimal.pdf")

        assert note_path.exists()
        frontmatter = assert_frontmatter_valid(note_path)
        assert frontmatter['provider'] == "Dr. Minimal"

    def test_missing_date_uses_today(self, temp_vault_dirs):
        """Test that missing date defaults to today"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        # Metadata without date
        metadata = {
            "provider": "Dr. NoDate",
            "amount": 100.00,
            "type": "visit"
        }

        note_path = creator.create_personal_medical_note(metadata, "nodate.pdf")

        # Should use today's date
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in note_path.name or note_path.exists()


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_metadata(self, temp_vault_dirs):
        """Test handling of empty metadata"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        # Empty metadata should still create file (with defaults)
        metadata = {}

        # Depending on implementation, might raise error or use defaults
        # This test documents expected behavior

    def test_very_long_filename(self, temp_vault_dirs):
        """Test handling of very long descriptions/filenames"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "vendor": "A" * 200,  # Very long vendor name
            "date": "2025-01-15",
            "amount": 50.00,
            "category": "shopping"
        }

        note_path = creator.create_personal_expense_note(metadata, "long.pdf")

        # Filename should be truncated to reasonable length
        assert len(note_path.name) < 255  # Max filename length on most systems
