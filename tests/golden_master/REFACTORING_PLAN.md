# File Splitting Proposal

This document outlines how to refactor the monolithic `geneweb_test_runner.py` into smaller, focused modules.

## Current Problem
- Single file with 852 lines
- Multiple responsibilities mixed together
- Hard to navigate and maintain
- Violates Single Responsibility Principle

## Proposed Structure

```
test/
├── geneweb_test_runner.py          # Main entry point (~50 lines)
├── config/
│   ├── __init__.py
│   └── configuration.py            # TestConfiguration class (~100 lines)
├── scenarios/
│   ├── __init__.py
│   ├── scenario.py                 # TestScenario class (~50 lines)
│   └── definitions.py              # All test scenario definitions (~300 lines)
├── runners/
│   ├── __init__.py
│   ├── base.py                     # Base runner interface (~50 lines)
│   ├── http_runner.py              # HTTP-based testing (~200 lines)
│   └── server_manager.py           # GWD server lifecycle (~100 lines)
└── utils/
    ├── __init__.py
    └── enums.py                    # TestMode, TestResult enums (~30 lines)
```

## Benefits of This Split

### 1. Single Responsibility
Each file has one clear purpose:
- `configuration.py` - Only handles test configuration
- `scenario.py` - Only defines what a test scenario is
- `definitions.py` - Only contains the actual test definitions
- `http_runner.py` - Only handles HTTP requests and responses
- `server_manager.py` - Only manages the GWD server lifecycle

### 2. Easier Testing
Each module can be unit tested independently:
```python
# Test configuration loading
def test_configuration_from_file():
    config = TestConfiguration.from_file("test_config.txt")
    assert config.database_name == "test_db"

# Test scenario creation
def test_scenario_filename_safe():
    scenario = TestScenario("test name!", "desc", "params")
    assert scenario.get_filename_safe_name() == "test_name_"
```

### 3. Better Import Management
Clear imports instead of everything in one file:
```python
from config.configuration import TestConfiguration
from scenarios.definitions import get_search_scenarios
from runners.http_runner import HttpTestRunner
```

### 4. Parallel Development
Different developers can work on different modules without conflicts.

## Implementation Plan

### Phase 1: Extract Configuration
1. Move `TestConfiguration` class to `config/configuration.py`
2. Update imports in main file
3. Test that everything still works

### Phase 2: Extract Scenarios
1. Move `TestScenario` class to `scenarios/scenario.py`
2. Move `get_test_scenarios()` method to `scenarios/definitions.py`
3. Update imports and test

### Phase 3: Extract Server Management
1. Move server start/stop methods to `runners/server_manager.py`
2. Make it a separate class that the main runner uses
3. Test server lifecycle independently

### Phase 4: Extract HTTP Runner
1. Move HTTP request handling to `runners/http_runner.py`
2. Separate golden master logic from HTTP logic
3. Create clean interfaces between components

### Phase 5: Clean Up Main File
1. Main file becomes just argument parsing and orchestration
2. All heavy lifting delegated to specialized modules
3. Much easier to understand the overall flow

## Example of Cleaned Up Main File

```python
#!/usr/bin/env python3
"""Geneweb Test Runner - Main entry point."""

import argparse
import sys
from pathlib import Path

from config.configuration import TestConfiguration
from scenarios.definitions import get_all_scenarios
from runners.http_runner import HttpTestRunner
from runners.server_manager import ServerManager


def main():
    """Main entry point."""
    args = parse_arguments()

    # Load configuration
    config = load_configuration(args)

    # Setup components
    server_manager = ServerManager(config)
    test_runner = HttpTestRunner(config)

    try:
        # Start server
        if not server_manager.start():
            print("Failed to start server")
            sys.exit(1)

        # Get and filter scenarios
        scenarios = get_all_scenarios(config)
        if args.category:
            scenarios = filter_by_category(scenarios, args.category)

        # Run tests
        results = test_runner.run_scenarios(scenarios)

        # Report results
        print_summary(results)

    finally:
        server_manager.stop()


def parse_arguments():
    """Parse command line arguments."""
    # ... argument parsing logic


def load_configuration(args):
    """Load test configuration."""
    # ... configuration loading logic


if __name__ == "__main__":
    main()
```

Much cleaner and easier to understand!

## Testing Strategy Integration

This modular structure also makes it easier to implement better testing strategies:

### Current HTML Golden Master
```python
# runners/golden_master_runner.py
class GoldenMasterRunner:
    """Legacy HTML comparison runner."""

    def run_scenario(self, scenario):
        response = self.http_client.get(scenario.url)
        if self.mode == "capture":
            self.save_html(scenario.name, response.text)
        elif self.mode == "compare":
            return self.compare_html(scenario.name, response.text)
```

### New Functional Testing
```python
# runners/functional_runner.py
class FunctionalTestRunner:
    """Functional behavior testing."""

    def test_person_search(self, person_name):
        response = self.http_client.search_person(person_name)
        assert response.status_code == 200
        assert person_name.lower() in response.text.lower()
        return TestResult.PASS

    def test_person_display(self, person_id):
        response = self.http_client.get_person(person_id)
        assert response.status_code == 200
        # Parse HTML and check for expected elements
        soup = BeautifulSoup(response.text, 'html.parser')
        assert soup.select_one('[data-person-id]')
        return TestResult.PASS
```

### API Testing (Future)
```python
# runners/api_runner.py
class ApiTestRunner:
    """API endpoint testing for headless Geneweb."""

    def test_person_api(self, person_id):
        response = self.api_client.get(f"/api/persons/{person_id}")
        data = response.json()
        assert "name" in data
        assert "birth_date" in data
        return TestResult.PASS
```

This modular approach makes it easy to:
1. **Keep legacy HTML tests** for backward compatibility
2. **Add functional tests** alongside HTML tests
3. **Gradually migrate** from HTML to functional testing
4. **Prepare for Vue.js** with component and API testing
5. **Remove HTML golden master** when no longer needed

The split also makes the codebase much more maintainable and testable.
