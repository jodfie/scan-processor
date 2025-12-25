#!/usr/bin/env python3
"""
WebSocket Broadcasting Utilities
For sending real-time updates from external processes to web clients
"""

import requests
import json

class WebSocketBroadcaster:
    """Broadcast events to WebSocket clients via Flask-SocketIO"""

    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url

    def broadcast_event(self, event_name, data):
        """
        Broadcast an event to all connected WebSocket clients

        Args:
            event_name: Name of the event (e.g., 'processing_started')
            data: Dictionary of data to send
        """
        try:
            # In production, this would use Redis or similar for pub/sub
            # For now, we can use HTTP POST to trigger events
            response = requests.post(
                f"{self.base_url}/api/broadcast",
                json={'event': event_name, 'data': data},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error broadcasting event: {e}")
            return False

    def processing_started(self, filename, category):
        """Notify that processing has started"""
        return self.broadcast_event('processing_started', {
            'filename': filename,
            'category': category,
            'timestamp': str(time.time())
        })

    def processing_completed(self, filename, category, status, **kwargs):
        """Notify that processing has completed"""
        return self.broadcast_event('processing_completed', {
            'filename': filename,
            'category': category,
            'status': status,
            **kwargs
        })

    def clarification_needed(self, filename, question, options=None):
        """Notify that clarification is needed"""
        return self.broadcast_event('clarification_needed', {
            'filename': filename,
            'question': question,
            'options': options or []
        })

    def error_occurred(self, filename, error_message):
        """Notify that an error occurred"""
        return self.broadcast_event('error_occurred', {
            'filename': filename,
            'error': error_message
        })


# Example usage
if __name__ == '__main__':
    import time

    broadcaster = WebSocketBroadcaster()

    # Test broadcast
    broadcaster.processing_started('test.pdf', 'MEDICAL')
    time.sleep(2)
    broadcaster.processing_completed('test.pdf', 'MEDICAL', 'success',
                                    paperless_id=123,
                                    basicmemory_path='Medical/test.md')
