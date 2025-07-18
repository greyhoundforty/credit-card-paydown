#!/usr/bin/env python3
"""
Tests for calendar functionality
"""

import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
import io
import sys

# Add the parent directory to path to import our modules
sys.path.insert(0, '..')

from cc_paydown_planner import (
    CreditCard,
    parse_due_date,
    parse_calendar_date,
    show_calendar_view,
    get_day_suffix,
    get_card_colors,
    assign_card_colors,
    show_rich_calendar_view,
    get_matplotlib_color,
    export_payment_schedule,
    RICH_AVAILABLE,
    MATPLOTLIB_AVAILABLE
)


class TestCalendarFunctions(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_cards = [
            CreditCard("Chase Freedom", 2850.00, 85.00, "15th", 19.99),
            CreditCard("Capital One Venture", 1250.00, 35.00, "28th", 17.24),
            CreditCard("Discover It", 580.00, 25.00, "5th", 15.99),
            CreditCard("Citi Double Cash", 3420.00, 105.00, "22nd", 21.99),
            CreditCard("Amazon Prime Card", 0.00, 0.00, "10th", 18.74),  # Zero balance
        ]
        
    def test_parse_due_date_valid_formats(self):
        """Test parsing various due date formats."""
        test_cases = [
            ("15th", 15),
            ("28th", 28),
            ("5th", 5),
            ("22nd", 22),
            ("1st", 1),
            ("2nd", 2),
            ("3rd", 3),
            ("31st", 31),
            ("15", 15),  # Without suffix
            ("05", 5),   # With leading zero
            ("10", 10),
        ]
        
        for due_date, expected_day in test_cases:
            with self.subTest(due_date=due_date):
                result = parse_due_date(due_date)
                self.assertEqual(result, expected_day)
    
    def test_parse_due_date_invalid_formats(self):
        """Test parsing invalid due date formats returns default."""
        invalid_cases = [
            "invalid",
            "32nd",  # Invalid day
            "0th",   # Invalid day
            "",      # Empty string
            "15th of month",  # Extra text
            "abc",   # No numbers
        ]
        
        for invalid_date in invalid_cases:
            with self.subTest(invalid_date=invalid_date):
                result = parse_due_date(invalid_date)
                self.assertEqual(result, 15)  # Default value
    
    def test_parse_calendar_date_valid_formats(self):
        """Test parsing valid calendar date formats."""
        test_cases = [
            ("2024-07", (2024, 7)),
            ("2024-12", (2024, 12)),
            ("2024-01", (2024, 1)),
            ("2025-06", (2025, 6)),
            ("1999-12", (1999, 12)),
            ("2100-01", (2100, 1)),
        ]
        
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                result = parse_calendar_date(date_str)
                self.assertEqual(result, expected)
    
    def test_parse_calendar_date_invalid_formats(self):
        """Test parsing invalid calendar date formats."""
        invalid_cases = [
            "2024-13",  # Invalid month
            "2024-00",  # Invalid month
            "1899-12",  # Invalid year (too old)
            "2101-01",  # Invalid year (too new)
            "2024",     # Missing month
            "2024-07-15",  # Too many parts
            "invalid",  # Not a date
            "24-07",    # Invalid year format
            "",         # Empty string
        ]
        
        for invalid_date in invalid_cases:
            with self.subTest(invalid_date=invalid_date):
                with self.assertRaises(ValueError):
                    parse_calendar_date(invalid_date)
    
    def test_get_day_suffix(self):
        """Test getting correct day suffixes."""
        test_cases = [
            (1, "st"), (2, "nd"), (3, "rd"), (4, "th"), (5, "th"),
            (11, "th"), (12, "th"), (13, "th"), (14, "th"), (15, "th"),
            (21, "st"), (22, "nd"), (23, "rd"), (24, "th"), (25, "th"),
            (31, "st")
        ]
        
        for day, expected_suffix in test_cases:
            with self.subTest(day=day):
                result = get_day_suffix(day)
                self.assertEqual(result, expected_suffix)
    
    @patch('cc_paydown_planner.click.echo')
    def test_show_calendar_view_current_month(self, mock_echo):
        """Test showing calendar view for current month."""
        # Test with cards that have balances
        cards_with_balance = [card for card in self.test_cards if card.balance > 0]
        
        with patch('cc_paydown_planner.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 7, 15)
            show_calendar_view(cards_with_balance)
        
        # Check that echo was called (calendar was displayed)
        self.assertTrue(mock_echo.called)
        
        # Check that the calendar header was displayed
        calls = [str(call) for call in mock_echo.call_args_list]
        output_text = " ".join(calls)
        self.assertIn("PAYMENT CALENDAR - July 2024", output_text)
    
    @patch('cc_paydown_planner.click.echo')
    def test_show_calendar_view_specific_month(self, mock_echo):
        """Test showing calendar view for specific month."""
        cards_with_balance = [card for card in self.test_cards if card.balance > 0]
        
        show_calendar_view(cards_with_balance, 8, 2024)
        
        # Check that echo was called
        self.assertTrue(mock_echo.called)
        
        # Check that the correct month was displayed
        calls = [str(call) for call in mock_echo.call_args_list]
        output_text = " ".join(calls)
        self.assertIn("PAYMENT CALENDAR - August 2024", output_text)
    
    @patch('cc_paydown_planner.click.echo')
    def test_show_calendar_view_no_balances(self, mock_echo):
        """Test showing calendar view with no cards having balances."""
        zero_balance_cards = [card for card in self.test_cards if card.balance == 0]
        
        show_calendar_view(zero_balance_cards)
        
        # Check that the no payments message was displayed
        calls = [str(call) for call in mock_echo.call_args_list]
        output_text = " ".join(calls)
        self.assertIn("No payment due dates found", output_text)
    
    @patch('cc_paydown_planner.click.echo')
    def test_show_calendar_view_invalid_month(self, mock_echo):
        """Test showing calendar view with invalid month."""
        cards_with_balance = [card for card in self.test_cards if card.balance > 0]
        
        show_calendar_view(cards_with_balance, 13, 2024)  # Invalid month
        
        # Check that error message was displayed
        calls = [str(call) for call in mock_echo.call_args_list]
        output_text = " ".join(calls)
        self.assertIn("Invalid month", output_text)
    
    @patch('cc_paydown_planner.click.echo')
    def test_show_calendar_view_invalid_year(self, mock_echo):
        """Test showing calendar view with invalid year."""
        cards_with_balance = [card for card in self.test_cards if card.balance > 0]
        
        show_calendar_view(cards_with_balance, 7, 1800)  # Invalid year
        
        # Check that error message was displayed
        calls = [str(call) for call in mock_echo.call_args_list]
        output_text = " ".join(calls)
        self.assertIn("Invalid year", output_text)
    
    @patch('cc_paydown_planner.click.echo')
    def test_show_calendar_view_payment_dates_highlighted(self, mock_echo):
        """Test that payment dates are properly highlighted in calendar."""
        cards_with_balance = [card for card in self.test_cards if card.balance > 0]
        
        show_calendar_view(cards_with_balance, 7, 2024)
        
        # Check that payment dates are mentioned in the output
        calls = [str(call) for call in mock_echo.call_args_list]
        output_text = " ".join(calls)
        
        # Should contain payment information for each card with balance
        self.assertIn("Chase Freedom", output_text)
        self.assertIn("Capital One Venture", output_text)
        self.assertIn("Discover It", output_text)
        self.assertIn("Citi Double Cash", output_text)
        
        # Should not contain the zero balance card
        self.assertNotIn("Amazon Prime Card", output_text)
        
        # Should contain the payment dates
        self.assertIn("5th", output_text)
        self.assertIn("15th", output_text)
        self.assertIn("22nd", output_text)
        self.assertIn("28th", output_text)


class TestRichCalendarFunctions(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_cards = [
            CreditCard("Chase Freedom", 2850.00, 85.00, "15th", 19.99),
            CreditCard("Capital One Venture", 1250.00, 35.00, "28th", 17.24),
            CreditCard("Discover It", 580.00, 25.00, "5th", 15.99),
            CreditCard("Citi Double Cash", 3420.00, 105.00, "22nd", 21.99),
            CreditCard("Amazon Prime Card", 0.00, 0.00, "10th", 18.74),  # Zero balance
        ]
    
    def test_get_card_colors(self):
        """Test getting card color palette."""
        colors = get_card_colors()
        
        # Should have at least 10 colors
        self.assertGreaterEqual(len(colors), 10)
        
        # Should contain basic colors (updated for dark-theme friendly palette)
        expected_colors = ['red', 'green', 'blue', 'magenta', 'cyan']
        for color in expected_colors:
            self.assertIn(color, colors)
        
        # Should not contain problematic colors for dark terminals
        problematic_colors = ['yellow', 'bright_yellow', 'white', 'bright_white']
        for color in problematic_colors:
            self.assertNotIn(color, colors)
    
    def test_assign_card_colors(self):
        """Test color assignment to cards."""
        card_colors = assign_card_colors(self.test_cards)
        
        # Should only assign colors to cards with balances
        cards_with_balance = [card for card in self.test_cards if card.balance > 0]
        self.assertEqual(len(card_colors), len(cards_with_balance))
        
        # Should not include zero balance cards
        self.assertNotIn("Amazon Prime Card", card_colors)
        
        # Should assign unique colors (up to available colors)
        assigned_colors = list(card_colors.values())
        if len(assigned_colors) <= len(get_card_colors()):
            # If we have enough colors, all should be unique
            self.assertEqual(len(assigned_colors), len(set(assigned_colors)))
        
        # Check that all assigned colors are valid
        valid_colors = get_card_colors()
        for color in assigned_colors:
            self.assertIn(color, valid_colors)
    
    def test_assign_card_colors_many_cards(self):
        """Test color assignment when there are more cards than colors."""
        # Create more cards than available colors
        many_cards = []
        colors = get_card_colors()
        for i in range(len(colors) + 5):  # More cards than colors
            many_cards.append(CreditCard(f"Card {i}", 100.0, 10.0, "15th", 18.0))
        
        card_colors = assign_card_colors(many_cards)
        
        # Should assign colors to all cards (cycling through available colors)
        self.assertEqual(len(card_colors), len(many_cards))
        
        # Should use all available colors at least once
        assigned_colors = list(card_colors.values())
        for color in colors:
            self.assertIn(color, assigned_colors)
    
    @patch('cc_paydown_planner.Console')
    def test_show_rich_calendar_view_with_rich(self, mock_console_class):
        """Test rich calendar view when rich is available."""
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        # Test with rich available
        if RICH_AVAILABLE:
            cards_with_balance = [card for card in self.test_cards if card.balance > 0]
            show_rich_calendar_view(cards_with_balance, 7, 2024)
            
            # Should have created console and called print
            mock_console_class.assert_called_once()
            self.assertTrue(mock_console.print.called)
    
    @patch('cc_paydown_planner.RICH_AVAILABLE', False)
    @patch('cc_paydown_planner.show_calendar_view')
    def test_show_rich_calendar_view_fallback(self, mock_show_calendar):
        """Test rich calendar view fallback when rich is not available."""
        cards_with_balance = [card for card in self.test_cards if card.balance > 0]
        
        show_rich_calendar_view(cards_with_balance, 7, 2024)
        
        # Should fallback to ASCII calendar
        mock_show_calendar.assert_called_once_with(cards_with_balance, 7, 2024)
    
    def test_assign_card_colors_empty_cards(self):
        """Test color assignment with empty card list."""
        card_colors = assign_card_colors([])
        self.assertEqual(len(card_colors), 0)
        self.assertEqual(card_colors, {})
    
    def test_assign_card_colors_zero_balance_only(self):
        """Test color assignment with only zero balance cards."""
        zero_balance_cards = [
            CreditCard("Card 1", 0.00, 0.00, "15th", 18.0),
            CreditCard("Card 2", 0.00, 0.00, "28th", 18.0),
        ]
        
        card_colors = assign_card_colors(zero_balance_cards)
        self.assertEqual(len(card_colors), 0)
        self.assertEqual(card_colors, {})


class TestExportFunctions(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_cards = [
            CreditCard("Chase Freedom", 2850.00, 85.00, "15th", 19.99),
            CreditCard("Capital One Venture", 1250.00, 35.00, "28th", 17.24),
            CreditCard("Discover It", 580.00, 25.00, "5th", 15.99),
            CreditCard("Amazon Prime Card", 0.00, 0.00, "10th", 18.74),  # Zero balance
        ]
    
    def test_get_matplotlib_color(self):
        """Test matplotlib color conversion."""
        test_cases = [
            ('red', '#FF0000'),
            ('green', '#00FF00'),
            ('blue', '#0000FF'),
            ('magenta', '#FF00FF'),
            ('invalid_color', '#000000'),  # Default fallback
        ]
        
        for rich_color, expected_hex in test_cases:
            with self.subTest(rich_color=rich_color):
                result = get_matplotlib_color(rich_color)
                self.assertEqual(result, expected_hex)
    
    def test_export_payment_schedule_requirements(self):
        """Test export functionality requirements."""
        if not MATPLOTLIB_AVAILABLE:
            # Test that function raises appropriate error when matplotlib unavailable
            with self.assertRaises(ImportError):
                export_payment_schedule(self.test_cards, 3, 'pdf')
        else:
            # Test that function works when matplotlib is available
            try:
                # This should work without error
                cards_with_balance = [card for card in self.test_cards if card.balance > 0]
                filename = export_payment_schedule(cards_with_balance, 3, 'pdf', 'test_export')
                self.assertTrue(filename.endswith('.pdf'))
                
                # Clean up test file
                import os
                if os.path.exists(filename):
                    os.remove(filename)
                    
            except Exception as e:
                self.fail(f"Export function failed with matplotlib available: {e}")
    
    def test_export_filename_handling(self):
        """Test export filename handling."""
        # Test default filename generation
        if MATPLOTLIB_AVAILABLE:
            cards_with_balance = [card for card in self.test_cards if card.balance > 0]
            
            # Test default filename
            filename = export_payment_schedule(cards_with_balance, 6, 'png', None)
            self.assertTrue(filename.startswith('payment_schedule_6months'))
            self.assertTrue(filename.endswith('.png'))
            
            # Clean up
            import os
            if os.path.exists(filename):
                os.remove(filename)
    
    def test_export_with_zero_balance_cards(self):
        """Test export with cards that have zero balance."""
        if MATPLOTLIB_AVAILABLE:
            # Should only process cards with balances > 0
            filename = export_payment_schedule(self.test_cards, 3, 'pdf', 'test_zero_balance')
            self.assertTrue(filename.endswith('.pdf'))
            
            # Clean up
            import os
            if os.path.exists(filename):
                os.remove(filename)


if __name__ == '__main__':
    unittest.main()