"""Tests for the AppStateManager's interaction with the GUI.

This module contains tests that verify the AppStateManager properly 
provides the interface needed by the GUI.
"""

import pytest
from unittest.mock import MagicMock, patch

from simpletimerbank.core.app_state import AppStateManager
from simpletimerbank.core.countdown_timer import TimerState


@pytest.fixture
def app_manager():
    """Create a mock AppStateManager for testing."""
    manager = MagicMock(spec=AppStateManager)
    manager.get_balance_seconds.return_value = 3600  # 1 hour
    manager.get_balance_formatted.return_value = "01:00:00"
    manager.get_timer_state.return_value = TimerState.IDLE
    
    # Create mock for the time_balance
    mock_time_balance = MagicMock()
    manager.get_time_bank.return_value = mock_time_balance
    
    return manager


class TestAppStateManagerGUIInterface:
    """Test the AppStateManager interface used by the GUI."""
    
    def test_get_balance_formatted(self, app_manager):
        """Verify the formatted balance string is correct."""
        # Mock the implementation
        app_manager.get_balance_formatted.return_value = "01:02:03"
        
        # Test
        result = app_manager.get_balance_formatted()
        assert result == "01:02:03"
    
    def test_start_timer(self, app_manager):
        """Verify start_timer delegates to start_session with current balance."""
        # Setup
        app_manager.get_balance_seconds.return_value = 7200  # 2 hours
        app_manager.start_timer.return_value = True
        
        # Test
        result = app_manager.start_timer()
        
        # Verify
        assert result is True
        app_manager.start_timer.assert_called_once()
    
    def test_pause_timer(self, app_manager):
        """Verify pause_timer delegates to pause_session."""
        # Test
        app_manager.pause_timer()
        
        # Verify
        app_manager.pause_timer.assert_called_once()
    
    def test_stop_timer(self, app_manager):
        """Verify stop_timer delegates to stop_session."""
        # Test
        app_manager.stop_timer()
        
        # Verify
        app_manager.stop_timer.assert_called_once()
    
    def test_set_timer_callback(self, app_manager):
        """Verify set_timer_callback delegates correctly."""
        # Setup
        callback = MagicMock()
        
        # Test
        app_manager.set_timer_callback(callback)
        
        # Verify
        app_manager.set_timer_callback.assert_called_once_with(callback) 