# Usage Guide

This guide provides detailed instructions on how to install and use the Simple Timer Bank application.

## Installation

This project uses `uv` for dependency and environment management.

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/SimpleTimerBank.git
    cd SimpleTimerBank
    ```

2.  **Create and Activate Virtual Environment**:
    ```bash
    # Create the venv
    uv venv

    # Activate the venv (Windows PowerShell)
    .venv\Scripts\Activate.ps1

    # On macOS/Linux, you would use:
    # source .venv/bin/activate
    ```

3.  **Install the Application**:
    Install the project in editable mode, which will also pull in all required dependencies like `PySide6` and `playsound`.
    ```bash
    uv pip install -e .
    ```

## Running the Application

Once the installation is complete, you can run the application with a single command:

```bash
python -m src.simpletimerbank.main
```

The application window will appear, ready for use.

---

## How to Use the Application

The interface is divided into three main sections, from top to bottom.

### 1. Your Time Bank Balance

This top section shows a large, digital display of your total available time. This is your "balance" that you can spend or add to.

### 2. Active Timer

This display shows the countdown of a currently running timer session. It remains at `00:00:00` until you start a timer.

### 3. Manage Bank Balance

This section is for performing instant transactions on your time bank.

-   **Amount**: This input field is where you set the time value for your transactions. You can type a value (HH:MM:SS) or use the preset buttons to adjust it.
-   **Preset Buttons**:
    -   `+15m`, `+30m`, `+1h`: Click these to add time to the **Amount** field.
    -   `-15m`, `-30m`, `-1h`: Click these to subtract time from the **Amount** field. The amount will not go below zero.
-   **Action Buttons**:
    -   **Deposit**: Instantly adds the value in the **Amount** field to your main bank balance.
    -   **Instant Withdraw**: Instantly subtracts the value from your bank balance.
    -   **Set Balance**: Sets your bank balance directly to the value in the **Amount** field.

### 4. Timer Controls

This section is for starting and managing a timed session, which "spends" the time from your bank.

-   **Start Timer**: Begins a countdown using the duration set in the **Amount** field. This amount is immediately subtracted from your bank balance.
-   **Pause Timer**: Pauses a running timer. The button will be disabled, and the "Start Timer" button will change to "Resume Timer".
-   **Stop Timer & Refund**: Stops the timer immediately and refunds any unused time back to your bank balance. For example, if you start a 1-hour timer and stop it after 10 minutes, 50 minutes will be deposited back into your bank.

### Overdraft Mode

This is a key feature of the application.

-   When your **Active Timer** counts down to zero, it doesn't just stop. It automatically enters Overdraft Mode.
-   You will receive a non-blocking system notification (with a sound) alerting you to this.
-   The Active Timer display will turn red, and a text indicator will appear.
-   The timer will start counting **up**, and for every second that passes, one second will be withdrawn from your **Time Bank Balance**.
-   To stop the overdraft, you must click the **Stop Timer & Refund** button (though in this case, there is no time to refund). The timer will stop, and your bank balance will be whatever remains. 