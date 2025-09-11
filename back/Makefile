# Makefile for Python project

# Variables
ASGI_SERVER = uvicorn
MAIN = src.main

# Default target
all: run

# Run the main Python script
run:
	$(ASGI_SERVER) $(MAIN):app --host 0.0.0.0 --port 8000 --reload

# Re-run (same as run for Python projects)
re: clean run

# Clean temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	find . -type f -name "*.swp" -delete

# Full clean (removes all generated files)
fclean: clean
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.log" -delete
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

# Declare phony targets
.PHONY: all run re clean fclean