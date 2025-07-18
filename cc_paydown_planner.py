#!/usr/bin/env python3
"""
Credit Card Debt Paydown Planner
Uses the debt snowball method to create a payment schedule.
"""

import calendar
import csv
import json
import os
import re
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import click

# Try to import rich for enhanced calendar styling
try:
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class CreditCard:
    def __init__(
        self,
        name: str,
        balance: float,
        minimum_payment: float,
        due_date: str,
        apr: float = 18.0,
        credit_limit: float = 0.0,
        notes: str = "",
    ):
        self.name = name
        self.balance = balance
        self.minimum_payment = minimum_payment
        self.due_date = due_date
        self.apr = apr
        self.credit_limit = credit_limit
        self.notes = notes
        self.monthly_interest_rate = apr / 100 / 12

    def __repr__(self):
        return f"CreditCard(name='{self.name}', balance=${self.balance:.2f}, min_payment=${self.minimum_payment:.2f})"


def calculate_interest(balance: float, monthly_rate: float) -> float:
    """Calculate monthly interest charge."""
    return balance * monthly_rate


def create_payment_schedule(
    cards: List[CreditCard], total_monthly_payment: float
) -> Dict:
    """Create a detailed payment schedule using the debt snowball method."""

    # Filter out cards with 0 balance and sort by balance (smallest first)
    cards_with_balance = [card for card in cards if card.balance > 0]
    cards_sorted = sorted(cards_with_balance, key=lambda x: x.balance)

    # Calculate total minimum payments (only for cards with balances)
    total_minimums = sum(card.minimum_payment for card in cards_sorted)

    if total_monthly_payment < total_minimums:
        return {
            "error": f"Total monthly payment (${total_monthly_payment:.2f}) is less than minimum payments required (${total_minimums:.2f})"
        }

    # Extra payment available for snowball
    extra_payment = total_monthly_payment - total_minimums

    schedule = []
    month = 1
    remaining_cards = [
        {
            "name": card.name,
            "balance": card.balance,
            "minimum": card.minimum_payment,
            "apr": card.apr,
            "monthly_rate": card.monthly_interest_rate,
        }
        for card in cards_sorted
    ]

    total_interest_paid = 0

    while remaining_cards:
        month_data = {
            "month": month,
            "payments": [],
            "balances_after": [],
            "total_paid": 0,
            "interest_paid": 0,
        }

        # Apply minimum payments to all cards
        for card in remaining_cards:
            interest_charge = calculate_interest(card["balance"], card["monthly_rate"])
            payment = card["minimum"]
            principal = payment - interest_charge

            if principal < 0:
                principal = 0
                payment = interest_charge

            new_balance = max(0, card["balance"] - principal)

            month_data["payments"].append(
                {
                    "card": card["name"],
                    "payment": payment,
                    "interest": interest_charge,
                    "principal": principal,
                    "balance_before": card["balance"],
                    "balance_after": new_balance,
                }
            )

            card["balance"] = new_balance
            month_data["total_paid"] += payment
            month_data["interest_paid"] += interest_charge

        # Apply extra payment to the card with smallest balance
        if extra_payment > 0 and remaining_cards:
            target_card = remaining_cards[0]  # Smallest balance

            if target_card["balance"] > 0:
                extra_applied = min(extra_payment, target_card["balance"])
                target_card["balance"] -= extra_applied

                # Update the payment record for this card
                for payment_record in month_data["payments"]:
                    if payment_record["card"] == target_card["name"]:
                        payment_record["payment"] += extra_applied
                        payment_record["principal"] += extra_applied
                        payment_record["balance_after"] = target_card["balance"]
                        break

                month_data["total_paid"] += extra_applied

        # Update balances after payments
        for card in remaining_cards:
            month_data["balances_after"].append(
                {"card": card["name"], "balance": card["balance"]}
            )

        # Remove paid-off cards
        remaining_cards = [card for card in remaining_cards if card["balance"] > 0]

        total_interest_paid += month_data["interest_paid"]
        schedule.append(month_data)
        month += 1

        # Safety check to prevent infinite loops
        if month > 1000:
            return {
                "error": "Payment schedule exceeds 1000 months. Please check your inputs."
            }

    return {
        "schedule": schedule,
        "total_months": len(schedule),
        "total_interest_paid": total_interest_paid,
        "total_amount_paid": sum(month["total_paid"] for month in schedule),
    }


def normalize_header(header: str) -> str:
    """Normalize CSV header by removing leading numbers and extra whitespace."""
    import re

    # Remove leading numbers and whitespace (e.g., "1   Current Balance" -> "Current Balance")
    normalized = re.sub(r"^\d+\s*", "", header.strip())
    return normalized


def parse_due_date(due_date: str) -> int:
    """Extract day number from due date string (e.g., '15th' -> 15)."""
    # Remove common suffixes and extract numeric part
    cleaned = re.sub(r'(st|nd|rd|th)\b', '', due_date.lower().strip())
    match = re.search(r'\d+', cleaned)
    if match:
        day = int(match.group())
        # Validate day range (1-31)
        if 1 <= day <= 31:
            return day
    # Return 15 as default if parsing fails
    return 15


def show_calendar_view(cards: List[CreditCard], month: int = None, year: int = None) -> None:
    """Display calendar view with payment due dates highlighted."""
    # Use current month/year if not specified
    if month is None or year is None:
        now = datetime.now()
        month = month or now.month
        year = year or now.year
    
    # Validate month/year ranges
    if not (1 <= month <= 12):
        click.echo("❌ Invalid month. Must be between 1 and 12.")
        return
    if not (1900 <= year <= 2100):
        click.echo("❌ Invalid year. Must be between 1900 and 2100.")
        return
    
    # Parse payment due dates from cards
    payment_dates = {}  # {day: [card_info]}
    
    for card in cards:
        if card.balance > 0:  # Only include cards with balances
            day = parse_due_date(card.due_date)
            if day not in payment_dates:
                payment_dates[day] = []
            payment_dates[day].append({
                'name': card.name,
                'payment': card.minimum_payment,
                'balance': card.balance
            })
    
    # Display calendar header
    month_name = calendar.month_name[month]
    click.echo(f"\n🗓️  PAYMENT CALENDAR - {month_name} {year}")
    click.echo("═" * 50)
    
    if not payment_dates:
        click.echo("No payment due dates found for cards with balances.")
        return
    
    # Generate calendar using Python's calendar module
    cal = calendar.monthcalendar(year, month)
    
    # Create header
    click.echo(f"      {month_name} {year}")
    click.echo("Mo Tu We Th Fr Sa Su")
    
    # Display calendar with highlighted payment dates
    for week in cal:
        week_str = ""
        for day in week:
            if day == 0:
                week_str += "   "  # Empty cell
            else:
                if day in payment_dates:
                    # Highlight payment due dates
                    if day < 10:
                        week_str += f" {day}*"
                    else:
                        week_str += f"{day}*"
                else:
                    if day < 10:
                        week_str += f" {day} "
                    else:
                        week_str += f"{day} "
        click.echo(week_str)
    
    # Display payment due dates legend
    click.echo("\nPayment Due Dates:")
    click.echo("─" * 20)
    
    # Sort by day for display
    for day in sorted(payment_dates.keys()):
        day_suffix = get_day_suffix(day)
        click.echo(f"• {day}{day_suffix}:")
        
        total_due = 0
        for card_info in payment_dates[day]:
            click.echo(f"  - {card_info['name']}: ${card_info['payment']:.2f} (Balance: ${card_info['balance']:,.2f})")
            total_due += card_info['payment']
        
        if len(payment_dates[day]) > 1:
            click.echo(f"  Total due: ${total_due:.2f}")
        click.echo()


def get_day_suffix(day: int) -> str:
    """Get the appropriate suffix for a day number (e.g., 1st, 2nd, 3rd, 4th)."""
    if 10 <= day % 100 <= 20:
        return "th"
    else:
        return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


def parse_calendar_date(date_str: str) -> Tuple[int, int]:
    """Parse calendar date string in format YYYY-MM."""
    try:
        parts = date_str.split('-')
        if len(parts) != 2:
            raise ValueError("Invalid format")
        
        year = int(parts[0])
        month = int(parts[1])
        
        if not (1 <= month <= 12):
            raise ValueError("Invalid month")
        if not (1900 <= year <= 2100):
            raise ValueError("Invalid year")
            
        return year, month
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM (e.g., 2024-07): {e}")


def get_card_colors() -> List[str]:
    """Get a list of distinct colors for credit cards optimized for dark terminals."""
    return [
        # Primary colors that work well with white text on dark backgrounds
        'red', 'green', 'blue', 'magenta', 'cyan',
        'bright_red', 'bright_green', 'bright_blue', 'bright_magenta', 'bright_cyan',
        # Additional colors for better visibility
        'purple', 'orange', 'grey', 'bright_black',
        # Darker shades that still provide good contrast
        'dark_red', 'dark_green', 'dark_blue', 'dark_magenta', 'dark_cyan'
    ]


def assign_card_colors(cards: List[CreditCard]) -> Dict[str, str]:
    """Assign unique colors to each credit card."""
    colors = get_card_colors()
    card_colors = {}
    
    # Only assign colors to cards with balances
    cards_with_balance = [card for card in cards if card.balance > 0]
    
    for i, card in enumerate(cards_with_balance):
        # Cycle through colors if there are more cards than colors
        color_index = i % len(colors)
        card_colors[card.name] = colors[color_index]
    
    return card_colors


def show_rich_calendar_view(cards: List[CreditCard], month: int = None, year: int = None) -> None:
    """Display enhanced calendar view with colored dates using rich library."""
    if not RICH_AVAILABLE:
        # Fallback to ASCII calendar if rich is not available
        show_calendar_view(cards, month, year)
        return
    
    console = Console()
    
    # Use current month/year if not specified
    if month is None or year is None:
        now = datetime.now()
        month = month or now.month
        year = year or now.year
    
    # Validate month/year ranges
    if not (1 <= month <= 12):
        console.print("[red]❌ Invalid month. Must be between 1 and 12.[/red]")
        return
    if not (1900 <= year <= 2100):
        console.print("[red]❌ Invalid year. Must be between 1900 and 2100.[/red]")
        return
    
    # Parse payment due dates from cards and assign colors
    payment_dates = {}  # {day: [card_info]}
    card_colors = assign_card_colors(cards)
    
    for card in cards:
        if card.balance > 0:  # Only include cards with balances
            day = parse_due_date(card.due_date)
            if day not in payment_dates:
                payment_dates[day] = []
            payment_dates[day].append({
                'name': card.name,
                'payment': card.minimum_payment,
                'balance': card.balance,
                'color': card_colors[card.name]
            })
    
    # Display calendar header
    month_name = calendar.month_name[month]
    console.print(f"\n🗓️  [bold magenta]PAYMENT CALENDAR - {month_name} {year}[/bold magenta]")
    console.print("═" * 50)
    
    if not payment_dates:
        console.print("[yellow]No payment due dates found for cards with balances.[/yellow]")
        return
    
    # Create rich calendar table
    table = Table(title=f"{month_name} {year}", show_header=True, header_style="bold cyan")
    
    # Add day headers
    for day in ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']:
        table.add_column(day, width=4, justify='center')
    
    # Generate calendar using Python's calendar module
    cal = calendar.monthcalendar(year, month)
    
    # Add calendar weeks with colored dates
    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append('')  # Empty cell for days outside the month
            elif day in payment_dates:
                # Color the date based on card(s) due
                cards_due = payment_dates[day]
                if len(cards_due) == 1:
                    # Single card due - use its color
                    color = cards_due[0]['color']
                    row.append(f'[white on {color}] {day:2d} [/white on {color}]')
                else:
                    # Multiple cards due - use first card's color with indicator
                    color = cards_due[0]['color']
                    row.append(f'[white on {color}] {day:2d}*[/white on {color}]')
            else:
                # Regular date
                row.append(f' {day:2d} ')
        table.add_row(*row)
    
    console.print(table)
    
    # Display color legend
    console.print("\n[bold cyan]Color Legend:[/bold cyan]")
    console.print("─" * 20)
    
    for card_name, color in card_colors.items():
        console.print(f"[white on {color}] {card_name} [/white on {color}]")
    
    # Display payment due dates details
    console.print("\n[bold cyan]Payment Due Dates:[/bold cyan]")
    console.print("─" * 20)
    
    # Sort by day for display
    for day in sorted(payment_dates.keys()):
        day_suffix = get_day_suffix(day)
        console.print(f"[bold]• {day}{day_suffix}:[/bold]")
        
        total_due = 0
        for card_info in payment_dates[day]:
            color = card_info['color']
            console.print(f"  - [{color}]{card_info['name']}[/{color}]: ${card_info['payment']:.2f} (Balance: ${card_info['balance']:,.2f})")
            total_due += card_info['payment']
        
        if len(payment_dates[day]) > 1:
            console.print(f"  [bold]Total due: ${total_due:.2f}[/bold]")
        console.print()


def read_cards_from_json(file_path: str, default_apr: float = 18.0) -> List[CreditCard]:
    """Read credit card data from JSON file."""
    cards = []

    try:
        with open(file_path, "r", encoding="utf-8") as jsonfile:
            data = json.load(jsonfile)

            # Support two formats:
            # 1. Direct array: [{"card_name": "...", ...}, ...]
            # 2. Object with cards array: {"cards": [...], "default_apr": 18.0}

            cards_data = []
            file_default_apr = default_apr

            if isinstance(data, list):
                # Format 1: Direct array
                cards_data = data
            elif isinstance(data, dict) and "cards" in data:
                # Format 2: Object with cards array
                cards_data = data["cards"]
                if "default_apr" in data:
                    file_default_apr = float(data["default_apr"])
            else:
                raise ValueError(
                    "JSON must be either an array of cards or an object with a 'cards' array"
                )

            if not cards_data:
                raise ValueError("No credit card data found in JSON file")

            click.echo(f"📋 Found {len(cards_data)} cards in JSON file")
            if file_default_apr != default_apr:
                click.echo(f"🔧 Using APR from file: {file_default_apr}%")

            for card_num, card_data in enumerate(cards_data, start=1):
                try:
                    # Validate required fields
                    required_fields = [
                        "card_name",
                        "current_balance",
                        "minimum_payment",
                    ]
                    missing_fields = [
                        field for field in required_fields if field not in card_data
                    ]
                    if missing_fields:
                        raise ValueError(
                            f"Missing required fields: {', '.join(missing_fields)}"
                        )

                    # Extract and validate data
                    name = str(card_data["card_name"]).strip()
                    if not name:
                        raise ValueError("card_name cannot be empty")

                    balance = float(card_data["current_balance"])
                    if balance < 0:
                        raise ValueError(
                            "current_balance must be greater than or equal to 0"
                        )

                    min_payment = float(card_data["minimum_payment"])
                    if min_payment < 0:
                        raise ValueError(
                            "minimum_payment must be greater than or equal to 0"
                        )
                    if balance > 0 and min_payment > balance:
                        raise ValueError(
                            "minimum_payment cannot be greater than current_balance"
                        )

                    # Optional fields
                    due_date = str(card_data.get("payment_due_date", "15th")).strip()
                    if not due_date:
                        due_date = "15th"

                    # APR can be specified per card or use file/default APR
                    apr = float(card_data.get("apr", file_default_apr))

                    # Credit limit is optional
                    credit_limit = float(card_data.get("credit_limit", 0.0))

                    # Notes is optional
                    notes = str(card_data.get("notes", "")).strip()

                    card = CreditCard(
                        name, balance, min_payment, due_date, apr, credit_limit, notes
                    )
                    cards.append(card)

                except (ValueError, KeyError, TypeError) as e:
                    click.echo(
                        f"❌ Error in card #{card_num} ({card_data.get('card_name', 'Unknown')}): {e}"
                    )
                    continue

    except FileNotFoundError:
        raise click.ClickException(f"File not found: {file_path}")
    except PermissionError:
        raise click.ClickException(f"Permission denied reading file: {file_path}")
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON format: {e}")
    except Exception as e:
        raise click.ClickException(f"Error reading JSON file: {e}")

    if not cards:
        raise click.ClickException("No valid credit card data found in JSON file")

    return cards


def read_cards_from_csv(file_path: str, default_apr: float = 18.0) -> List[CreditCard]:
    """Read credit card data from CSV file."""
    cards = []

    try:
        with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            # Normalize headers and create mapping
            original_headers = reader.fieldnames or []
            normalized_headers = {normalize_header(h): h for h in original_headers}

            # Debug: Show what headers were found
            click.echo(f"📋 Found CSV headers: {', '.join(original_headers)}")
            click.echo(f"🔧 Normalized headers: {', '.join(normalized_headers.keys())}")

            # Check if required headers exist after normalization
            required_headers = [
                "Card Name",
                "Current Balance",
                "Credit Limit",
                "Minimum Payment",
                "Payment Due Date",
            ]
            optional_headers = [
                "Notes",
            ]
            missing_headers = [
                h for h in required_headers if h not in normalized_headers
            ]

            if missing_headers:
                click.echo(
                    f"❌ Missing required headers after normalization: {', '.join(missing_headers)}"
                )
                click.echo(f"📝 Required headers: {', '.join(required_headers)}")
                click.echo(
                    f"🔍 Available normalized headers: {', '.join(normalized_headers.keys())}"
                )
                raise ValueError(
                    f"Missing required CSV headers: {', '.join(missing_headers)}"
                )

            for row_num, row in enumerate(
                reader, start=2
            ):  # Start at 2 since row 1 is headers
                try:
                    # Use original header names to access data
                    name_col = normalized_headers["Card Name"]
                    balance_col = normalized_headers["Current Balance"]
                    credit_limit_col = normalized_headers["Credit Limit"]
                    min_payment_col = normalized_headers["Minimum Payment"]
                    due_date_col = normalized_headers["Payment Due Date"]

                    # Validate and convert data
                    name = row[name_col].strip()
                    if not name:
                        raise ValueError(f"Card Name cannot be empty")

                    balance = float(row[balance_col])
                    if balance < 0:
                        raise ValueError(
                            f"Current Balance must be greater than or equal to 0"
                        )

                    # Credit limit is read but not used in calculations (for future enhancement)
                    credit_limit = (
                        float(row[credit_limit_col])
                        if row[credit_limit_col].strip()
                        else 0
                    )

                    min_payment = float(row[min_payment_col])
                    if min_payment < 0:
                        raise ValueError(
                            f"Minimum Payment must be greater than or equal to 0"
                        )
                    if balance > 0 and min_payment > balance:
                        raise ValueError(
                            f"Minimum Payment cannot be greater than Current Balance"
                        )

                    due_date = row[due_date_col].strip()
                    if not due_date:
                        due_date = "15th"  # Default due date

                    # Notes is optional
                    notes = ""
                    if "Notes" in normalized_headers:
                        notes_col = normalized_headers["Notes"]
                        notes = row[notes_col].strip()

                    card = CreditCard(
                        name,
                        balance,
                        min_payment,
                        due_date,
                        default_apr,
                        credit_limit,
                        notes,
                    )
                    cards.append(card)

                except (ValueError, KeyError) as e:
                    click.echo(f"❌ Error in CSV row {row_num}: {e}")
                    continue

    except FileNotFoundError:
        raise click.ClickException(f"File not found: {file_path}")
    except PermissionError:
        raise click.ClickException(f"Permission denied reading file: {file_path}")
    except Exception as e:
        raise click.ClickException(f"Error reading CSV file: {e}")

    if not cards:
        raise click.ClickException("No valid credit card data found in CSV file")

    return cards


@click.command()
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    help="CSV file containing credit card details",
)
@click.option(
    "--budget", "-b", type=float, help="Monthly budget for credit card payments"
)
@click.option(
    "--save-to-file",
    "-s",
    type=str,
    help="Save entered card data to JSON file (e.g., card-balances.json)",
)
@click.option(
    "--calendar",
    "-c",
    is_flag=True,
    help="Show calendar view with payment due dates for current month",
)
@click.option(
    "--calendar-month",
    type=str,
    default=None,
    help="Show calendar view for specific month (YYYY-MM format)",
)
def main(file, budget, save_to_file, calendar, calendar_month):
    """Credit Card Debt Paydown Planner using the Debt Snowball Method."""

    click.echo("🏦 Credit Card Debt Paydown Planner")
    click.echo("=" * 40)
    click.echo(
        "This tool helps you create a payment plan using the debt snowball method."
    )
    click.echo("(Paying off smallest balances first)")
    if not file:
        click.echo(
            "💡 You can also use --file option to load data from CSV or JSON files"
        )
    click.echo()

    cards = []

    # Handle file input or interactive input
    if file:
        file_ext = os.path.splitext(file)[1].lower()
        click.echo(f"📁 Reading credit card data from: {file}")

        try:
            if file_ext == ".json":
                cards = read_cards_from_json(file)
            elif file_ext == ".csv":
                cards = read_cards_from_csv(file)
            else:
                raise click.ClickException(
                    f"Unsupported file type: {file_ext}. Supported types: .csv, .json"
                )

            click.echo(f"✅ Successfully loaded {len(cards)} credit cards from file")
        except click.ClickException:
            raise
        except Exception as e:
            raise click.ClickException(f"Unexpected error reading file: {e}")
    else:
        # Interactive input mode (existing code)
        while True:
            click.echo(f"\n📝 Enter details for credit card #{len(cards) + 1}:")

            # Get card name
            name = click.prompt("Card name", type=str)

            # Get credit limit
            credit_limit = click.prompt("Credit limit", type=float, default=0.0)

            # Get current balance
            while True:
                try:
                    balance = click.prompt("Current balance", type=float)
                    if balance < 0:
                        click.echo("Balance must be greater than or equal to 0.")
                        continue
                    if credit_limit > 0 and balance > credit_limit:
                        click.echo("Current balance cannot exceed credit limit.")
                        continue
                    break
                except click.BadParameter:
                    click.echo("Please enter a valid number.")

            # Get minimum payment
            while True:
                try:
                    min_payment = click.prompt("Minimum payment", type=float)
                    if min_payment < 0:
                        click.echo(
                            "Minimum payment must be greater than or equal to 0."
                        )
                        continue
                    if balance > 0 and min_payment > balance:
                        click.echo("Minimum payment cannot be greater than balance.")
                        continue
                    break
                except click.BadParameter:
                    click.echo("Please enter a valid number.")

            # Get due date
            due_date = click.prompt(
                "Payment due date (e.g., 15th of month)", type=str, default="15th"
            )

            # Get APR (optional)
            apr = click.prompt("Annual Percentage Rate (APR)", type=float, default=18.0)

            # Get notes (optional)
            notes = click.prompt(
                "Notes (optional)", type=str, default="", show_default=False
            )

            # Create card object
            card = CreditCard(
                name, balance, min_payment, due_date, apr, credit_limit, notes
            )
            cards.append(card)

            # Display card summary
            available_credit = credit_limit - balance if credit_limit > 0 else 0
            click.echo(
                f"\n✅ Added: {name} - Balance: ${balance:.2f}, Min Payment: ${min_payment:.2f}, APR: {apr}%"
            )
            if credit_limit > 0:
                click.echo(
                    f"   Credit Limit: ${credit_limit:.2f}, Available Credit: ${available_credit:.2f}"
                )
            if notes:
                click.echo(f"   Notes: {notes}")

            # Ask if user wants to add another card
            if not click.confirm("\nAdd another credit card?"):
                break

    if not cards:
        click.echo("No credit cards entered. Exiting.")
        sys.exit(1)

    # Handle calendar view
    if calendar or calendar_month:
        try:
            if calendar_month:
                # Parse specific month/year
                year, month = parse_calendar_date(calendar_month)
                show_rich_calendar_view(cards, month, year)
            else:
                # Show current month calendar
                show_rich_calendar_view(cards)
        except ValueError as e:
            click.echo(f"❌ Calendar error: {e}")
            sys.exit(1)
        # Exit after showing calendar (calendar-only mode)
        return

    # Filter out cards with 0 balance for payment calculations
    cards_with_balance = [card for card in cards if card.balance > 0]

    if not cards_with_balance:
        click.echo(
            "\n🎉 All credit cards have a $0 balance! No payment schedule needed."
        )
        sys.exit(0)

    # Display summary of all cards
    click.echo("\n" + "=" * 50)
    click.echo("📊 CREDIT CARD SUMMARY")
    click.echo("=" * 50)

    total_balance = sum(card.balance for card in cards)
    total_minimums = sum(card.minimum_payment for card in cards_with_balance)

    for i, card in enumerate(sorted(cards, key=lambda x: x.balance), 1):
        click.echo(f"{i}. {card.name}:")
        click.echo(f"   Balance: ${card.balance:,.2f}")
        click.echo(f"   Minimum Payment: ${card.minimum_payment:.2f}")
        click.echo(f"   APR: {card.apr}%")
        if card.credit_limit > 0:
            available_credit = card.credit_limit - card.balance
            click.echo(f"   Credit Limit: ${card.credit_limit:,.2f}")
            click.echo(f"   Available Credit: ${available_credit:,.2f}")

    click.echo(f"\nTotal Debt: ${total_balance:,.2f}")
    click.echo(f"Total Minimum Payments: ${total_minimums:.2f}")

    # Get total monthly payment amount
    click.echo("\n" + "=" * 50)
    click.echo("💰 PAYMENT PLANNING")
    click.echo("=" * 50)

    if budget is not None:
        # Validate provided budget
        if budget < total_minimums:
            click.echo(
                f"❌ Error: Budget (${budget:.2f}) is less than minimum payments required (${total_minimums:.2f})"
            )
            sys.exit(1)
        monthly_payment = budget
        click.echo(f"💵 Using provided budget: ${monthly_payment:.2f}")
    else:
        # Interactive budget input (existing behavior)
        while True:
            try:
                monthly_payment = click.prompt(
                    f"How much can you pay toward credit cards each month?\n(Minimum required: ${total_minimums:.2f})",
                    type=float,
                )
                if monthly_payment < total_minimums:
                    click.echo(
                        f"Amount must be at least ${total_minimums:.2f} to cover minimum payments."
                    )
                    continue
                break
            except click.BadParameter:
                click.echo("Please enter a valid number.")

    # Calculate payment schedule
    click.echo("\n🔄 Calculating payment schedule...")
    result = create_payment_schedule(cards_with_balance, monthly_payment)

    if "error" in result:
        click.echo(f"❌ Error: {result['error']}")
        sys.exit(1)

    # Display results
    schedule = result["schedule"]

    click.echo("\n" + "=" * 80)
    click.echo("📅 DEBT PAYOFF SCHEDULE (Debt Snowball Method)")
    click.echo("=" * 80)

    click.echo(
        f"🎯 Strategy: Pay minimums on all cards, extra payment goes to smallest balance"
    )
    click.echo(f"💵 Monthly Budget: ${monthly_payment:.2f}")
    click.echo(
        f"📆 Payoff Time: {result['total_months']} months ({result['total_months']//12} years, {result['total_months']%12} months)"
    )
    click.echo(f"💸 Total Interest Paid: ${result['total_interest_paid']:.2f}")
    click.echo(f"💰 Total Amount Paid: ${result['total_amount_paid']:,.2f}")

    if click.confirm("\nShow detailed month-by-month schedule?"):
        click.echo("\n" + "=" * 100)
        click.echo("DETAILED PAYMENT SCHEDULE")
        click.echo("=" * 100)

        for month_data in schedule:
            click.echo(f"\n📅 Month {month_data['month']}:")
            click.echo(
                f"   Total Paid: ${month_data['total_paid']:.2f} | Interest: ${month_data['interest_paid']:.2f}"
            )

            for payment in month_data["payments"]:
                if payment["payment"] > 0:
                    click.echo(
                        f"   • {payment['card']}: ${payment['payment']:.2f} "
                        f"(Interest: ${payment['interest']:.2f}, Principal: ${payment['principal']:.2f}) "
                        f"→ Balance: ${payment['balance_after']:,.2f}"
                    )

            # Show remaining balances
            remaining_cards = [
                b for b in month_data["balances_after"] if b["balance"] > 0
            ]
            if remaining_cards:
                click.echo("   Remaining balances:")
                for balance_info in remaining_cards:
                    # Find the original card to get credit limit
                    original_card = next(
                        (c for c in cards if c.name == balance_info["card"]), None
                    )
                    if original_card and original_card.credit_limit > 0:
                        available_credit = (
                            original_card.credit_limit - balance_info["balance"]
                        )
                        click.echo(
                            f"     - {balance_info['card']}: ${balance_info['balance']:,.2f} "
                            f"(Available Credit: ${available_credit:,.2f})"
                        )
                    else:
                        click.echo(
                            f"     - {balance_info['card']}: ${balance_info['balance']:,.2f}"
                        )
            else:
                click.echo("   🎉 All cards paid off!")

    click.echo(
        f"\n🎉 Congratulations! You'll be debt-free in {result['total_months']} months!"
    )
    click.echo(
        "💡 Pro tip: Consider putting the money you were paying toward debt into savings once you're done!"
    )

    # Show file format help if user used interactive mode
    if not file:
        if click.confirm(
            "\n💾 Would you like to see the CSV/JSON format for future use?"
        ):
            show_file_format_help()

    # Save card data to file if requested or if user entered data interactively
    if save_to_file and not file:
        save_cards_to_json(cards, save_to_file)
    elif not file and not save_to_file:
        # Offer to save if user entered data interactively
        if click.confirm(
            "\n💾 Would you like to save this card data to a JSON file for future use?"
        ):
            filename = click.prompt(
                "Enter filename (e.g., card-balances.json)",
                default="card-balances.json",
            )
            save_cards_to_json(cards, filename)


def save_cards_to_json(cards: List[CreditCard], filename: str) -> None:
    """Save credit card data to JSON file."""
    try:
        cards_data = []
        for card in cards:
            card_data = {
                "card_name": card.name,
                "current_balance": card.balance,
                "minimum_payment": card.minimum_payment,
                "payment_due_date": card.due_date,
                "apr": card.apr,
                "credit_limit": card.credit_limit,
                "notes": card.notes,
            }
            cards_data.append(card_data)

        # Ensure filename has .json extension
        if not filename.lower().endswith(".json"):
            filename += ".json"

        with open(filename, "w", encoding="utf-8") as jsonfile:
            json.dump(cards_data, jsonfile, indent=2)

        click.echo(f"✅ Credit card data saved to: {filename}")
        click.echo(
            f"💡 You can use this file with: python cc_paydown_planner.py --file {filename}"
        )

    except PermissionError:
        click.echo(f"❌ Permission denied writing to file: {filename}")
    except Exception as e:
        click.echo(f"❌ Error saving file: {e}")


def show_file_format_help():
    """Display help for CSV and JSON file formats."""
    click.echo("\n" + "=" * 60)
    click.echo("📄 SUPPORTED FILE FORMATS")
    click.echo("=" * 60)

    # JSON Format (recommended)
    click.echo("🌟 JSON FORMAT (Recommended):")
    click.echo("Create a .json file with this structure:")
    click.echo()
    click.echo(
        json.dumps(
            [
                {
                    "card_name": "Chase Freedom",
                    "current_balance": 3500.00,
                    "credit_limit": 5000.00,
                    "minimum_payment": 75.00,
                    "payment_due_date": "15th",
                    "apr": 19.99,
                    "notes": "Main rewards card",
                },
                {
                    "card_name": "Capital One",
                    "current_balance": 1200.00,
                    "credit_limit": 2000.00,
                    "minimum_payment": 35.00,
                    "payment_due_date": "28th",
                    "notes": "",
                },
            ],
            indent=2,
        )
    )
    click.echo()
    click.echo("📝 Alternative JSON format with default APR:")
    click.echo(
        json.dumps(
            {
                "default_apr": 18.0,
                "cards": [
                    {
                        "card_name": "Discover",
                        "current_balance": 875.50,
                        "credit_limit": 1500.00,
                        "minimum_payment": 25.00,
                        "payment_due_date": "5th",
                        "notes": "Cashback card",
                    }
                ],
            },
            indent=2,
        )
    )
    click.echo()

    # CSV Format
    click.echo("📊 CSV FORMAT:")
    click.echo("Create a .csv file with these headers:")
    click.echo()
    click.echo(
        "Card Name,Current Balance,Credit Limit,Minimum Payment,Payment Due Date,Notes"
    )
    click.echo("Chase Freedom,3500.00,5000.00,75.00,15th,Main rewards card")
    click.echo("Capital One,1200.00,2000.00,35.00,28th,")
    click.echo("Discover,875.50,1500.00,25.00,5th,Cashback card")
    click.echo()

    # Usage examples
    click.echo("🚀 USAGE:")
    click.echo("  python cc_paydown_planner.py --file cards.json")
    click.echo("  python cc_paydown_planner.py --file cards.csv")
    click.echo("  python cc_paydown_planner.py -f cards.json")
    click.echo("  python cc_paydown_planner.py --save-to-file my-cards.json")
    click.echo("  python cc_paydown_planner.py -s my-cards.json")

    click.echo()
    click.echo("📋 JSON FIELD REFERENCE:")
    click.echo("  • card_name (required): Name of the credit card")
    click.echo("  • current_balance (required): Current balance amount")
    click.echo("  • credit_limit (optional): Credit limit for the card, defaults to 0")
    click.echo("  • minimum_payment (required): Minimum monthly payment")
    click.echo("  • payment_due_date (optional): Due date, defaults to '15th'")
    click.echo("  • apr (optional): Annual Percentage Rate, defaults to 18.0%")
    click.echo(
        "  • notes (optional): Additional notes about the card, defaults to empty string"
    )


if __name__ == "__main__":
    main()
