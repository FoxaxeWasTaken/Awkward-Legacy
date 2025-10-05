# Awkward Legacy Backend

FastAPI backend with Docker development and production environments.

## Quick Start

### Development (Default)
```bash
make                    # Build and run development server with hot reload
make stop-dev          # Stop development server
```

### Production
```bash
make build-prod        # Build production image
make run-prod          # Run production server
make stop-prod         # Stop production server
```

## Available Commands

### Development
- `make build-dev` - Build development Docker image
- `make run-dev` - Run development server with hot reload
- `make stop-dev` - Stop development container
- `make logs-dev` - Show development logs

### Production
- `make build-prod` - Build production Docker image
- `make run-prod` - Run production server
- `make stop-prod` - Stop production container

### Testing & Quality
- `make test` - Run tests in Docker
- `make lint` - Run linting in Docker
- `make format` - Format code in Docker

### Cleanup
- `make clean` - Clean up containers, images, and cache

## Docker Images

- **Development**: Includes hot reload, testing tools, and code quality tools
- **Production**: Optimized multi-stage build with only production dependencies

## Requirements

- Docker
- Make