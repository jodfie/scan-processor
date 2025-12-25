# Testing Guide - Scan Processor

**Complete guide for testing the scan-processor document classification and processing system.**

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Writing New Tests](#writing-new-tests)
5. [Sample Documents](#sample-documents)
6. [Debugging Tests](#debugging-tests)
7. [Coverage Reports](#coverage-reports)
8. [CI/CD Integration](#cicd-integration)

---

## Quick Start

### Initial Setup

```bash
# Navigate to project directory
cd /home/jodfie/scan-processor

# Install development dependencies
pip3 install --break-system-packages -r requirements-dev.txt

# Verify installation
pytest --version
```

### Run All Tests

```bash
# Run complete test suite
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=scripts --cov-report=html
```

### Expected Output

```
================================ test session starts =================================
collected 89 items

tests/test_classifier.py .......................                              [ 25%]
tests/test_basicmemory.py ...............................                      [ 60%]
tests/test_dual_vault.py .................                                     [ 79%]
tests/test_process.py ......................                                   [100%]

---------- coverage: platform linux, python 3.x.x -----------
Name                       Stmts   Miss  Cover
----------------------------------------------
scripts/classifier.py        245     18    93%
scripts/basicmemory.py       198     12    94%
scripts/process.py           312     25    92%
scripts/paperless.py          87      8    91%
scripts/notify.py             45      4    91%
----------------------------------------------
TOTAL                        887     67    92%

================================ 89 passed in 12.34s =================================
```

---

## Test Structure

### Directory Layout

```
tests/
├── __init__.py                 # Package marker
├── conftest.py                 # Shared fixtures (400+ lines)
├── test_classifier.py          # Classifier tests (580 lines)
├── test_basicmemory.py         # BasicMemory tests (700 lines)
├── test_dual_vault.py          # Dual-vault routing (400 lines)
├── test_process.py             # Integration tests (600 lines)
├── fixtures/                   # Test data
│   ├── mock_responses.json    # Claude Code mock responses
│   └── test_metadata.json     # Sample metadata
└── utils/                      # Test utilities
    ├── __init__.py
    ├── mocks.py               # Mock objects (450 lines)
    └── helpers.py             # Helper functions (400 lines)
```

### Test Files Overview

#### test_classifier.py (580 lines)
**Purpose**: Test document classification and metadata extraction

**Key Test Classes**:
- `TestDocumentClassifierInit` - Classifier initialization and prompt loading
- `TestPersonalMedicalMetadata` - Personal medical extraction (NEW)
- `TestPersonalExpenseMetadata` - Personal expense extraction (NEW)
- `TestUtilityMetadata` - Utility bill extraction (NEW)
- `TestAutoMetadata` - Automotive document extraction (NEW)
- `TestJSONParsing` - JSON extraction from Claude responses
- `TestErrorHandling` - Classification error scenarios
- `TestCorrectionInjection` - Re-processing with corrections

**Example**:
```python
def test_extract_personal_medical_metadata(self, tmp_path, mocker):
    """Test personal medical metadata extraction"""
    classifier = DocumentClassifier(tmp_path)

    # Mock Claude Code response
    mock_response = json.dumps({
        "provider": "Dr. Smith",
        "date": "2025-01-15",
        "amount": 125.50
    })
    mocker.patch('subprocess.run', return_value=MagicMock(stdout=mock_response))

    # Test extraction
    metadata = classifier.extract_personal_medical_metadata("test.pdf")

    assert metadata['provider'] == "Dr. Smith"
    assert metadata['date'] == "2025-01-15"
    assert metadata['amount'] == 125.50
```

#### test_basicmemory.py (700 lines)
**Purpose**: Test BasicMemory note creation for all document types

**Key Test Classes**:
- `TestPersonalMedicalNotes` - Personal medical note creation (NEW)
- `TestPersonalExpenseNotes` - Personal expense note creation (NEW)
- `TestUtilityNotes` - Utility bill note creation (NEW)
- `TestAutoNotes` - Automotive note creation (NEW)
- `TestDualVaultInitialization` - Verify both vaults initialized
- `TestDryRunMode` - Verify dry-run doesn't create files
- `TestFilenameFormatting` - Verify filename conventions

**Example**:
```python
def test_create_personal_medical_note(self, temp_vault_dirs):
    """Test personal medical note creation"""
    cps_vault, personal_vault = temp_vault_dirs

    creator = BasicMemoryNoteCreator(
        cps_path=cps_vault,
        personal_vault=personal_vault
    )

    metadata = {
        "provider": "Dr. Smith",
        "date": "2025-01-15",
        "amount": 125.50,
        "type": "visit"
    }

    note_path = creator.create_personal_medical_note(metadata, "test.pdf")

    # Verify file created in Personal vault
    assert note_path.exists()
    assert "Personal" in str(note_path)
    assert "Medical" in str(note_path)

    # Verify frontmatter
    frontmatter = assert_frontmatter_valid(note_path)
    assert frontmatter['provider'] == "Dr. Smith"
```

#### test_dual_vault.py (400 lines)
**Purpose**: Test dual-vault routing (CPS vs Personal)

**Key Test Classes**:
- `TestCPSCategoryRouting` - CPS-* categories go to CoparentingSystem vault
- `TestPersonalCategoryRouting` - PERSONAL-* go to Personal vault
- `TestUtilityRouting` - UTILITY goes to Personal vault
- `TestAutoRouting` - AUTO-* goes to Personal vault
- `TestVaultDirectoryStructure` - Verify directory structure
- `TestIsCPSRelatedFlag` - Test is_cps_related flag routing

**Example**:
```python
def test_personal_medical_routes_to_personal_vault(self, temp_vault_dirs):
    """PERSONAL-MEDICAL documents go to Personal vault"""
    cps_vault, personal_vault = temp_vault_dirs

    creator = BasicMemoryNoteCreator(
        cps_path=cps_vault,
        personal_vault=personal_vault
    )

    note_path = creator.create_personal_medical_note(metadata, "test.pdf")

    # Verify in Personal vault, NOT CPS
    assert "Personal" in str(note_path)
    assert "CoparentingSystem" not in str(note_path)
```

#### test_process.py (600 lines)
**Purpose**: Integration/end-to-end tests for complete pipeline

**Key Test Classes**:
- `TestEndToEndPipeline` - Complete pipeline tests
- `TestDevMode` - Dev mode testing (no actual uploads)
- `TestCorrectionsWorkflow` - Re-processing with corrections
- `TestErrorHandling` - Failed processing scenarios
- `TestDatabaseLogging` - Verify logging to database
- `TestNotifications` - Notification handling
- `TestCategorySpecificProcessing` - Tests for each category
- `TestPaperlessTags` - Tag generation validation
- `TestIntegrationWithSamples` - Tests using generated samples

**Example**:
```python
def test_full_pipeline_personal_medical(
    self, sample_medical_pdf, temp_vault_dirs, test_database, mocker
):
    """Test complete pipeline for personal medical document"""
    # Mock external calls
    mock_claude = mocker.patch('scripts.classifier.subprocess.run')
    mock_paperless = mocker.patch('scripts.paperless.PaperlessClient.upload_document')
    mock_notify = mocker.patch('scripts.notify.NotificationHandler.send')

    # Configure mocks
    mock_claude.return_value.stdout = json.dumps({
        "category": "PERSONAL-MEDICAL",
        "confidence": 0.95
    })
    mock_paperless.return_value = {"id": 12345, "status": "success"}

    # Run pipeline
    result = process_document(sample_medical_pdf, dev_mode=False)

    # Verify all steps executed
    assert result['category'] == "PERSONAL-MEDICAL"
    assert result['paperless_id'] == 12345
    assert result['basicmemory_path'] is not None
    assert mock_notify.called
```

---

## Running Tests

### Run All Tests

```bash
# Run complete test suite
pytest

# With verbose output
pytest -v

# With very verbose output (show each test)
pytest -vv
```

### Run Specific Test Files

```bash
# Run only classifier tests
pytest tests/test_classifier.py

# Run only basicmemory tests
pytest tests/test_basicmemory.py

# Run only dual-vault tests
pytest tests/test_dual_vault.py

# Run only integration tests
pytest tests/test_process.py
```

### Run Specific Test Classes

```bash
# Run specific test class
pytest tests/test_classifier.py::TestPersonalMedicalMetadata

# Run specific test method
pytest tests/test_classifier.py::TestPersonalMedicalMetadata::test_extract_personal_medical_metadata
```

### Run Tests Matching Pattern

```bash
# Run all tests with "personal_medical" in name
pytest -k "personal_medical"

# Run all tests with "utility" in name
pytest -k "utility"

# Run all tests with "auto" in name
pytest -k "auto"

# Exclude tests matching pattern
pytest -k "not slow"
```

### Run Tests with Coverage

```bash
# Generate HTML coverage report
pytest --cov=scripts --cov-report=html

# View coverage in terminal
pytest --cov=scripts --cov-report=term-missing

# Generate both HTML and terminal reports
pytest --cov=scripts --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run Tests in Parallel

```bash
# Run tests across 4 CPU cores
pytest -n 4

# Auto-detect CPU count
pytest -n auto
```

### Run Tests with Timeout

```bash
# Fail tests that run longer than 30 seconds
pytest --timeout=30
```

---

## Writing New Tests

### Basic Test Template

```python
import pytest
from pathlib import Path
from scripts.classifier import DocumentClassifier

class TestNewFeature:
    """Test description"""

    def test_feature_works(self, tmp_path):
        """Test that new feature works correctly"""
        # Arrange - Set up test data
        test_file = tmp_path / "test.pdf"

        # Act - Execute the feature
        result = some_function(test_file)

        # Assert - Verify expected behavior
        assert result is not None
        assert result['status'] == 'success'
```

### Using Fixtures

```python
def test_with_temp_vault(self, temp_vault_dirs):
    """Test using temporary vault directories"""
    cps_vault, personal_vault = temp_vault_dirs

    # Both vaults are created with full directory structure
    assert (cps_vault / "60-medical" / "morgan").exists()
    assert (personal_vault / "Medical").exists()
```

### Mocking External Calls

```python
def test_with_mock_claude(self, mocker):
    """Test with mocked Claude Code CLI"""
    # Mock the subprocess call
    mock_run = mocker.patch('subprocess.run')
    mock_run.return_value.stdout = json.dumps({
        "category": "PERSONAL-MEDICAL",
        "confidence": 0.95
    })

    # Your test code
    result = classifier.classify("test.pdf")

    # Verify mock was called
    assert mock_run.called
```

### Parametrized Tests

```python
@pytest.mark.parametrize("utility_type,expected_subfolder", [
    ("electric", "Utilities"),
    ("water", "Utilities"),
    ("gas", "Utilities"),
    ("internet", "Utilities"),
    ("phone", "Utilities"),
])
def test_utility_routing(self, utility_type, expected_subfolder, temp_vault_dirs):
    """Test that all utility types route to Personal vault"""
    cps_vault, personal_vault = temp_vault_dirs

    creator = BasicMemoryNoteCreator(
        cps_path=cps_vault,
        personal_vault=personal_vault
    )

    metadata = {"utility_type": utility_type, "provider": "Test"}
    note_path = creator.create_utility_note(metadata, f"{utility_type}.pdf")

    assert expected_subfolder in str(note_path)
```

### Testing Exceptions

```python
def test_handles_missing_file(self):
    """Test error handling for missing file"""
    with pytest.raises(FileNotFoundError):
        classifier.classify("nonexistent.pdf")
```

### Testing File Creation

```python
def test_creates_note_file(self, temp_vault_dirs):
    """Test that note file is created"""
    cps_vault, personal_vault = temp_vault_dirs

    creator = BasicMemoryNoteCreator(
        cps_path=cps_vault,
        personal_vault=personal_vault
    )

    note_path = creator.create_personal_medical_note(metadata, "test.pdf")

    # Verify file exists
    assert note_path.exists()

    # Verify content
    content = note_path.read_text()
    assert "provider: Dr. Smith" in content
```

---

## Sample Documents

### Generated Samples

48 realistic sample PDF documents are available in `samples/`:

```
samples/
├── personal-medical/          # 9 samples
│   ├── medical-bill-1.pdf
│   ├── medical-bill-2.pdf
│   ├── lab-result-1.pdf
│   └── ...
├── personal-expense/          # 9 samples
│   ├── restaurant-1.pdf
│   ├── amazon-invoice-1.pdf
│   └── ...
├── utility/                   # 12 samples
│   ├── electric-1.pdf
│   ├── water-1.pdf
│   ├── internet-1.pdf
│   └── ...
├── auto-insurance/            # 6 samples
│   ├── insurance-policy-1.pdf
│   └── ...
├── auto-maintenance/          # 6 samples
│   ├── oil-change-1.pdf
│   └── ...
└── auto-registration/         # 6 samples
    ├── registration-renewal-1.pdf
    └── ...
```

### Using Samples in Tests

```python
def test_with_real_sample(self):
    """Test using generated sample PDF"""
    sample_path = Path("samples/personal-medical/medical-bill-1.pdf")

    result = classifier.classify(str(sample_path))

    assert result['category'] == "PERSONAL-MEDICAL"
```

### Creating New Samples

```bash
# Generate all samples
python3 scripts/generate_samples.py

# Generate specific category
python3 scripts/generate_samples.py --category personal-medical --count 5
```

### Sample Documentation

See `samples/README.md` for:
- Expected classification for each sample
- Expected metadata extraction results
- Sample naming conventions
- How to add new samples

---

## Debugging Tests

### Common Issues

#### Issue 1: Tests Fail with "No such file or directory"

**Problem**: Test can't find a file

**Solution**: Use `tmp_path` fixture for temporary files
```python
def test_example(self, tmp_path):
    test_file = tmp_path / "test.pdf"
    # Create the file before using it
    test_file.touch()
```

#### Issue 2: Mock Not Working

**Problem**: Mock doesn't intercept the call

**Solution**: Ensure you're patching the correct import path
```python
# If classifier.py has: from subprocess import run
mocker.patch('subprocess.run')  # ✅ Correct

# If classifier.py has: import subprocess; subprocess.run()
mocker.patch('subprocess.run')  # ✅ Also correct

# If you're patching in the wrong module
mocker.patch('scripts.classifier.run')  # ❌ Wrong if not imported this way
```

#### Issue 3: Database Already Exists

**Problem**: Test database conflicts

**Solution**: Use `test_database` fixture which creates a fresh database
```python
def test_example(self, test_database):
    # test_database is a fresh SQLite database
    conn = sqlite3.connect(test_database)
```

#### Issue 4: Fixture Not Found

**Problem**: pytest can't find a fixture

**Solution**: Check `conftest.py` has the fixture and is in the right location
```bash
# Fixtures in conftest.py are auto-discovered
tests/conftest.py  # ✅ Found by all tests in tests/
tests/utils/conftest.py  # ✅ Found by tests in tests/utils/
```

### Verbose Output

```bash
# Show print statements
pytest -s

# Show full test output
pytest -vv

# Show local variables on failure
pytest -l

# Combine for maximum debugging
pytest -vv -s -l
```

### Debugging with pdb

```python
def test_debug_example(self):
    """Test with debugger"""
    import pdb; pdb.set_trace()  # Debugger will stop here

    result = some_function()
    assert result is not None
```

### Run Specific Failed Test

```bash
# Run last failed tests only
pytest --lf

# Run failed tests first, then others
pytest --ff
```

---

## Coverage Reports

### Generate Coverage Report

```bash
# HTML report (most detailed)
pytest --cov=scripts --cov-report=html

# Terminal report
pytest --cov=scripts --cov-report=term-missing

# Both reports
pytest --cov=scripts --cov-report=html --cov-report=term-missing
```

### View HTML Coverage Report

```bash
# The report is generated in htmlcov/
cd htmlcov
python3 -m http.server 8000

# Open browser to http://localhost:8000
```

### Understanding Coverage Output

```
---------- coverage: platform linux, python 3.x.x -----------
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
scripts/classifier.py        245     18    93%   23-25, 145-148
scripts/basicmemory.py       198     12    94%   67-69, 201-205
scripts/process.py           312     25    92%   78-82, 234-240
--------------------------------------------------------
TOTAL                        887     67    92%
```

**Columns**:
- **Stmts**: Total statements in file
- **Miss**: Statements not covered by tests
- **Cover**: Coverage percentage
- **Missing**: Line numbers not covered

### Coverage Goals

- **Target**: 80% minimum (enforced by pytest.ini)
- **Good**: 90%+
- **Excellent**: 95%+

### Improving Coverage

1. **Identify uncovered lines**: Check "Missing" column
2. **Write tests for those lines**: Focus on error paths, edge cases
3. **Re-run coverage**: `pytest --cov=scripts --cov-report=term-missing`
4. **Verify improvement**: Check new coverage percentage

---

## CI/CD Integration

### GitHub Actions (Future)

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt

    - name: Run tests with coverage
      run: |
        pytest --cov=scripts --cov-report=xml --cov-fail-under=80

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run tests before allowing commit

pytest --cov=scripts --cov-fail-under=80

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Continuous Monitoring

```bash
# Watch for file changes and re-run tests
pytest-watch

# Or use pytest-xdist with looponfail
pytest --looponfail
```

---

## Best Practices

### 1. Test Naming

✅ **Good**:
```python
def test_personal_medical_routes_to_personal_vault(self):
    """PERSONAL-MEDICAL documents go to Personal vault"""
```

❌ **Bad**:
```python
def test_routing(self):
    """Test routing"""
```

### 2. Test Independence

✅ **Good**:
```python
def test_example(self, tmp_path):
    # Creates own temp directory
    test_file = tmp_path / "test.pdf"
```

❌ **Bad**:
```python
def test_example(self):
    # Uses shared directory - tests can interfere
    test_file = Path("/tmp/test.pdf")
```

### 3. Arrange-Act-Assert Pattern

```python
def test_example(self):
    # Arrange - Set up test data
    metadata = {"provider": "Dr. Smith"}

    # Act - Execute the function
    result = create_note(metadata)

    # Assert - Verify expected behavior
    assert result is not None
```

### 4. Use Fixtures

✅ **Good**:
```python
def test_example(self, temp_vault_dirs, test_database):
    # Fixtures provide clean test environment
```

❌ **Bad**:
```python
def test_example(self):
    # Manually creating temp directories, databases
    vault = Path("/tmp/vault")
    vault.mkdir()
    # ... cleanup required
```

### 5. Mock External Dependencies

✅ **Good**:
```python
def test_example(self, mocker):
    mocker.patch('subprocess.run')  # Mock external call
    mocker.patch('scripts.paperless.PaperlessClient')
```

❌ **Bad**:
```python
def test_example(self):
    # Makes real API calls - slow, unreliable, requires credentials
    paperless_client.upload()
```

---

## Quick Reference

### Common Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scripts --cov-report=html

# Run specific test file
pytest tests/test_classifier.py

# Run tests matching pattern
pytest -k "personal_medical"

# Run last failed tests
pytest --lf

# Run with verbose output
pytest -vv

# Generate samples
python3 scripts/generate_samples.py
```

### Common Fixtures

```python
tmp_path              # Temporary directory (pathlib.Path)
temp_vault_dirs       # Temporary CPS and Personal vaults
test_database         # Temporary SQLite database
sample_medical_pdf    # Generated medical PDF sample
mocker               # pytest-mock fixture for mocking
```

### Common Assertions

```python
assert value is not None
assert value == expected
assert "text" in string
assert value > 0
assert isinstance(value, dict)
assert path.exists()
with pytest.raises(ValueError):
    function_that_raises()
```

---

## Additional Resources

- **pytest documentation**: https://docs.pytest.org/
- **pytest-cov documentation**: https://pytest-cov.readthedocs.io/
- **pytest-mock documentation**: https://pytest-mock.readthedocs.io/

---

**Last Updated**: 2025-12-25
**Version**: 1.0
**Maintainer**: scan-processor project
