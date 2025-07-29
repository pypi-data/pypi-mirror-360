"""Time bank management module.

This module contains the TimeBank class responsible for managing
a time balance with banking operations (deposit, withdraw).
"""


class TimeBank:
    """Manages time banking operations for the SimpleTimerBank application.
    
    This class handles depositing and withdrawing time from the user's balance,
    and provides methods to access and modify the balance.
    """
    
    def __init__(self) -> None:
        """Initialize TimeBank with zero balance."""
        self._balance_seconds: int = 0
    
    def deposit(self, seconds: int) -> None:
        """Deposit time to the balance.
        
        Parameters
        ----------
        seconds : int
            Number of seconds to add to the balance.
            
        Raises
        ------
        ValueError
            If seconds is negative.
        """
        if seconds < 0:
            raise ValueError("Cannot deposit negative time")
        self._balance_seconds += seconds
    
    def withdraw(self, seconds: int) -> None:
        """Withdraw time from the balance.
        
        Parameters
        ----------
        seconds : int
            Number of seconds to withdraw from the balance.
            
        Raises
        ------
        ValueError
            If seconds is negative or if the balance is insufficient.
        """
        if seconds < 0:
            raise ValueError("Cannot withdraw negative time")
            
        if self._balance_seconds < seconds:
            raise ValueError("Insufficient balance")
            
        self._balance_seconds -= seconds
    
    def get_balance(self) -> int:
        """Get current balance in seconds.
        
        Returns
        -------
        int
            Current time balance in seconds.
        """
        return self._balance_seconds
    
    def set_balance(self, seconds: int) -> None:
        """Set the balance to an absolute value.
        
        Parameters
        ----------
        seconds : int
            The total number of seconds to set the balance to.
            
        Raises
        ------
        ValueError
            If seconds is negative.
        """
        if seconds < 0:
            raise ValueError("Balance cannot be negative")
        self._balance_seconds = seconds 