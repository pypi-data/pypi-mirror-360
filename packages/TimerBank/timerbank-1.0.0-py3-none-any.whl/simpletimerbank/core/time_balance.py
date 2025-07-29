"""Time balance management module.

This module contains the TimeBalance class responsible for managing
the user's time balance (add time, subtract time, format display).
"""


class TimeBalance:
    """Manages time balance operations for the SimpleTimerBank application.
    
    This class handles adding and subtracting time from the user's balance,
    formatting time for display, and validating time operations.
    """
    
    def __init__(self) -> None:
        """Initialize TimeBalance with zero balance."""
        self._balance_seconds: int = 0
    
    def add_time(self, seconds: int) -> None:
        """Add time to the balance.
        
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
            raise ValueError("Cannot add negative time")
        self._balance_seconds += seconds
    
    def subtract_time(self, seconds: int) -> bool:
        """Subtract time from the balance.
        
        Parameters
        ----------
        seconds : int
            Number of seconds to subtract from the balance.
            
        Returns
        -------
        bool
            True if subtraction was successful, False if insufficient balance.
            
        Raises
        ------
        ValueError
            If seconds is negative.
        """
        if seconds < 0:
            raise ValueError("Cannot subtract negative time")
            
        if self._balance_seconds >= seconds:
            self._balance_seconds -= seconds
            return True
        return False
    
    def get_balance_seconds(self) -> int:
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
    
    def format_time(self, seconds: int) -> str:
        """Format seconds into HH:MM:SS string.
        
        Parameters
        ----------
        seconds : int
            Time in seconds to format.
            
        Returns
        -------
        str
            Formatted time string in HH:MM:SS format.
            
        Raises
        ------
        ValueError
            If seconds is negative.
        """
        if seconds < 0:
            raise ValueError("Cannot format negative time")
            
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"
    
    def get_balance_formatted(self) -> str:
        """Get current balance as formatted string.
        
        Returns
        -------
        str
            Current balance formatted as HH:MM:SS.
        """
        return self.format_time(self._balance_seconds) 