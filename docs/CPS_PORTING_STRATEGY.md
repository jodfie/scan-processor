# CPS Scanner Porting Strategy

**Strategic guide for porting improvements from scan-processor to CPS scanner.**

This document outlines which features should be ported to the CPS scanner, which should remain scan-processor-specific, and how to generalize code for reuse across both systems.

---

## Table of Contents

1. [Overview](#overview)
2. [Generalizable Improvements](#generalizable-improvements)
3. [Personal-Specific Code (DO NOT PORT)](#personal-specific-code-do-not-port)
4. [Porting Phases](#porting-phases)
5. [Generalization Patterns](#generalization-patterns)
6. [Migration Checklist](#migration-checklist)
7. [Testing Strategy](#testing-strategy)

---

## Overview

### Two Scanner Systems

**scan-processor** (this repository):
- **Purpose**: Process personal documents (medical, expenses, utilities, auto)
- **Vaults**: CoparentingSystem (CPS) + Personal vault
- **Categories**: 29 total (6 CPS + 23 Personal)
- **Focus**: Dual-vault routing, personal document types

**CPS scanner** (separate repository):
- **Purpose**: Process co-parenting documents only
- **Vaults**: CoparentingSystem only (or configurable)
- **Categories**: 6 CPS categories (MEDICAL, EXPENSE, SCHOOLWORK, CUSTODY, COMMUNICATION, LEGAL)
- **Focus**: Children-related documents, co-parenting workflow

### Porting Goal

Extract **generalizable** improvements from scan-processor and apply them to CPS scanner, while keeping **personal-specific** features separate.

---

## Generalizable Improvements

These features should be ported to CPS scanner:

### 1. Testing Infrastructure ✅ PORT

**What**: Complete pytest test suite with fixtures, mocks, and sample generation

**Why**: CPS scanner currently has no automated tests

**Files to Port**:
- `tests/conftest.py` - Core fixtures (adapt for CPS categories)
- `tests/utils/mocks.py` - Mock objects (reusable)
- `tests/utils/helpers.py` - Helper functions (reusable)
- `pytest.ini` - Pytest configuration
- `requirements-dev.txt` - Development dependencies
- `docs/TESTING_GUIDE.md` - Testing documentation

**Adaptation Required**:
- Replace Personal category fixtures with CPS-only fixtures
- Create CPS-specific sample documents (not personal ones)
- Adjust vault fixtures (may only need CPS vault)

**Example**:
```python
# scan-processor (dual-vault)
@pytest.fixture
def temp_vault_dirs(tmp_path):
    cps_vault = tmp_path / "CoparentingSystem"
    personal_vault = tmp_path / "Personal"
    return cps_vault, personal_vault

# CPS scanner (single vault or configurable)
@pytest.fixture
def temp_vault_dir(tmp_path):
    cps_vault = tmp_path / "CoparentingSystem"
    # Create CPS-specific structure
    return cps_vault
```

### 2. Enhanced Database Logging ✅ PORT

**What**: Store prompts, responses, corrections in database

**Why**: Better debugging, re-processing capability, transparency

**Database Changes**:
```sql
ALTER TABLE processing_history ADD COLUMN classification_prompt TEXT;
ALTER TABLE processing_history ADD COLUMN classification_response TEXT;
ALTER TABLE processing_history ADD COLUMN metadata_prompt TEXT;
ALTER TABLE processing_history ADD COLUMN metadata_response TEXT;
ALTER TABLE processing_history ADD COLUMN files_created TEXT;  -- JSON
ALTER TABLE processing_history ADD COLUMN corrections TEXT;     -- JSON
```

**Files to Port**:
- Database schema changes from `scripts/process.py`
- Logging logic from `scripts/classifier.py`
- Re-processing with corrections logic

**Adaptation Required**:
- None - this is fully generalizable

### 3. Re-Processing with Corrections ✅ PORT

**What**: Allow users to provide corrections and re-process documents

**Why**: Improves classification accuracy over time

**Files to Port**:
- Corrections workflow from `scripts/process.py`
- Corrections modal from `web/` (if CPS scanner has web UI)
- Correction injection logic in `scripts/classifier.py`

**Adaptation Required**:
- None - this is fully generalizable

**Example**:
```python
# Fully generalizable
def classify_with_corrections(self, file_path, corrections=None):
    prompt_text = self._load_prompt("classifier.md")

    if corrections:
        correction_text = f"\n\n## User Corrections\n\n{corrections['notes']}\n"
        correction_text += f"Reason: {corrections['reason']}\n"
        prompt_text += correction_text

    # Continue with classification
```

### 4. Improved Error Handling ✅ PORT

**What**: Better error messages, graceful failures, retry logic

**Why**: More robust processing, better user experience

**Files to Port**:
- Error handling patterns from `scripts/classifier.py`
- Error handling patterns from `scripts/process.py`
- Failed file handling (move to failed/ directory)

**Adaptation Required**:
- None - error handling is universal

### 5. Dev Mode Enhancements ✅ PORT

**What**: Enhanced development mode with dry-run, verbose logging

**Why**: Easier testing without affecting production data

**Files to Port**:
- `--dev` flag handling from `scripts/process.py`
- Dry-run logic from `scripts/basicmemory.py`
- Verbose logging in dev mode

**Adaptation Required**:
- None - dev mode is universal

**Example**:
```python
# Fully generalizable
def process_document(file_path, dev_mode=False):
    if dev_mode:
        print(f"[DEV MODE] Would upload to Paperless: {file_path}")
        print(f"[DEV MODE] Would create BasicMemory note")
        return {"status": "dev_mode", "uploaded": False}

    # Actual processing
```

### 6. Sample Document Testing Approach ✅ PORT

**What**: Generate realistic sample PDFs for testing

**Why**: Validate classification without real sensitive documents

**Files to Port**:
- Sample generation approach from `scripts/generate_samples.py`
- `samples/README.md` structure

**Adaptation Required**:
- Create CPS-specific samples only (medical bills for children, school expenses, etc.)
- Remove personal category samples

**Example CPS Samples**:
- Children's medical bills
- School expense receipts
- Custody schedule documents
- Co-parent communication logs

### 7. Dual-Vault Architecture (Generalized) ⚠️ ADAPT

**What**: Support for multiple vaults with configurable routing

**Why**: CPS scanner might need secondary vault in future, or make vault paths configurable

**Files to Port**:
- Vault routing logic from `scripts/basicmemory.py` (generalized)
- Configuration approach for vault paths

**Adaptation Required**:
- **Significant** - Make vault routing configurable
- CPS scanner may only need one vault initially
- But architecture should support multiple vaults if needed

**Generalization Pattern**:
```python
# Before (scan-processor hardcoded)
if category.startswith('CPS-'):
    vault_path = '/home/jodfie/vault/jodys-brain/CoparentingSystem'
else:
    vault_path = '/home/jodfie/vault/jodys-brain/Personal'

# After (generalized with config)
class VaultRouter:
    def __init__(self, primary_vault, secondary_vault=None):
        self.primary_vault = primary_vault
        self.secondary_vault = secondary_vault

    def get_vault_for_category(self, category):
        if self.secondary_vault and self._is_secondary_category(category):
            return self.secondary_vault
        return self.primary_vault

    def _is_secondary_category(self, category):
        # Configurable logic
        return category.startswith('PERSONAL-')
```

---

## Personal-Specific Code (DO NOT PORT)

These features should **remain in scan-processor only**:

### 1. Personal Document Categories ❌ DO NOT PORT

**Categories to Exclude from CPS Scanner**:
- PERSONAL-MEDICAL
- PERSONAL-EXPENSE
- UTILITY
- AUTO-INSURANCE
- AUTO-MAINTENANCE
- AUTO-REGISTRATION
- RECEIPT
- INVOICE
- TAX-DOCUMENT
- BANK-STATEMENT
- INVESTMENT
- MORTGAGE
- LEASE
- HOME-MAINTENANCE
- PROPERTY-TAX
- PRESCRIPTION
- INSURANCE
- CONTRACT
- LEGAL-DOCUMENT
- TRAVEL-BOOKING
- TRAVEL-RECEIPT
- GENERAL
- REFERENCE

**Files NOT to Port**:
- `prompts/personal-medical.md`
- `prompts/personal-expense.md`
- `prompts/utility.md`
- `prompts/auto.md`

### 2. Personal Vault Paths ❌ DO NOT PORT

**Hardcoded Personal Paths**:
```python
# DO NOT PORT to CPS scanner
personal_vault = '/home/jodfie/vault/jodys-brain/Personal'
personal_medical_path = personal_vault / "Medical"
personal_expense_path = personal_vault / "Expenses"
utilities_path = personal_vault / "Utilities"
auto_insurance_path = personal_vault / "Auto" / "Insurance"
# etc.
```

### 3. Personal-Specific Extraction Methods ❌ DO NOT PORT

**Methods NOT to Port**:
```python
# These are personal-specific
classifier.extract_personal_medical_metadata()
classifier.extract_personal_expense_metadata()
classifier.extract_utility_metadata()
classifier.extract_auto_metadata()

# These are personal-specific
creator.create_personal_medical_note()
creator.create_personal_expense_note()
creator.create_utility_note()
creator.create_auto_note()
```

### 4. Personal Document Templates ❌ DO NOT PORT

**Templates NOT to Port**:
- Personal medical note template
- Personal expense note template
- Utility note template
- Auto document templates

---

## Porting Phases

### Phase 1: Port Testing Infrastructure (1-2 days)

**Goal**: Get CPS scanner under test coverage

**Steps**:
1. Create `tests/` directory structure in CPS scanner repo
2. Copy and adapt `conftest.py` (remove Personal vault, keep CPS only)
3. Copy `utils/mocks.py` and `utils/helpers.py` (fully reusable)
4. Copy `pytest.ini` and `requirements-dev.txt`
5. Create CPS-specific sample documents (6 categories)
6. Write initial tests for existing CPS categories

**Deliverables**:
- [ ] `tests/` directory created
- [ ] Core fixtures adapted for CPS
- [ ] 18-24 CPS sample documents generated (3-4 per category)
- [ ] Basic tests for CPS-MEDICAL, CPS-EXPENSE, CPS-SCHOOLWORK
- [ ] Test suite runs successfully

### Phase 2: Port Enhanced Logging (1 day)

**Goal**: Add prompts/responses to database

**Steps**:
1. Update database schema (add new columns)
2. Modify `scripts/classifier.py` to log prompts/responses
3. Modify `scripts/process.py` to log to new columns
4. Create database migration script
5. Test logging with sample documents

**Deliverables**:
- [ ] Database schema updated
- [ ] Migration script created
- [ ] Logging implemented and tested
- [ ] Historical data preserved

### Phase 3: Port Corrections Workflow (1 day)

**Goal**: Enable re-processing with corrections

**Steps**:
1. Add `--corrections` flag to `scripts/process.py`
2. Implement correction injection in prompts
3. Update database to track corrections
4. Add web UI corrections modal (if CPS scanner has web UI)
5. Test re-processing workflow

**Deliverables**:
- [ ] Corrections flag implemented
- [ ] Correction injection works
- [ ] Database tracks corrections
- [ ] End-to-end re-processing tested

### Phase 4: Port Error Handling & Dev Mode (0.5 days)

**Goal**: Improve robustness and testing

**Steps**:
1. Copy error handling patterns from scan-processor
2. Enhance `--dev` flag functionality
3. Add dry-run mode
4. Improve error messages
5. Test error scenarios

**Deliverables**:
- [ ] Error handling improved
- [ ] Dev mode enhanced
- [ ] Dry-run mode works
- [ ] Error paths tested

### Phase 5: Generalize Vault Architecture (1-2 days)

**Goal**: Make vault routing configurable

**Steps**:
1. Create `VaultRouter` class (see generalization pattern)
2. Make vault paths configurable (environment variables or config file)
3. Update `basicmemory.py` to use `VaultRouter`
4. Test with CPS vault only
5. Test with CPS + optional secondary vault

**Deliverables**:
- [ ] `VaultRouter` class created
- [ ] Vault paths configurable
- [ ] Works with single vault (CPS)
- [ ] Works with optional secondary vault
- [ ] Tests updated

### Phase 6: Documentation & Validation (0.5 days)

**Goal**: Document changes and validate

**Steps**:
1. Update CPS scanner `CLAUDE.md`
2. Create CPS scanner `TESTING_GUIDE.md`
3. Update `README.md` with new features
4. Run full test suite
5. Validate with sample documents

**Deliverables**:
- [ ] Documentation updated
- [ ] Tests passing (≥ 80% coverage)
- [ ] Sample documents validated
- [ ] Production-ready

**Total Estimated Effort**: 5-7 days

---

## Generalization Patterns

### Pattern 1: Configurable Vault Paths

**Before (scan-processor hardcoded)**:
```python
class BasicMemoryNoteCreator:
    def __init__(self, cps_path, personal_vault):
        self.cps_path = Path(cps_path)
        self.personal_vault = Path(personal_vault)
```

**After (CPS scanner generalized)**:
```python
class BasicMemoryNoteCreator:
    def __init__(self, primary_vault, secondary_vault=None):
        self.primary_vault = Path(primary_vault)
        self.secondary_vault = Path(secondary_vault) if secondary_vault else None
```

### Pattern 2: Conditional Category Routing

**Before (scan-processor hardcoded)**:
```python
if category.startswith('CPS-'):
    return self._create_cps_note(metadata, category)
elif category == 'PERSONAL-MEDICAL':
    return self.create_personal_medical_note(metadata, filename)
elif category == 'UTILITY':
    return self.create_utility_note(metadata, filename)
# ... many more conditions
```

**After (CPS scanner generalized)**:
```python
class VaultRouter:
    def __init__(self, category_vault_map):
        self.category_vault_map = category_vault_map

    def get_vault_for_category(self, category):
        return self.category_vault_map.get(category, self.primary_vault)

# Configuration
router = VaultRouter({
    'CPS-MEDICAL': cps_vault,
    'CPS-EXPENSE': cps_vault,
    'CPS-SCHOOLWORK': cps_vault,
    # Future: 'SECONDARY-CATEGORY': secondary_vault
})
```

### Pattern 3: Extraction Method Registry

**Before (scan-processor hardcoded)**:
```python
if category == "MEDICAL":
    return self.extract_medical_metadata(file_path)
elif category == "CPS_EXPENSE":
    return self.extract_expense_metadata(file_path)
elif category == "PERSONAL-MEDICAL":
    return self.extract_personal_medical_metadata(file_path)
# ... many more conditions
```

**After (CPS scanner generalized)**:
```python
class DocumentClassifier:
    def __init__(self):
        self.extraction_methods = {
            'MEDICAL': self.extract_medical_metadata,
            'CPS_EXPENSE': self.extract_expense_metadata,
            # Register extraction methods dynamically
        }

    def extract_metadata(self, category, file_path):
        method = self.extraction_methods.get(category)
        if method:
            return method(file_path)
        else:
            return self._extract_generic_metadata(file_path)
```

### Pattern 4: Configuration Files

**Before (scan-processor hardcoded)**:
```python
# Hardcoded in Python
CPS_VAULT = '/home/jodfie/vault/jodys-brain/CoparentingSystem'
PERSONAL_VAULT = '/home/jodfie/vault/jodys-brain/Personal'
```

**After (CPS scanner generalized)**:
```python
# config.yaml
vaults:
  primary: /home/jodfie/vault/jodys-brain/CoparentingSystem
  secondary: null  # Optional

categories:
  cps:
    - CPS-MEDICAL
    - CPS-EXPENSE
    - CPS-SCHOOLWORK
```

```python
# Load from config
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

creator = BasicMemoryNoteCreator(
    primary_vault=config['vaults']['primary'],
    secondary_vault=config['vaults'].get('secondary')
)
```

---

## Migration Checklist

### Pre-Migration

- [ ] Review all scan-processor changes since last CPS sync
- [ ] Identify generalizable vs personal-specific code
- [ ] Create feature branch in CPS scanner repo: `feature/testing-and-logging`
- [ ] Back up CPS scanner database
- [ ] Document current CPS scanner state

### Phase 1: Testing Infrastructure

- [ ] Create `tests/` directory structure
- [ ] Copy and adapt `conftest.py`
- [ ] Copy `utils/mocks.py` and `utils/helpers.py`
- [ ] Copy `pytest.ini` and `requirements-dev.txt`
- [ ] Install dev dependencies
- [ ] Create CPS-specific sample generator
- [ ] Generate 18-24 CPS sample documents
- [ ] Write basic tests for CPS categories
- [ ] Run tests - verify passing
- [ ] Measure initial coverage

### Phase 2: Enhanced Logging

- [ ] Create database migration script
- [ ] Run migration on test database
- [ ] Update `classifier.py` to log prompts/responses
- [ ] Update `process.py` to log to new columns
- [ ] Test logging with sample documents
- [ ] Verify database contains prompts/responses
- [ ] Update web UI to display new data (if applicable)

### Phase 3: Corrections Workflow

- [ ] Add `--corrections` flag to `process.py`
- [ ] Implement correction injection in classifier
- [ ] Update database schema for corrections
- [ ] Test re-processing with corrections
- [ ] Add web UI corrections modal (if applicable)
- [ ] Verify corrections are logged and applied

### Phase 4: Error Handling & Dev Mode

- [ ] Copy error handling patterns
- [ ] Enhance `--dev` flag
- [ ] Add dry-run mode
- [ ] Test error scenarios
- [ ] Update documentation

### Phase 5: Vault Architecture (Optional)

- [ ] Create `VaultRouter` class
- [ ] Make vault paths configurable
- [ ] Update `basicmemory.py` to use router
- [ ] Test with CPS vault only
- [ ] Test with optional secondary vault
- [ ] Update tests

### Phase 6: Documentation & Validation

- [ ] Update `CLAUDE.md`
- [ ] Create/update `TESTING_GUIDE.md`
- [ ] Update `README.md`
- [ ] Run full test suite (≥ 80% coverage)
- [ ] Validate all CPS samples
- [ ] Create PR for review
- [ ] Merge to main
- [ ] Deploy to production
- [ ] Monitor for issues

---

## Testing Strategy

### Test Coverage Goals

**CPS Scanner Target Coverage**:
- Overall: ≥ 80%
- `classifier.py`: ≥ 85%
- `basicmemory.py`: ≥ 85%
- `process.py`: ≥ 85%

### CPS-Specific Sample Documents

Create 3-4 samples per CPS category:

**CPS-MEDICAL** (9 samples):
- Children's doctor visit bills (3)
- Children's lab results (2)
- Children's prescription receipts (2)
- Children's medical imaging bills (2)

**CPS-EXPENSE** (6 samples):
- School supply receipts (2)
- Activity fees (2)
- Childcare invoices (2)

**CPS-SCHOOLWORK** (3 samples):
- Report cards (1)
- Homework assignments (1)
- School projects (1)

**CPS-CUSTODY** (3 samples):
- Custody schedules (1)
- Visitation logs (1)
- Exchange records (1)

**CPS-COMMUNICATION** (3 samples):
- Email exchanges with co-parent (1)
- Text message logs (1)
- Communication logs (1)

**CPS-LEGAL** (3 samples):
- Court orders (1)
- Custody decree updates (1)
- Legal correspondence (1)

**Total**: 27 CPS-specific samples

### Test Structure for CPS Scanner

```python
# tests/test_classifier.py
class TestCPSMedicalMetadata:
    """Test CPS medical metadata extraction"""

class TestCPSExpenseMetadata:
    """Test CPS expense metadata extraction"""

class TestCPSSchoolworkMetadata:
    """Test CPS schoolwork metadata extraction"""

# tests/test_basicmemory.py
class TestCPSMedicalNotes:
    """Test CPS medical note creation"""

class TestCPSExpenseNotes:
    """Test CPS expense note creation"""

# tests/test_vault_routing.py (adapted from test_dual_vault.py)
class TestCPSVaultRouting:
    """Test that all CPS categories route to CPS vault"""

class TestVaultDirectoryStructure:
    """Test CPS vault directory structure"""
```

---

## Code Review Checklist

When reviewing ported code:

- [ ] **No personal-specific categories** in CPS scanner
- [ ] **No personal vault paths** hardcoded
- [ ] **Vault routing is configurable** (not hardcoded)
- [ ] **Tests use CPS samples only** (not personal samples)
- [ ] **Database schema is compatible** with CPS categories
- [ ] **Error handling is robust**
- [ ] **Dev mode works correctly**
- [ ] **Documentation is updated**
- [ ] **All tests passing** (≥ 80% coverage)
- [ ] **No breaking changes** to existing CPS functionality

---

## Rollback Plan

If issues arise after porting:

1. **Revert database changes**:
   ```bash
   # Restore from backup
   cp queue/pending.db.backup queue/pending.db
   ```

2. **Revert code changes**:
   ```bash
   git revert <commit-hash>
   # Or checkout previous tag
   git checkout <previous-tag>
   ```

3. **Test with previous version**:
   ```bash
   pytest
   python3 scripts/process.py --dev samples/medical-1.pdf
   ```

4. **Notify users**:
   - Document the issue
   - Communicate timeline for fix
   - Re-attempt port after fixing issues

---

## Success Criteria

**Porting is successful when**:

1. ✅ All CPS scanner tests passing (100% pass rate)
2. ✅ Test coverage ≥ 80% for CPS scanner
3. ✅ All 27 CPS samples classify and extract correctly
4. ✅ Enhanced logging works (prompts/responses in database)
5. ✅ Re-processing with corrections functions
6. ✅ Dev mode works correctly
7. ✅ Error handling is robust
8. ✅ No personal-specific code in CPS scanner
9. ✅ Documentation is complete and accurate
10. ✅ Production deployment successful with no issues

---

## Long-Term Maintenance

### Code Sync Strategy

**When to Sync**:
- After major features added to either system
- After bug fixes that apply to both
- Quarterly maintenance sync

**What to Sync**:
- Testing infrastructure improvements
- Database enhancements
- Error handling patterns
- Dev mode features
- General utility functions

**What NOT to Sync**:
- Personal-specific categories
- Personal vault paths
- Personal document templates

### Divergence Management

**Acceptable Divergence**:
- CPS scanner: 6 categories (CPS-*)
- scan-processor: 29 categories (6 CPS + 23 Personal)
- CPS scanner: Single vault (or configurable)
- scan-processor: Dual vault (CPS + Personal)

**Problematic Divergence** (requires sync):
- Different database schemas
- Different error handling approaches
- Different testing strategies
- Different Claude Code integration methods

---

## Resources

**Repositories**:
- scan-processor: `/home/jodfie/scan-processor/`
- CPS scanner: [CPS scanner repo path]

**Documentation**:
- scan-processor `CLAUDE.md`
- scan-processor `TESTING_GUIDE.md`
- scan-processor `VALIDATION_CHECKLIST.md`
- CPS scanner `CLAUDE.md` (to be updated)

**Contact**:
- Questions about porting: [contact info]
- Issues with ported code: [issue tracker]

---

**Last Updated**: 2025-12-25
**Version**: 1.0
**Next Review**: After Phase 6 completion
