"""Main window for the SimpleTimerBank application.

This module provides the main application window, which assembles all
the GUI components and connects them to the core business logic.
"""

from PySide6.QtCore import QTimer, Qt, QTime
from PySide6.QtGui import QCloseEvent, QFontDatabase, QColor, QPalette, QFont
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QLabel,
    QStatusBar,
    QFrame,
    QHBoxLayout,
    QGroupBox,
    QPushButton,
    QTimeEdit,
    QSizePolicy,
)
import os

from simpletimerbank.core.app_state import AppStateManager
from simpletimerbank.core.countdown_timer import TimerState
from simpletimerbank.gui.widgets.time_display import TimeDisplayWidget
from simpletimerbank.gui.widgets.timer_control import TimerControlWidget


class MainWindow(QMainWindow):
    """The main application window for SimpleTimerBank.
    
    This class sets up the main window, lays out all the custom widgets,
    and handles the integration between the GUI and the AppStateManager.
    """
    
    def __init__(self, app_manager: AppStateManager, parent: QWidget = None) -> None:
        """Initialize the MainWindow.
        
        Parameters
        ----------
        app_manager : AppStateManager
            The application state manager instance.
        parent : QWidget, optional
            The parent widget, by default None.
        """
        super().__init__(parent)
        self._app_manager = app_manager
        
        # Window configuration
        self.setWindowTitle("Time Bank - Manage Your Time Assets")
        self.setFixedSize(500, 700)
        
        # Load custom font
        font_family = self._load_custom_font()
        
        # Create central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # --- Bank Balance Section ---
        balance_section = QVBoxLayout()
        
        # Bank balance header with explanation
        bank_header_layout = QVBoxLayout()
        bank_header = QLabel("Your Time Bank Balance", self)
        bank_header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 5px;")
        
        bank_header_layout.addWidget(bank_header)
        balance_section.addLayout(bank_header_layout)
        
        self._time_display = TimeDisplayWidget(self, font_family=font_family)
        balance_section.addWidget(self._time_display)
        main_layout.addLayout(balance_section)
        
        # Add separator
        separator = QFrame(self)
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        # --- Timer Countdown Section ---
        withdrawal_section = QVBoxLayout()
        
        timer_header = QLabel("Active Timer", self)
        timer_header.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 15px; margin-bottom: 5px;")
        withdrawal_section.addWidget(timer_header)
        
        self._timer_countdown_label = QLabel("00:00:00", self)
        timer_font = QFont(font_family, 36, QFont.Weight.Bold)  # Use same font as bank balance
        self._timer_countdown_label.setFont(timer_font)
        self._timer_countdown_label.setStyleSheet("""
            color: #4CAF50;
            background-color: #1E1E1E;
            border: 2px solid #4A4A4A;
            border-radius: 10px;
            padding: 10px;
        """)
        self._timer_countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        withdrawal_section.addWidget(self._timer_countdown_label)
        
        # Overdraft indicator
        self._overdraft_indicator = QLabel("", self)
        self._overdraft_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._overdraft_indicator.setStyleSheet("font-weight: bold; color: #FF4500; font-size: 12px;")
        self._overdraft_indicator.setVisible(False)
        withdrawal_section.addWidget(self._overdraft_indicator)
        
        main_layout.addLayout(withdrawal_section)

        # --- Transaction Controls ---
        transaction_group = QGroupBox("Manage Bank Balance")
        transaction_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #999;
                border-radius: 5px;
                margin-top: 10px;
                background-color: #f0f0f0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 8px 12px;
            }
        """)
        transaction_group_layout = QVBoxLayout()

        # Amount entry
        amount_layout = QHBoxLayout()
        amount_label = QLabel("Amount:")
        self._amount_edit = QTimeEdit(self)
        self._amount_edit.setDisplayFormat("HH:mm:ss")
        self._amount_edit.setTime(QTime(0, 0, 0))
        self._amount_edit.setStyleSheet("font-size: 14px; font-weight: bold;")
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self._amount_edit)
        transaction_group_layout.addLayout(amount_layout)

        # Convenience buttons
        convenience_layout_add = QHBoxLayout()
        add_presets = {"+15m": 15 * 60, "+30m": 30 * 60, "+1h": 60 * 60}
        for text, seconds in add_presets.items():
            btn = QPushButton(text, self)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            btn.clicked.connect(lambda checked=False, secs=seconds: self._adjust_amount(secs))
            convenience_layout_add.addWidget(btn)
        transaction_group_layout.addLayout(convenience_layout_add)

        convenience_layout_sub = QHBoxLayout()
        sub_presets = {"-15m": -15 * 60, "-30m": -30 * 60, "-1h": -60 * 60}
        for text, seconds in sub_presets.items():
            btn = QPushButton(text, self)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            btn.clicked.connect(lambda checked=False, secs=seconds: self._adjust_amount(secs))
            convenience_layout_sub.addWidget(btn)
        transaction_group_layout.addLayout(convenience_layout_sub)

        # Direct operations
        direct_ops_layout = QHBoxLayout()
        self._deposit_button = QPushButton("Deposit", self)
        self._withdraw_button = QPushButton("Instant Withdraw", self)
        self._set_balance_button = QPushButton("Set Balance", self)

        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._deposit_button.setSizePolicy(size_policy)
        self._withdraw_button.setSizePolicy(size_policy)
        self._set_balance_button.setSizePolicy(size_policy)

        direct_ops_layout.addWidget(self._deposit_button)
        direct_ops_layout.addWidget(self._withdraw_button)
        direct_ops_layout.addWidget(self._set_balance_button)
        transaction_group_layout.addLayout(direct_ops_layout)
        
        transaction_group.setLayout(transaction_group_layout)
        main_layout.addWidget(transaction_group)
        
        # --- Timed Withdrawal Controls ---
        self._timer_control = TimerControlWidget(self)
        self._timer_control.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #88c;
                border-radius: 5px;
                margin-top: 10px;
                background-color: #e8e8ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 8px 12px;
            }
        """)
        main_layout.addWidget(self._timer_control)
        
        # Add status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready. Set an amount and use the controls.")
        
        # State tracking
        self._is_overdrafting = False
        
        # Setup timer for regular ticks
        self._setup_timer()
        
        # Connect signals and slots
        self._connect_signals()
        
        # Set initial state from AppManager
        self._update_ui_from_manager()

    def _load_custom_font(self) -> str:
        """Load custom font and return its family name."""
        font_family = "Courier New"
        font_paths = [
            "assets/fonts/DSEG7-Classic-Bold.ttf",
            os.path.join(os.path.dirname(__file__), "../../../assets/fonts/DSEG7-Classic-Bold.ttf"),
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        return families[0]
        return font_family
    
    def _setup_timer(self) -> None:
        """Set up the Qt timer for regular timer ticks."""
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._handle_timer_tick)
        self._app_manager.set_qt_timer(self._timer)
    
    def _connect_signals(self) -> None:
        """Connect widget signals to the appropriate handler methods.
        
        This method is central to the application's interactivity, wiring up
        user actions (like button clicks) to the functions that execute the
        corresponding logic, such as depositing time or starting a timer.
        """
        # Bank operations
        self._deposit_button.clicked.connect(self._handle_deposit)
        self._withdraw_button.clicked.connect(self._handle_direct_withdraw)
        self._set_balance_button.clicked.connect(self._handle_set_balance)

        # Timer control signals
        self._timer_control.start_requested.connect(self._handle_start_timer)
        self._timer_control.pause_requested.connect(self._handle_pause_timer)
        self._timer_control.stop_requested.connect(self._handle_stop_timer)
        
        # App manager callbacks
        self._app_manager.set_timer_callback(self._on_timer_tick)
        self._app_manager.set_timer_completion_callback(self._on_timer_completion)
    
    def _update_ui_from_manager(self) -> None:
        """Update the entire UI based on the current state from the AppManager.
        
        This method is called whenever a state change occurs (e.g., after a
        transaction or during a timer tick) to ensure the GUI is a consistent
        reflection of the application's data. It updates the balance display,
        the timer countdown, button states, and status messages.
        """
        # Update bank balance display
        balance_formatted = self._app_manager.get_balance_formatted()
        self._time_display.update_time(balance_formatted)
        
        # Update timer countdown display
        timer_state = self._app_manager.get_timer_state()
        if timer_state in (TimerState.RUNNING, TimerState.PAUSED):
            # Get remaining seconds using the appropriate method
            remaining_seconds = self._app_manager._app_state.get_countdown_timer().get_remaining_seconds()
            self._timer_countdown_label.setText(self._format_time(remaining_seconds))
            
            # Update overdraft state
            self._is_overdrafting = self._app_manager.is_overdrafting()
            self._overdraft_indicator.setVisible(self._is_overdrafting)
            if self._is_overdrafting:
                self._overdraft_indicator.setText("OVERDRAFT ACTIVE - TIME IS BEING WITHDRAWN FROM YOUR BANK")
            else:
                self._overdraft_indicator.setText("")
        else:
            self._timer_countdown_label.setText("00:00:00")
            self._is_overdrafting = False
            self._overdraft_indicator.setVisible(False)
            
        # Update button and status states
        self._timer_control.update_button_states(timer_state)
        self._update_status_message(timer_state)

    def _update_status_message(self, state: TimerState) -> None:
        """Update the status bar message based on the current timer state.
        
        This provides contextual feedback to the user at the bottom of the
        window, guiding them on what to do next or confirming an action.
        
        Parameters
        ----------
        state : TimerState
            The current state of the countdown timer, used to determine the
            appropriate message to display.
        """
        if state == TimerState.IDLE:
            self.statusBar.showMessage("Ready. Set an amount and start a timer or transaction.")
            self._timer_countdown_label.setStyleSheet("""
                color: #4CAF50;
                background-color: #1E1E1E;
                border: 2px solid #4A4A4A;
                border-radius: 10px;
                padding: 10px;
            """)
        elif state == TimerState.RUNNING:
            if self._is_overdrafting:
                self.statusBar.showMessage("Overdraft Mode: Time is being withdrawn from your bank balance.")
                self._timer_countdown_label.setStyleSheet("""
                    color: #FFFFFF;
                    background-color: #8B0000;
                    border: 2px solid #FF4500;
                    border-radius: 10px;
                    padding: 10px;
                """)
            else:
                self.statusBar.showMessage("Timer running...")
                self._timer_countdown_label.setStyleSheet("""
                    color: #4CAF50;
                    background-color: #1E1E1E;
                    border: 2px solid #4A4A4A;
                    border-radius: 10px;
                    padding: 10px;
                """)
        elif state == TimerState.PAUSED:
            self.statusBar.showMessage("Timer paused.")
            self._timer_countdown_label.setStyleSheet("""
                color: #FFA500;
                background-color: #1E1E1E;
                border: 2px solid #4A4A4A;
                border-radius: 10px;
                padding: 10px;
            """)
        elif state == TimerState.STOPPED:
            self.statusBar.showMessage("Timer stopped. Unused time has been returned to your bank.")
            self._is_overdrafting = False
            self._timer_countdown_label.setStyleSheet("""
                color: #4CAF50;
                background-color: #1E1E1E;
                border: 2px solid #4A4A4A;
                border-radius: 10px;
                padding: 10px;
            """)

    def _get_amount_seconds(self) -> int:
        """Get the current time value from the amount input field.
        
        Returns
        -------
        int
            The number of seconds specified in the 'Amount' QTimeEdit widget.
        """
        time = self._amount_edit.time()
        return time.hour() * 3600 + time.minute() * 60 + time.second()

    def _adjust_amount(self, seconds_delta: int) -> None:
        """Adjust the amount in the QTimeEdit by a relative number of seconds.
        
        This method is connected to the preset +/- buttons (e.g., '+15m')
        and handles the logic of adding or subtracting time from the amount
        field, ensuring the value stays within a valid 24-hour range.

        Parameters
        ----------
        seconds_delta : int
            The number of seconds to add or subtract. Can be positive or
            negative.
        """
        current_time = self._amount_edit.time()
        current_seconds = (current_time.hour() * 3600 +
                           current_time.minute() * 60 +
                           current_time.second())
        
        new_total_seconds = current_seconds + seconds_delta
        
        # Clamp the value between 0 and 23:59:59
        if new_total_seconds < 0:
            new_total_seconds = 0
        
        max_seconds = (23 * 3600) + (59 * 60) + 59
        if new_total_seconds > max_seconds:
            new_total_seconds = max_seconds
            self.statusBar.showMessage("Amount cannot exceed 23:59:59.", 3000)
            
        h, rem = divmod(new_total_seconds, 3600)
        m, s = divmod(rem, 60)
        self._amount_edit.setTime(QTime(h, m, s))

    def _handle_deposit(self) -> None:
        """Handle a deposit action from the user.
        
        Reads the amount from the input field and adds it to the time bank.
        """
        seconds = self._get_amount_seconds()
        if seconds <= 0:
            QMessageBox.warning(self, "Invalid Amount", "Please set a deposit amount greater than zero.")
            return
        self._app_manager.add_time(seconds)
        self.statusBar.showMessage(f"Deposited {self._format_time(seconds)} to your bank balance.", 3000)
        self._update_ui_from_manager()

    def _handle_direct_withdraw(self) -> None:
        """Handle an instant withdrawal from the time bank.
        
        Reads the amount from the input field and immediately subtracts it
        from the bank balance, if sufficient funds are available.
        """
        seconds = self._get_amount_seconds()
        if seconds <= 0:
            QMessageBox.warning(self, "Invalid Amount", "Please set a withdrawal amount greater than zero.")
            return
        try:
            self._app_manager.get_time_bank().withdraw(seconds)
            self.statusBar.showMessage(f"Instantly withdrew {self._format_time(seconds)} from your bank balance.", 3000)
        except ValueError as e:
            QMessageBox.warning(self, "Insufficient Balance", str(e))
        self._update_ui_from_manager()
    
    def _handle_set_balance(self) -> None:
        """Handle a request to set the bank balance to a specific value.
        
        Reads the amount from the input field and sets the bank balance
        directly to that value.
        """
        seconds = self._get_amount_seconds()
        try:
            self._app_manager.set_balance(seconds)
            self.statusBar.showMessage(f"Set bank balance to {self._format_time(seconds)}", 3000)
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Time", str(e))
        self._update_ui_from_manager()
        
    def _handle_start_timer(self) -> None:
        """Handle the user's request to start or resume the countdown timer.
        
        If the timer is paused, it resumes. Otherwise, it starts a new
        timer session with the duration specified in the amount field.
        """
        timer_state = self._app_manager.get_timer_state()

        if timer_state == TimerState.PAUSED:
            self._app_manager.resume_timer()
            self.statusBar.showMessage("Timer resumed.", 3000)
        else:
            duration = self._get_amount_seconds()
            if duration <= 0:
                QMessageBox.warning(self, "Invalid Duration", "Please set a timer duration greater than zero.")
                return
            
            if not self._app_manager.start_timer(duration):
                QMessageBox.warning(self, "Insufficient Balance", "Not enough time in your bank for this timer.")
                return
            
            self.statusBar.showMessage(f"Timer started for {self._format_time(duration)}.", 3000)
        
        self._timer.start()
        self._update_ui_from_manager()
    
    def _handle_pause_timer(self) -> None:
        """Handle the user's request to pause the running timer."""
        self._app_manager.pause_timer()
        self.statusBar.showMessage("Timer paused.", 3000)
        self._update_ui_from_manager()
    
    def _handle_stop_timer(self) -> None:
        """Handle the user's request to stop the timer.
        
        This action stops the timer and refunds any unused time back to the
        bank balance.
        """
        self._app_manager.stop_timer()
        self._is_overdrafting = False
        self.statusBar.showMessage("Timer stopped. Unused time refunded to your balance.", 3000)
        self._timer.stop()
        self._update_ui_from_manager()
    
    def _handle_timer_tick(self) -> None:
        """Process a single tick of the main application timer (QTimer).
        
        This method is connected to the QTimer's timeout signal and is
        called every second. It drives the countdown logic in the core
        application state and triggers a UI update.
        """
        if self._app_manager.get_timer_state() == TimerState.RUNNING:
            # Direct access to app_state.tick_timer() is not ideal but works for now
            self._app_manager._app_state.tick_timer()
            self._update_ui_from_manager()
    
    def _on_timer_tick(self, remaining_seconds: int) -> None:
        """Callback executed by the core logic on each second of the countdown.
        
        This method is registered with the AppStateManager and is called
        by the core application logic to signal that the UI should be updated.

        Parameters
        ----------
        remaining_seconds : int
            The number of seconds left on the timer.
        """
        # This callback now drives the UI update
        self._update_ui_from_manager()
        
    def _on_timer_completion(self) -> None:
        """Handle the timer completion event from the core logic.
        
        This is called when the timer's initial duration runs out and
        overdraft mode begins. It triggers a system notification.
        """
        self.statusBar.showMessage("Timer complete - Now in overdraft mode!", 5000)
        self._app_manager.get_notification_service().notify_overdraft_started()
        
    def _format_time(self, total_seconds: int) -> str:
        """Format seconds as HH:MM:SS string.
        
        Parameters
        ----------
        total_seconds : int
            Total number of seconds to format.
            
        Returns
        -------
        str
            Formatted time string.
        """
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event.
        
        This method ensures application state is saved when the window is closed.
        
        Parameters
        ----------
        event : QCloseEvent
            The close event.
        """
        print("Shutting down and saving state...")
        self._app_manager.shutdown()
        event.accept() 