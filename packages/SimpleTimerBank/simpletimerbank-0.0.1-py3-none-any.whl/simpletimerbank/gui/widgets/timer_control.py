"""Timer control widget for SimpleTimerBank.

This module provides a dedicated widget containing the primary controls for
managing a timer session: Start, Pause, and Stop.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QGroupBox, QVBoxLayout, QLabel, QSizePolicy

from simpletimerbank.core.countdown_timer import TimerState


class TimerControlWidget(QWidget):
    """A widget for controlling the main countdown timer.
    
    This widget groups the 'Start Timer', 'Pause Timer', and 'Stop Timer & Refund'
    buttons. It emits signals when these buttons are clicked and dynamically
    updates their enabled states and labels based on the current timer state
    (e.g., changing 'Start' to 'Resume').
    """
    
    # Signals
    start_requested = Signal()
    """Signal emitted when the start/resume button is clicked."""
    pause_requested = Signal()
    """Signal emitted when the pause button is clicked."""
    stop_requested = Signal()
    """Signal emitted when the stop button is clicked."""
    
    def __init__(self, parent: QWidget = None) -> None:
        """Initialize the TimerControlWidget and its buttons.
        
        Parameters
        ----------
        parent : QWidget, optional
            The parent widget of this component. Defaults to None.
        """
        super().__init__(parent)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Group box for controls
        group_box = QGroupBox("Timer Controls", self)
        button_layout = QHBoxLayout(group_box)
        
        # Create buttons
        self._start_button = QPushButton("Start Timer", self)
        self._pause_button = QPushButton("Pause Timer", self)
        self._stop_button = QPushButton("Stop Timer", self)
        
        # Set size policy to make buttons expand
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._start_button.setSizePolicy(size_policy)
        self._pause_button.setSizePolicy(size_policy)
        self._stop_button.setSizePolicy(size_policy)
        
        button_layout.addWidget(self._start_button)
        button_layout.addWidget(self._pause_button)
        button_layout.addWidget(self._stop_button)
        
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)
        
        # Connect signals
        self._start_button.clicked.connect(self.start_requested)
        self._pause_button.clicked.connect(self.pause_requested)
        self._stop_button.clicked.connect(self.stop_requested)
        
        # Set initial button state
        self.update_button_states(TimerState.IDLE)
    
    def update_button_states(self, state: TimerState) -> None:
        """Update button enabled states and labels based on the timer's state.
        
        This method ensures that only valid actions are available to the user.
        For example, 'Pause' is only enabled when the timer is running, and
        the 'Start' button text changes to 'Resume' when the timer is paused.
        
        Parameters
        ----------
        state : TimerState
            The current state of the countdown timer.
        """
        if state == TimerState.IDLE:
            self._start_button.setEnabled(True)
            self._start_button.setText("Start Timer")
            self._pause_button.setEnabled(False)
            self._stop_button.setEnabled(False)
        elif state == TimerState.RUNNING:
            self._start_button.setEnabled(False)
            self._pause_button.setEnabled(True)
            self._stop_button.setEnabled(True)
        elif state == TimerState.PAUSED:
            self._start_button.setEnabled(True)
            self._start_button.setText("Resume Timer")
            self._pause_button.setEnabled(False)
            self._stop_button.setEnabled(True)
        elif state == TimerState.STOPPED:
            self._start_button.setEnabled(True)
            self._start_button.setText("Start Timer")
            self._pause_button.setEnabled(False)
            self._stop_button.setEnabled(False) 