#!/usr/bin/env python3
"""
Pushover Notification Handler
Sends notifications about document processing events
"""

import os
import requests
from pathlib import Path

class NotificationHandler:
    """Handle Pushover notifications"""

    def __init__(self):
        self.user_key = os.getenv('PUSHOVER_USER')
        self.app_token = os.getenv('PUSHOVER_TOKEN')
        self.api_url = 'https://api.pushover.net/1/messages.json'
        self.enabled = bool(self.user_key and self.app_token)

    def send(self, message, title=None, priority=0, url=None, url_title=None):
        """
        Send a Pushover notification

        Args:
            message: The message content
            title: Notification title (optional)
            priority: -2 (lowest) to 2 (emergency), default 0
            url: URL to include in notification
            url_title: Title for the URL

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enabled:
            print("⚠️  Pushover notifications disabled (credentials not configured or expired)")
            return False

        payload = {
            'token': self.app_token,
            'user': self.user_key,
            'message': message,
            'priority': priority
        }

        if title:
            payload['title'] = title

        if url:
            payload['url'] = url
            if url_title:
                payload['url_title'] = url_title

        try:
            response = requests.post(self.api_url, data=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"ERROR: Failed to send Pushover notification: {e}")
            return False

    def notify_processing_started(self, filename, category):
        """Notify that processing has started"""
        return self.send(
            message=f"Started processing: {filename}",
            title=f"Document Processing ({category})",
            priority=-1  # Low priority
        )

    def notify_processing_completed(self, filename, category, paperless_id=None, basicmemory_path=None):
        """Notify that processing completed successfully"""
        message = f"Successfully processed: {filename}\nCategory: {category}"

        if basicmemory_path:
            message += f"\nBasicMemory note created"

        url = None
        url_title = None
        if paperless_id:
            url = f"https://paperless.redleif.dev/documents/{paperless_id}"
            url_title = "View in Paperless"

        return self.send(
            message=message,
            title="✓ Document Processed",
            priority=0,
            url=url,
            url_title=url_title
        )

    def notify_clarification_needed(self, filename, category, question):
        """Notify that clarification is needed"""
        return self.send(
            message=f"Document: {filename}\nCategory: {category}\n\nQuestion: {question}",
            title="⚠ Clarification Needed",
            priority=1,  # High priority
            url="https://scanui.redleif.dev/pending",
            url_title="View Pending"
        )

    def notify_processing_failed(self, filename, error_message):
        """Notify that processing failed"""
        return self.send(
            message=f"Failed to process: {filename}\n\nError: {error_message}",
            title="✗ Processing Failed",
            priority=1,  # High priority
            url="https://scanui.redleif.dev/history?status=failed",
            url_title="View Failures"
        )

    def notify_batch_completed(self, count, category=None):
        """Notify that a batch of documents was processed"""
        category_str = f" ({category})" if category else ""
        return self.send(
            message=f"Processed {count} document(s){category_str}",
            title="Batch Processing Complete",
            priority=-1
        )


if __name__ == '__main__':
    # Test notification
    notifier = NotificationHandler()

    print("Sending test notification...")
    success = notifier.send(
        message="This is a test notification from the scan processor system",
        title="Test Notification",
        priority=0
    )

    if success:
        print("✓ Test notification sent successfully")
    else:
        print("✗ Failed to send test notification")
