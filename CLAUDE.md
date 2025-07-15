# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Running the Application
```bash
# Interactive mode (prompts for card details)
python cc_paydown_planner.py

# Using JSON file input
python cc_paydown_planner.py --file card-balances.json

# Using CSV file input
python cc_paydown_planner.py --file credit-cards.csv

# Specify budget via command line (skips budget prompt)
python cc_paydown_planner.py --file card-balances.json --budget 1000

# Save card data to JSON file during interactive entry
python cc_paydown_planner.py --save-to-file my-cards.json

# Short form flags
python cc_paydown_planner.py -f card-balances.json -b 1000
python cc_paydown_planner.py -s my-cards.json

# Combined options
python cc_paydown_planner.py -f cards.json -b 1000 -s updated-cards.json

# Alternative entry point
python app.py
```

### Dependencies
- Only external dependency: `click` (install with `pip install click`)
- Uses Python standard library modules: `datetime`, `typing`, `sys`, `csv`, `os`, `json`
- Development dependencies: `pre-commit`, `detect-secrets` (optional, for development)

### Development Setup

#### Pre-commit Hooks
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
- **Basic file checks**: trailing whitespace, end-of-file fixer, YAML/JSON validation
- **Black**: Python code formatting (88 character line length)
- **Flake8**: Python linting and style checks
- **isort**: Import statement sorting
- **detect-secrets**: Scans for potential secrets in code

**Secrets Detection:**
The project uses `detect-secrets` to prevent committing sensitive information. A baseline file (`.secrets.baseline`) tracks known false positives.

## Code Architecture

### Core Components

**CreditCard Class** (`cc_paydown_planner.py:15`):
- Represents a single credit card with balance, minimum payment, due date, and APR
- Automatically calculates monthly interest rate from APR

**Payment Schedule Algorithm** (`cc_paydown_planner.py:31`):
- Implements debt snowball method (pay minimums on all cards, extra payment goes to smallest balance)
- Returns detailed month-by-month payment schedule with interest calculations
- Includes safety check to prevent infinite loops (max 1000 months)

**File Input Support**:
- JSON format: Direct array of card objects or structured format with default APR
- CSV format: Supports normalized headers with leading numbers (e.g., "1   Current Balance")
- Validation and error handling for malformed data

### Key Functions

- `calculate_interest()`: Calculates monthly interest charges
- `create_payment_schedule()`: Main algorithm implementing debt snowball strategy
- `read_cards_from_json()`: Parses JSON input files with validation
- `read_cards_from_csv()`: Parses CSV input files with normalized headers
- `save_cards_to_json()`: Exports card data to JSON format for future use
- `normalize_header()`: Handles CSV headers with leading numbers
- `show_file_format_help()`: Displays supported file formats

### Data Files

- `card-balances.json`: Example JSON file with actual credit card data
- `credit-cards.csv`: Example CSV file format
- `credit-cards.xls`: Excel file (not directly supported by code)

### Application Flow

1. **Input**: Interactive prompts OR file input (JSON/CSV)
2. **Validation**: Check minimum payment requirements and data integrity
3. **Processing**: Sort cards by balance, calculate debt snowball schedule
4. **Output**: Summary statistics and optional detailed month-by-month breakdown

The debt snowball method prioritizes psychological wins by paying off smallest balances first, while maintaining minimum payments on all other cards. Extra payments are applied to the card with the lowest balance until it's paid off, then moved to the next smallest balance.

## Development History

### Session 2025-07-15: Zero Balance Support & Data Export

**Issues Fixed:**
- Fixed error when using `--budget` flag with cards that have $0 balance
- Cards with 0 balance were being rejected during JSON/CSV validation
- Missing `read_cards_from_csv()` function implementation

**New Features Added:**
- `--save-to-file` (`-s`) option to export card data to JSON files
- Interactive prompt to save card data when not using file input
- Automatic `.json` extension handling for export files
- Graceful handling of all-zero-balance scenarios

**Code Changes:**
- **JSON validation** (`cc_paydown_planner.py:194`): Changed `balance <= 0` to `balance < 0` to allow zero balances
- **CSV validation** (`cc_paydown_planner.py:271`): Same validation fix for CSV input
- **Payment schedule logic** (`cc_paydown_planner.py:34`): Filter out 0 balance cards before processing
- **Zero balance check** (`cc_paydown_planner.py:393`): Added check to exit gracefully when all cards have 0 balance
- **New function** `save_cards_to_json()`: Exports card data to JSON format
- **Enhanced CLI**: Added `--save-to-file` option to command interface
- **Fixed CSV function**: Completed missing `read_cards_from_csv()` implementation

**Updated Commands:**
```bash
# Save card data during interactive entry
python cc_paydown_planner.py --save-to-file my-cards.json

# Short form
python cc_paydown_planner.py -s my-cards.json

# Combined with other options
python cc_paydown_planner.py -f cards.json -b 1000 -s updated-cards.json
```

**Files Modified:**
- `cc_paydown_planner.py`: Core logic fixes and new export functionality
- `README.md`: Updated with comprehensive quick start guide and new features
