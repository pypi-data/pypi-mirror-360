# SimpleTimerBank - The Time Bank Edition

## Background and Motivation

The project's goal is to create a "Time Bank" application. A user can store units of time in a "bank" and then "spend" this time via a countdown timer. This allows for disciplined time management, where time must be earned before it can be spent.

The core features required are:
1.  **Time Bank**: A central store for the user's time balance.
2.  **Balance Display**: A clear, visible display of the current time balance.
3.  **Manual Adjustments**: The ability to add or remove time from the bank.
4.  **Consumption Timer**: A timer to spend a specific amount of time withdrawn from the bank. This timer has `Start`, `Pause`, `Resume`, and `Stop` controls.
5.  **Refund on Stop**: If a timer session is stopped early, the unused time is refunded to the bank.
6.  **Overdraft**: If the timer completes its initial cycle and is not stopped, it will continue to run, draining the main bank balance until it hits zero.
7.  **Notifications**: A notification is triggered when the initial timer cycle completes.

## Key Challenges and Analysis

1.  **Stateful Timer Logic**: The `CountdownTimer` is no longer a simple countdown. It must be a state machine that manages `Idle`, `Running`, `Paused`, and `Stopped` states to handle the user controls correctly.
2.  **Timer-Bank Interaction Protocol**: The relationship between the `CountdownTimer` and `TimeBank` is now highly transactional and must be robust.
    -   **Start**: Time must be withdrawn from the bank to fund the timer. This is a hard requirement.
    -   **Stop**: Unused time from the timer's initial duration must be reliably refunded to the bank.
    -   **Overdraft Tick**: During the overdraft phase, the timer must trigger a 1-second withdrawal from the bank on every tick.
3.  **The Overdraft Mechanism**: This is the most complex logic. The `CountdownTimer` must seamlessly transition from its "normal countdown" phase to an "overdraft" phase. This requires a clear state flag (e.g., `is_overdrafting`). The UI must also visually reflect this critical state change.
4.  **UI Decoupling**: The application UI needs to be conceptually split. There should be a "Bank" area for managing the balance and a "Timer" area for the countdown. Both must communicate through a central controller (`AppState`) to remain decoupled and maintainable.
5.  **Atomicity**: Actions like stopping and refunding must be treated as atomic operations to prevent data corruption (e.g., refunding time without actually stopping the timer).

## High-level Task Breakdown

The project will be implemented in phases, focusing on building a robust core logic foundation before the UI.

*   **Phase 1**: Core Logic - The `TimeBank`
*   **Phase 2**: Core Logic - The Advanced `CountdownTimer`
*   **Phase 3**: Core Logic - The `AppState` Orchestrator
*   **Phase 4**: GUI Implementation
*   **Phase 5**: Final Features and Polish

## Project Status Board

### Phase 1: Core Logic - The `TimeBank`
- [x] **Task 1.1**: Implement the `TimeBank` class.
  - [x] Create `src/simpletimerbank/core/time_bank.py` with a `TimeBank` class.
  - [x] The class will manage a single time balance in seconds.
  - [x] Implement `get_balance() -> int`, `deposit(seconds: int)`, and `withdraw(seconds: int)`.
  - [x] `withdraw` must raise a `ValueError` if funds are insufficient.
  - [x] Create `tests/test_time_bank.py` and ensure all methods are fully tested.

### Phase 2: Core Logic - The Advanced `CountdownTimer`
- [x] **Task 2.1**: Implement `CountdownTimer` with internal state management.
  - [x] Create `src/simpletimerbank/core/countdown_timer.py` with a `CountdownTimer` class.
  - [x] Define states: `IDLE`, `RUNNING`, `PAUSED`, `STOPPED`.
  - [x] It should also have a boolean flag: `is_overdrafting`.
  - [x] Implement `start(duration: int)`, `pause()`, `resume()`, and `stop()`.
- [x] **Task 2.2**: Implement the `tick` and overdraft logic.
  - [x] The timer's `tick` method (called every second) should decrement `remaining_seconds`.
  - [x] When `remaining_seconds` hits zero, the timer should set `is_overdrafting` to `True`.
  - [x] In overdraft mode, each `tick` must signal that 1 second should be withdrawn from the bank.
- [x] **Task 2.3**: Create `tests/test_countdown_timer.py` to test all state transitions, the countdown, and the overdraft signaling.

### Phase 3: Core Logic - The `AppState` Orchestrator
- [x] **Task 3.1**: Implement the `AppState` class.
  - [x] Create `src/simpletimerbank/core/app_state.py` with an `AppState` class to manage `TimeBank` and `CountdownTimer` instances.
- [x] **Task 3.2**: Implement the core session logic in `AppState`.
  - [x] `start_session(duration: int)`: Withdraws from bank, then starts the timer. Fails if bank funds are too low.
  - [x] `stop_session()`: Stops the timer, gets its `remaining_seconds`, and deposits them back to the bank.
  - [x] `pause_session()` and `resume_session()`.
- [x] **Task 3.3**: Connect timer signals to `AppState` actions.
  - [x] Handle the overdraft signal from the timer to withdraw 1 second from the `TimeBank`.
  - [x] Handle the timer completion signal to trigger notifications.
- [x] **Task 3.4**: Add persistence to `AppState` to save/load the `TimeBank` balance.
- [x] **Task 3.5**: Update `tests/test_app_state.py` to test these interaction workflows.
  - [x] Add a specific test case to verify that stopping a session early correctly refunds the remaining time to the `TimeBank`.

### Phase 4: GUI Implementation
- [x] **Task 4.1**: Implement the `AppStateManager` class as a bridge between the core logic and the GUI.
  - [x] Create the `AppStateManager` class in `src/simpletimerbank/core/app_state.py`.
  - [x] Add convenience methods for the GUI to interact with the core logic.
  - [x] Create `tests/test_app_state_manager.py` to test the manager's functionality.
- [x] **Task 4.2**: Enhance the MainWindow class to connect with the AppStateManager.
  - [x] Update `src/simpletimerbank/gui/main_window.py` to use the AppStateManager.
  - [x] Implement regular timer tick functionality with QTimer.
  - [x] Create `tests/test_main_window.py` to test the GUI functionality.

### Phase 5: Final Features and Polish
- [x] **Task 5.1**: Implement desktop notifications.
  - [x] Create `src/simpletimerbank/core/notification_service.py` for desktop notifications.
  - [x] Add notification support for timer completion, overdraft mode, and bank depletion.
  - [x] Integrate notifications with the `AppState` class.
- [x] **Task 5.2**: Refine UI/UX and document the application.
  - [x] Enhance the UI with visual indicators for overdraft mode.
  - [x] Add a status bar with informative messages.
  - [x] Update the launcher script for better user experience.
  - [x] Add feedback messages for user actions.

## Executor's Feedback or Assistance Requests
### 2023-10-15: Phase 1 Complete
Phase 1 has been successfully completed. The `TimeBank` class has been implemented following the specifications, with full test coverage. All tests are passing.

The `TimeBank` class provides these core features:
- Initializes with a zero balance
- `deposit(seconds)` method to add time to the bank
- `withdraw(seconds)` method that enforces sufficient funds, raising ValueError if insufficient
- `get_balance()` method to retrieve the current balance
- `set_balance(seconds)` method to directly set the balance

The implementation follows all the required development standards:
- Full NumPy-style docstrings
- Complete type hinting
- PEP 8 compliant code
- Pure unit tests with no I/O
- Tests execute in well under the 5s target time

Next, I will begin implementing Phase 2 - the Advanced `CountdownTimer`.

### 2023-10-16: Phase 2 Complete
Phase 2 has been successfully completed. The `CountdownTimer` class has been completely redesigned following TDD principles. All tests are passing.

The new `CountdownTimer` implementation includes:
- Four clearly defined states: `IDLE`, `RUNNING`, `PAUSED`, and `STOPPED`
- An `is_overdrafting` flag to indicate when the timer has reached zero and is in overdraft mode
- Self-contained time tracking with `_remaining_seconds` (instead of relying on `TimeBalance`)
- A `tick()` method that returns a signal (1 second) when in overdraft mode to communicate with the bank
- Completion callback for notification when the timer transitions to overdraft mode

The implementation addresses the key challenges mentioned in the plan:
- The timer is now a proper state machine with clear transitions and appropriate error handling
- Overdraft detection and signaling are properly implemented
- The timer preserves its state (remaining seconds) when stopped for refund purposes
- Timer and bank logic are now fully decoupled for better separation of concerns

All tests are passing with 100% coverage of the new functionality.

Next, I will begin implementing Phase 3 - the `AppState` Orchestrator.

### 2023-10-17: Phase 3 Complete
Phase 3 has been successfully completed. The `AppState` class has been implemented to orchestrate the interactions between the `TimeBank` and `CountdownTimer`. All tests are passing.

The new `AppState` implementation includes:
- Session management with `start_session()`, `pause_session()`, `resume_session()`, and `stop_session()` methods
- Proper handling of timer signals, including overdraft handling and time refunds
- Integration with the `PersistenceService` to save and load the bank balance
- Event callback hooks for timer ticks and timer completion notifications

Key features implemented:
- The session logic now properly handles the timer lifecycle and bank transactions as atomic operations
- When a session is stopped early, remaining time is correctly refunded to the bank
- When the timer enters overdraft mode, the app state withdraws time from the bank on each tick
- When the bank balance is depleted, the timer is automatically stopped

The `AppState` tests validate all these workflows with comprehensive test cases, including a specific test to verify the refund mechanism. All tests are passing with good coverage.

The implementation successfully addresses the key challenges from the plan:
- Timer-bank interactions are now properly orchestrated
- The overdraft mechanism withdraws time from the bank appropriately
- Transactions (start, stop, refund) are handled atomically
- The UI can be properly decoupled with the callback system

Next, I would begin implementing Phase 4 - GUI Implementation.

### 2023-10-18: Phase 4 Complete
Phase 4 has been successfully completed. The GUI implementation now integrates with the core application logic through the new `AppStateManager` class. All tests are passing.

Key implementations completed:
- Created the `AppStateManager` class as a bridge between the core logic and the GUI
  - Provides simplified methods for the GUI to interact with the core logic
  - Handles time formatting and state management
  - Exposes core functionality in a GUI-friendly way
- Enhanced the `MainWindow` class to integrate with the `AppStateManager`
  - Set up a QTimer for regular timer ticks to keep the UI and logic in sync
  - Improved error handling with user-friendly message dialogs
  - Fixed the logic for timer control (start, pause, resume, stop)
- Added comprehensive unit tests for both classes
  - Tests for the `AppStateManager` verify that it correctly delegates to the `AppState`
  - Tests for the GUI functionality focus on the interface between GUI and business logic
  - All tests use mocking to avoid I/O and maintain unit test isolation

The integration successfully addresses the key challenges:
- UI decoupling is maintained through the `AppStateManager`, which serves as a façade
- The timer-bank interaction protocol is properly implemented in the UI
- Timer states are properly reflected in the UI controls
- The UI properly handles error conditions and prevents invalid actions

The implementation follows all the required development standards:
- Full NumPy-style docstrings
- Complete type hinting
- PEP 8 compliant code
- Pure unit tests with aggressive mocking to avoid I/O
- Tests execute in well under the 5s target time

Next, I would move on to Phase 5 - Final Features and Polish.

### 2023-10-19: Phase 5 Complete
Phase 5 has been successfully completed. The application now has enhanced UI features and desktop notifications. All tests are passing.

Key implementations completed:
- Created the `NotificationService` class for desktop notifications
  - Added methods for different notification types: timer completion, overdraft, bank depletion
  - Used the cross-platform plyer library for notifications
  - Added comprehensive unit tests with proper mocking
- Enhanced the user interface
  - Added a status bar with informative messages for user actions
  - Implemented visual indicators for overdraft mode (red display, status bar indicator, and mode label)
  - Added a header and improved the overall layout
  - Updated the timer display to show the current mode (normal vs. overdraft)
- Improved the user experience
  - Added feedback messages for all user actions
  - Updated the launcher script for a better user experience
  - Implemented proper window title and sizing

The implementation successfully addresses the final challenges:
- The UI now visually reflects the overdraft state with color changes and text indicators
- Desktop notifications alert the user to important events even when the app is not in focus
- The status bar provides contextual information about the current state and recent actions
- The user gets clear feedback for all interactions with the app

All tests are passing with good coverage, and the test suite executes in under 0.5 seconds, well below the 5-second target.

The SimpleTimerBank application is now complete with all features implemented according to the requirements. The codebase follows clean architecture principles with proper separation of concerns, and all components are well-tested.

## Reviewer's Audit & Feedback

### Reviewer's Audit Checklist

#### A. Requirement Fulfillment
- [x] **Functional Correctness**: The code fully achieves the requirements for all phases of the project. All core features (TimeBank, CountdownTimer, AppState, GUI, Notifications) work together correctly.

#### B. Test Protocol Adherence (`.cursor/pytest rule.md`)
- [x] **Pure Unit Tests**: All tests are 100% isolated with aggressive mocking, including notifications and GUI components.
- [x] **No Forbidden Tests**: The test suite contains only unit tests, with no integration/E2E tests or I/O operations.
- [x] **Test Execution**: `pytest` passes without errors, with all 128 tests passing successfully.
- [x] **Speed**: The test suite is extremely fast, executing in 0.49s, well under the 5s target.

#### C. Python Development Protocol Adherence
- [x] **Package Structure**: The code follows the `src` layout with proper package organization.
- [x] **Docstrings**: All public APIs are documented via NumPy-style docstrings.
- [x] **Type Hinting**: All function signatures have complete type hints.
- [x] **Code Quality**: The code is modular, clean, and PEP 8 compliant.

#### D. Workflow & Documentation Hygiene
- [x] **Scratchpad Integrity**: The project history is clear and status is up-to-date.
- [x] **Lessons Learned**: Major challenges and their solutions were documented.

### Additional Feedback
The implementation of Phase 5 successfully adds the final features and polish to the application. The desktop notifications provide important alerts to the user, and the enhanced UI clearly communicates the current state, especially during the critical overdraft mode.

The visual indicators for overdraft mode (red display, status bar indicator, and mode label) make it immediately clear to the user when they are withdrawing from their bank balance, which is a key usability feature.

The separation of concerns is maintained throughout the implementation, with the notification service properly encapsulated and integrated with the existing architecture. The tests are comprehensive and follow the pure unit testing principle.

Overall, the SimpleTimerBank application is now complete and ready for use. The project has successfully addressed all the key challenges identified at the beginning, creating a robust, maintainable, and user-friendly application.

## Lessons
- **GUI Testing Approach**: When testing GUI components, focus on testing the interaction with the underlying business logic rather than attempting to test the GUI itself. This approach is more maintainable and less brittle.
- **Qt Integration**: Qt's signal/slot mechanism requires careful integration with Python's event handling. Using the `AppStateManager` as a bridge helps maintain clean separation of concerns.
- **Mocking Strategy**: For complex GUI components, aggressively mock the dependencies and focus tests on the business logic rather than the GUI implementation details.
- **Visual Feedback**: For critical state changes like entering overdraft mode, use multiple visual cues (color, text, status messages) to ensure the user understands the current state.
- **Notification Design**: Desktop notifications should be concise but informative, providing just enough context for the user to understand what action might be needed.
- **Cross-Platform Considerations**: Using libraries like plyer helps ensure notifications work across different operating systems without platform-specific code.