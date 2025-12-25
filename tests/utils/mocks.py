"""
Mock objects for testing scan-processor

Provides realistic mock implementations for:
- Claude Code CLI subprocess calls
- Paperless API client
- Notification handlers
- File system operations
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class MockClaudeCodeCLI:
    """Mock Claude Code subprocess calls with realistic responses

    Usage:
        mock_cli = MockClaudeCodeCLI()
        result = mock_cli(prompt_text, file_path)
    """

    def __init__(self, response_mode='success'):
        """
        Args:
            response_mode: 'success', 'failure', 'invalid_json', or 'timeout'
        """
        self.response_mode = response_mode
        self.call_count = 0
        self.last_prompt = None
        self.last_file = None

    def __call__(self, prompt_text: str, file_path: str) -> Dict[str, Any]:
        """Simulate Claude Code CLI execution

        Args:
            prompt_text: The prompt text sent to Claude
            file_path: Path to document being processed

        Returns:
            Dict containing classification/extraction results
        """
        self.call_count += 1
        self.last_prompt = prompt_text
        self.last_file = file_path

        if self.response_mode == 'failure':
            raise RuntimeError("Claude Code subprocess failed")

        if self.response_mode == 'timeout':
            raise TimeoutError("Claude Code timed out")

        if self.response_mode == 'invalid_json':
            return {"raw_response": "This is not valid JSON{{{"}

        # Determine response based on prompt content
        if "classify" in prompt_text.lower() or "category" in prompt_text.lower():
            return self._classification_response(file_path)
        elif "medical" in prompt_text.lower():
            return self._medical_metadata_response()
        elif "expense" in prompt_text.lower():
            return self._expense_metadata_response()
        elif "utility" in prompt_text.lower():
            return self._utility_metadata_response()
        elif "auto" in prompt_text.lower():
            return self._auto_metadata_response()
        else:
            return self._generic_response()

    def _classification_response(self, file_path: str) -> Dict[str, Any]:
        """Return classification based on filename hints"""
        filename = Path(file_path).name.lower()

        if "medical" in filename or "doctor" in filename:
            return {
                "category": "PERSONAL-MEDICAL",
                "confidence": 0.95,
                "is_cps_related": False,
                "reasoning": "This appears to be a personal medical document"
            }
        elif "receipt" in filename or "restaurant" in filename or "amazon" in filename:
            return {
                "category": "PERSONAL-EXPENSE",
                "confidence": 0.92,
                "is_cps_related": False,
                "reasoning": "This is a personal expense receipt"
            }
        elif "electric" in filename or "water" in filename or "utility" in filename:
            return {
                "category": "UTILITY",
                "confidence": 0.88,
                "is_cps_related": False,
                "reasoning": "This is a utility bill"
            }
        elif "insurance" in filename or "policy" in filename:
            return {
                "category": "AUTO-INSURANCE",
                "confidence": 0.90,
                "is_cps_related": False,
                "reasoning": "This is an auto insurance document"
            }
        elif "oil" in filename or "tire" in filename or "maintenance" in filename:
            return {
                "category": "AUTO-MAINTENANCE",
                "confidence": 0.87,
                "is_cps_related": False,
                "reasoning": "This is an auto maintenance record"
            }
        elif "registration" in filename or "inspection" in filename:
            return {
                "category": "AUTO-REGISTRATION",
                "confidence": 0.89,
                "is_cps_related": False,
                "reasoning": "This is a vehicle registration document"
            }
        else:
            return {
                "category": "GENERAL",
                "confidence": 0.60,
                "is_cps_related": False,
                "reasoning": "Unable to determine specific category"
            }

    def _medical_metadata_response(self) -> Dict[str, Any]:
        """Return mock medical metadata extraction"""
        return {
            "provider": "Dr. Smith Family Medicine",
            "date": "2025-09-15",
            "amount": 125.50,
            "type": "medical_bill",
            "description": "Office visit and lab work"
        }

    def _expense_metadata_response(self) -> Dict[str, Any]:
        """Return mock expense metadata extraction"""
        return {
            "vendor": "The Bistro Restaurant",
            "date": "2025-12-15",
            "amount": 45.75,
            "category": "dining",
            "description": "Dinner receipt"
        }

    def _utility_metadata_response(self) -> Dict[str, Any]:
        """Return mock utility metadata extraction"""
        return {
            "utility_type": "electric",
            "provider": "City Power & Light",
            "billing_date": "2025-12-01",
            "due_date": "2025-12-21",
            "amount": 142.37,
            "account_number": "1234567890"
        }

    def _auto_metadata_response(self) -> Dict[str, Any]:
        """Return mock auto document metadata extraction"""
        return {
            "insurance_company": "State Farm",
            "policy_number": "POL-12345678",
            "vehicle": "2020 Honda Accord",
            "effective_date": "2025-01-01",
            "expiration_date": "2026-01-01",
            "premium": 1200.00
        }

    def _generic_response(self) -> Dict[str, Any]:
        """Return generic successful response"""
        return {
            "status": "success",
            "data": "Generic mock response"
        }


class MockPaperlessClient:
    """Mock Paperless API client for testing

    Usage:
        client = MockPaperlessClient()
        result = client.upload_document(file_path, tags)
    """

    def __init__(self, mode='success'):
        """
        Args:
            mode: 'success', 'failure', or 'network_error'
        """
        self.mode = mode
        self.uploaded_documents = []
        self.call_count = 0

    def upload_document(self, file_path: str, tags: list, **kwargs) -> Dict[str, Any]:
        """Mock document upload

        Args:
            file_path: Path to document to upload
            tags: List of tag names
            **kwargs: Additional upload parameters

        Returns:
            Dict with upload result

        Raises:
            Exception: If mode is 'failure' or 'network_error'
        """
        self.call_count += 1

        if self.mode == 'failure':
            raise Exception("Paperless upload failed: Invalid file format")

        if self.mode == 'network_error':
            raise ConnectionError("Network error: Could not connect to Paperless server")

        # Record uploaded document
        doc_record = {
            "file_path": file_path,
            "tags": tags,
            "kwargs": kwargs,
            "document_id": 10000 + self.call_count
        }
        self.uploaded_documents.append(doc_record)

        return {
            "id": doc_record["document_id"],
            "status": "success",
            "tags": tags
        }

    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve uploaded document info"""
        for doc in self.uploaded_documents:
            if doc["document_id"] == doc_id:
                return doc
        return None


class MockNotificationHandler:
    """Mock Pushover notification handler

    Usage:
        handler = MockNotificationHandler()
        handler.send("Message", priority=1)
    """

    def __init__(self, mode='success'):
        """
        Args:
            mode: 'success' or 'failure'
        """
        self.mode = mode
        self.sent_notifications = []

    def send(self, message: str, priority: int = 0, **kwargs) -> bool:
        """Mock notification send

        Args:
            message: Notification message
            priority: Priority level (0=normal, 1=high)
            **kwargs: Additional notification parameters

        Returns:
            bool: True if successful

        Raises:
            Exception: If mode is 'failure'
        """
        if self.mode == 'failure':
            raise Exception("Pushover notification failed: Invalid API token")

        notification_record = {
            "message": message,
            "priority": priority,
            "kwargs": kwargs
        }
        self.sent_notifications.append(notification_record)

        return True


class MockFileSystem:
    """Mock file system operations for testing

    Tracks file moves, copies, and deletions without actually performing them
    """

    def __init__(self):
        self.moved_files = []
        self.copied_files = []
        self.deleted_files = []
        self.created_directories = []

    def move(self, src: Path, dest: Path):
        """Record file move"""
        self.moved_files.append({"src": src, "dest": dest})

    def copy(self, src: Path, dest: Path):
        """Record file copy"""
        self.copied_files.append({"src": src, "dest": dest})

    def delete(self, path: Path):
        """Record file deletion"""
        self.deleted_files.append(path)

    def mkdir(self, path: Path):
        """Record directory creation"""
        self.created_directories.append(path)


class MockDatabaseConnection:
    """Mock SQLite database connection

    Provides in-memory operations that don't persist
    """

    def __init__(self):
        self.queries = []
        self.inserts = []
        self.updates = []

    def execute(self, query: str, params: tuple = ()):
        """Record query execution"""
        self.queries.append({"query": query, "params": params})

        if query.strip().upper().startswith('INSERT'):
            self.inserts.append({"query": query, "params": params})
        elif query.strip().upper().startswith('UPDATE'):
            self.updates.append({"query": query, "params": params})

    def commit(self):
        """Mock commit (no-op)"""
        pass

    def close(self):
        """Mock close (no-op)"""
        pass


# Convenience function for creating mock responses
def create_mock_classification(category: str, confidence: float = 0.9,
                               is_cps_related: bool = False) -> Dict[str, Any]:
    """Create a mock classification response

    Args:
        category: Document category
        confidence: Classification confidence (0-1)
        is_cps_related: Whether document is CPS-related

    Returns:
        Dict with classification response structure
    """
    return {
        "category": category,
        "confidence": confidence,
        "is_cps_related": is_cps_related,
        "reasoning": f"Mock classification for {category}"
    }


def create_mock_metadata(category: str, **kwargs) -> Dict[str, Any]:
    """Create mock metadata for any category

    Args:
        category: Document category
        **kwargs: Additional metadata fields

    Returns:
        Dict with category-specific metadata
    """
    base_metadata = {
        "PERSONAL-MEDICAL": {
            "provider": "Mock Provider",
            "date": "2025-01-15",
            "amount": 100.00,
            "type": "medical_bill"
        },
        "PERSONAL-EXPENSE": {
            "vendor": "Mock Vendor",
            "date": "2025-01-15",
            "amount": 50.00,
            "category": "shopping"
        },
        "UTILITY": {
            "utility_type": "electric",
            "provider": "Mock Utility",
            "billing_date": "2025-01-01",
            "due_date": "2025-01-21",
            "amount": 100.00
        },
        "AUTO-INSURANCE": {
            "insurance_company": "Mock Insurance",
            "policy_number": "MOCK-123",
            "vehicle": "2020 Mock Car",
            "premium": 1000.00
        }
    }.get(category, {})

    # Merge with custom kwargs
    base_metadata.update(kwargs)

    return base_metadata
