# Docker Testing Guide

This guide helps you test the credit card paydown planner in a clean Docker environment to isolate potential prompt/backspace issues.

## Prerequisites

- Docker installed on your system
- Docker Compose installed (usually comes with Docker Desktop)

## Quick Start

### Build and Test

```bash
# Build the Docker image
docker-compose build

# Test interactive prompts in a clean environment
docker-compose run credit-card-planner

# Test with JSON file (non-interactive)
docker-compose run test-json

# Test with CSV file (non-interactive)
docker-compose run test-csv

# Get a bash shell in the container for manual testing
docker-compose run interactive
```

### Debug Backspace Issues

```bash
# Run the prompt test script
docker-compose run credit-card-planner python test_prompt.py

# Show only environment information
docker-compose run credit-card-planner python test_prompt.py --env-only

# Get a bash shell and test manually
docker-compose run interactive
# Then inside the container:
python test_prompt.py
python cc_paydown_planner.py
```

## Testing Scenarios

### 1. Basic Prompt Testing
```bash
docker-compose run credit-card-planner python test_prompt.py
```

This will test:
- Basic string prompts
- Number prompts with validation
- Optional prompts with defaults
- Environment information

### 2. Interactive Card Entry
```bash
docker-compose run credit-card-planner
```

Follow the prompts in this order:
1. Card name
2. Credit limit
3. Current balance
4. Minimum payment
5. Payment due date
6. Notes (optional)

### 3. File-based Testing (No Prompts)
```bash
# Test JSON format
docker-compose run test-json

# Test CSV format
docker-compose run test-csv
```

## What to Look For

### Backspace Issue Symptoms:
- Typing backspace shows `^?` characters
- Cannot delete characters in prompts
- Terminal editing doesn't work properly

### Normal Behavior:
- Backspace deletes previous character
- Arrow keys work for navigation
- No strange characters appear

## Environment Comparison

### Local Environment
```bash
# Test locally first
python test_prompt.py --env-only
python test_prompt.py
```

### Docker Environment
```bash
# Test in Docker
docker-compose run credit-card-planner python test_prompt.py --env-only
docker-compose run credit-card-planner python test_prompt.py
```

Compare the environment information between local and Docker to identify differences.

## Troubleshooting

### If Docker Terminal Issues Persist:
```bash
# Try different terminal settings
docker-compose run -e TERM=xterm credit-card-planner python test_prompt.py
docker-compose run -e TERM=vt100 credit-card-planner python test_prompt.py
```

### Manual Container Testing:
```bash
# Get a bash shell
docker-compose run interactive

# Inside container, test different approaches:
python -c "import sys; print(sys.stdin.isatty())"
python -c "import click; print(click.prompt('Test'))"
stty -a
```

## Clean Up

```bash
# Remove containers and images
docker-compose down
docker rmi credit-card-paydown_credit-card-planner
```

## Expected Results

- **If backspace works in Docker but not locally**: Issue is with your local terminal/shell configuration
- **If backspace doesn't work in either**: Issue may be with the Click library or Python prompt handling
- **If works in both**: Issue may be specific to your terminal emulator or SSH session

## Next Steps

Based on test results:

1. **Docker works, local doesn't**: Check terminal settings, shell configuration, or try different terminal app
2. **Neither works**: May need to investigate Click library configuration or use alternative prompt method
3. **Both work**: Issue may be intermittent or specific to certain conditions
