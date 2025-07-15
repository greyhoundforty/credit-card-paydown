"""Tests for payment schedule calculation functions."""

import pytest

from cc_paydown_planner import CreditCard, create_payment_schedule


class TestPaymentSchedule:
    """Test the create_payment_schedule function."""

    def test_single_card_payment_schedule(self):
        """Test payment schedule with a single credit card."""
        card = CreditCard("Test Card", 1000.0, 50.0, "15th", 18.0)
        monthly_payment = 100.0

        result = create_payment_schedule([card], monthly_payment)

        assert "error" not in result
        assert "schedule" in result
        assert "total_months" in result
        assert "total_interest_paid" in result
        assert "total_amount_paid" in result

        # Should be paid off in reasonable time
        assert result["total_months"] > 0
        assert result["total_months"] < 20  # Should be less than 20 months

        # Interest should be positive but reasonable
        assert result["total_interest_paid"] > 0
        assert result["total_interest_paid"] < 200  # Shouldn't be excessive

    def test_multiple_cards_debt_snowball(self):
        """Test debt snowball method with multiple cards."""
        cards = [
            CreditCard("Small Card", 500.0, 25.0, "15th", 18.0),
            CreditCard("Large Card", 2000.0, 75.0, "28th", 20.0),
            CreditCard("Medium Card", 1000.0, 40.0, "5th", 15.0),
        ]
        monthly_payment = 200.0

        result = create_payment_schedule(cards, monthly_payment)

        assert "error" not in result
        schedule = result["schedule"]

        # First month should pay minimums plus extra to smallest balance
        first_month = schedule[0]
        small_card_payment = next(
            p for p in first_month["payments"] if p["card"] == "Small Card"
        )

        # Small card should get extra payment (more than minimum)
        assert small_card_payment["payment"] > 25.0

    def test_insufficient_budget_error(self):
        """Test error when budget is less than minimum payments."""
        cards = [
            CreditCard("Card 1", 1000.0, 50.0, "15th", 18.0),
            CreditCard("Card 2", 2000.0, 75.0, "28th", 20.0),
        ]
        # Total minimums = 125, but budget is only 100
        monthly_payment = 100.0

        result = create_payment_schedule(cards, monthly_payment)

        assert "error" in result
        assert "less than minimum payments required" in result["error"]

    def test_zero_balance_cards_filtered(self):
        """Test that cards with zero balance are filtered out."""
        cards = [
            CreditCard("Zero Card", 0.0, 0.0, "15th", 18.0),
            CreditCard("Active Card", 1000.0, 50.0, "28th", 20.0),
        ]
        monthly_payment = 100.0

        result = create_payment_schedule(cards, monthly_payment)

        assert "error" not in result
        # Should only process the active card
        schedule = result["schedule"]
        first_month = schedule[0]

        # Should only have one payment (for the active card)
        assert len(first_month["payments"]) == 1
        assert first_month["payments"][0]["card"] == "Active Card"

    def test_exact_minimum_payment(self):
        """Test when monthly payment exactly equals minimum payments."""
        cards = [
            CreditCard("Card 1", 1000.0, 50.0, "15th", 18.0),
            CreditCard("Card 2", 2000.0, 75.0, "28th", 20.0),
        ]
        monthly_payment = 125.0  # Exactly the sum of minimums

        result = create_payment_schedule(cards, monthly_payment)

        assert "error" not in result
        # Should work but take longer to pay off (no extra payments)
        assert result["total_months"] > 12  # Will take a while with no extra

    def test_large_extra_payment(self):
        """Test with large extra payment that pays off quickly."""
        card = CreditCard("Quick Payoff", 500.0, 25.0, "15th", 18.0)
        monthly_payment = 1000.0  # Way more than needed

        result = create_payment_schedule([card], monthly_payment)

        assert "error" not in result
        # Should pay off in 1 month
        assert result["total_months"] == 1
        # Total paid should be close to original balance plus one month interest
        assert result["total_amount_paid"] < 600  # Original + some interest

    def test_payment_schedule_structure(self):
        """Test the structure of the payment schedule."""
        card = CreditCard("Structure Test", 1000.0, 50.0, "15th", 18.0)
        monthly_payment = 100.0

        result = create_payment_schedule([card], monthly_payment)

        assert "error" not in result
        schedule = result["schedule"]

        # Check first month structure
        first_month = schedule[0]
        assert "month" in first_month
        assert "payments" in first_month
        assert "balances_after" in first_month
        assert "total_paid" in first_month
        assert "interest_paid" in first_month

        # Check payment structure
        payment = first_month["payments"][0]
        assert "card" in payment
        assert "payment" in payment
        assert "interest" in payment
        assert "principal" in payment
        assert "balance_before" in payment
        assert "balance_after" in payment

    def test_interest_calculation_in_schedule(self):
        """Test that interest is calculated correctly in the schedule."""
        card = CreditCard("Interest Test", 1000.0, 50.0, "15th", 24.0)  # 2% monthly
        monthly_payment = 100.0

        result = create_payment_schedule([card], monthly_payment)

        first_month = result["schedule"][0]
        payment = first_month["payments"][0]

        # Interest should be 2% of 1000 = $20
        expected_interest = 1000.0 * (24.0 / 100 / 12)
        assert payment["interest"] == pytest.approx(expected_interest, rel=1e-6)

        # Principal should be payment minus interest
        expected_principal = 100.0 - expected_interest
        assert payment["principal"] == pytest.approx(expected_principal, rel=1e-6)

    def test_empty_card_list(self):
        """Test behavior with empty card list."""
        result = create_payment_schedule([], 100.0)

        # Should return a valid result with empty schedule
        assert "schedule" in result
        assert result["schedule"] == []
        assert result["total_months"] == 0
        assert result["total_interest_paid"] == 0
        assert result["total_amount_paid"] == 0

    def test_all_zero_balance_cards(self):
        """Test with all cards having zero balance."""
        cards = [
            CreditCard("Zero 1", 0.0, 0.0, "15th", 18.0),
            CreditCard("Zero 2", 0.0, 0.0, "28th", 20.0),
        ]
        monthly_payment = 100.0

        result = create_payment_schedule(cards, monthly_payment)

        # Should return empty schedule since no cards have balance
        assert "schedule" in result
        assert result["schedule"] == []
        assert result["total_months"] == 0

    def test_card_sorting_by_balance(self):
        """Test that cards are sorted by balance (smallest first)."""
        cards = [
            CreditCard("Large", 3000.0, 100.0, "15th", 18.0),
            CreditCard("Small", 500.0, 25.0, "28th", 20.0),
            CreditCard("Medium", 1500.0, 60.0, "5th", 15.0),
        ]
        monthly_payment = 300.0

        result = create_payment_schedule(cards, monthly_payment)

        first_month = result["schedule"][0]

        # Find which card got the extra payment (should be the smallest)
        extra_payment_card = None
        for payment in first_month["payments"]:
            if (
                payment["payment"] > payment["interest"] + 25
            ):  # More than min + interest
                extra_payment_card = payment["card"]
                break

        # The small card should get the extra payment
        assert extra_payment_card == "Small"
