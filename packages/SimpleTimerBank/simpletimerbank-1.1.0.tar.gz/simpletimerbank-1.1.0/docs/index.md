# Welcome to Simple Timer Bank

**Simple Timer Bank** is a sophisticated desktop application designed to help you manage your time like a financial asset. By "banking" your time, you can make conscious decisions about how you spend it, improving focus and productivity.

The application is built using Python and the PySide6 framework, featuring a polished, intuitive user interface.

![SimpleTimerBank Screenshot](assets/screenshot.png)

## The Philosophy

The core idea is to treat time as a finite resource. Before you can "spend" time on an activity, you must first "deposit" it into your bank. This simple act makes you more aware of your time allocation. The timer lets you spend your banked time on focused sessions, and the overdraft feature ensures you're aware when you exceed your planned duration.

## Key Features

-   **Visual Time Bank**: A large, digital display shows your exact time balance (HH:MM:SS).
-   **Full-Featured Timer**: A second digital display shows the active timer, which can be started, paused, resumed, and stopped.
-   **Transaction Management**:
    -   Deposit or instantly withdraw time from your bank.
    -   Set your balance directly to a specific value.
    -   Use relative preset buttons (`+15m`, `-30m`, `+1h`) to quickly modify the transaction amount.
-   **Automatic Overdraft & Refunds**:
    -   When a timer finishes, it automatically enters **Overdraft Mode**, withdrawing from your main balance and triggering a non-blocking system notification with sound.
    -   If you stop a timer early, the unused time is instantly **refunded** to your bank.
-   **Data Persistence**: Your balance is always saved on exit and reloaded on start.

## Getting Started

Ready to take control of your time? Head over to the **[Usage Guide](usage.md)** to learn how to install and use the application.
