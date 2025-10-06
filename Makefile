# Docker Compose configuration
COMPOSE_DEV = docker compose -f docker-compose.dev.yml
COMPOSE_PROD = docker compose -f docker-compose.prod.yml

# Default target - start development environment
all: up-dev

# Development environment management
up-dev:
	@echo "Starting development environment..."
	$(COMPOSE_DEV) up -d --build

down-dev:
	@echo "Stopping development environment..."
	$(COMPOSE_DEV) down

logs-dev:
	@echo "Showing development logs..."
	$(COMPOSE_DEV) logs -f

# Production environment management
up-prod:
	@echo "Starting production environment..."
	$(COMPOSE_PROD) up -d --build

down-prod:
	@echo "Stopping production environment..."
	$(COMPOSE_PROD) down

logs-prod:
	@echo "Showing production logs..."
	$(COMPOSE_PROD) logs -f

# serverend testing and quality
test-server:
	@echo "Running serverend tests..."
	$(COMPOSE_DEV) run --rm server-dev python -m pytest -v

test-server-coverage:
	@echo "Running serverend tests with coverage..."
	$(COMPOSE_DEV) run --rm server-dev python -m pytest --cov=src --cov-report=html -v

lint-server:
	@echo "Running serverend linting..."
	$(COMPOSE_DEV) run --rm server-dev sh -c "python -m black --check . && python -m pylint src/"

format-server:
	@echo "Formatting serverend code..."
	$(COMPOSE_DEV) run --rm server-dev python -m black .

# Client testing and quality
test-client:
	@echo "Running client unit tests..."
	$(COMPOSE_DEV) run --rm client-dev npm run test:unit -- --run

test-client-e2e:
	@echo "Running client e2e tests..."
	$(COMPOSE_DEV) run --rm client-dev npm run test:e2e

test-client-e2e-parallel:
	@echo "Running client e2e tests in parallel (shard $(shard)/$(total-shards))..."
	$(COMPOSE_DEV) run --rm -e CYPRESS_RECORD_KEY=$(CYPRESS_RECORD_KEY) client-dev npm run test:e2e:parallel -- --shard $(shard)/$(total-shards) --ci-build-id $(ci-build-id)

test-client-watch:
	@echo "Running client tests in watch mode..."
	$(COMPOSE_DEV) run --rm client-dev npm run test:unit

lint-client:
	@echo "Running client linting..."
	$(COMPOSE_DEV) run --rm client-dev npm run lint

format-client:
	@echo "Formatting client code..."
	$(COMPOSE_DEV) run --rm client-dev npm run format

# Full testing
test: test-server test-client
	@echo "All tests completed!"

lint: lint-server lint-client
	@echo "All linting completed!"

format: format-server format-client
	@echo "All formatting completed!"

# Cleanup
clean:
	@echo "Cleaning up Docker resources..."
	$(COMPOSE_DEV) down -v --remove-orphans
	$(COMPOSE_PROD) down -v --remove-orphans
	$(COMPOSE_DEV) down --rmi all
	$(COMPOSE_PROD) down --rmi all
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null
	find . -type d -name "coverage" -exec rm -rf {} + 2>/dev/null


# Declare phony targets
.PHONY: all up-dev down-dev logs-dev up-prod down-prod logs-prod \
        test-server test-server-coverage test-client test-client-e2e test-client-e2e-parallel test-client-watch \
        test lint-server lint-client lint format-server format-client format \
        clean
