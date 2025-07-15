# Credit Card Debt Paydown Planner

A Python-based tool that helps create payment schedules for credit card debt using the debt snowball method. This tool calculates optimal payment strategies to help users pay off their credit cards efficiently while minimizing interest charges.

## Features

- **Debt Snowball Method**: Pays off smallest balances first for psychological wins
- **Multiple Input Formats**: Interactive mode, JSON files, or CSV files
- **Zero Balance Support**: Handles cards with $0 balances gracefully
- **Data Export**: Save your card data to JSON files for future use
- **Budget Planning**: Specify monthly budget via command line or interactive prompts
- **Detailed Schedules**: Month-by-month payment breakdowns with interest calculations
- **Validation**: Ensures payments meet minimum requirements and data integrity

### How It Works

1. **Input**: Enter card details interactively or load from file
2. **Validation**: Ensures minimum payments are feasible and data is valid
3. **Sorting**: Cards are sorted by balance (smallest first) for debt snowball method
4. **Calculation**: Creates month-by-month payment schedule with interest
5. **Output**: Shows payoff timeline, total interest, and optional detailed breakdown

## Quick Start

### Option 1: Using mise (Recommended)

If you have [mise](https://mise.jdx.dev/) installed:

```bash
# Clone the repository
git clone https://github.com/yourusername/credit-card-paydown.git
cd credit-card-paydown

# mise will automatically create virtualenv and install dependencies
mise install
mise run start

# Or run directly
python cc_paydown_planner.py
```

### Option 2: Manual Virtual Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/credit-card-paydown.git
cd credit-card-paydown

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install click

# Run the application
python cc_paydown_planner.py
```

### First Time Usage

```bash
# Start with interactive mode and save your data
python cc_paydown_planner.py --save-to-file my-cards.json

# Use your saved data file later
python cc_paydown_planner.py --file my-cards.json --budget 500
```

## Usage Examples

### Interactive Mode (New Users)
```bash
# Enter card details interactively and save for later
python cc_paydown_planner.py --save-to-file my-cards.json
```

### File Input Mode (Returning Users)
```bash
# Load from JSON file
python cc_paydown_planner.py --file my-cards.json

# Load from CSV file
python cc_paydown_planner.py --file credit-cards.csv

# Specify budget directly (skips budget prompt)
python cc_paydown_planner.py --file my-cards.json --budget 1000

# Short form flags
python cc_paydown_planner.py -f my-cards.json -b 1000 -s updated-cards.json
```

### Supported File Formats

#### JSON Format (Recommended)
```json
[
  {
    "card_name": "Chase Freedom",
    "current_balance": 3500.00,
    "minimum_payment": 75.00,
    "payment_due_date": "15th",
    "apr": 19.99
  },
  {
    "card_name": "Capital One",
    "current_balance": 0,
    "minimum_payment": 0,
    "payment_due_date": "28th",
    "apr": 18.5
  }
]
```

#### CSV Format
```csv
Card Name,Current Balance,Credit Limit,Minimum Payment,Payment Due Date
Chase Freedom,3500.00,5000.00,75.00,15th
Capital One,0,2000.00,0,28th
```

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--file` | `-f` | Load card data from CSV or JSON file |
| `--budget` | `-b` | Specify monthly budget (skips budget prompt) |
| `--save-to-file` | `-s` | Save entered card data to JSON file |
| `--help` | | Show help message |


## Dependencies

- **Python 3.x** (required)
- **click** (only external dependency)
- Standard library modules: `datetime`, `typing`, `sys`, `csv`, `os`, `json`

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Install Dependencies
```bash
pip install click
```

### Error Handling

The tool handles various error conditions gracefully:
- Invalid file formats or missing files
- Cards with negative balances or payments
- Insufficient budget to cover minimum payments
- Malformed data in input files

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project appears to be unlicensed. Contact the project maintainers for usage permissions.

## Support

For bug reports, feature requests, or questions:
- Open an issue in the project repository
- Check existing issues for similar problems
- Provide sample data files when reporting bugs
