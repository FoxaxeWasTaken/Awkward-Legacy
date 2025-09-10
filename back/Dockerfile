# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Copy the Makefile
COPY Makefile .

# Add src directory to Python path
ENV PYTHONPATH=/app/src:/app

# Expose port for FastAPI
EXPOSE 8000

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Run code formatting and linting checks\n\
echo "Running Black formatter check..."\n\
python -m black --check . || echo "Black formatting issues found"\n\
\n\
echo "Running Pylint..."\n\
python -m pylint src/**/*.py || echo "Pylint warnings found"\n\
\n\
# Run Python tests\n\
echo "Running Python tests..."\n\
python -m pytest -v || echo "Some tests failed"\n\
\n\
# Start the application using Makefile\n\
echo "Starting FastAPI application..."\n\
exec make run\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Default command
# CMD ["/app/entrypoint.sh"]

# Alternative commands for different stages:
# Development mode with hot reload - Fixed to use src.main
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production mode
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Run tests only
# CMD ["python", "-m", "pytest", "-v"]

# Run linting only
# CMD ["python", "-m", "pylint", "src/**/*.py"]