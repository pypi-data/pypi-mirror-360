"""Unit tests for TimeBalance class.

This module contains comprehensive unit tests for the TimeBalance class,
following the pytest protocol with pure unit testing (no I/O operations).
"""

import pytest
from simpletimerbank.core.time_balance import TimeBalance


class TestTimeBalance:
    """Test suite for TimeBalance class."""
    
    def test_init_creates_zero_balance(self) -> None:
        """Test that TimeBalance initializes with zero balance."""
        tb = TimeBalance()
        assert tb.get_balance_seconds() == 0
    
    def test_add_time_increases_balance(self) -> None:
        """Test adding time increases the balance correctly."""
        tb = TimeBalance()
        tb.add_time(300)  # 5 minutes
        assert tb.get_balance_seconds() == 300
        
        tb.add_time(60)   # 1 more minute
        assert tb.get_balance_seconds() == 360
    
    def test_add_time_with_zero_does_not_change_balance(self) -> None:
        """Test adding zero time does not change balance."""
        tb = TimeBalance()
        tb.add_time(100)
        tb.add_time(0)
        assert tb.get_balance_seconds() == 100
    
    def test_add_time_with_negative_raises_error(self) -> None:
        """Test adding negative time raises ValueError."""
        tb = TimeBalance()
        with pytest.raises(ValueError, match="Cannot add negative time"):
            tb.add_time(-100)
    
    def test_subtract_time_with_sufficient_balance_succeeds(self) -> None:
        """Test subtracting time with sufficient balance returns True."""
        tb = TimeBalance()
        tb.add_time(300)
        result = tb.subtract_time(100)
        assert result is True
        assert tb.get_balance_seconds() == 200
    
    def test_subtract_time_with_insufficient_balance_fails(self) -> None:
        """Test subtracting time with insufficient balance returns False."""
        tb = TimeBalance()
        tb.add_time(100)
        result = tb.subtract_time(200)
        assert result is False
        assert tb.get_balance_seconds() == 100  # Should not change
    
    def test_subtract_time_exact_balance_succeeds(self) -> None:
        """Test subtracting exact balance amount succeeds."""
        tb = TimeBalance()
        tb.add_time(150)
        result = tb.subtract_time(150)
        assert result is True
        assert tb.get_balance_seconds() == 0
    
    def test_subtract_time_with_zero_does_not_change_balance(self) -> None:
        """Test subtracting zero time does not change balance."""
        tb = TimeBalance()
        tb.add_time(100)
        result = tb.subtract_time(0)
        assert result is True
        assert tb.get_balance_seconds() == 100
    
    def test_subtract_time_with_negative_raises_error(self) -> None:
        """Test subtracting negative time raises ValueError."""
        tb = TimeBalance()
        with pytest.raises(ValueError, match="Cannot subtract negative time"):
            tb.subtract_time(-50)
    
    def test_format_time_zero_seconds(self) -> None:
        """Test formatting zero seconds."""
        tb = TimeBalance()
        assert tb.format_time(0) == "00:00:00"
    
    def test_format_time_seconds_only(self) -> None:
        """Test formatting seconds only."""
        tb = TimeBalance()
        assert tb.format_time(45) == "00:00:45"
    
    def test_format_time_minutes_and_seconds(self) -> None:
        """Test formatting minutes and seconds."""
        tb = TimeBalance()
        assert tb.format_time(125) == "00:02:05"  # 2 minutes, 5 seconds
    
    def test_format_time_hours_minutes_seconds(self) -> None:
        """Test formatting hours, minutes, and seconds."""
        tb = TimeBalance()
        assert tb.format_time(3661) == "01:01:01"  # 1 hour, 1 minute, 1 second
    
    def test_format_time_large_values(self) -> None:
        """Test formatting large time values."""
        tb = TimeBalance()
        assert tb.format_time(86400) == "24:00:00"  # 24 hours
        assert tb.format_time(90061) == "25:01:01"  # 25 hours, 1 minute, 1 second
    
    def test_format_time_negative_raises_error(self) -> None:
        """Test formatting negative time raises ValueError."""
        tb = TimeBalance()
        with pytest.raises(ValueError, match="Cannot format negative time"):
            tb.format_time(-100)
    
    def test_get_balance_formatted(self) -> None:
        """Test getting formatted balance string."""
        tb = TimeBalance()
        tb.add_time(3725)  # 1 hour, 2 minutes, 5 seconds
        assert tb.get_balance_formatted() == "01:02:05"
    
    def test_set_balance_updates_correctly(self) -> None:
        """Test setting the balance directly."""
        tb = TimeBalance()
        tb.add_time(1000)  # Initial value
        tb.set_balance(300)
        assert tb.get_balance_seconds() == 300

    def test_set_balance_with_zero(self) -> None:
        """Test setting the balance to zero."""
        tb = TimeBalance()
        tb.add_time(500)
        tb.set_balance(0)
        assert tb.get_balance_seconds() == 0

    def test_set_balance_with_negative_raises_error(self) -> None:
        """Test setting the balance to a negative value raises ValueError."""
        tb = TimeBalance()
        with pytest.raises(ValueError, match="Balance cannot be negative"):
            tb.set_balance(-100)
    
    def test_multiple_operations_sequence(self) -> None:
        """Test a sequence of multiple operations."""
        tb = TimeBalance()
        
        # Add some time
        tb.add_time(1000)
        assert tb.get_balance_seconds() == 1000
        
        # Subtract some time
        result = tb.subtract_time(300)
        assert result is True
        assert tb.get_balance_seconds() == 700
        
        # Add more time
        tb.add_time(500)
        assert tb.get_balance_seconds() == 1200
        
        # Try to subtract more than available
        result = tb.subtract_time(1500)
        assert result is False
        assert tb.get_balance_seconds() == 1200
        
        # Format the final balance
        assert tb.get_balance_formatted() == "00:20:00"  # 20 minutes 