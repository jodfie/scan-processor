"""
Tests for Paperless-NGX API Client
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from paperless import PaperlessClient


class TestPaperlessClientInit:
    """Test PaperlessClient initialization"""

    def test_init_with_env_vars(self, monkeypatch):
        """Test initialization with environment variables"""
        monkeypatch.setenv('PAPERLESS_API_TOKEN', 'test_token_123')

        client = PaperlessClient()

        assert client.api_token == 'test_token_123'
        assert 'Authorization' in client.headers

    def test_init_without_credentials_raises_error(self, monkeypatch):
        """Test initialization without credentials raises error"""
        monkeypatch.delenv('PAPERLESS_API_TOKEN', raising=False)

        with pytest.raises(ValueError, match="PAPERLESS_API_TOKEN"):
            PaperlessClient()

    def test_init_dry_run_mode(self, monkeypatch):
        """Test dry run mode allows missing credentials"""
        monkeypatch.delenv('PAPERLESS_API_TOKEN', raising=False)

        client = PaperlessClient(dry_run=True)

        assert client.dry_run is True


class TestDocumentUploadDryRun:
    """Test document upload in dry run mode"""

    def test_upload_document_dry_run(self, tmp_path, monkeypatch):
        """Test document upload in dry run mode"""
        monkeypatch.delenv('PAPERLESS_API_TOKEN', raising=False)

        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"PDF content")

        client = PaperlessClient(dry_run=True)
        result = client.upload_document(str(test_pdf), tags=["test"])

        assert result['success'] is True
        assert result['dry_run'] is True
        assert 'DRY_RUN' in result['task_id']


class TestDocumentUploadReal:
    """Test real document upload"""

    def test_upload_document_success(self, tmp_path, mocker, monkeypatch):
        """Test successful document upload"""
        monkeypatch.setenv('PAPERLESS_API_TOKEN', 'test_token')

        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"PDF content")

        # Mock tag resolution
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": [{"id": 1, "name": "test"}]}

        # Mock upload
        mock_post = mocker.patch('requests.post')
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = '"task-id-123"'

        client = PaperlessClient()
        result = client.upload_document(str(test_pdf), tags=["test"])

        assert result['success'] is True
        assert result['task_id'] == 'task-id-123'

    def test_upload_document_with_metadata(self, tmp_path, mocker, monkeypatch):
        """Test upload with full metadata"""
        monkeypatch.setenv('PAPERLESS_API_TOKEN', 'test_token')

        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"PDF content")

        # Mock all resolution methods
        def mock_get_side_effect(url, **kwargs):
            mock_response = mocker.Mock()
            mock_response.status_code = 200
            
            if 'tags' in url:
                mock_response.json.return_value = {"results": [{"id": 1, "name": "tag1"}]}
            elif 'document_types' in url:
                mock_response.json.return_value = {"results": [{"id": 3, "name": "Medical"}]}
            elif 'correspondents' in url:
                mock_response.json.return_value = {"results": [{"id": 5, "name": "Dr. Smith"}]}
            else:
                mock_response.json.return_value = {"results": []}
            
            return mock_response
        
        mock_get = mocker.patch('requests.get')
        mock_get.side_effect = mock_get_side_effect

        mock_post = mocker.patch('requests.post')
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = '"task-id-456"'

        client = PaperlessClient()
        result = client.upload_document(
            str(test_pdf),
            tags=["tag1"],
            title="Test Document",
            created_date="2024-01-15",
            document_type="Medical",
            correspondent="Dr. Smith"
        )

        assert result['success'] is True
        assert result['task_id'] == 'task-id-456'


class TestTagResolution:
    """Test tag resolution and creation"""

    def test_resolve_existing_tags(self, mocker, monkeypatch):
        """Test resolving existing tags"""
        monkeypatch.setenv('PAPERLESS_API_TOKEN', 'test_token')

        # Mock GET to return different tags based on params
        def mock_get_side_effect(url, **kwargs):
            params = kwargs.get('params', {})
            tag_name = params.get('name__iexact', '')
            
            mock_response = mocker.Mock()
            mock_response.status_code = 200
            
            if tag_name == 'medical':
                mock_response.json.return_value = {"results": [{"id": 1, "name": "medical"}]}
            elif tag_name == 'personal':
                mock_response.json.return_value = {"results": [{"id": 2, "name": "personal"}]}
            else:
                mock_response.json.return_value = {"results": []}
            
            return mock_response
        
        mock_get = mocker.patch('requests.get')
        mock_get.side_effect = mock_get_side_effect

        client = PaperlessClient()
        tag_ids = client._resolve_tags(["medical", "personal"])

        assert tag_ids == [1, 2]

    def test_get_or_create_tag_creates_new(self, mocker, monkeypatch):
        """Test creating new tag"""
        monkeypatch.setenv('PAPERLESS_API_TOKEN', 'test_token')

        mock_get = mocker.patch('requests.get')
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": []}

        mock_post = mocker.patch('requests.post')
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": 10}

        client = PaperlessClient()
        tag_id = client._get_or_create_tag("new-tag")

        assert tag_id == 10


class TestDocumentTypeResolution:
    """Test document type resolution"""

    def test_resolve_document_type(self, mocker, monkeypatch):
        """Test resolving document type"""
        monkeypatch.setenv('PAPERLESS_API_TOKEN', 'test_token')

        mock_get = mocker.patch('requests.get')
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "results": [{"id": 3, "name": "Medical"}]
        }

        client = PaperlessClient()
        doc_type_id = client._resolve_document_type("Medical")

        assert doc_type_id == 3

    def test_create_new_document_type(self, mocker, monkeypatch):
        """Test creating new document type"""
        monkeypatch.setenv('PAPERLESS_API_TOKEN', 'test_token')

        # GET returns empty (not found)
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": []}

        # POST creates new
        mock_post = mocker.patch('requests.post')
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": 10}

        client = PaperlessClient()
        doc_type_id = client._resolve_document_type("NewType")

        assert doc_type_id == 10


class TestCorrespondentResolution:
    """Test correspondent resolution"""

    def test_resolve_correspondent(self, mocker, monkeypatch):
        """Test resolving correspondent"""
        monkeypatch.setenv('PAPERLESS_API_TOKEN', 'test_token')

        mock_get = mocker.patch('requests.get')
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "results": [{"id": 7, "name": "Dr. Smith"}]
        }

        client = PaperlessClient()
        correspondent_id = client._resolve_correspondent("Dr. Smith")

        assert correspondent_id == 7

    def test_create_new_correspondent(self, mocker, monkeypatch):
        """Test creating new correspondent"""
        monkeypatch.setenv('PAPERLESS_API_TOKEN', 'test_token')

        # GET returns empty (not found)
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": []}

        # POST creates new
        mock_post = mocker.patch('requests.post')
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": 15}

        client = PaperlessClient()
        correspondent_id = client._resolve_correspondent("New Person")

        assert correspondent_id == 15


class TestDocumentRetrieval:
    """Test document retrieval"""

    def test_get_document_success(self, mocker, monkeypatch):
        """Test successful document retrieval"""
        monkeypatch.setenv('PAPERLESS_API_TOKEN', 'test_token')

        mock_get = mocker.patch('requests.get')
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 123,
            "title": "Test Document"
        }

        client = PaperlessClient()
        doc = client.get_document(123)

        assert doc is not None
        assert doc['id'] == 123


class TestDocumentUpdate:
    """Test document updates"""

    def test_update_document_success(self, mocker, monkeypatch):
        """Test successful document update"""
        monkeypatch.setenv('PAPERLESS_API_TOKEN', 'test_token')

        # Mock GET to return existing document
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 123,
            "title": "Old Title",
            "tags": []
        }

        # Mock PATCH for the update
        mock_patch = mocker.patch('requests.patch')
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"id": 123}

        client = PaperlessClient()
        result = client.update_document(123, title="Updated Title")

        assert result['success'] is True

    def test_update_document_not_found(self, mocker, monkeypatch):
        """Test updating non-existent document"""
        monkeypatch.setenv('PAPERLESS_API_TOKEN', 'test_token')

        # Mock GET to return None (document not found)
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.status_code = 404
        mock_get.return_value.raise_for_status.side_effect = Exception("Not found")

        client = PaperlessClient()
        result = client.update_document(999, title="New Title")

        assert result['success'] is False
        assert 'not found' in result['error']

    def test_update_document_with_tags(self, mocker, monkeypatch):
        """Test updating document with tags"""
        monkeypatch.setenv('PAPERLESS_API_TOKEN', 'test_token')

        # Mock GET for existing document and tag lookups
        def mock_get_side_effect(url, **kwargs):
            mock_response = mocker.Mock()
            mock_response.status_code = 200
            
            if 'tags' in url:
                params = kwargs.get('params', {})
                tag_name = params.get('name__iexact', '')
                if tag_name == 'medical':
                    mock_response.json.return_value = {"results": [{"id": 5, "name": "medical"}]}
                else:
                    mock_response.json.return_value = {"results": []}
            else:
                # Document GET
                mock_response.json.return_value = {
                    "id": 123,
                    "title": "Old Title",
                    "tags": [1, 2]
                }
            
            return mock_response
        
        mock_get = mocker.patch('requests.get')
        mock_get.side_effect = mock_get_side_effect

        mock_patch = mocker.patch('requests.patch')
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"id": 123}

        client = PaperlessClient()
        result = client.update_document(123, tags=["medical"])

        assert result['success'] is True

    def test_update_document_dry_run(self, monkeypatch):
        """Test update in dry run mode"""
        monkeypatch.delenv('PAPERLESS_API_TOKEN', raising=False)

        client = PaperlessClient(dry_run=True)
        result = client.update_document(123, title="New Title")

        assert result['success'] is True
        assert result['dry_run'] is True
