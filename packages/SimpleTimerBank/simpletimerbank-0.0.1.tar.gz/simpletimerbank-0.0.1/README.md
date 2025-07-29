# Simple Timer Bank

A sophisticated desktop application built with PySide6 that allows you to manage time as a resource. Bank your time, then spend it on focused work sessions using a flexible timer system. This tool is designed to help you stay productive by making you conscious of how you spend your time.

![SimpleTimerBank Screenshot](docs/assets/screenshot.png)

## Core Concepts

-   **Time as a Resource**: Think of time like money in a bank. You can deposit it, withdraw it, and spend it.
-   **The Time Bank**: Your central repository of available time. The main display shows your current balance.
-   **Transactions**: Instantly add or remove time from your bank using the "Manage Bank Balance" controls.
-   **Timer Sessions**: "Spend" your banked time by running a countdown timer for a specific duration.
-   **Overdraft Mode**: If a timer session runs out, it doesn't just stop. It automatically enters "Overdraft Mode" and begins withdrawing time directly from your bank balance, complete with sound and system notifications.
-   **Refunds**: If you stop a timer session early, the unused time is instantly refunded to your bank.

## Features

-   **Digital Clock Displays**: Clear, easy-to-read displays for both your bank balance and the active timer.
-   **Intuitive Transaction Controls**:
    -   Deposit, instantly withdraw, or set your bank balance to a specific value.
    -   Use relative preset buttons (`+15m`, `-30m`, etc.) to quickly adjust the transaction amount.
-   **Flexible Timer Controls**: Start, pause, resume, and stop timer sessions with clear, expanding buttons.
-   **Audio-Visual Alerts**: Receive non-blocking system notifications with custom sounds for key events like overdraft activation and bank depletion.
-   **Persistent State**: Your time bank balance is automatically saved when you close the application and reloaded on startup.
-   **Polished UI**: A clean, visually organized interface with distinct sections for different actions.

## Installation and Running

### For Users

1.  **Download the Application**:
    -   Get the latest version from the releases page or directly via this link:
      [SimpleTimerBank_v1.1.0.zip](assets/SimpleTimerBank_v1.0.0.zip)

2.  **Unzip and Run**:
    -   Unzip the downloaded file.
    -   Navigate into the `SimpleTimerBank` folder.
    -   Double-click `SimpleTimerBank.exe` to start the application.

### For Developers

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/SimpleTimerBank.git
    cd SimpleTimerBank
    ```

2.  **Set up a Virtual Environment and Install**:
    This project uses `uv` for package management.
    ```bash
    # Create a virtual environment
    uv venv
    # Activate it (example for Windows PowerShell)
    .venv\Scripts\Activate.ps1
    # Install the project and its dependencies
    uv pip install -e .
    ```

3.  **Run the Application**:
    ```bash
    python -m simpletimerbank.main
    ```

## Development

-   **Run Tests**: `make test` or `uv run pytest`
-   **Build Documentation**: `make doc`
-   **Publish Documentation**: `make publish-docs`

## License

This project is licensed under the [MIT License](LICENSE).
