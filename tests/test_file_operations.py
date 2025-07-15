"""Tests for file input/output operations."""

import json
import tempfile

import click
import pytest

from cc_paydown_planner import (
    CreditCard,
    normalize_header,
    read_cards_from_json,
    save_cards_to_json,
)


class TestNormalizeHeader:
    """Test the normalize_header function."""

    def test_normalize_header_with_numbers(self):
        """Test header normalization with leading numbers."""
        test_cases = [
            ("1   Current Balance", "Current Balance"),
            ("2 Card Name", "Card Name"),
            ("10   Payment Due Date", "Payment Due Date"),
            ("123    APR", "APR"),
        ]

        for input_header, expected in test_cases:
            result = normalize_header(input_header)
            assert result == expected

    def test_normalize_header_without_numbers(self):
        """Test header normalization without leading numbers."""
        test_cases = [
            ("Current Balance", "Current Balance"),
            ("Card Name", "Card Name"),
            ("  Payment Due Date  ", "Payment Due Date"),
        ]

        for input_header, expected in test_cases:
            result = normalize_header(input_header)
            assert result == expected

    def test_normalize_header_edge_cases(self):
        """Test header normalization edge cases."""
        test_cases = [
            ("", ""),
            ("   ", ""),
            ("123", ""),
            ("1", ""),
            ("1a", "a"),
        ]

        for input_header, expected in test_cases:
            result = normalize_header(input_header)
            assert result == expected


class TestReadCardsFromJSON:
    """Test the read_cards_from_json function."""

    def test_read_simple_json_array(self):
        """Test reading a simple JSON array format."""
        json_data = [
            {
                "card_name": "Test Card 1",
                "current_balance": 1000.0,
                "minimum_payment": 50.0,
                "payment_due_date": "15th",
                "apr": 18.0,
            },
            {
                "card_name": "Test Card 2",
                "current_balance": 2000.0,
                "minimum_payment": 75.0,
                "payment_due_date": "28th",
                "apr": 20.0,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(json_data, f)
            temp_path = f.name

        try:
            cards = read_cards_from_json(temp_path)

            assert len(cards) == 2
            assert cards[0].name == "Test Card 1"
            assert cards[0].balance == 1000.0
            assert cards[0].minimum_payment == 50.0
            assert cards[0].due_date == "15th"
            assert cards[0].apr == 18.0

            assert cards[1].name == "Test Card 2"
            assert cards[1].balance == 2000.0
        finally:
            import os

            os.unlink(temp_path)

    def test_read_json_with_default_apr(self):
        """Test reading JSON with default APR structure."""
        json_data = {
            "default_apr": 15.0,
            "cards": [
                {
                    "card_name": "Default APR Card",
                    "current_balance": 1500.0,
                    "minimum_payment": 60.0,
                    "payment_due_date": "5th",
                }
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(json_data, f)
            temp_path = f.name

        try:
            cards = read_cards_from_json(temp_path)

            assert len(cards) == 1
            assert cards[0].apr == 15.0  # Should use default APR
        finally:
            import os

            os.unlink(temp_path)

    def test_read_json_with_zero_balance(self):
        """Test reading JSON with zero balance cards."""
        json_data = [
            {
                "card_name": "Zero Balance Card",
                "current_balance": 0.0,
                "minimum_payment": 0.0,
                "payment_due_date": "15th",
                "apr": 18.0,
            },
            {
                "card_name": "Active Card",
                "current_balance": 1000.0,
                "minimum_payment": 50.0,
                "payment_due_date": "28th",
                "apr": 20.0,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(json_data, f)
            temp_path = f.name

        try:
            cards = read_cards_from_json(temp_path)

            assert len(cards) == 2
            assert cards[0].balance == 0.0
            assert cards[1].balance == 1000.0
        finally:
            import os

            os.unlink(temp_path)

    def test_read_json_missing_required_fields(self):
        """Test reading JSON with missing required fields."""
        json_data = [
            {
                "card_name": "Incomplete Card",
                "current_balance": 1000.0,
                # missing minimum_payment
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(json_data, f)
            temp_path = f.name

        try:
            # Should raise ClickException due to no valid cards
            with pytest.raises(click.ClickException, match="No valid credit card data"):
                read_cards_from_json(temp_path)
        finally:
            import os

            os.unlink(temp_path)

    def test_read_json_invalid_format(self):
        """Test reading invalid JSON format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name

        try:
            with pytest.raises(click.ClickException, match="Invalid JSON format"):
                read_cards_from_json(temp_path)
        finally:
            import os

            os.unlink(temp_path)

    def test_read_json_file_not_found(self):
        """Test reading non-existent JSON file."""
        with pytest.raises(click.ClickException, match="File not found"):
            read_cards_from_json("/nonexistent/file.json")

    def test_read_json_negative_balance(self):
        """Test reading JSON with negative balance."""
        json_data = [
            {
                "card_name": "Negative Balance",
                "current_balance": -100.0,
                "minimum_payment": 25.0,
                "payment_due_date": "15th",
                "apr": 18.0,
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(json_data, f)
            temp_path = f.name

        try:
            with pytest.raises(click.ClickException, match="No valid credit card data"):
                read_cards_from_json(temp_path)
        finally:
            import os

            os.unlink(temp_path)


class TestSaveCardsToJSON:
    """Test the save_cards_to_json function."""

    def test_save_cards_basic(self):
        """Test basic card saving functionality."""
        cards = [
            CreditCard("Save Test 1", 1000.0, 50.0, "15th", 18.0),
            CreditCard("Save Test 2", 2000.0, 75.0, "28th", 20.0),
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            # Test the function (it prints messages, so we can't easily capture them)
            save_cards_to_json(cards, temp_path)

            # Verify the file was created and contains correct data
            with open(temp_path, "r") as f:
                saved_data = json.load(f)

            assert len(saved_data) == 2

            assert saved_data[0]["card_name"] == "Save Test 1"
            assert saved_data[0]["current_balance"] == 1000.0
            assert saved_data[0]["minimum_payment"] == 50.0
            assert saved_data[0]["payment_due_date"] == "15th"
            assert saved_data[0]["apr"] == 18.0

            assert saved_data[1]["card_name"] == "Save Test 2"
            assert saved_data[1]["current_balance"] == 2000.0

        finally:
            import os

            os.unlink(temp_path)

    def test_save_cards_auto_json_extension(self):
        """Test that .json extension is automatically added."""
        cards = [CreditCard("Extension Test", 1000.0, 50.0, "15th", 18.0)]

        with tempfile.TemporaryDirectory() as temp_dir:
            import os

            temp_path = os.path.join(temp_dir, "test_file")  # No extension

            save_cards_to_json(cards, temp_path)

            # Check that .json was added
            json_path = temp_path + ".json"
            assert os.path.exists(json_path)

            with open(json_path, "r") as f:
                saved_data = json.load(f)

            assert len(saved_data) == 1
            assert saved_data[0]["card_name"] == "Extension Test"

    def test_save_cards_with_existing_json_extension(self):
        """Test saving when filename already has .json extension."""
        cards = [CreditCard("JSON Ext Test", 1000.0, 50.0, "15th", 18.0)]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            save_cards_to_json(cards, temp_path)

            # Should not add another .json extension
            assert temp_path.endswith(".json")
            assert not temp_path.endswith(".json.json")

            with open(temp_path, "r") as f:
                saved_data = json.load(f)

            assert saved_data[0]["card_name"] == "JSON Ext Test"

        finally:
            import os

            os.unlink(temp_path)

    def test_save_empty_card_list(self):
        """Test saving empty card list."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            save_cards_to_json([], temp_path)

            with open(temp_path, "r") as f:
                saved_data = json.load(f)

            assert saved_data == []

        finally:
            import os

            os.unlink(temp_path)

    def test_save_cards_zero_balance(self):
        """Test saving cards with zero balance."""
        cards = [
            CreditCard("Zero Balance", 0.0, 0.0, "15th", 18.0),
            CreditCard("Active Card", 1000.0, 50.0, "28th", 20.0),
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            save_cards_to_json(cards, temp_path)

            with open(temp_path, "r") as f:
                saved_data = json.load(f)

            assert len(saved_data) == 2
            assert saved_data[0]["current_balance"] == 0.0
            assert saved_data[1]["current_balance"] == 1000.0

        finally:
            import os

            os.unlink(temp_path)
