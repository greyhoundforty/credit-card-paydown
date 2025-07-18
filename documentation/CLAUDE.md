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

# Calendar view - show payment due dates for current month
python cc_paydown_planner.py --file card-balances.json --calendar

# Calendar view - show payment due dates for specific month
python cc_paydown_planner.py --file card-balances.json --calendar-month 2024-08

# Short form calendar
python cc_paydown_planner.py -f card-balances.json -c

# Export payment schedule calendar (PDF format)
python cc_paydown_planner.py --file card-balances.json --export 12
python cc_paydown_planner.py --file card-balances.json --export 6 --export-format png

# Export with custom filename
python cc_paydown_planner.py --file card-balances.json --export 3 --export-filename my_schedule

# Alternative entry point
python app.py
```

### Dependencies
- **Required dependencies**: 
  - `click` (install with `pip install click`)
- **Optional dependencies**:
  - `rich` (install with `pip install rich`) - for enhanced calendar view with colors
  - `matplotlib` (install with `pip install matplotlib`) - for PDF/PNG export functionality
- Uses Python standard library modules: `datetime`, `typing`, `sys`, `csv`, `os`, `json`, `calendar`, `re`
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

#### Testing

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
- `tests/test_calendar.py`: Tests for calendar view functionality and date parsing

**Test Coverage:**
- CreditCard class initialization and methods
- Interest calculation functions
- Payment schedule generation (debt snowball method)
- File format validation and error handling
- Zero balance card handling
- Calendar view functionality and date parsing
- Edge cases and error conditions

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
- `show_calendar_view()`: Displays ASCII calendar with payment due dates highlighted
- `parse_due_date()`: Extracts day numbers from due date strings (e.g., "15th" → 15)
- `parse_calendar_date()`: Parses calendar date strings in YYYY-MM format
- `get_day_suffix()`: Returns appropriate suffix for day numbers (1st, 2nd, 3rd, etc.)

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

## Calendar View Feature

The calendar view feature provides a visual representation of payment due dates for financial planning purposes.

### Usage
```bash
# Show calendar for current month
python cc_paydown_planner.py --file cards.json --calendar

# Show calendar for specific month
python cc_paydown_planner.py --file cards.json --calendar-month 2024-08

# Short form
python cc_paydown_planner.py -f cards.json -c
```

### Features
- **ASCII Calendar Display**: Uses Python's built-in `calendar` module
- **Payment Date Highlighting**: Due dates marked with asterisks (e.g., `15*`)
- **Card Information**: Shows card names, minimum payments, and balances
- **Zero Balance Filtering**: Only displays cards with outstanding balances
- **Date Parsing**: Supports various due date formats ("15th", "28th", "5th", etc.)
- **Error Handling**: Validates month/year ranges and date formats

### Example Output
```
🗓️  PAYMENT CALENDAR - July 2024
══════════════════════════════════════════════════
      July 2024
Mo Tu We Th Fr Sa Su
 1  2  3  4  5* 6  7
 8  9 10 11 12 13 14
15*16 17 18 19 20 21
22*23 24 25 26 27 28
29*30 31

Payment Due Dates:
────────────────────
• 5th:
  - Discover It: $25.00 (Balance: $580.00)

• 15th:
  - Chase Freedom: $85.00 (Balance: $2,850.00)

• 22nd:
  - Citi Double Cash: $105.00 (Balance: $3,420.00)
```

### Technical Implementation
- **Dependencies**: Uses Python standard library (`calendar`, `datetime`, `re`) + optional `rich` for enhanced styling
- **Date Parsing**: Regex-based extraction of day numbers from due date strings
- **Validation**: Month (1-12) and year (1900-2100) range validation
- **Formatting**: Proper day suffix generation (1st, 2nd, 3rd, 4th, etc.)
- **Color System**: Automatic color assignment to credit cards with rich styling
- **Fallback**: Graceful fallback to ASCII calendar if rich is not available

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

### Session 2025-07-18: Calendar View Implementation

**New Features Added:**
- **Calendar View**: Visual representation of payment due dates in ASCII calendar format
- **CLI Options**: `--calendar` flag for current month, `--calendar-month YYYY-MM` for specific months
- **Payment Date Highlighting**: Due dates marked with asterisks in calendar display
- **Smart Filtering**: Only shows cards with outstanding balances in calendar view
- **Comprehensive Testing**: Full test suite for calendar functionality

**Technical Implementation:**
- **Date Parsing**: Regex-based extraction from due date strings ("15th" → 15)
- **Calendar Generation**: Uses Python's built-in `calendar` module for ASCII display
- **Error Handling**: Validates month/year ranges and date formats
- **Zero Dependencies**: Implementation uses only Python standard library

**Code Changes:**
- **New Functions**:
  - `show_calendar_view()`: Main calendar display function
  - `parse_due_date()`: Extract day numbers from due date strings
  - `parse_calendar_date()`: Parse YYYY-MM format dates
  - `get_day_suffix()`: Generate proper day suffixes (1st, 2nd, 3rd, etc.)
- **Enhanced CLI**: Added `--calendar` and `--calendar-month` options
- **Calendar Exit Mode**: Calendar view runs independently without payment calculations

**Updated Commands:**
```bash
# Show calendar for current month
python cc_paydown_planner.py --file cards.json --calendar

# Show calendar for specific month
python cc_paydown_planner.py --file cards.json --calendar-month 2024-08

# Short form
python cc_paydown_planner.py -f cards.json -c
```

**Files Modified:**
- `cc_paydown_planner.py`: Added calendar functionality and CLI options
- `tests/test_calendar.py`: Comprehensive test suite for calendar features
- `CLAUDE.md`: Updated documentation with calendar usage examples

### Session 2025-07-18: Enhanced Calendar View with Rich Colors

**New Features Added:**
- **Rich Calendar Styling**: Enhanced calendar view with colored date backgrounds
- **Color Assignment System**: Automatic unique color assignment to each credit card
- **Color Legend**: Visual legend showing card-to-color mapping
- **Fallback Support**: Graceful fallback to ASCII calendar if rich library not available
- **Multiple Card Handling**: Smart handling of multiple cards due on same date

**Technical Implementation:**
- **Rich Integration**: Optional rich library integration for enhanced terminal styling
- **Color Palette**: 19 distinct colors optimized for dark terminals with good contrast
- **Background Coloring**: Payment due dates filled with card-specific background colors
- **Dark Theme Friendly**: Excludes problematic colors (yellow, white) for better readability
- **Import Safety**: Graceful handling of missing rich dependency with fallback to ASCII

**Code Changes:**
- **New Functions**:
  - `show_rich_calendar_view()`: Enhanced calendar display with rich styling
  - `get_card_colors()`: Returns available color palette for cards
  - `assign_card_colors()`: Assigns unique colors to each card with balances
- **Enhanced Features**:
  - Colored date backgrounds in calendar table
  - Visual color legend showing card assignments
  - Rich styling for headers and payment details
  - Automatic color cycling for many cards

**Updated Dependencies:**
- **Optional**: `rich` library for enhanced calendar styling
- **Maintained**: Full backward compatibility with ASCII calendar

**Enhanced Calendar Features:**
- Each card gets a unique color optimized for dark terminals (red, green, blue, magenta, etc.)
- Payment due dates are filled with card's background color
- Multiple cards on same date shown with primary card color + asterisk
- Color legend shows which card corresponds to each color
- Rich formatting for headers and payment details
- Dark theme friendly: excludes hard-to-read colors (yellow, white) for better contrast

**Files Modified:**
- `cc_paydown_planner.py`: Added rich calendar functionality and color system
- `CLAUDE.md`: Updated documentation with rich calendar information

### Session 2025-07-18: Dark Theme Color Optimization

**Improvements Made:**
- **Dark Theme Optimization**: Updated color palette to be more friendly for dark terminal themes
- **Color Contrast**: Removed problematic colors (yellow, bright_yellow, white, bright_white) that are hard to read with white text
- **Enhanced Palette**: Expanded from 14 to 19 colors with better dark theme support
- **Better Readability**: All colors now provide good contrast with white text on dark backgrounds

**Updated Color Palette:**
- **Removed**: yellow, bright_yellow, white, bright_white (poor contrast on dark terminals)
- **Added**: purple, orange, grey, bright_black, dark_red, dark_green, dark_blue, dark_magenta, dark_cyan
- **Optimized**: All colors tested for readability with white text on dark backgrounds

**Technical Changes:**
- **Color Function**: Updated `get_card_colors()` to return dark-theme optimized palette
- **Test Updates**: Modified tests to validate new color requirements
- **Documentation**: Updated color information and technical specifications

**User Benefits:**
- Much better readability in dark terminal environments
- Consistent white text visibility across all card colors
- More color options (19 vs 14) for better card differentiation
- Maintains all existing functionality with improved visual experience

**Files Modified:**
- `cc_paydown_planner.py`: Updated color palette function for dark theme optimization
- `tests/test_calendar.py`: Updated tests for new color palette validation
- `CLAUDE.md`: Updated documentation with new color information
