# CI/CD Pipeline Documentation

## Overview

This document explains the GitHub Actions CI/CD pipeline implemented for the Awkward Legacy project. The pipeline is designed to ensure code quality, test coverage, and maintain a mirrored repository for Epitech.

## Pipeline Trigger

The pipeline is triggered on:
- **Pull Requests** to any branch except those starting with `ga-ignore-`
- This ensures that all code changes go through quality checks before being merged and don't waste our free github actions credits

## Pipeline Architecture

The pipeline follows a sophisticated workflow with multiple jobs that run in parallel and have dependencies to optimize execution time and resource usage.

### Job Dependencies Flow

```
checkout-and-artifact
    ├── build-prod
    └── build-dev
            ├── run-server-lint
            │   └── run-server-tests
            └── run-client-lint
                ├── run-client-tests
                └── run-client-e2e-tests
                        └── mirror
```

## Detailed Job Breakdown

### 1. Checkout and Artifact Upload (`checkout-and-artifact`)

**Purpose**: Initial code checkout and artifact preparation for subsequent jobs.

**What it does**:
- Checks out the repository code
- Uploads the entire codebase as an artifact named `source-code`
- This artifact is reused by all other jobs to avoid redundant checkouts

**Why this approach**: 
- Reduces network overhead by sharing code across jobs
- Ensures all jobs work with the exact same code version
- Improves pipeline reliability and speed

### 2. Production Environment Build (`build-prod`)

**Purpose**: Validates that the production environment can be built and deployed successfully.

**What it does**:
- Downloads the source code artifact
- Builds the production environment using `make up-prod`
- Waits for services to be healthy (60-second timeout)
- Tests production endpoints:
  - Server: `http://localhost:8000/`
  - Client: `http://localhost:80/`
- Cleans up the production environment

**Why this job**:
- Ensures production builds work correctly
- Validates that both client and server are accessible
- Catches production-specific configuration issues early
- Prevents deployment of broken production builds

### 3. Development Environment Build (`build-dev`)

**Purpose**: Builds the development environment and prepares Docker images for testing.

**What it does**:
- Downloads the source code artifact
- Builds the development environment using `make up-dev`
- Saves Docker images as tar files:
  - `awkward-legacy-server-dev.tar`
  - `awkward-legacy-client-dev.tar`
- Stops the development environment
- Uploads the built images as artifacts

**Why this approach**:
- Pre-builds images once and reuses them across multiple test jobs
- Significantly reduces build time for subsequent jobs
- Ensures consistent testing environment across all test jobs
- Optimizes resource usage in the CI environment

### 4. Server Linting (`run-server-lint`)

**Purpose**: Ensures server code follows Python coding standards and best practices.

**What it does**:
- Downloads source code and built images
- Loads the pre-built Docker images
- Runs server linting using `make lint-server`
- Checks code formatting with Black
- Runs static analysis with Pylint

**Why linting is important**:
- Maintains consistent code style across the project
- Catches potential bugs and bad code early
- Improves code readability and maintainability
- Enforces Python best practices

### 5. Client Linting (`run-client-lint`)

**Purpose**: Ensures client code follows JavaScript/TypeScript coding standards.

**What it does**:
- Downloads source code and built images
- Loads the pre-built Docker images
- Runs client linting using `make lint-client`
- Executes ESLint checks

**Why this is necessary**:
- Maintains consistent JavaScript/TypeScript code style
- Catches syntax errors and potential issues
- Ensures code quality standards are met

### 6. Server Tests (`run-server-tests`)

**Purpose**: Executes the server-side test suite to ensure functionality works correctly.

**What it does**:
- Downloads source code and built images
- Loads the pre-built Docker images
- Runs server tests using `make test-server`
- Executes pytest with verbose output

**Dependencies**: Requires `run-server-lint` to pass first

**Why this dependency**:
- Ensures code quality before running tests
- Prevents wasting time on tests if code doesn't meet standards
- Maintains a logical flow: lint → test

### 7. Client Unit Tests (`run-client-tests`)

**Purpose**: Executes the client-side unit test suite.

**What it does**:
- Downloads source code and built images
- Loads the pre-built Docker images
- Runs client unit tests using `make test-client`
- Executes Vitest tests

**Dependencies**: Requires `run-client-lint` to pass first

**Why this approach**:
- Validates individual component functionality
- Ensures client-side logic works correctly
- Provides fast feedback on code changes

### 8. Client E2E Tests (`run-client-e2e-tests`)

**Purpose**: Executes end-to-end tests to validate the complete user workflow.

**What it does**:
- Downloads source code and built images
- Loads the pre-built Docker images
- Runs E2E tests in parallel using a matrix strategy
- Uses 4 shards for parallel execution
- Integrates with Cypress Dashboard for test recording

**Key Features**:
- **Parallel Execution**: Uses 4 shards to run tests simultaneously
- **Cypress Integration**: Records test results for analysis
- **Fail-fast disabled**: Allows all shards to complete even if one fails
- **CI Build ID**: Tracks test runs across shards

**Why parallel execution**:
- Significantly reduces test execution time
- Enables faster feedback loops

**Dependencies**: Requires `run-client-lint` to pass first

### 9. Repository Mirroring (`mirror`)

**Purpose**: Creates a backup mirror of the repository to Epitech repository.

**What it does**:
- Checks out the repository with full history
- Pushes the entire repository to Epitech
- Uses SSH authentication for secure access

**Configuration**:
- **Target Repository**: `git@github.com:EpitechPGE45-2025/G-ING-900-PAR-9-1-legacy-14.git`
- **Authentication**: Uses SSH private key from GitHub secrets
- **Full History**: Ensures complete repository backup

**Dependencies**: Requires all tests to pass (`run-server-tests`, `run-client-tests`, `run-client-e2e-tests`)

## Pipeline Optimization Strategies

### 1. Artifact Reuse
- Source code is checked out once and shared across all jobs
- Docker images are built once and reused for all testing jobs
- Reduces build time and resource consumption

### 2. Parallel Execution
- Independent jobs run in parallel where possible
- E2E tests use matrix strategy for parallel sharding
- Optimizes overall pipeline execution time

### 3. Dependency Management
- Logical job dependencies ensure proper execution order
- Linting runs before testing to catch issues early
- All tests must pass before mirroring occurs

### 4. Resource Efficiency
- Development environment is built once and reused
- Production environment is tested and immediately cleaned up
- Docker images are saved and loaded efficiently

## Security Considerations

- SSH keys are stored as GitHub secrets
- Repository mirroring uses secure SSH authentication
- No sensitive data is exposed in pipeline logs
- Docker containers run in isolated environments

## Monitoring and Debugging

### Test Results
- Unit tests provide immediate feedback
- E2E tests are recorded in Cypress Dashboard
- Linting results show code quality metrics
- All results are visible in GitHub Actions interface

### Failure Handling
- Pipeline fails fast on critical issues (linting, build)
- E2E tests allow all shards to complete for full visibility
- Detailed logs are available for debugging
- Artifacts are preserved for investigation

## Benefits of This Pipeline Design

1. **Comprehensive Quality Assurance**: Multiple layers of testing and validation
2. **Efficient Resource Usage**: Optimized build and test execution
3. **Fast Feedback**: Parallel execution and early failure detection
4. **Reliability**: Robust error handling and cleanup procedures
5. **Maintainability**: Clear job separation and logical dependencies
6. **Scalability**: Matrix strategy allows easy scaling of test execution
7. **Backup Strategy**: Automated repository mirroring for disaster recovery

## Note on Hosting

**Important**: Since Epitech did not provide us with a cloud provider or hosting credits, I have not set up automated hosting/deployment to avoid wasting free credits from personal cloud accounts. The pipeline focuses on code quality, testing, and repository management rather than deployment to production environments. This approach ensures that the project maintains high standards while being mindful of resource costs.

If hosting becomes available in the future, the pipeline can be easily extended to include deployment jobs that would:
- Deploy to temporary environments for testing
- Deploy to production after successful validation
- Include environment-specific configuration management
