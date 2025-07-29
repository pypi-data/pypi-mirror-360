"""Unit tests for AppState class.

This module contains comprehensive unit tests for the AppState class,
following the pytest protocol with pure unit testing and mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call

from simpletimerbank.core.app_state import AppState
from simpletimerbank.core.time_bank import TimeBank
from simpletimerbank.core.countdown_timer import CountdownTimer, TimerState
from simpletimerbank.core.persistence import PersistenceService


class TestAppState:
    """Test suite for AppState class."""
    
    def setup_method(self):
        """Mock dependencies for all tests in this class."""
        self.notification_patcher = patch('simpletimerbank.core.app_state.NotificationService')
        self.mock_notification_service = self.notification_patcher.start()

    def teardown_method(self):
        """Stop all patchers."""
        self.notification_patcher.stop()
    
    def test_init_creates_components(self) -> None:
        """Test AppState initializes and creates all components."""
        app_state = AppState()
        
        # Should have created all components
        assert isinstance(app_state.get_time_bank(), TimeBank)
        assert isinstance(app_state.get_countdown_timer(), CountdownTimer)
        assert isinstance(app_state.get_persistence_service(), PersistenceService)
    
    @patch('simpletimerbank.core.persistence.PersistenceService.load_data')
    def test_initialize_loads_existing_data(self, mock_load: Mock) -> None:
        """Test initialize loads existing data from persistence."""
        mock_load.return_value = {"balance": 600}
        
        app_state = AppState()
        app_state.initialize()
        
        # Time bank should be loaded
        assert app_state.get_time_bank().get_balance() == 600
        mock_load.assert_called_once()
    
    @patch('simpletimerbank.core.persistence.PersistenceService.load_data')
    def test_initialize_handles_missing_data(self, mock_load: Mock) -> None:
        """Test initialize handles missing data gracefully."""
        mock_load.return_value = {}
        
        app_state = AppState()
        app_state.initialize()
        
        # Should start with zero balance
        assert app_state.get_time_bank().get_balance() == 0
    
    @patch('simpletimerbank.core.persistence.PersistenceService.save_data')
    def test_shutdown_saves_current_state(self, mock_save: Mock) -> None:
        """Test shutdown saves current application state."""
        app_state = AppState()
        
        # Set some state
        app_state.get_time_bank().deposit(450)
        
        app_state.shutdown()
        
        # Should have saved the current balance
        mock_save.assert_called_once()
        saved_data = mock_save.call_args[0][0]
        assert saved_data["balance"] == 450
    
    def test_start_session_with_sufficient_balance(self) -> None:
        """Test starting a session with sufficient balance."""
        app_state = AppState()
        app_state.get_time_bank().deposit(300)
        
        # Start a session with 60 seconds
        result = app_state.start_session(60)
        
        assert result is True
        assert app_state.get_countdown_timer().get_state() == TimerState.RUNNING
        assert app_state.get_countdown_timer().get_remaining_seconds() == 60
        assert app_state.get_time_bank().get_balance() == 240  # 300 - 60
    
    def test_start_session_with_insufficient_balance(self) -> None:
        """Test starting a session with insufficient balance fails."""
        app_state = AppState()
        app_state.get_time_bank().deposit(30)
        
        # Try to start a session with 60 seconds
        result = app_state.start_session(60)
        
        assert result is False
        assert app_state.get_countdown_timer().get_state() == TimerState.IDLE
        assert app_state.get_time_bank().get_balance() == 30  # Unchanged
    
    def test_pause_session(self) -> None:
        """Test pausing a session."""
        app_state = AppState()
        app_state.get_time_bank().deposit(300)
        app_state.start_session(60)
        
        app_state.pause_session()
        
        assert app_state.get_countdown_timer().get_state() == TimerState.PAUSED
    
    def test_resume_session(self) -> None:
        """Test resuming a paused session."""
        app_state = AppState()
        app_state.get_time_bank().deposit(300)
        app_state.start_session(60)
        app_state.pause_session()
        
        app_state.resume_session()
        
        assert app_state.get_countdown_timer().get_state() == TimerState.RUNNING
    
    def test_stop_session_refunds_remaining_time(self) -> None:
        """Test stopping a session refunds remaining time to the bank."""
        app_state = AppState()
        app_state.get_time_bank().deposit(300)
        app_state.start_session(60)
        
        # Stop the session - should refund 60 seconds
        app_state.stop_session()
        
        assert app_state.get_countdown_timer().get_state() == TimerState.STOPPED
        assert app_state.get_time_bank().get_balance() == 300  # Fully refunded
    
    def test_stop_session_after_some_time_refunds_correctly(self) -> None:
        """Test stopping a session after some time correctly refunds remaining time."""
        app_state = AppState()
        app_state.get_time_bank().deposit(300)
        app_state.start_session(60)
        
        # Simulate time passing (20 seconds)
        timer = app_state.get_countdown_timer()
        for _ in range(20):
            timer.tick()
        
        # Now 40 seconds should remain
        assert timer.get_remaining_seconds() == 40
        
        # Stop the session - should refund 40 seconds
        app_state.stop_session()
        
        assert timer.get_state() == TimerState.STOPPED
        assert app_state.get_time_bank().get_balance() == 280  # 300 - 60 + 40
    
    def test_tick_timer_in_overdraft_withdraws_from_bank(self) -> None:
        """Test ticking timer in overdraft mode withdraws from bank."""
        app_state = AppState()
        app_state.get_time_bank().deposit(300)
        app_state.start_session(2)
        
        timer = app_state.get_countdown_timer()
        
        # Tick twice to reach zero and enter overdraft
        timer.tick()
        timer.tick()
        assert timer.is_overdrafting()
        
        # Now tick once in overdraft mode - should withdraw 1 second
        app_state.tick_timer()
        
        assert app_state.get_time_bank().get_balance() == 297  # 300 - 2 - 1
    
    def test_tick_timer_stops_when_bank_depleted(self) -> None:
        """Test ticking timer stops and notifies when bank balance is depleted."""
        app_state = AppState()
        mock_notification_service = app_state.get_notification_service()
        app_state.get_time_bank().deposit(2)
        app_state.start_session(1)
        
        timer = app_state.get_countdown_timer()
        
        # Tick once to reach zero and enter overdraft
        timer.tick()
        assert timer.is_overdrafting()
        
        # Bank has 1 second left
        assert app_state.get_time_bank().get_balance() == 1
        
        # Tick once in overdraft - should withdraw last second
        app_state.tick_timer()
        assert app_state.get_time_bank().get_balance() == 0
        
        # Tick again - should stop timer since bank is depleted
        app_state.tick_timer()
        assert timer.get_state() == TimerState.STOPPED
        
        # Verify notification was sent
        mock_notification_service.notify_bank_depleted.assert_called_once()
    
    def test_timer_completion_triggers_callback_and_notification(self) -> None:
        """Test timer completion triggers user callback and notification."""
        callback_mock = Mock()
        
        app_state = AppState()
        mock_notification_service = app_state.get_notification_service()
        app_state.set_timer_completion_callback(callback_mock)
        app_state.get_time_bank().deposit(300)
        app_state.start_session(1)
        
        # This will call AppState._on_timer_completion via callback
        app_state.get_countdown_timer().tick()
        
        callback_mock.assert_called_once()
        mock_notification_service.notify_timer_completed.assert_called_once()
    
    def test_handle_overdraft_signal(self) -> None:
        """Test the internal _handle_overdraft_signal method."""
        app_state = AppState()
        app_state.get_time_bank().deposit(10)
        
        # Call the method directly
        app_state._handle_overdraft_signal(5)
        
        assert app_state.get_time_bank().get_balance() == 5  # 10 - 5
    
    def test_handle_overdraft_signal_stops_timer_if_insufficient(self) -> None:
        """Test _handle_overdraft_signal stops timer if balance insufficient."""
        app_state = AppState()
        app_state.get_time_bank().deposit(3)
        app_state.start_session(1)
        
        timer = app_state.get_countdown_timer()
        timer.tick()  # Enter overdraft
        
        # Try to withdraw 5 seconds, but only 2 seconds remain
        app_state._handle_overdraft_signal(5)
        
        assert app_state.get_time_bank().get_balance() == 0  # Drained
        assert timer.get_state() == TimerState.STOPPED  # Should be stopped
    
    @patch.object(CountdownTimer, 'tick')
    def test_tick_timer_calls_countdown_timer_tick(self, mock_tick: Mock) -> None:
        """Test tick_timer calls the countdown timer's tick method."""
        mock_tick.return_value = None  # No overdraft
        
        app_state = AppState()
        app_state.tick_timer()
        
        mock_tick.assert_called_once()
    
    @patch.object(CountdownTimer, 'tick')
    def test_tick_timer_handles_overdraft_signal(self, mock_tick: Mock) -> None:
        """Test tick_timer properly handles overdraft signal from countdown timer."""
        mock_tick.return_value = 1  # 1 second overdraft
        
        app_state = AppState()
        app_state.get_time_bank().deposit(10)
        app_state.tick_timer()
        
        mock_tick.assert_called_once()
        assert app_state.get_time_bank().get_balance() == 9  # 10 - 1
    
    def test_multiple_sessions(self) -> None:
        """Test running multiple consecutive sessions."""
        app_state = AppState()
        app_state.get_time_bank().deposit(100)
        
        # First session
        app_state.start_session(20)
        app_state.stop_session()  # Immediate stop should refund all time
        
        # Second session
        app_state.start_session(30)
        
        # Simulate 10 seconds passing
        timer = app_state.get_countdown_timer()
        for _ in range(10):
            timer.tick()
        
        app_state.stop_session()  # Stop with 20 seconds left
        
        assert app_state.get_time_bank().get_balance() == 90  # 100 - 30 + 20
    
    def test_comprehensive_session_lifecycle(self) -> None:
        """Test a comprehensive session lifecycle including all state transitions."""
        completion_callback = Mock()
        tick_callback = Mock()
        
        app_state = AppState()
        app_state.set_timer_completion_callback(completion_callback)
        app_state.set_timer_tick_callback(tick_callback)
        app_state.get_time_bank().deposit(100)
        
        # Start a session with 3 seconds
        app_state.start_session(3)
        assert app_state.get_time_bank().get_balance() == 97
        
        # First tick
        app_state.tick_timer()
        tick_callback.assert_called_with(2)  # 2 seconds left
        completion_callback.assert_not_called()
        
        # Pause
        app_state.pause_session()
        assert app_state.get_countdown_timer().get_state() == TimerState.PAUSED
        
        # Resume
        app_state.resume_session()
        assert app_state.get_countdown_timer().get_state() == TimerState.RUNNING
        
        # Second tick
        tick_callback.reset_mock()
        app_state.tick_timer()
        tick_callback.assert_called_with(1)  # 1 second left
        
        # Third tick - enters overdraft
        tick_callback.reset_mock()
        app_state.tick_timer()
        tick_callback.assert_called_with(0)  # 0 seconds left
        completion_callback.assert_called_once()
        
        # Tick in overdraft - should withdraw from bank
        tick_callback.reset_mock()
        completion_callback.reset_mock()
        app_state.tick_timer()
        tick_callback.assert_called_with(0)  # Still 0 in display
        completion_callback.assert_not_called()  # Called only once
        assert app_state.get_time_bank().get_balance() == 96  # 97 - 1
        
        # Stop and verify state
        app_state.stop_session()
        assert app_state.get_countdown_timer().get_state() == TimerState.STOPPED
        assert app_state.get_time_bank().get_balance() == 96  # No refund in overdraft 