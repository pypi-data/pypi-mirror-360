"""Time edit widget for SimpleTimerBank.

This module provides a widget for users to input and adjust a time
duration, which can then be used to start a timer session.
"""

from PySide6.QtCore import Signal, Qt, QTime
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTimeEdit,
    QLabel,
    QFrame,
)


class TimeEditWidget(QWidget):
    """A widget for inputting and adjusting a time duration for a session.
    
    This widget provides controls to set, add, or subtract time from a
    session duration field. The final duration can then be used to start
    a timer. It emits signals when the user requests these actions.
    """
    
    add_time_requested = Signal(int)
    subtract_time_requested = Signal(int)
    set_time_requested = Signal(int)

    def __init__(self, parent: QWidget = None) -> None:
        """Initialize the TimeEditWidget.
        
        Parameters
        ----------
        parent : QWidget, optional
            The parent widget, by default None.
        """
        super().__init__(parent)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Header for the section
        header_label = QLabel("Transaction Management", self)
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(header_label)
        
        # Add a separator line
        separator = QFrame(self)
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        # Time input field with label
        time_input_layout = QVBoxLayout()
        time_input_label = QLabel("Time Amount:", self)
        time_input_label.setStyleSheet("margin-bottom: 2px;")
        time_input_layout.addWidget(time_input_label)
        
        self._time_edit = QTimeEdit(self)
        self._time_edit.setDisplayFormat("HH:mm:ss")
        self._time_edit.setTime(QTime(0, 30, 0))  # Default to 30 minutes
        time_input_layout.addWidget(self._time_edit)
        main_layout.addLayout(time_input_layout)

        # Button layout
        button_layout = QHBoxLayout()
        self._set_button = QPushButton("Set Bank Balance", self)
        self._add_button = QPushButton("Deposit to Bank", self)
        self._subtract_button = QPushButton("Withdraw from Bank", self)
        
        button_layout.addWidget(self._set_button)
        button_layout.addWidget(self._add_button)
        button_layout.addWidget(self._subtract_button)
        main_layout.addLayout(button_layout)
        
        # Connect signals
        self._set_button.clicked.connect(self._on_set_time)
        self._add_button.clicked.connect(self._on_add_time)
        self._subtract_button.clicked.connect(self._on_subtract_time)
        
        # Internal state for duration
        self._session_duration_seconds = 30 * 60

    def _on_set_time(self) -> None:
        """Handle the set time button click."""
        time = self._time_edit.time()
        seconds = time.hour() * 3600 + time.minute() * 60 + time.second()
        self._session_duration_seconds = seconds
        self.set_time_requested.emit(seconds)

    def _on_add_time(self) -> None:
        """Handle the add time button click."""
        time = self._time_edit.time()
        seconds = time.hour() * 3600 + time.minute() * 60 + time.second()
        self.add_time_requested.emit(seconds)

    def _on_subtract_time(self) -> None:
        """Handle the subtract time button click."""
        time = self._time_edit.time()
        seconds = time.hour() * 3600 + time.minute() * 60 + time.second()
        self.subtract_time_requested.emit(seconds)
        
    def get_duration_seconds(self) -> int:
        """Get the currently configured session duration in seconds.
        
        Returns
        -------
        int
            The duration in seconds.
        """
        time = self._time_edit.time()
        return time.hour() * 3600 + time.minute() * 60 + time.second() 