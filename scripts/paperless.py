#!/usr/bin/env python3
"""
Paperless-NGX API Client
Handles document upload and metadata management
"""

import os
import requests
from pathlib import Path
import json

class PaperlessClient:
    """Client for Paperless-NGX API"""

    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.base_url = os.getenv('PAPERLESS_URL', 'https://paperless.redleif.dev')
        self.api_token = os.getenv('PAPERLESS_API_TOKEN')

        if not self.dry_run and not self.api_token:
            raise ValueError("PAPERLESS_API_TOKEN environment variable not set")

        self.headers = {
            'Authorization': f'Token {self.api_token}'
        } if self.api_token else {}

    def upload_document(self, file_path, title=None, tags=None, document_type=None,
                       correspondent=None, created_date=None, custom_fields=None):
        """
        Upload a document to Paperless

        Args:
            file_path: Path to the PDF file
            title: Document title (optional, uses filename if not provided)
            tags: List of tag names or IDs
            document_type: Document type name or ID
            correspondent: Correspondent name or ID
            created_date: Document creation date (YYYY-MM-DD)
            custom_fields: Dictionary of custom field values

        Returns:
            dict: Response containing document_id if successful
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # DRY RUN MODE
        if self.dry_run:
            print("\n" + "="*60)
            print("🔧 PAPERLESS DRY RUN - Would upload with:")
            print("="*60)
            print(f"  File: {file_path.name}")
            print(f"  Title: {title or file_path.stem}")
            print(f"  Tags: {tags or 'None'}")
            print(f"  Document Type: {document_type or 'None'}")
            print(f"  Correspondent: {correspondent or 'None'}")
            print(f"  Created Date: {created_date or 'None'}")
            print(f"  URL: {self.base_url}/api/documents/post_document/")
            print("="*60 + "\n")

            return {
                'success': True,
                'document_id': 'DRY_RUN_12345',
                'task_id': 'DRY_RUN_TASK',
                'message': '✓ DRY RUN: Would upload to Paperless (no actual upload performed)',
                'dry_run': True
            }

        # Prepare upload URL
        url = f"{self.base_url}/api/documents/post_document/"

        # Prepare files
        files = {
            'document': (file_path.name, open(file_path, 'rb'), 'application/pdf')
        }

        # Prepare data as list of tuples to allow multiple values for same key
        data = []

        if title:
            data.append(('title', title))

        if created_date:
            data.append(('created', created_date))

        # Handle tags - send as multiple form fields
        if tags:
            tag_ids = self._resolve_tags(tags)
            for tag_id in tag_ids:
                # Send each tag ID as a separate form field
                data.append(('tags', str(tag_id)))

        # Handle document type
        if document_type:
            type_id = self._resolve_document_type(document_type)
            if type_id:
                data.append(('document_type', str(type_id)))

        # Handle correspondent
        if correspondent:
            corr_id = self._resolve_correspondent(correspondent)
            if corr_id:
                data.append(('correspondent', str(corr_id)))

        try:
            response = requests.post(
                url,
                headers=self.headers,
                files=files,
                data=data,
                timeout=60
            )

            response.raise_for_status()

            # Paperless-NGX returns just a UUID string, not JSON
            # The UUID is the task ID
            task_id = response.text.strip().strip('"')

            print(f"✓ Paperless upload initiated (task ID: {task_id})")

            return {
                'success': True,
                'task_id': task_id,
                'message': 'Document uploaded successfully'
            }

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to upload to Paperless: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            # Close file
            if 'document' in files:
                files['document'][1].close()

    def _resolve_tags(self, tags):
        """Convert tag names to IDs, creating tags if they don't exist"""
        tag_ids = []

        for tag in tags:
            if isinstance(tag, int):
                tag_ids.append(tag)
            else:
                # Look up or create tag
                tag_id = self._get_or_create_tag(tag)
                if tag_id:
                    tag_ids.append(tag_id)

        return tag_ids

    def _get_or_create_tag(self, tag_name):
        """Get tag ID by name, creating if it doesn't exist"""
        try:
            # Search for existing tag
            url = f"{self.base_url}/api/tags/"
            response = requests.get(
                url,
                headers=self.headers,
                params={'name__iexact': tag_name},
                timeout=10
            )

            response.raise_for_status()
            results = response.json().get('results', [])

            if results:
                return results[0]['id']

            # Create new tag
            response = requests.post(
                url,
                headers=self.headers,
                json={'name': tag_name},
                timeout=10
            )

            response.raise_for_status()
            return response.json()['id']

        except Exception as e:
            print(f"ERROR: Failed to get/create tag '{tag_name}': {e}")
            return None

    def _resolve_document_type(self, doc_type):
        """Convert document type name to ID"""
        if isinstance(doc_type, int):
            return doc_type

        try:
            url = f"{self.base_url}/api/document_types/"
            response = requests.get(
                url,
                headers=self.headers,
                params={'name__iexact': doc_type},
                timeout=10
            )

            response.raise_for_status()
            results = response.json().get('results', [])

            if results:
                return results[0]['id']

            # Create new document type
            response = requests.post(
                url,
                headers=self.headers,
                json={'name': doc_type},
                timeout=10
            )

            response.raise_for_status()
            return response.json()['id']

        except Exception as e:
            print(f"ERROR: Failed to resolve document type '{doc_type}': {e}")
            return None

    def _resolve_correspondent(self, correspondent):
        """Convert correspondent name to ID"""
        if isinstance(correspondent, int):
            return correspondent

        try:
            url = f"{self.base_url}/api/correspondents/"
            response = requests.get(
                url,
                headers=self.headers,
                params={'name__iexact': correspondent},
                timeout=10
            )

            response.raise_for_status()
            results = response.json().get('results', [])

            if results:
                return results[0]['id']

            # Create new correspondent
            response = requests.post(
                url,
                headers=self.headers,
                json={'name': correspondent},
                timeout=10
            )

            response.raise_for_status()
            return response.json()['id']

        except Exception as e:
            print(f"ERROR: Failed to resolve correspondent '{correspondent}': {e}")
            return None

    def update_document(self, document_id, title=None, tags=None, document_type=None,
                       correspondent=None, created_date=None, custom_fields=None):
        """
        Update an existing Paperless document's metadata (does not replace the file)

        Args:
            document_id: Existing document ID
            title: Document title
            tags: List of tag names or IDs
            document_type: Document type name or ID
            correspondent: Correspondent name or ID
            created_date: Document creation date (YYYY-MM-DD)
            custom_fields: Dictionary of custom field values

        Returns:
            dict: Response containing success status
        """
        # DRY RUN MODE
        if self.dry_run:
            print("\n" + "="*60)
            print("🔧 PAPERLESS DRY RUN - Would update document:")
            print("="*60)
            print(f"  Document ID: {document_id}")
            print(f"  Title: {title or 'No change'}")
            print(f"  Tags: {tags or 'No change'}")
            print(f"  Document Type: {document_type or 'No change'}")
            print(f"  Correspondent: {correspondent or 'No change'}")
            print(f"  Created Date: {created_date or 'No change'}")
            print(f"  URL: {self.base_url}/api/documents/{document_id}/")
            print("="*60 + "\n")

            return {
                'success': True,
                'document_id': document_id,
                'message': '✓ DRY RUN: Would update Paperless document (no actual update performed)',
                'dry_run': True
            }

        # Get current document
        current_doc = self.get_document(document_id)
        if not current_doc:
            return {
                'success': False,
                'error': f'Document {document_id} not found'
            }

        # Prepare update data
        update_data = {}

        if title:
            update_data['title'] = title

        if created_date:
            update_data['created'] = created_date

        # Handle tags
        if tags:
            tag_ids = self._resolve_tags(tags)
            # Merge with existing tags instead of replacing
            existing_tags = current_doc.get('tags', [])
            all_tags = list(set(existing_tags + tag_ids))
            update_data['tags'] = all_tags

        # Handle document type
        if document_type:
            type_id = self._resolve_document_type(document_type)
            if type_id:
                update_data['document_type'] = type_id

        # Handle correspondent
        if correspondent:
            corr_id = self._resolve_correspondent(correspondent)
            if corr_id:
                update_data['correspondent'] = corr_id

        try:
            url = f"{self.base_url}/api/documents/{document_id}/"
            response = requests.patch(
                url,
                headers={**self.headers, 'Content-Type': 'application/json'},
                json=update_data,
                timeout=30
            )

            response.raise_for_status()

            print(f"✓ Paperless document {document_id} updated successfully")

            return {
                'success': True,
                'document_id': document_id,
                'message': 'Document metadata updated successfully'
            }

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to update Paperless document {document_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_document(self, document_id):
        """Get document details by ID"""
        try:
            url = f"{self.base_url}/api/documents/{document_id}/"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"ERROR: Failed to get document {document_id}: {e}")
            return None


if __name__ == '__main__':
    # Test Paperless connection
    try:
        client = PaperlessClient()
        print(f"✓ Paperless client initialized")
        print(f"  Base URL: {client.base_url}")
        print(f"  API Token: {'*' * 20}{client.api_token[-4:]}")
    except Exception as e:
        print(f"✗ Failed to initialize Paperless client: {e}")
