"""Unit tests for TimeBank class.

This module contains comprehensive unit tests for the TimeBank class,
following the pytest protocol with pure unit testing (no I/O operations).
"""

import pytest
from simpletimerbank.core.time_bank import TimeBank


class TestTimeBank:
    """Test suite for TimeBank class."""
    
    def test_init_creates_zero_balance(self) -> None:
        """Test that TimeBank initializes with zero balance."""
        bank = TimeBank()
        assert bank.get_balance() == 0
    
    def test_deposit_increases_balance(self) -> None:
        """Test depositing time increases the balance correctly."""
        bank = TimeBank()
        bank.deposit(300)  # 5 minutes
        assert bank.get_balance() == 300
        
        bank.deposit(60)   # 1 more minute
        assert bank.get_balance() == 360
    
    def test_deposit_with_zero_does_not_change_balance(self) -> None:
        """Test depositing zero time does not change balance."""
        bank = TimeBank()
        bank.deposit(100)
        bank.deposit(0)
        assert bank.get_balance() == 100
    
    def test_deposit_with_negative_raises_error(self) -> None:
        """Test depositing negative time raises ValueError."""
        bank = TimeBank()
        with pytest.raises(ValueError, match="Cannot deposit negative time"):
            bank.deposit(-100)
    
    def test_withdraw_with_sufficient_balance_succeeds(self) -> None:
        """Test withdrawing time with sufficient balance."""
        bank = TimeBank()
        bank.deposit(300)
        bank.withdraw(100)
        assert bank.get_balance() == 200
    
    def test_withdraw_with_insufficient_balance_raises_error(self) -> None:
        """Test withdrawing time with insufficient balance raises ValueError."""
        bank = TimeBank()
        bank.deposit(100)
        with pytest.raises(ValueError, match="Insufficient balance"):
            bank.withdraw(200)
        assert bank.get_balance() == 100  # Should not change
    
    def test_withdraw_exact_balance_succeeds(self) -> None:
        """Test withdrawing exact balance amount succeeds."""
        bank = TimeBank()
        bank.deposit(150)
        bank.withdraw(150)
        assert bank.get_balance() == 0
    
    def test_withdraw_with_zero_does_not_change_balance(self) -> None:
        """Test withdrawing zero time does not change balance."""
        bank = TimeBank()
        bank.deposit(100)
        bank.withdraw(0)
        assert bank.get_balance() == 100
    
    def test_withdraw_with_negative_raises_error(self) -> None:
        """Test withdrawing negative time raises ValueError."""
        bank = TimeBank()
        with pytest.raises(ValueError, match="Cannot withdraw negative time"):
            bank.withdraw(-50)
    
    def test_set_balance_updates_correctly(self) -> None:
        """Test setting the balance directly."""
        bank = TimeBank()
        bank.deposit(1000)  # Initial value
        bank.set_balance(300)
        assert bank.get_balance() == 300

    def test_set_balance_with_zero(self) -> None:
        """Test setting the balance to zero."""
        bank = TimeBank()
        bank.deposit(500)
        bank.set_balance(0)
        assert bank.get_balance() == 0

    def test_set_balance_with_negative_raises_error(self) -> None:
        """Test setting the balance to a negative value raises ValueError."""
        bank = TimeBank()
        with pytest.raises(ValueError, match="Balance cannot be negative"):
            bank.set_balance(-100)
    
    def test_multiple_operations_sequence(self) -> None:
        """Test a sequence of multiple operations."""
        bank = TimeBank()
        
        # Add some time
        bank.deposit(1000)
        assert bank.get_balance() == 1000
        
        # Withdraw some time
        bank.withdraw(300)
        assert bank.get_balance() == 700
        
        # Add more time
        bank.deposit(500)
        assert bank.get_balance() == 1200
        
        # Set to a specific balance
        bank.set_balance(500)
        assert bank.get_balance() == 500 