"""Tests for CreditCard class and basic functionality."""

import pytest

from cc_paydown_planner import CreditCard, calculate_interest


class TestCreditCard:
    """Test the CreditCard class."""

    def test_credit_card_creation(self):
        """Test creating a CreditCard instance."""
        card = CreditCard("Test Card", 1000.0, 50.0, "15th", 18.0)

        assert card.name == "Test Card"
        assert card.balance == 1000.0
        assert card.minimum_payment == 50.0
        assert card.due_date == "15th"
        assert card.apr == 18.0
        assert card.monthly_interest_rate == 18.0 / 100 / 12

    def test_credit_card_default_apr(self):
        """Test CreditCard with default APR."""
        card = CreditCard("Default APR Card", 2000.0, 100.0, "28th")

        assert card.apr == 18.0
        assert card.monthly_interest_rate == 18.0 / 100 / 12

    def test_credit_card_zero_balance(self):
        """Test CreditCard with zero balance."""
        card = CreditCard("Zero Balance", 0.0, 0.0, "1st", 15.0)

        assert card.balance == 0.0
        assert card.minimum_payment == 0.0
        assert card.apr == 15.0

    def test_credit_card_repr(self):
        """Test string representation of CreditCard."""
        card = CreditCard("Test Card", 1500.50, 75.25, "15th", 19.99)
        repr_str = repr(card)

        assert "Test Card" in repr_str
        assert "1500.50" in repr_str
        assert "75.25" in repr_str

    def test_monthly_interest_rate_calculation(self):
        """Test monthly interest rate calculation."""
        # Test different APR values
        test_cases = [
            (12.0, 12.0 / 100 / 12),  # 1% monthly
            (24.0, 24.0 / 100 / 12),  # 2% monthly
            (0.0, 0.0),  # 0% APR
            (36.0, 36.0 / 100 / 12),  # 3% monthly
        ]

        for apr, expected_monthly_rate in test_cases:
            card = CreditCard("Test", 1000.0, 50.0, "15th", apr)
            assert card.monthly_interest_rate == pytest.approx(expected_monthly_rate)


class TestCalculateInterest:
    """Test the calculate_interest function."""

    def test_calculate_interest_positive_balance(self):
        """Test interest calculation with positive balance."""
        balance = 1000.0
        monthly_rate = 0.015  # 1.5% monthly
        expected_interest = 1000.0 * 0.015

        interest = calculate_interest(balance, monthly_rate)
        assert interest == pytest.approx(expected_interest)

    def test_calculate_interest_zero_balance(self):
        """Test interest calculation with zero balance."""
        interest = calculate_interest(0.0, 0.015)
        assert interest == 0.0

    def test_calculate_interest_zero_rate(self):
        """Test interest calculation with zero rate."""
        interest = calculate_interest(1000.0, 0.0)
        assert interest == 0.0

    def test_calculate_interest_realistic_scenarios(self):
        """Test interest calculation with realistic credit card scenarios."""
        test_cases = [
            # (balance, APR, expected_monthly_interest)
            (5000.0, 18.0, 5000.0 * (18.0 / 100 / 12)),  # $75 interest
            (2500.0, 24.0, 2500.0 * (24.0 / 100 / 12)),  # $50 interest
            (1000.0, 15.0, 1000.0 * (15.0 / 100 / 12)),  # $12.50 interest
        ]

        for balance, apr, expected in test_cases:
            monthly_rate = apr / 100 / 12
            interest = calculate_interest(balance, monthly_rate)
            assert interest == pytest.approx(expected, rel=1e-6)
