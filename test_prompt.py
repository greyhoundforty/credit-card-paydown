#!/usr/bin/env python3
"""
Simple test script to debug prompt/backspace issues
"""

import os
import sys

import click


def test_basic_prompt():
    """Test basic click prompt functionality"""
    print("Testing basic click prompt...")
    name = click.prompt("Enter your name", type=str)
    print(f"You entered: {name}")


def test_number_prompt():
    """Test number prompt with validation"""
    print("\nTesting number prompt...")
    while True:
        try:
            amount = click.prompt("Enter a number", type=float)
            if amount < 0:
                print("Number must be positive")
                continue
            break
        except click.BadParameter:
            print("Please enter a valid number")
    print(f"You entered: {amount}")


def test_optional_prompt():
    """Test optional prompt with default"""
    print("\nTesting optional prompt...")
    notes = click.prompt(
        "Enter notes (optional)", type=str, default="", show_default=False
    )
    print(f"Notes: '{notes}'")


def test_environment():
    """Display environment information"""
    print("\n" + "=" * 50)
    print("ENVIRONMENT INFORMATION")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"TERM: {os.environ.get('TERM', 'Not set')}")
    print(f"PYTHONUNBUFFERED: {os.environ.get('PYTHONUNBUFFERED', 'Not set')}")
    print(f"TTY: {os.isatty(sys.stdin.fileno())}")
    print(f"stdin encoding: {sys.stdin.encoding}")
    print(f"stdout encoding: {sys.stdout.encoding}")

    # Test terminal capabilities
    try:
        import termios

        print(f"termios available: Yes")
    except ImportError:
        print(f"termios available: No")

    try:
        import readline

        print(f"readline available: Yes")
    except ImportError:
        print(f"readline available: No")


@click.command()
@click.option("--env-only", is_flag=True, help="Only show environment info")
def main(env_only):
    """Test script for debugging prompt issues"""

    test_environment()

    if env_only:
        return

    print("\n" + "=" * 50)
    print("PROMPT TESTING")
    print("=" * 50)
    print("Instructions:")
    print("1. Try typing and using backspace in each prompt")
    print("2. Note if you see ^? characters when pressing backspace")
    print("3. Test in both Docker and your local environment")
    print("4. Press Ctrl+C to exit at any time")
    print()

    try:
        test_basic_prompt()
        test_number_prompt()
        test_optional_prompt()

        print("\n✅ All tests completed successfully!")

    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")


if __name__ == "__main__":
    main()
