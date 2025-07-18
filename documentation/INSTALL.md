# Installation & Setup Guide

This guide provides detailed installation instructions, development setup, and advanced usage information for the Credit Card Debt Paydown Planner.

## Installation Options

### Option 1: Using mise (Recommended)

[mise](https://mise.jdx.dev/) provides automatic environment management and task execution:

```bash
# Clone the repository
git clone https://github.com/yourusername/credit-card-paydown.git
cd credit-card-paydown

# mise will automatically create virtualenv and install dependencies
mise install
mise run start

# Available mise tasks
mise run install    # Install dependencies
mise run start      # Run the application
mise run test       # Run test suite
mise run demo       # Run demo with sample data
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

### Option 3: Global Installation

```bash
# Install dependencies globally (not recommended for development)
pip install click

# Clone and run
git clone https://github.com/yourusername/credit-card-paydown.git
cd credit-card-paydown
python cc_paydown_planner.py
```

## Prerequisites

- **Python 3.7 or higher** (3.12 recommended)
- **pip** (Python package installer)
- **Git** (for cloning the repository)

### Checking Your Python Version

```bash
python --version
# or
python3 --version
```

If you don't have Python installed, download it from [python.org](https://python.org).

## Dependencies

### Runtime Dependencies

- **click** - Command-line interface framework (only external dependency)

### Development Dependencies (Optional)

- **pytest** - Testing framework
- **pre-commit** - Git hooks for code quality
- **detect-secrets** - Secret detection
- **black** - Code formatting
- **isort** - Import sorting

Install development dependencies:

```bash
pip install pytest pre-commit
```

## Development Setup

### Setting Up Pre-commit Hooks

The project uses pre-commit hooks for code quality and security:

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install the hooks
pre-commit install

# Run hooks on all files (optional)
pre-commit run --all-files
```

**Configured Hooks:**
- Basic file checks (trailing whitespace, end-of-file fixer, YAML/JSON validation)
- **Black**: Python code formatting (88 character line length)
- **isort**: Import statement sorting
- **detect-secrets**: Scans for potential secrets in code

**Secrets Detection:**
The project uses `detect-secrets` to prevent committing sensitive information. A baseline file (`.secrets.baseline`) tracks known false positives.

### Testing

The project uses pytest for testing:

```bash
# Install pytest (if not already installed)
pip install pytest

# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_credit_card.py

# Run tests with coverage (if pytest-cov installed)
pytest --cov=cc_paydown_planner

# Run tests and stop on first failure
pytest -x
```

**Test Structure:**
- `tests/test_credit_card.py`: Tests for CreditCard class and calculate_interest function
- `tests/test_payment_schedule.py`: Tests for payment schedule calculation and debt snowball logic
- `tests/test_file_operations.py`: Tests for JSON/CSV file input/output operations

**Test Coverage:**
- CreditCard class initialization and methods
- Interest calculation functions
- Payment schedule generation (debt snowball method)
- File format validation and error handling
- Zero balance card handling
- Edge cases and error conditions

## Project Structure

```
credit-card-paydown/
├── cc_paydown_planner.py  # Main application with CLI
├── app.py                 # Alternative entry point
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_credit_card.py
│   ├── test_payment_schedule.py
│   └── test_file_operations.py
├── demo-cards.json        # Example data for demos
├── test-cards.json        # Sample data for testing
├── card-balances.json     # Example JSON data file
├── credit-cards.csv       # Example CSV data file
├── .mise.toml            # mise configuration
├── .pre-commit-config.yaml # Pre-commit hooks config
├── .secrets.baseline     # detect-secrets baseline
├── pytest.ini           # pytest configuration
├── CLAUDE.md             # Development instructions
├── INSTALL.md            # This file
└── README.md             # Main documentation
```

## How It Works

The debt snowball method prioritizes psychological wins by paying off smallest balances first:

1. **Input**: Enter card details interactively or load from file
2. **Validation**: Ensures minimum payments are feasible and data is valid
3. **Sorting**: Cards are sorted by balance (smallest first) for debt snowball method
4. **Calculation**: Creates month-by-month payment schedule with interest
5. **Output**: Shows payoff timeline, total interest, and optional detailed breakdown

### Debt Snowball Strategy

- Pay minimum amounts on all cards
- Apply extra payment to the card with the smallest balance
- Once a card is paid off, roll that payment into the next smallest balance
- Provides psychological wins and momentum as cards are eliminated

## Advanced Usage

### Programmatic Usage

```python
from cc_paydown_planner import CreditCard, create_payment_schedule

# Create credit cards
cards = [
    CreditCard("Card 1", 5000.00, 150.00, "15th", 18.0),
    CreditCard("Card 2", 2500.00, 75.00, "28th", 15.0)
]

# Calculate payment schedule
result = create_payment_schedule(cards, 500.00)

if 'error' not in result:
    print(f"Payoff time: {result['total_months']} months")
    print(f"Total interest: ${result['total_interest_paid']:.2f}")
```

### File Format Details

#### JSON Format (Recommended)

```json
[
  {
    "card_name": "Chase Freedom",
    "current_balance": 3500.00,
    "minimum_payment": 75.00,
    "payment_due_date": "15th",
    "apr": 19.99
  }
]
```

**Alternative JSON format with default APR:**
```json
{
  "default_apr": 18.0,
  "cards": [
    {
      "card_name": "Discover",
      "current_balance": 875.50,
      "minimum_payment": 25.00,
      "payment_due_date": "5th"
    }
  ]
}
```

#### CSV Format

```csv
Card Name,Current Balance,Credit Limit,Minimum Payment,Payment Due Date
Chase Freedom,3500.00,5000.00,75.00,15th
Capital One,1200.00,2000.00,35.00,28th
```

**JSON Field Reference:**
- `card_name` (required): Name of the credit card
- `current_balance` (required): Current balance amount
- `credit_limit` (optional): Credit limit for the card
- `minimum_payment` (required): Minimum monthly payment
- `payment_due_date` (optional): Due date, defaults to '15th'
- `apr` (optional): Annual Percentage Rate, defaults to 18.0%

## Error Handling

The tool handles various error conditions gracefully:
- Invalid file formats or missing files
- Cards with negative balances or payments
- Insufficient budget to cover minimum payments
- Malformed data in input files

## Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
# Make sure you're in the right directory and virtual environment
cd credit-card-paydown
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install click
```

**Permission errors on file operations:**
- Ensure you have write permissions in the current directory
- Check file permissions for existing JSON/CSV files

**Pre-commit hooks failing:**
```bash
# Update pre-commit hooks
pre-commit autoupdate

# Clear cache and reinstall
pre-commit clean
pre-commit install
```

**Tests failing:**
```bash
# Run tests in verbose mode to see detailed errors
pytest -v

# Run a specific test to isolate issues
pytest tests/test_credit_card.py::TestCreditCard::test_credit_card_creation -v
```

### Performance Notes

- The tool can handle hundreds of credit cards efficiently
- Payment schedules are calculated quickly even for long payoff periods
- File I/O operations use efficient streaming for large CSV files

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Set up development environment with pre-commit hooks
4. Write tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -am 'Add new feature'`)
7. Push to the branch (`git push origin feature/new-feature`)
8. Create a Pull Request

## License

This project appears to be unlicensed. Contact the project maintainers for usage permissions.
