"""
Match data parser utility module - Stub implementation for testing
"""

from datetime import datetime


class MatchDataParser:
    """
    Stub implementation of MatchDataParser for testing purposes.
    This handles sports/match data parsing but provides fallback for general testing.
    """

    def __init__(self, payload=None, event_type=None):
        self.payload = payload
        self.event_type = event_type

    def create_detailed_summary(self):
        """
        Create a detailed summary from match data.
        For testing purposes, this returns default values.

        Returns:
            tuple: (message, overBall, timestamp, match_id, feed_id)
        """
        # For testing, just return the payload as the message with default values
        message = str(self.payload) if self.payload else "test payload"
        overBall = "test_over"
        timestamp = str(datetime.now())
        match_id = "test_match_123"
        feed_id = "test_feed_456"

        return message, overBall, timestamp, match_id, feed_id
