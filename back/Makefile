IMAGE_NAME = awkward-legacy-back
DEV_TAG = dev
PROD_TAG = prod
CONTAINER_NAME = awkward-legacy-back
PORT = 8000

# Default target - build and run dev server
all: build-dev run-dev

# Development targets
build-dev:
	@echo "Building development image..."
	docker build -f Dockerfile.dev -t $(IMAGE_NAME):$(DEV_TAG) .

run-dev:
	@echo "Starting development server with hot reload..."
	docker run --rm -d \
		--name $(CONTAINER_NAME)-dev \
		-p $(PORT):$(PORT) \
		-v $(PWD)/src:/app/src \
		-v $(PWD)/tests:/app/tests \
		$(IMAGE_NAME):$(DEV_TAG)

stop-dev:
	@echo "Stopping development container..."
	docker stop $(CONTAINER_NAME)-dev

# Production targets
build-prod:
	@echo "Building production image..."
	docker build -f Dockerfile.prod -t $(IMAGE_NAME):$(PROD_TAG) .

run-prod:
	@echo "Starting production server..."
	docker run --rm -d \
		--name $(CONTAINER_NAME)-prod \
		-p $(PORT):$(PORT) \
		$(IMAGE_NAME):$(PROD_TAG)

stop-prod:
	@echo "Stopping production container..."
	docker stop $(CONTAINER_NAME)-prod

# Testing and linting
test:
	@echo "Running tests..."
	docker run --rm \
		-v $(PWD):/app \
		$(IMAGE_NAME):$(DEV_TAG) \
		python -m pytest -v

lint:
	@echo "Running linting..."
	docker run --rm \
		-v $(PWD):/app \
		$(IMAGE_NAME):$(DEV_TAG) \
		sh -c "python -m black --check . && python -m pylint src/"

format:
	@echo "Formatting code..."
	docker run --rm \
		-v $(PWD):/app \
		$(IMAGE_NAME):$(DEV_TAG) \
		python -m black .

# Cleanup
clean:
	@echo "Cleaning up containers and images..."
	docker stop $(CONTAINER_NAME)-dev $(CONTAINER_NAME)-prod || true  
	docker rm $(CONTAINER_NAME)-dev $(CONTAINER_NAME)-prod || true
	docker image rm $(IMAGE_NAME):$(DEV_TAG) $(IMAGE_NAME):$(PROD_TAG) || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null


# Declare phony targets
.PHONY: all build-dev run-dev stop-dev build-prod run-prod stop-prod test lint format clean