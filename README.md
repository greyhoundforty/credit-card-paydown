# Credit Card Debt Paydown Planner

A Python-based tool that helps create payment schedules for credit card debt using the debt snowball method. This tool calculates optimal payment strategies to help users pay off their credit cards efficiently while minimizing interest charges.

## Features

- **Debt Snowball Method**: Pays off smallest balances first for psychological wins
- **Multiple Input Formats**: Interactive mode, JSON files, or CSV files
- **Calendar View**: Visual calendar showing payment due dates with color-coded cards
- **Zero Balance Support**: Handles cards with $0 balances gracefully
- **Data Export**: Save your card data to JSON files for future use
- **Budget Planning**: Specify monthly budget via command line or interactive prompts
- **Detailed Schedules**: Month-by-month payment breakdowns with interest calculations

## Quick Start

### Option 1: Using mise (Recommended)

```bash
git clone https://github.com/yourusername/credit-card-paydown.git
cd credit-card-paydown
mise install
mise run start
```

### Option 2: Manual Setup

```bash
git clone https://github.com/yourusername/credit-card-paydown.git
cd credit-card-paydown
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install click
python cc_paydown_planner.py
```

### First Time Usage

```bash
# Interactive mode with data export
python cc_paydown_planner.py --save-to-file my-cards.json

# Use saved data file later
python cc_paydown_planner.py --file my-cards.json --budget 500
```

## CLI Usage

### Command Options

| Option | Short | Description |
|--------|-------|-------------|
| `--file` | `-f` | Load card data from CSV or JSON file |
| `--budget` | `-b` | Specify monthly budget (skips budget prompt) |
| `--save-to-file` | `-s` | Save entered card data to JSON file |
| `--calendar` | `-c` | Show calendar view with payment due dates for current month |
| `--calendar-month` | | Show calendar view for specific month (YYYY-MM format) |
| `--help` | | Show help message |

### Usage Examples

```bash
# Interactive mode (new users)
python cc_paydown_planner.py --save-to-file my-cards.json

# File input mode (returning users)
python cc_paydown_planner.py --file my-cards.json
python cc_paydown_planner.py --file credit-cards.csv

# Specify budget directly
python cc_paydown_planner.py --file my-cards.json --budget 1000

# Combined options
python cc_paydown_planner.py -f cards.json -b 1000 -s updated-cards.json

# Calendar view (current month)
python cc_paydown_planner.py --file my-cards.json --calendar

# Calendar view (specific month)
python cc_paydown_planner.py --file my-cards.json --calendar-month 2024-08
```

### File Formats

**JSON Format (Recommended):**
```json
[
  {
    "card_name": "Chase Freedom",
    "current_balance": 3500.00,
    "minimum_payment": 75.00,
    "payment_due_date": "15th",
    "apr": 19.99,
    "credit_limit": 5000.00,
    "notes": "Main rewards card"
  }
]
```

**CSV Format:**
```csv
Card Name,Current Balance,Credit Limit,Minimum Payment,Payment Due Date
Chase Freedom,3500.00,5000.00,75.00,15th
```

## Demo

![asciinema demo recording](./demo.gif)


## Dependencies

- Python 3.7 or higher
- click (required dependency)
- rich (optional, for enhanced calendar view with colors)

For detailed installation instructions, development setup, testing, and advanced usage, see [INSTALL.md](INSTALL.md).

## Support

For bug reports, feature requests, or questions:
- Open an issue in the project repository
- Check existing issues for similar problems
- Provide sample data files when reporting bugs
