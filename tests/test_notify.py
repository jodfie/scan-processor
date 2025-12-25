"""
Tests for Notification Handler

Tests the Pushover notification system
"""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from notify import NotificationHandler


class TestNotificationHandlerInit:
    """Test NotificationHandler initialization"""

    def test_init_with_env_vars(self, monkeypatch):
        """Test initialization with environment variables"""
        monkeypatch.setenv('PUSHOVER_USER', 'test_user')
        monkeypatch.setenv('PUSHOVER_TOKEN', 'test_token')

        handler = NotificationHandler()

        assert handler.user_key == 'test_user'
        assert handler.app_token == 'test_token'
        assert handler.enabled is True

    def test_init_without_credentials(self, monkeypatch):
        """Test initialization without credentials disables notifications"""
        monkeypatch.delenv('PUSHOVER_USER', raising=False)
        monkeypatch.delenv('PUSHOVER_TOKEN', raising=False)

        handler = NotificationHandler()

        assert handler.enabled is False


class TestSendMethod:
    """Test basic send method"""

    def test_send_with_default_priority(self, mocker, monkeypatch):
        """Test sending notification with default priority"""
        monkeypatch.setenv('PUSHOVER_USER', 'test_user')
        monkeypatch.setenv('PUSHOVER_TOKEN', 'test_token')

        mock_post = mocker.patch('requests.post')
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_post.return_value = mock_response

        handler = NotificationHandler()
        result = handler.send("Test message")

        assert result is True
        assert mock_post.called
        call_args = mock_post.call_args

        # Verify correct data sent
        assert call_args[1]['data']['message'] == "Test message"
        assert call_args[1]['data']['user'] == 'test_user'
        assert call_args[1]['data']['token'] == 'test_token'
        assert call_args[1]['data']['priority'] == 0

    def test_send_with_high_priority(self, mocker, monkeypatch):
        """Test sending notification with high priority"""
        monkeypatch.setenv('PUSHOVER_USER', 'test')
        monkeypatch.setenv('PUSHOVER_TOKEN', 'test')

        mock_post = mocker.patch('requests.post')
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_post.return_value = mock_response

        handler = NotificationHandler()
        result = handler.send("Urgent message", priority=1)

        assert result is True
        call_args = mock_post.call_args
        assert call_args[1]['data']['priority'] == 1

    def test_send_with_title(self, mocker, monkeypatch):
        """Test sending notification with custom title"""
        monkeypatch.setenv('PUSHOVER_USER', 'test')
        monkeypatch.setenv('PUSHOVER_TOKEN', 'test')

        mock_post = mocker.patch('requests.post')
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_post.return_value = mock_response

        handler = NotificationHandler()
        result = handler.send("Test message", title="Custom Title")

        assert result is True
        call_args = mock_post.call_args
        assert call_args[1]['data']['title'] == "Custom Title"

    def test_send_with_url(self, mocker, monkeypatch):
        """Test sending notification with URL"""
        monkeypatch.setenv('PUSHOVER_USER', 'test')
        monkeypatch.setenv('PUSHOVER_TOKEN', 'test')

        mock_post = mocker.patch('requests.post')
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_post.return_value = mock_response

        handler = NotificationHandler()
        result = handler.send(
            "Test message",
            url="https://example.com",
            url_title="Click here"
        )

        assert result is True
        call_args = mock_post.call_args
        assert call_args[1]['data']['url'] == "https://example.com"
        assert call_args[1]['data']['url_title'] == "Click here"

    def test_send_handles_network_error(self, mocker, monkeypatch):
        """Test handling of network errors"""
        monkeypatch.setenv('PUSHOVER_USER', 'test')
        monkeypatch.setenv('PUSHOVER_TOKEN', 'test')

        mock_post = mocker.patch('requests.post')
        mock_post.side_effect = Exception("Network error")

        handler = NotificationHandler()
        result = handler.send("Test message")

        assert result is False

    def test_send_disabled_when_no_credentials(self, monkeypatch):
        """Test send returns False when credentials not configured"""
        monkeypatch.delenv('PUSHOVER_USER', raising=False)
        monkeypatch.delenv('PUSHOVER_TOKEN', raising=False)

        handler = NotificationHandler()
        result = handler.send("Test message")

        assert result is False


class TestProcessingNotifications:
    """Test processing-related notifications"""

    def test_notify_processing_started(self, mocker, monkeypatch):
        """Test notification for processing start"""
        monkeypatch.setenv('PUSHOVER_USER', 'test')
        monkeypatch.setenv('PUSHOVER_TOKEN', 'test')

        mock_post = mocker.patch('requests.post')
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_post.return_value = mock_response

        handler = NotificationHandler()
        result = handler.notify_processing_started("test.pdf", "PERSONAL-MEDICAL")

        assert result is True
        call_args = mock_post.call_args
        assert "test.pdf" in call_args[1]['data']['message']

    def test_notify_processing_completed(self, mocker, monkeypatch):
        """Test notification for completed document"""
        monkeypatch.setenv('PUSHOVER_USER', 'test')
        monkeypatch.setenv('PUSHOVER_TOKEN', 'test')

        mock_post = mocker.patch('requests.post')
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_post.return_value = mock_response

        handler = NotificationHandler()
        result = handler.notify_processing_completed(
            filename="medical-bill.pdf",
            category="PERSONAL-MEDICAL"
        )

        assert result is True

    def test_notify_clarification_needed(self, mocker, monkeypatch):
        """Test notification for documents needing clarification"""
        monkeypatch.setenv('PUSHOVER_USER', 'test')
        monkeypatch.setenv('PUSHOVER_TOKEN', 'test')

        mock_post = mocker.patch('requests.post')
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_post.return_value = mock_response

        handler = NotificationHandler()
        result = handler.notify_clarification_needed(
            filename="unclear.pdf",
            category="UNKNOWN",
            question="Could not determine document type"
        )

        assert result is True

    def test_notify_processing_failed(self, mocker, monkeypatch):
        """Test notification for processing failures"""
        monkeypatch.setenv('PUSHOVER_USER', 'test')
        monkeypatch.setenv('PUSHOVER_TOKEN', 'test')

        mock_post = mocker.patch('requests.post')
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_post.return_value = mock_response

        handler = NotificationHandler()
        result = handler.notify_processing_failed(
            filename="failed.pdf",
            error_message="Classification timeout"
        )

        assert result is True

    def test_notify_batch_completed(self, mocker, monkeypatch):
        """Test notification for batch processing completion"""
        monkeypatch.setenv('PUSHOVER_USER', 'test')
        monkeypatch.setenv('PUSHOVER_TOKEN', 'test')

        mock_post = mocker.patch('requests.post')
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_post.return_value = mock_response

        handler = NotificationHandler()
        result = handler.notify_batch_completed(
            count=10,
            category="PERSONAL-MEDICAL"
        )

        assert result is True
