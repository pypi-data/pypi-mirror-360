"""Unit tests for the notification service module.

This module contains tests for the NotificationService class,
which handles desktop notifications.
"""

import pytest
from unittest.mock import MagicMock, patch

from simpletimerbank.core.notification_service import NotificationService


class TestNotificationService:
    """Test cases for the NotificationService class."""
    
    @patch('simpletimerbank.core.notification_service.notification')
    def test_init(self, mock_notification):
        """Test initialization of NotificationService."""
        # Create an instance
        service = NotificationService()
        # Verify that it initialized correctly
        assert service is not None
    
    @patch('simpletimerbank.core.notification_service.notification')
    def test_notify_timer_completed(self, mock_notification):
        """Test sending a timer completion notification."""
        # Setup
        service = NotificationService()
        
        # Execute
        service.notify_timer_completed()
        
        # Verify
        mock_notification.notify.assert_called_once()
        # Check title and message
        title = mock_notification.notify.call_args[1]['title']
        message = mock_notification.notify.call_args[1]['message']
        assert "Timer" in title
        assert "completed" in message
    
    @patch('simpletimerbank.core.notification_service.notification')
    def test_notify_overdraft_started(self, mock_notification):
        """Test sending an overdraft started notification."""
        # Setup
        service = NotificationService()
        
        # Execute
        service.notify_overdraft_started()
        
        # Verify
        mock_notification.notify.assert_called_once()
        # Check title and message
        title = mock_notification.notify.call_args[1]['title']
        message = mock_notification.notify.call_args[1]['message']
        assert "Overdraft" in title
        assert "withdrawing" in message
    
    @patch('simpletimerbank.core.notification_service.notification')
    def test_notify_bank_depleted(self, mock_notification):
        """Test sending a bank depleted notification."""
        # Setup
        service = NotificationService()
        
        # Execute
        service.notify_bank_depleted()
        
        # Verify
        mock_notification.notify.assert_called_once()
        # Check title and message
        title = mock_notification.notify.call_args[1]['title']
        message = mock_notification.notify.call_args[1]['message']
        assert "Bank" in title
        assert "depleted" in message 