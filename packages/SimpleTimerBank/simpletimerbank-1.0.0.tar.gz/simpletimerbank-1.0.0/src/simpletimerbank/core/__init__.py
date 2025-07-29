"""Core business logic package for SimpleTimerBank.

This package contains all the core business logic components that are independent
of the GUI framework. This separation enables comprehensive unit testing and
potential reuse in different interface implementations.

Modules
-------
time_balance : TimeBalance
    Manages time balance operations (add, subtract, format display).
time_bank : TimeBank
    Manages time banking operations (deposit, withdraw).
countdown_timer : CountdownTimer  
    Handles countdown timer logic and state management.
persistence : PersistenceService
    Manages data loading and saving to persistent storage.
app_state : AppState
    Coordinates application state across all components.
""" 