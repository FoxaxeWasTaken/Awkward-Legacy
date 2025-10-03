# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get --no-install-recommends install -y build-essential \
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
COPY ./README.md ./README.md
COPY ./src ./src
COPY ./tests ./tests
COPY ./__init__.py ./__init__.py
COPY ./Makefile ./Makefile
COPY ./entrypoint.sh ./entrypoint.sh

# Add src directory to Python path
ENV PYTHONPATH=/app/src:/app

# Expose port for FastAPI
EXPOSE 8000

# Copy entrypoint script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Default command
CMD ["/app/entrypoint.sh"]

# Alternative commands for different stages:
# Development mode with hot reload - Fixed to use src.main
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production mode
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Run tests only
# CMD ["python", "-m", "pytest", "-v"]

# Run linting only
# CMD ["python", "-m", "pylint", "src/**/*.py"]