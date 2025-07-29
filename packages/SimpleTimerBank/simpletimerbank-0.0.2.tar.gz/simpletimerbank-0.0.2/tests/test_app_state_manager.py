"""Unit tests for the AppStateManager class.

This module contains tests for the AppStateManager, which integrates
the core application state with the GUI layer.
"""

import pytest
from unittest.mock import MagicMock, patch

from simpletimerbank.core.app_state import AppStateManager
from simpletimerbank.core.time_bank import TimeBank
from simpletimerbank.core.countdown_timer import CountdownTimer, TimerState


class TestAppStateManager:
    """Test cases for the AppStateManager class."""
    
    def test_init(self):
        """Test initialization of AppStateManager."""
        manager = AppStateManager()
        # Verify core components are initialized
        assert manager._app_state is not None
        
    @patch('simpletimerbank.core.app_state.AppState')
    def test_initialize(self, mock_app_state):
        """Test that initialize calls AppState.initialize."""
        # Setup
        mock_instance = mock_app_state.return_value
        
        # Execute
        manager = AppStateManager()
        manager.initialize()
        
        # Verify
        mock_instance.initialize.assert_called_once()
    
    @patch('simpletimerbank.core.app_state.AppState')
    def test_shutdown(self, mock_app_state):
        """Test that shutdown calls AppState.shutdown."""
        # Setup
        mock_instance = mock_app_state.return_value
        
        # Execute
        manager = AppStateManager()
        manager.shutdown()
        
        # Verify
        mock_instance.shutdown.assert_called_once()
    
    @patch('simpletimerbank.core.app_state.AppState')
    def test_set_balance(self, mock_app_state):
        """Test setting time balance."""
        # Setup
        mock_instance = mock_app_state.return_value
        mock_bank = MagicMock(spec=TimeBank)
        mock_instance.get_time_bank.return_value = mock_bank
        
        # Execute
        manager = AppStateManager()
        manager.set_balance(3600)  # 1 hour
        
        # Verify
        mock_bank.set_balance.assert_called_once_with(3600)
    
    @patch('simpletimerbank.core.app_state.AppState')
    def test_add_time(self, mock_app_state):
        """Test adding time to balance."""
        # Setup
        mock_instance = mock_app_state.return_value
        mock_bank = MagicMock(spec=TimeBank)
        mock_instance.get_time_bank.return_value = mock_bank
        
        # Execute
        manager = AppStateManager()
        manager.add_time(1800)  # 30 minutes
        
        # Verify
        mock_bank.deposit.assert_called_once_with(1800)
    
    @patch('simpletimerbank.core.app_state.AppState')
    def test_start_timer(self, mock_app_state):
        """Test starting the timer."""
        # Setup
        mock_instance = mock_app_state.return_value
        
        # Execute
        manager = AppStateManager()
        manager.start_timer(60) # Start with a 60-second duration
        
        # Verify
        mock_instance.start_session.assert_called_once_with(60)
    
    @patch('simpletimerbank.core.app_state.AppState')
    def test_pause_timer(self, mock_app_state):
        """Test pausing the timer."""
        # Setup
        mock_instance = mock_app_state.return_value
        
        # Execute
        manager = AppStateManager()
        manager.pause_timer()
        
        # Verify
        mock_instance.pause_session.assert_called_once()
    
    @patch('simpletimerbank.core.app_state.AppState')
    def test_stop_timer(self, mock_app_state):
        """Test stopping the timer."""
        # Setup
        mock_instance = mock_app_state.return_value
        
        # Execute
        manager = AppStateManager()
        manager.stop_timer()
        
        # Verify
        mock_instance.stop_session.assert_called_once()
    
    @patch('simpletimerbank.core.app_state.AppState')
    def test_get_timer_state(self, mock_app_state):
        """Test getting the timer state."""
        # Setup
        mock_instance = mock_app_state.return_value
        mock_timer = MagicMock(spec=CountdownTimer)
        mock_timer.get_state.return_value = TimerState.RUNNING
        mock_instance.get_countdown_timer.return_value = mock_timer
        
        # Execute
        manager = AppStateManager()
        state = manager.get_timer_state()
        
        # Verify
        assert state == TimerState.RUNNING
        mock_timer.get_state.assert_called_once()
    
    @patch('simpletimerbank.core.app_state.AppState')
    def test_get_balance_seconds(self, mock_app_state):
        """Test getting the balance in seconds."""
        # Setup
        mock_instance = mock_app_state.return_value
        mock_bank = MagicMock(spec=TimeBank)
        mock_bank.get_balance.return_value = 7200  # 2 hours
        mock_instance.get_time_bank.return_value = mock_bank
        
        # Execute
        manager = AppStateManager()
        balance = manager.get_balance_seconds()
        
        # Verify
        assert balance == 7200
        mock_bank.get_balance.assert_called_once()
    
    def test_get_balance_formatted(self):
        """Test getting the formatted balance."""
        # Setup
        manager = AppStateManager()
        
        # Mock the get_balance_seconds method
        manager.get_balance_seconds = MagicMock(return_value=3661)  # 1h 1m 1s
        
        # Execute
        formatted = manager.get_balance_formatted()
        
        # Verify
        assert formatted == "01:01:01"
    
    @patch('simpletimerbank.core.app_state.AppState')
    def test_set_timer_callback(self, mock_app_state):
        """Test setting timer tick callback."""
        # Setup
        mock_instance = mock_app_state.return_value
        callback = MagicMock()
        
        # Execute
        manager = AppStateManager()
        manager.set_timer_callback(callback)
        
        # Verify
        mock_instance.set_timer_tick_callback.assert_called_once_with(callback)

    @patch('simpletimerbank.core.app_state.AppState')
    def test_set_timer_completion_callback(self, mock_app_state):
        """Test setting the timer completion callback."""
        # Setup
        mock_instance = mock_app_state.return_value
        callback = MagicMock()
        
        # Execute
        manager = AppStateManager()
        manager.set_timer_completion_callback(callback)
        manager._app_state.set_timer_completion_callback.assert_called_once_with(callback)

    @patch('simpletimerbank.core.app_state.AppState')
    def test_is_overdrafting(self, mock_app_state):
        """Test checking the overdraft status."""
        manager = AppStateManager()
        mock_timer = manager._app_state.get_countdown_timer()

        # Case 1: Not overdrafting
        mock_timer.is_overdrafting.return_value = False
        assert not manager.is_overdrafting()
        mock_timer.is_overdrafting.assert_called_once()

        # Case 2: Is overdrafting
        mock_timer.is_overdrafting.return_value = True
        assert manager.is_overdrafting() 