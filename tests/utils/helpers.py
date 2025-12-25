"""
Test helper functions for scan-processor test suite

Provides utility functions for:
- PDF creation and manipulation
- File validation
- Metadata verification
- YAML frontmatter validation
"""

import yaml
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime


# ========== PDF Creation Helpers ==========

def create_test_pdf(content: str, output_path: Path, title: str = "Test Document"):
    """Create a simple PDF for testing

    Args:
        content: Text content to include in PDF
        output_path: Where to save the PDF
        title: Document title

    Returns:
        Path: Path to created PDF file
    """
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, title)

    # Content (split into lines)
    c.setFont("Helvetica", 12)
    y_position = height - 150
    lines = content.split('\n')

    for line in lines:
        if y_position < 100:  # Start new page if needed
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - 100

        c.drawString(100, y_position, line)
        y_position -= 20

    c.save()

    return output_path


def create_medical_bill_pdf(output_path: Path, provider: str = "Dr. Smith",
                            date: str = "2025-01-15", amount: float = 125.50):
    """Create a realistic medical bill PDF

    Args:
        output_path: Where to save PDF
        provider: Provider name
        date: Service date
        amount: Bill amount

    Returns:
        Path: Path to created PDF
    """
    content = f"""MEDICAL BILL

Provider: {provider}
Date of Service: {date}
Total Amount: ${amount:.2f}

Services:
- Office Visit
- Lab Work
"""
    return create_test_pdf(content, output_path, "Medical Bill")


def create_utility_bill_pdf(output_path: Path, utility_type: str = "electric",
                           provider: str = "City Power", amount: float = 142.37):
    """Create a realistic utility bill PDF

    Args:
        output_path: Where to save PDF
        utility_type: Type of utility (electric, water, gas, etc.)
        provider: Utility company name
        amount: Bill amount

    Returns:
        Path: Path to created PDF
    """
    content = f"""{utility_type.upper()} BILL

Provider: {provider}
Billing Date: 2025-01-01
Due Date: 2025-01-21
Amount Due: ${amount:.2f}
"""
    return create_test_pdf(content, output_path, f"{utility_type.title()} Bill")


# ========== Frontmatter Validation Helpers ==========

def assert_frontmatter_valid(note_path: Path) -> Dict[str, Any]:
    """Verify YAML frontmatter is valid and extract it

    Args:
        note_path: Path to markdown note file

    Returns:
        Dict: Parsed frontmatter data

    Raises:
        AssertionError: If frontmatter is invalid or missing
    """
    assert note_path.exists(), f"Note file does not exist: {note_path}"

    content = note_path.read_text()

    # Check for frontmatter delimiters
    assert content.startswith('---'), f"Note missing frontmatter start: {note_path}"
    assert '\n---\n' in content, f"Note missing frontmatter end: {note_path}"

    # Extract frontmatter
    parts = content.split('\n---\n', 2)
    assert len(parts) >= 2, f"Note has malformed frontmatter: {note_path}"

    frontmatter_text = parts[0].replace('---', '').strip()

    # Parse YAML
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        raise AssertionError(f"Invalid YAML frontmatter in {note_path}: {e}")

    assert isinstance(frontmatter, dict), f"Frontmatter is not a dictionary: {note_path}"

    return frontmatter


def assert_frontmatter_has_fields(note_path: Path, required_fields: List[str]):
    """Verify frontmatter contains required fields

    Args:
        note_path: Path to markdown note
        required_fields: List of required field names

    Raises:
        AssertionError: If any required field is missing
    """
    frontmatter = assert_frontmatter_valid(note_path)

    for field in required_fields:
        assert field in frontmatter, \
            f"Note missing required frontmatter field '{field}': {note_path}"


def extract_frontmatter_field(note_path: Path, field_name: str) -> Any:
    """Extract a specific field from frontmatter

    Args:
        note_path: Path to markdown note
        field_name: Name of field to extract

    Returns:
        Value of the field

    Raises:
        AssertionError: If field doesn't exist
    """
    frontmatter = assert_frontmatter_valid(note_path)

    assert field_name in frontmatter, \
        f"Field '{field_name}' not found in frontmatter: {note_path}"

    return frontmatter[field_name]


# ========== File Location Validation Helpers ==========

def assert_file_in_vault(file_path: Path, vault_name: str):
    """Verify file was created in the correct vault

    Args:
        file_path: Path to file to check
        vault_name: Expected vault name (e.g., "CoparentingSystem" or "Personal")

    Raises:
        AssertionError: If file is not in expected vault
    """
    assert file_path.exists(), f"File does not exist: {file_path}"

    path_str = str(file_path)
    assert vault_name in path_str, \
        f"File not in {vault_name} vault: {file_path}"


def assert_file_in_directory(file_path: Path, expected_dir: str):
    """Verify file is in expected directory (anywhere in path)

    Args:
        file_path: Path to file to check
        expected_dir: Expected directory name (can be anywhere in path)

    Raises:
        AssertionError: If file is not in expected directory
    """
    assert file_path.exists(), f"File does not exist: {file_path}"

    path_str = str(file_path)
    assert expected_dir in path_str, \
        f"File not in expected directory '{expected_dir}': {file_path}"


def assert_filename_matches_pattern(file_path: Path, pattern: str):
    """Verify filename matches a regex pattern

    Args:
        file_path: Path to file
        pattern: Regex pattern to match

    Raises:
        AssertionError: If filename doesn't match pattern
    """
    filename = file_path.name

    assert re.match(pattern, filename), \
        f"Filename '{filename}' doesn't match pattern '{pattern}'"


# ========== Metadata Validation Helpers ==========

def assert_metadata_has_fields(metadata: Dict[str, Any], required_fields: List[str]):
    """Verify metadata contains required fields

    Args:
        metadata: Metadata dictionary
        required_fields: List of required field names

    Raises:
        AssertionError: If any required field is missing
    """
    for field in required_fields:
        assert field in metadata, \
            f"Metadata missing required field: {field}"


def assert_metadata_types(metadata: Dict[str, Any], field_types: Dict[str, type]):
    """Verify metadata fields have correct types

    Args:
        metadata: Metadata dictionary
        field_types: Dict mapping field names to expected types

    Raises:
        AssertionError: If any field has wrong type
    """
    for field, expected_type in field_types.items():
        if field in metadata:
            actual_value = metadata[field]
            assert isinstance(actual_value, expected_type), \
                f"Field '{field}' has wrong type. Expected {expected_type}, got {type(actual_value)}"


def assert_date_format(date_string: str, format_str: str = "%Y-%m-%d"):
    """Verify date string matches expected format

    Args:
        date_string: Date string to validate
        format_str: Expected strftime format

    Raises:
        AssertionError: If date doesn't match format
    """
    try:
        datetime.strptime(date_string, format_str)
    except ValueError as e:
        raise AssertionError(f"Date '{date_string}' doesn't match format '{format_str}': {e}")


# ========== Database Validation Helpers ==========

def assert_record_exists(db_connection, table: str, conditions: Dict[str, Any]):
    """Verify a database record exists with given conditions

    Args:
        db_connection: SQLite database connection
        table: Table name
        conditions: Dict of column: value conditions

    Raises:
        AssertionError: If record doesn't exist
    """
    cursor = db_connection.cursor()

    # Build WHERE clause
    where_parts = [f"{col} = ?" for col in conditions.keys()]
    where_clause = " AND ".join(where_parts)
    values = tuple(conditions.values())

    query = f"SELECT COUNT(*) FROM {table} WHERE {where_clause}"
    cursor.execute(query, values)

    count = cursor.fetchone()[0]

    assert count > 0, \
        f"No record found in {table} matching conditions: {conditions}"


def get_record_count(db_connection, table: str, conditions: Optional[Dict[str, Any]] = None) -> int:
    """Get count of records matching conditions

    Args:
        db_connection: SQLite database connection
        table: Table name
        conditions: Optional dict of column: value conditions

    Returns:
        int: Number of matching records
    """
    cursor = db_connection.cursor()

    if conditions:
        where_parts = [f"{col} = ?" for col in conditions.keys()]
        where_clause = " AND ".join(where_parts)
        values = tuple(conditions.values())
        query = f"SELECT COUNT(*) FROM {table} WHERE {where_clause}"
        cursor.execute(query, values)
    else:
        query = f"SELECT COUNT(*) FROM {table}"
        cursor.execute(query)

    return cursor.fetchone()[0]


# ========== General Test Helpers ==========

def assert_files_created(file_paths: List[Path]):
    """Verify all files in list were created

    Args:
        file_paths: List of file paths to check

    Raises:
        AssertionError: If any file doesn't exist
    """
    for file_path in file_paths:
        assert file_path.exists(), f"Expected file was not created: {file_path}"


def assert_directory_exists(dir_path: Path):
    """Verify directory exists

    Args:
        dir_path: Directory path to check

    Raises:
        AssertionError: If directory doesn't exist or is not a directory
    """
    assert dir_path.exists(), f"Directory does not exist: {dir_path}"
    assert dir_path.is_dir(), f"Path exists but is not a directory: {dir_path}"


def count_files_in_directory(dir_path: Path, pattern: str = "*") -> int:
    """Count files matching pattern in directory

    Args:
        dir_path: Directory to search
        pattern: Glob pattern for files

    Returns:
        int: Number of matching files
    """
    return len(list(dir_path.glob(pattern)))


def read_note_content(note_path: Path) -> str:
    """Read note content without frontmatter

    Args:
        note_path: Path to markdown note

    Returns:
        str: Note content (excluding frontmatter)
    """
    assert note_path.exists(), f"Note does not exist: {note_path}"

    content = note_path.read_text()

    # Remove frontmatter
    if content.startswith('---'):
        parts = content.split('\n---\n', 2)
        if len(parts) >= 2:
            return parts[1].strip()

    return content


def get_note_sections(note_path: Path) -> Dict[str, str]:
    """Parse note into sections

    Args:
        note_path: Path to markdown note

    Returns:
        Dict mapping section headers to content
    """
    content = read_note_content(note_path)

    sections = {}
    current_section = "intro"
    current_content = []

    for line in content.split('\n'):
        if line.startswith('##'):
            # Save previous section
            if current_content:
                sections[current_section] = '\n'.join(current_content).strip()

            # Start new section
            current_section = line.replace('##', '').strip()
            current_content = []
        else:
            current_content.append(line)

    # Save last section
    if current_content:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections


# ========== Comparison Helpers ==========

def assert_dicts_equal(dict1: Dict, dict2: Dict, ignore_keys: Optional[List[str]] = None):
    """Compare two dictionaries, optionally ignoring certain keys

    Args:
        dict1: First dictionary
        dict2: Second dictionary
        ignore_keys: Optional list of keys to ignore in comparison

    Raises:
        AssertionError: If dictionaries don't match
    """
    ignore_keys = ignore_keys or []

    # Create filtered copies
    filtered1 = {k: v for k, v in dict1.items() if k not in ignore_keys}
    filtered2 = {k: v for k, v in dict2.items() if k not in ignore_keys}

    assert filtered1 == filtered2, \
        f"Dictionaries don't match.\nExpected: {filtered2}\nActual: {filtered1}"


def assert_contains_substring(text: str, substring: str, case_sensitive: bool = True):
    """Verify text contains substring

    Args:
        text: Text to search
        substring: Substring to find
        case_sensitive: Whether search is case-sensitive

    Raises:
        AssertionError: If substring not found
    """
    if not case_sensitive:
        text = text.lower()
        substring = substring.lower()

    assert substring in text, \
        f"Substring '{substring}' not found in text"
