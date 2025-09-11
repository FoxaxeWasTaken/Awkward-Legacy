#!/bin/bash
set -e

# Run code formatting and linting checks
echo "Running Black formatter check..."
python -m black --check . || echo "Black formatting issues found"

echo "Running Pylint..."
python -m pylint $(find src -name '*.py') || echo "Pylint warnings found"

# Run Python tests
echo "Running Python tests..."
python -m pytest -v || echo "Some tests failed"

# Start the application using Makefile
echo "Starting FastAPI application..."
exec make run