#!/bin/bash

# Ensure we're in the project root directory
cd "$(dirname "$0")"

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Install pytest and coverage explicitly
pip install pytest pytest-asyncio pytest-cov coverage flake8 black

# Add the current directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run linting
echo "Running Flake8 linter..."
flake8 . --ignore=E203,E266,E501,W503 --max-line-length=88

# Run formatting check
echo "Checking code formatting with Black..."
black --check .

# Run pytest with coverage
pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
coverage html

echo "Tests completed. HTML coverage report generated in htmlcov/index.html"

# Deactivate the virtual environment
deactivate
