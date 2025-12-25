#!/usr/bin/env python3
"""
Main Document Processing Orchestrator
Coordinates document classification, metadata extraction, and routing
"""

import sys
import os
import time
import sqlite3
import json
import argparse
import traceback
from pathlib import Path
from datetime import datetime
import shutil

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from classifier import DocumentClassifier
from paperless import PaperlessClient
from basicmemory import BasicMemoryNoteCreator
from notify import NotificationHandler

class DocumentProcessor:
    """Main document processing orchestrator"""

    def __init__(self, base_dir=None, dev_mode=False, corrections=None, paperless_id=None):
        # Auto-detect container vs host environment
        if base_dir is None:
            if Path('/app/incoming').exists():
                base_dir = '/app'
            else:
                base_dir = '/home/jodfie/scan-processor'
        self.base_dir = Path(base_dir)
        self.dev_mode = dev_mode
        self.corrections = corrections  # Store corrections for re-processing
        self.paperless_id = paperless_id  # Existing Paperless document ID (UPDATE mode)

        self.incoming_dir = self.base_dir / 'incoming'
        self.processing_dir = self.base_dir / 'processing'
        self.completed_dir = self.base_dir / 'completed'
        self.failed_dir = self.base_dir / 'failed'
        self.db_path = self.base_dir / 'queue' / 'pending.db'

        # Initialize components
        self.classifier = DocumentClassifier(self.base_dir / 'prompts')
        self.paperless = PaperlessClient(dry_run=dev_mode)
        self.basicmemory = BasicMemoryNoteCreator(dry_run=dev_mode)
        self.notifier = NotificationHandler()

        if self.dev_mode:
            print("\n" + "="*60)
            print("🔧 DEVELOPMENT MODE ENABLED")
            print("="*60)
            print("⚠️  No actual uploads will be performed")
            print("⚠️  Paperless: DRY RUN")
            print("⚠️  BasicMemory: DRY RUN")
            print("⚠️  Verbose error logging enabled")
            print("="*60 + "\n")

        if self.paperless_id:
            print("\n" + "="*60)
            print("🔄 UPDATE MODE - Existing Paperless Document")
            print("="*60)
            print(f"📄 Document ID: {self.paperless_id}")
            print("✓ Will UPDATE metadata (not upload new file)")
            print("="*60 + "\n")

    def process_document(self, file_path):
        """
        Process a single document through the full pipeline

        Args:
            file_path: Path to the PDF document

        Returns:
            dict: Processing result
        """
        file_path = Path(file_path)
        start_time = time.time()

        print(f"\n{'='*60}")
        print(f"Processing: {file_path.name}")
        print(f"{'='*60}")

        try:
            # Move to processing directory
            processing_path = self.processing_dir / file_path.name
            shutil.move(str(file_path), str(processing_path))
            print(f"✓ Moved to processing directory")

            # Step 1: Classify document
            print("\n[1/5] Classifying document...")

            # Use override category if provided in corrections
            if self.corrections and self.corrections.get('override_category'):
                category = self.corrections['override_category']
                print(f"📝 Using override category from corrections: {category}")
                # Still run classification but with correction context
                classification = self.classifier.classify_document(processing_path, corrections=self.corrections)
                classification['category'] = category  # Override with correction
            else:
                classification = self.classifier.classify_document(processing_path, corrections=self.corrections)
                category = classification.get('category', 'GENERAL')

            print(f"✓ Category: {category} (confidence: {classification.get('confidence', 0):.2%})")

            # Check if clarification needed
            if classification.get('needs_clarification'):
                print(f"⚠ Clarification needed: {classification.get('clarification_question')}")
                self._handle_clarification_needed(processing_path, classification)
                return {
                    'status': 'pending_clarification',
                    'category': category,
                    'processing_time_ms': int((time.time() - start_time) * 1000)
                }

            # Step 2: Extract detailed metadata based on category
            print(f"\n[2/5] Extracting {category} metadata...")
            metadata = self._extract_metadata(processing_path, category)
            print(f"✓ Metadata extracted")

            # Step 3: Sync to Paperless (Upload or Update)
            if self.paperless_id:
                print(f"\n[3/5] Updating existing Paperless document {self.paperless_id}...")
                paperless_result = self._update_paperless_metadata(self.paperless_id, category, metadata)
                paperless_id = self.paperless_id
            else:
                print("\n[3/5] Uploading to Paperless...")
                paperless_result = self._upload_to_paperless(processing_path, category, metadata)
                paperless_id = paperless_result.get('document_id')

            if paperless_result.get('success'):
                action = "Updated" if self.paperless_id else "Uploaded to"
                print(f"✓ {action} Paperless (ID: {paperless_id})")
            else:
                action = "update" if self.paperless_id else "upload"
                print(f"✗ Paperless {action} failed: {paperless_result.get('error')}")

            # Step 4: Create BasicMemory note (for MEDICAL and CPS_EXPENSE only)
            basicmemory_path = None
            if category in ['MEDICAL', 'CPS_EXPENSE']:
                print(f"\n[4/5] Creating BasicMemory note...")
                basicmemory_path = self._create_basicmemory_note(category, metadata)

                if basicmemory_path:
                    print(f"✓ BasicMemory note created: {basicmemory_path}")
                else:
                    print(f"⚠ BasicMemory note creation skipped or failed")
            else:
                print(f"\n[4/5] Skipping BasicMemory note (category: {category})")

            # Step 5: Send notification
            print("\n[5/5] Sending notification...")
            self.notifier.notify_processing_completed(
                filename=file_path.name,
                category=category,
                paperless_id=paperless_id,
                basicmemory_path=str(basicmemory_path) if basicmemory_path else None
            )
            print(f"✓ Notification sent")

            # Move to completed
            completed_path = self.completed_dir / file_path.name
            shutil.move(str(processing_path), str(completed_path))
            print(f"\n✓ Moved to completed directory")

            # Log to history with prompts, responses, and files created
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Build list of files created
            files_created = []
            if paperless_id:
                files_created.append({
                    'type': 'paperless',
                    'id': paperless_id,
                    'url': f"https://paperless.redleif.dev/documents/{paperless_id}"
                })
            if basicmemory_path:
                files_created.append({
                    'type': 'basicmemory',
                    'path': str(basicmemory_path)
                })

            self._log_to_history(
                filename=file_path.name,
                category=category,
                status='success',
                paperless_id=paperless_id,
                basicmemory_path=str(basicmemory_path) if basicmemory_path else None,
                processing_time_ms=processing_time_ms,
                classification_prompt=classification.get('_prompt'),
                classification_response=classification.get('_response'),
                metadata_prompt=metadata.get('_prompt') if metadata else None,
                metadata_response=metadata.get('_response') if metadata else None,
                files_created=files_created if files_created else None,
                corrections=self.corrections
            )

            print(f"\n{'='*60}")
            print(f"✓ Processing completed in {processing_time_ms/1000:.2f}s")
            print(f"{'='*60}\n")

            return {
                'status': 'success',
                'category': category,
                'paperless_id': paperless_id,
                'basicmemory_path': str(basicmemory_path) if basicmemory_path else None,
                'processing_time_ms': processing_time_ms
            }

        except Exception as e:
            print(f"\n✗ ERROR: {e}")

            # Verbose error logging in dev mode
            if self.dev_mode:
                print("\n" + "="*60)
                print("📋 VERBOSE ERROR DETAILS (Development Mode)")
                print("="*60)
                print(f"Error Type: {type(e).__name__}")
                print(f"Error Message: {str(e)}")
                print("\nFull Traceback:")
                print(traceback.format_exc())
                print("="*60 + "\n")

            # Move to failed directory
            try:
                failed_path = self.failed_dir / file_path.name
                if processing_path.exists():
                    shutil.move(str(processing_path), str(failed_path))
                elif file_path.exists():
                    shutil.move(str(file_path), str(failed_path))
                print(f"✓ Moved to failed directory")
            except Exception as move_error:
                print(f"✗ Failed to move file: {move_error}")
                if self.dev_mode:
                    print(f"Move error traceback: {traceback.format_exc()}")

            # Send failure notification (skip in dev mode)
            if not self.dev_mode:
                self.notifier.notify_processing_failed(file_path.name, str(e))
            else:
                print("🔇 Skipping failure notification (dev mode)")

            # Log failure
            processing_time_ms = int((time.time() - start_time) * 1000)
            self._log_to_history(
                filename=file_path.name,
                category='UNKNOWN',
                status='failed',
                error_message=str(e),
                processing_time_ms=processing_time_ms,
                corrections=self.corrections
            )

            return {
                'status': 'failed',
                'error': str(e),
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc() if self.dev_mode else None,
                'processing_time_ms': processing_time_ms
            }

    def _extract_metadata(self, file_path, category):
        """Extract metadata based on document category"""
        # CPS categories (dash-based naming)
        if category == 'CPS-MEDICAL':
            return self.classifier.extract_medical_metadata(file_path, corrections=self.corrections)
        elif category == 'CPS-EXPENSE':
            return self.classifier.extract_expense_metadata(file_path, corrections=self.corrections)
        elif category == 'CPS-SCHOOLWORK':
            return self.classifier.extract_schoolwork_metadata(file_path, corrections=self.corrections)
        
        # Personal categories (dash-based naming)
        elif category == 'PERSONAL-MEDICAL':
            return self.classifier.extract_personal_medical_metadata(file_path, corrections=self.corrections)
        elif category == 'PERSONAL-EXPENSE':
            return self.classifier.extract_personal_expense_metadata(file_path, corrections=self.corrections)
        elif category == 'UTILITY':
            return self.classifier.extract_utility_metadata(file_path, corrections=self.corrections)
        elif category in ['AUTO-INSURANCE', 'AUTO-MAINTENANCE', 'AUTO-REGISTRATION']:
            return self.classifier.extract_auto_metadata(file_path, corrections=self.corrections)
        
        # Categories without specific extractors (GENERAL, REFERENCE, etc.)
        else:
            return {}

    def _upload_to_paperless(self, file_path, category, metadata):
        """Upload document to Paperless with appropriate tags"""
        tags = [category.lower()]

        # Add child tag if available
        if metadata.get('child'):
            tags.append(metadata['child'].lower())

        # Determine document type
        doc_type = {
            'MEDICAL': 'Medical',
            'CPS_EXPENSE': 'Expense',
            'SCHOOLWORK': 'Schoolwork',
            'GENERAL': 'Document'
        }.get(category, 'Document')

        # Upload
        return self.paperless.upload_document(
            file_path=file_path,
            title=metadata.get('title', file_path.stem),
            tags=tags,
            document_type=doc_type,
            created_date=metadata.get('date')
        )

    def _update_paperless_metadata(self, document_id, category, metadata):
        """Update existing Paperless document metadata with Claude-extracted info"""
        tags = [category.lower()]

        # Add child tag if available
        if metadata.get('child'):
            tags.append(metadata['child'].lower())

        # Determine document type
        doc_type = {
            'MEDICAL': 'Medical',
            'CPS_EXPENSE': 'Expense',
            'SCHOOLWORK': 'Schoolwork',
            'GENERAL': 'Document'
        }.get(category, 'Document')

        # Update (merges with existing tags, doesn't replace)
        return self.paperless.update_document(
            document_id=document_id,
            title=metadata.get('title'),
            tags=tags,
            document_type=doc_type,
            created_date=metadata.get('date')
        )

    def _create_basicmemory_note(self, category, metadata):
        """Create BasicMemory note with dual-vault routing"""
        try:
            # CPS categories go to CoparentingSystem vault
            if category == 'CPS-MEDICAL':
                return self.basicmemory.create_medical_note(metadata)
            elif category == 'CPS-EXPENSE':
                return self.basicmemory.create_expense_note(metadata)
            
            # Personal categories go to Personal vault
            elif category == 'PERSONAL-MEDICAL':
                return self.basicmemory.create_personal_medical_note(metadata)
            elif category == 'PERSONAL-EXPENSE':
                return self.basicmemory.create_personal_expense_note(metadata)
            elif category == 'UTILITY':
                return self.basicmemory.create_utility_note(metadata)
            elif category in ['AUTO-INSURANCE', 'AUTO-MAINTENANCE', 'AUTO-REGISTRATION']:
                return self.basicmemory.create_auto_note(metadata)
            
            # Other categories don't get BasicMemory notes
            else:
                return None
                
        except Exception as e:
            print(f"ERROR creating BasicMemory note: {e}")
            return None

    def _handle_clarification_needed(self, file_path, classification):
        """Handle document that needs clarification"""
        # Add to pending database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO pending_documents (filename, category, question, metadata)
            VALUES (?, ?, ?, ?)
        """, (
            file_path.name,
            classification.get('category', 'UNKNOWN'),
            classification.get('clarification_question', 'Please review this document'),
            json.dumps(classification.get('metadata', {}))
        ))

        conn.commit()
        conn.close()

        # Send notification
        self.notifier.notify_clarification_needed(
            filename=file_path.name,
            category=classification.get('category', 'UNKNOWN'),
            question=classification.get('clarification_question', 'Please review')
        )

    def _log_to_history(self, filename, category, status, paperless_id=None,
                       basicmemory_path=None, processing_time_ms=None, error_message=None,
                       classification_prompt=None, classification_response=None,
                       metadata_prompt=None, metadata_response=None, files_created=None,
                       corrections=None):
        """Log processing result to history database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Convert files_created list to JSON if provided
        import json
        files_created_json = json.dumps(files_created) if files_created else None
        corrections_json = json.dumps(corrections) if corrections else None

        cursor.execute("""
            INSERT INTO processing_history
            (filename, category, status, paperless_id, basicmemory_path, processing_time_ms, error_message,
             classification_prompt, classification_response, metadata_prompt, metadata_response, files_created, corrections)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename,
            category,
            status,
            paperless_id,
            basicmemory_path,
            processing_time_ms,
            error_message,
            classification_prompt,
            classification_response,
            metadata_prompt,
            metadata_response,
            files_created_json,
            corrections_json
        ))

        conn.commit()
        conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process scanned documents through classification and routing pipeline'
    )
    parser.add_argument('file_path', help='Path to the PDF document to process')
    parser.add_argument(
        '--dev', '--dry-run',
        action='store_true',
        dest='dev_mode',
        help='Development mode: Skip actual uploads to Paperless/BasicMemory, show verbose errors'
    )
    parser.add_argument(
        '--corrections',
        type=str,
        help='JSON string with corrections for re-processing (override_category, notes, reason)'
    )
    parser.add_argument(
        '--paperless-id',
        type=int,
        dest='paperless_id',
        help='Existing Paperless document ID to update instead of uploading new document'
    )

    args = parser.parse_args()

    # Parse corrections if provided
    corrections = None
    if args.corrections:
        import json
        try:
            corrections = json.loads(args.corrections)
            print(f"\n📝 Re-processing with corrections:")
            print(f"  Reason: {corrections.get('reason', 'N/A')}")
            if corrections.get('override_category'):
                print(f"  Override Category: {corrections['override_category']}")
            if corrections.get('notes'):
                print(f"  Notes: {corrections['notes'][:100]}...")
        except Exception as e:
            print(f"⚠️  Warning: Could not parse corrections JSON: {e}")

    processor = DocumentProcessor(
        dev_mode=args.dev_mode,
        corrections=corrections,
        paperless_id=args.paperless_id
    )
    result = processor.process_document(args.file_path)

    print(f"\nFinal result: {json.dumps(result, indent=2)}")
    sys.exit(0 if result['status'] == 'success' else 1)
