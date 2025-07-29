"""Countdown timer management module.

This module contains the CountdownTimer class, which encapsulates the logic
for a countdown timer that supports starting, pausing, resuming, and stopping.
It includes a key feature for "overdraft" mode.
"""

from enum import Enum
from typing import Callable, Optional, Union


class TimerState(Enum):
    """Enumeration of possible timer states."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class CountdownTimer:
    """Manages all operations for a countdown timer session.
    
    This class handles the core timer mechanics, including state transitions
    (IDLE, RUNNING, PAUSED, STOPPED). Its main responsibility is to manage the
    countdown of a specified duration. When the countdown reaches zero, it
    seamlessly transitions into "overdraft" mode, where it continues to tick
    and signals that time should be withdrawn from an external source (like a
    TimeBank). It also manages callbacks for ticks and completion events.
    """
    
    def __init__(self) -> None:
        """Initialize CountdownTimer in an IDLE state."""
        self._state: TimerState = TimerState.IDLE
        self._remaining_seconds: int = 0
        self._initial_duration: int = 0
        self._is_overdrafting: bool = False
        self._tick_callback: Optional[Callable[[int], None]] = None
        self._completion_callback: Optional[Callable[[], None]] = None
    
    def start(self, duration: int) -> None:
        """Start a new countdown timer session with a specified duration.
        
        This resets the timer to the given duration and puts it in the RUNNING
        state. It also resets the overdraft flag.
        
        Parameters
        ----------
        duration : int
            The duration in seconds for the new timer session.
            
        Raises
        ------
        ValueError
            If the duration is not a positive integer or if the timer is
            already running.
        """
        if duration <= 0:
            raise ValueError("Duration must be positive")
            
        if self._state == TimerState.RUNNING:
            raise ValueError("Timer is already running")
        
        self._initial_duration = duration
        self._remaining_seconds = duration
        self._is_overdrafting = False
        self._state = TimerState.RUNNING
    
    def pause(self) -> None:
        """Pause the currently running countdown timer.
        
        The timer's remaining time is preserved. Does nothing if the timer
        is not currently running.

        Raises
        ------
        ValueError
            If the timer is not in the RUNNING state.
        """
        if self._state != TimerState.RUNNING:
            if self._state == TimerState.PAUSED:
                raise ValueError("Timer is already paused")
            else:
                raise ValueError("Timer is not running")
        
        self._state = TimerState.PAUSED
    
    def resume(self) -> None:
        """Resume a timer that was previously paused.
        
        Sets the timer's state back to RUNNING. Does nothing if the timer
        is not paused.
        
        Raises
        ------
        ValueError
            If the timer is not in the PAUSED state.
        """
        if self._state != TimerState.PAUSED:
            raise ValueError("Timer is not paused")
        
        self._state = TimerState.RUNNING
    
    def stop(self) -> None:
        """Stop the timer session completely.
        
        This moves the timer to the STOPPED state. If the timer is stopped
        before its duration is complete (i.e., not in overdraft), the
        remaining seconds are preserved to allow for a refund. If stopped
        during overdraft, the remaining time is set to zero.
        
        Raises
        ------
        ValueError
            If the timer is already stopped or has never been started.
        """
        if self._state == TimerState.IDLE:
            raise ValueError("Timer has not been started")
            
        if self._state == TimerState.STOPPED:
            raise ValueError("Timer is already stopped")
        
        self._state = TimerState.STOPPED
        
        # If in overdraft, set remaining seconds to 0 (no refund)
        if self._is_overdrafting:
            self._remaining_seconds = 0
            self._is_overdrafting = False
    
    def tick(self) -> Optional[int]:
        """Process a single one-second tick of the timer.
        
        This is the core method that drives the countdown. It should be called
        once per second. It decrements the remaining time. If the timer reaches
        zero, it enables overdraft mode and fires the completion callback.
        On subsequent ticks in overdraft mode, it returns a value to indicate
        that one second should be withdrawn from the bank.
        
        Returns
        -------
        Optional[int]
            Returns 1 if a second of overdraft occurred, otherwise returns None.
        """
        if self._state != TimerState.RUNNING:
            return None
        
        # If already in overdraft mode, signal to withdraw 1 second
        if self._is_overdrafting:
            if self._tick_callback:
                self._tick_callback(0)
            return 1
            
        # Normal countdown mode - decrement time
        if self._remaining_seconds > 0:
            self._remaining_seconds -= 1
            
            # Call tick callback with new remaining time
            if self._tick_callback:
                self._tick_callback(self._remaining_seconds)
            
            # Check if we've just reached zero
            if self._remaining_seconds == 0:
                self._is_overdrafting = True
                # Notify that the initial countdown is complete
                if self._completion_callback:
                    self._completion_callback()
            
            return None
            
        return None
    
    def get_state(self) -> TimerState:
        """Get the current state of the timer.
        
        Returns
        -------
        TimerState
            The current state, e.g., IDLE, RUNNING, PAUSED, or STOPPED.
        """
        return self._state
    
    def get_remaining_seconds(self) -> int:
        """Get the remaining seconds on the timer's initial duration.
        
        This value decrements during a normal countdown. In overdraft mode,
        it will be 0.
        
        Returns
        -------
        int
            The number of seconds remaining in the countdown.
        """
        return self._remaining_seconds
    
    def is_overdrafting(self) -> bool:
        """Check if the timer is currently in overdraft mode.
        
        Returns
        -------
        bool
            True if the timer's initial duration has elapsed and it is now
            counting up in overdraft; False otherwise.
        """
        return self._is_overdrafting
    
    def set_tick_callback(self, callback: Callable[[int], None]) -> None:
        """Register a callback to be executed on each tick while running.
        
        Parameters
        ----------
        callback : Callable[[int], None]
            A function to call with the remaining seconds on each tick.
        """
        self._tick_callback = callback
    
    def set_completion_callback(self, callback: Callable[[], None]) -> None:
        """Register a callback to be executed when the timer first hits zero.
        
        This callback is fired once at the exact moment the timer transitions
        from its normal countdown to overdraft mode.
        
        Parameters
        ----------
        callback : Callable[[], None]
            A function to call when the timer's duration is complete.
        """
        self._completion_callback = callback 