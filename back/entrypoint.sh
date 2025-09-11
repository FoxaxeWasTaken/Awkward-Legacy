#!/bin/bash
set -e

# Run code formatting and linting checks
echo "Running Black formatter check..."
python -m black --check .

echo "Running Pylint..."
python -m pylint $(find src -name '*.py')

# Run Python tests
echo "Running Python tests..."
python -m pytest -v

# Start the application using Makefile
echo "Starting FastAPI application..."
exec make run