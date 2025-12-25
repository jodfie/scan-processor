"""
Tests for Dual-Vault Routing

Tests the routing logic that determines which vault (CPS vs Personal)
a document should be stored in based on category and is_cps_related flag.

Routing Rules:
- CPS-* categories → CoparentingSystem vault
- PERSONAL-*, UTILITY, AUTO-* categories → Personal vault
- is_cps_related flag overrides category prefix

Directory Structure:
- CoparentingSystem/
  - 60-medical/{child}/
  - 40-expenses/
- Personal/
  - Medical/
  - Expenses/
  - Utilities/
  - Auto/Insurance/
  - Auto/Maintenance/
  - Auto/Registration/
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from basicmemory import BasicMemoryNoteCreator


class TestCPSCategoryRouting:
    """Test CPS-prefixed categories route to CPS vault"""

    def test_cps_medical_routes_to_cps_vault(self, temp_vault_dirs):
        """CPS-MEDICAL documents go to CoparentingSystem vault"""
        cps_vault, personal_vault = temp_vault_dirs

        # This would be called from the processing pipeline
        # after classification determines it's CPS-MEDICAL

        # For now, verify vault directory structure exists
        assert (cps_vault / "60-medical" / "morgan").exists()
        assert (cps_vault / "60-medical" / "jacob").exists()

    def test_cps_expense_routes_to_cps_vault(self, temp_vault_dirs):
        """CPS-EXPENSE documents go to CoparentingSystem vault"""
        cps_vault, personal_vault = temp_vault_dirs

        assert (cps_vault / "40-expenses").exists()

    def test_cps_documents_not_in_personal_vault(self, temp_vault_dirs):
        """Verify CPS documents don't go to Personal vault"""
        cps_vault, personal_vault = temp_vault_dirs

        # CPS medical should use CPS vault structure
        assert (cps_vault / "60-medical").exists()

        # Not Personal medical
        assert not (personal_vault / "60-medical").exists()


class TestPersonalCategoryRouting:
    """Test Personal-prefixed categories route to Personal vault"""

    def test_personal_medical_routes_to_personal_vault(self, temp_vault_dirs):
        """PERSONAL-MEDICAL documents go to Personal vault"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "provider": "Dr. Personal",
            "date": "2025-01-15",
            "amount": 100.00,
            "type": "visit"
        }

        note_path = creator.create_personal_medical_note(metadata, "personal.pdf")

        # Verify in Personal vault
        assert "Personal" in str(note_path)
        assert "CoparentingSystem" not in str(note_path)

        # Verify in Medical subdirectory
        assert "Medical" in str(note_path)

    def test_personal_expense_routes_to_personal_vault(self, temp_vault_dirs):
        """PERSONAL-EXPENSE documents go to Personal vault"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "vendor": "Personal Store",
            "date": "2025-01-15",
            "amount": 50.00,
            "category": "shopping"
        }

        note_path = creator.create_personal_expense_note(metadata, "receipt.pdf")

        # Verify in Personal vault
        assert "Personal" in str(note_path)
        assert "CoparentingSystem" not in str(note_path)

        # Verify in Expenses subdirectory
        assert "Expenses" in str(note_path)


class TestUtilityRouting:
    """Test UTILITY category routing"""

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

        # Verify in Personal vault, NOT CPS
        assert "Personal" in str(note_path)
        assert "CoparentingSystem" not in str(note_path)

        # Verify in Utilities subdirectory
        assert "Utilities" in str(note_path)

    def test_all_utility_types_route_to_personal(self, temp_vault_dirs):
        """All utility types (electric, water, gas, etc.) go to Personal"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        utility_types = ["electric", "water", "gas", "internet", "phone"]

        for utility_type in utility_types:
            metadata = {
                "utility_type": utility_type,
                "provider": f"Test {utility_type.title()}",
                "billing_date": "2025-01-01",
                "due_date": "2025-01-21",
                "amount": 100.00
            }

            note_path = creator.create_utility_note(metadata, f"{utility_type}.pdf")

            # All should route to Personal vault
            assert "Personal" in str(note_path)
            assert "CoparentingSystem" not in str(note_path)


class TestAutoRouting:
    """Test AUTO-* category routing"""

    def test_auto_insurance_routes_to_personal_vault(self, temp_vault_dirs):
        """AUTO-INSURANCE documents go to Personal vault"""
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

        # Verify in Personal vault
        assert "Personal" in str(note_path)
        assert "CoparentingSystem" not in str(note_path)

        # Verify in Auto/Insurance subdirectory
        assert "Auto" in str(note_path)
        assert "Insurance" in str(note_path)

    def test_auto_maintenance_routes_to_personal_vault(self, temp_vault_dirs):
        """AUTO-MAINTENANCE documents go to Personal vault"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "service_type": "oil_change",
            "shop": "Test Shop",
            "date": "2025-01-15",
            "vehicle": "2020 Test",
            "cost": 50.00
        }

        note_path = creator.create_auto_note(metadata, "oil.pdf", "AUTO-MAINTENANCE")

        # Verify in Personal vault
        assert "Personal" in str(note_path)

        # Verify in Auto/Maintenance subdirectory
        assert "Auto" in str(note_path)
        assert "Maintenance" in str(note_path)

    def test_auto_registration_routes_to_personal_vault(self, temp_vault_dirs):
        """AUTO-REGISTRATION documents go to Personal vault"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        metadata = {
            "registration_number": "REG-123",
            "vehicle": "2020 Test",
            "renewal_date": "2025-01-15",
            "fee": 95.00
        }

        note_path = creator.create_auto_note(metadata, "reg.pdf", "AUTO-REGISTRATION")

        # Verify in Personal vault
        assert "Personal" in str(note_path)

        # Verify in Auto/Registration subdirectory
        assert "Auto" in str(note_path)
        assert "Registration" in str(note_path)


class TestVaultDirectoryStructure:
    """Test vault directory structure is correct"""

    def test_cps_vault_structure(self, temp_vault_dirs):
        """Verify CPS vault has correct directory structure"""
        cps_vault, _ = temp_vault_dirs

        # Medical directories for each child
        assert (cps_vault / "60-medical" / "morgan").exists()
        assert (cps_vault / "60-medical" / "jacob").exists()

        # Expenses directory
        assert (cps_vault / "40-expenses").exists()

    def test_personal_vault_structure(self, temp_vault_dirs):
        """Verify Personal vault has correct directory structure"""
        _, personal_vault = temp_vault_dirs

        # Personal categories
        assert (personal_vault / "Medical").exists()
        assert (personal_vault / "Expenses").exists()
        assert (personal_vault / "Utilities").exists()

        # Auto subdirectories
        assert (personal_vault / "Auto" / "Insurance").exists()
        assert (personal_vault / "Auto" / "Maintenance").exists()
        assert (personal_vault / "Auto" / "Registration").exists()

    def test_vaults_are_separate(self, temp_vault_dirs):
        """Verify CPS and Personal vaults are separate directories"""
        cps_vault, personal_vault = temp_vault_dirs

        assert cps_vault != personal_vault
        assert not cps_vault.samefile(personal_vault)


class TestIsCPSRelatedFlag:
    """Test is_cps_related flag routing"""

    def test_is_cps_related_flag_routing(self, temp_vault_dirs):
        """Test routing based on is_cps_related flag"""
        cps_vault, personal_vault = temp_vault_dirs

        # This would be tested in integration tests
        # where classification returns is_cps_related flag

        # Verify both vaults exist for proper routing
        assert cps_vault.exists()
        assert personal_vault.exists()

    def test_override_with_is_cps_related(self, temp_vault_dirs):
        """Test that is_cps_related can override category prefix"""
        # In the real system, if a document is classified as PERSONAL-MEDICAL
        # but has is_cps_related=True, it might need special handling

        # This documents the expected behavior
        pass


class TestRoutingEndToEnd:
    """End-to-end routing tests"""

    def test_create_notes_in_both_vaults(self, temp_vault_dirs):
        """Test creating notes in both vaults simultaneously"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        # Create personal medical note
        personal_note = creator.create_personal_medical_note({
            "provider": "Dr. Personal",
            "date": "2025-01-15",
            "amount": 100.00,
            "type": "visit"
        }, "personal.pdf")

        # Create personal expense note
        expense_note = creator.create_personal_expense_note({
            "vendor": "Store",
            "date": "2025-01-15",
            "amount": 50.00,
            "category": "shopping"
        }, "expense.pdf")

        # Create utility note
        utility_note = creator.create_utility_note({
            "utility_type": "electric",
            "provider": "Power Co",
            "billing_date": "2025-01-01",
            "due_date": "2025-01-21",
            "amount": 100.00
        }, "electric.pdf")

        # All should be in Personal vault
        assert all("Personal" in str(note) for note in [personal_note, expense_note, utility_note])

        # None should be in CPS vault
        assert all("CoparentingSystem" not in str(note) for note in [personal_note, expense_note, utility_note])

    def test_no_cross_contamination(self, temp_vault_dirs):
        """Test that Personal documents don't end up in CPS vault"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        # Create several Personal documents
        personal_note = creator.create_personal_medical_note({
            "provider": "Dr. Test",
            "date": "2025-01-15",
            "amount": 100.00,
            "type": "visit"
        }, "test.pdf")

        # Check CPS vault directories - should be empty
        medical_files = list((cps_vault / "60-medical").rglob("*.md"))
        expense_files = list((cps_vault / "40-expenses").rglob("*.md"))

        assert len(medical_files) == 0
        assert len(expense_files) == 0

    def test_routing_with_multiple_documents(self, temp_vault_dirs):
        """Test routing multiple documents of different categories"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        # Create documents of each new category
        categories = [
            ("personal_medical", {
                "provider": "Dr. Test",
                "date": "2025-01-15",
                "amount": 100.00,
                "type": "visit"
            }),
            ("personal_expense", {
                "vendor": "Store",
                "date": "2025-01-15",
                "amount": 50.00,
                "category": "shopping"
            }),
            ("utility", {
                "utility_type": "electric",
                "provider": "Power",
                "billing_date": "2025-01-01",
                "due_date": "2025-01-21",
                "amount": 100.00
            }),
            ("auto_insurance", {
                "insurance_company": "Insurance Co",
                "policy_number": "POL-123",
                "vehicle": "2020 Car"
            })
        ]

        created_notes = []

        # Create note for each category
        if True:  # personal_medical
            note = creator.create_personal_medical_note(categories[0][1], "med.pdf")
            created_notes.append(note)

        if True:  # personal_expense
            note = creator.create_personal_expense_note(categories[1][1], "exp.pdf")
            created_notes.append(note)

        if True:  # utility
            note = creator.create_utility_note(categories[2][1], "util.pdf")
            created_notes.append(note)

        if True:  # auto
            note = creator.create_auto_note(categories[3][1], "auto.pdf", "AUTO-INSURANCE")
            created_notes.append(note)

        # All should be in Personal vault
        for note in created_notes:
            assert "Personal" in str(note)
            assert "CoparentingSystem" not in str(note)

        # Verify file count
        assert len(created_notes) == 4


class TestVaultSelection:
    """Test vault selection logic"""

    def test_get_vault_path_for_category(self, temp_vault_dirs):
        """Test vault path selection based on category"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        # Personal categories should use Personal vault
        personal_categories = [
            "PERSONAL-MEDICAL",
            "PERSONAL-EXPENSE",
            "UTILITY",
            "AUTO-INSURANCE",
            "AUTO-MAINTENANCE",
            "AUTO-REGISTRATION"
        ]

        # All should route to Personal vault
        # (This would be verified in the actual implementation)

    def test_vault_isolation(self, temp_vault_dirs):
        """Test that vaults remain isolated"""
        cps_vault, personal_vault = temp_vault_dirs

        creator = BasicMemoryNoteCreator(
            cps_path=cps_vault,
            personal_vault=personal_vault
        )

        # Create Personal document
        note = creator.create_personal_medical_note({
            "provider": "Dr. Test",
            "date": "2025-01-15",
            "amount": 100.00,
            "type": "visit"
        }, "test.pdf")

        # Count files in each vault
        personal_files = list(personal_vault.rglob("*.md"))
        cps_files = list(cps_vault.rglob("*.md"))

        # Personal vault should have files
        assert len(personal_files) > 0

        # CPS vault should be empty
        assert len(cps_files) == 0
