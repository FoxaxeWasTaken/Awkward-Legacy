# Geneweb Test Architecture Documentation

## Overview

This document explains the architecture and design decisions for the Geneweb test suite, which migrated from a shell script (`run_gw_test.sh`) to a Python-based system (`geneweb_test_runner.py`).

## Migration Goals vs Reality

### Original Goals
- **Cleaner code**: Replace 300-line shell script with maintainable Python
- **Better structure**: Organize tests by categories and scenarios
- **Improved error handling**: More robust error detection and reporting
- **Golden master testing**: Capture and compare HTML outputs

### Reality Check
The Python version is **~850 lines** vs the original **~450 lines** shell script. This raises important questions about whether we achieved our goals.

## Architecture Components

### 1. TestConfiguration Class
**Purpose**: Centralized configuration management

**Replaces**: Hardcoded variables in bash script header
```bash
# Original bash approach
DBNAME='galichet'
FN=anthoine
SN=geruzet
ID=26
```

**Benefits**:
- Type safety with dataclasses
- Default values with override capability
- Structured configuration loading

**Cost**: ~100 lines of code for what was ~20 lines of shell variables

### 2. TestScenario Class
**Purpose**: Structured test case representation

**Replaces**: Simple bash function calls
```bash
# Original: 1 line per test
crl "m=S&n=$FN+$SN&p="

# New: 6 lines per test
TestScenario(
    name="search_person",
    description="Search for a specific person",
    url_params=f"m=S&n={c.first_name}+{c.surname}&p=",
    category="search"
),
```

**Benefits**:
- Self-documenting tests
- Categorization
- Expected result tracking
- Better organization

**Cost**: 6x more verbose per test

### 3. GenewebTestRunner Class
**Purpose**: Test orchestration and execution

**Key Methods**:
- `_start_gwd_server()`: Server lifecycle management
- `_make_request()`: HTTP request handling with error detection
- `_save_output()`: Golden master file management
- `get_test_scenarios()`: Test scenario generation

**Benefits**:
- Better error handling
- Structured logging
- Process management
- Golden master functionality

## Current Golden Master Implementation

### How It Works
```python
def _save_output(self, scenario: TestScenario, content: str):
    if self.config.mode == TestMode.CAPTURE:
        # Save HTML response to reference files
        # Both clean names AND legacy compatibility
        golden_output_file = references_dir / filename
        legacy_output_file = self.reference_dir / filename

    elif self.config.mode == TestMode.COMPARE:
        # Compare current HTML against saved references
        # Byte-by-byte diff of HTML content
```

### The Problem We Identified

**HTML Golden Master Issues**:

1. **Fragility**: Any small frontend change breaks ALL tests
   ```html
   <!-- Change this: -->
   <div class="person-info">
   <!-- To this: -->
   <div class="person-details">
   <!-- Result: Every test fails -->
   ```

2. **False Positives**: Changes in whitespace, formatting, or CSS classes cause failures
3. **Hard to Debug**: HTML diffs are noisy and hard to read
4. **Frontend Coupling**: Tests are tightly coupled to HTML structure
5. **Vue.js Migration**: When moving to Vue, ALL golden master files become useless

### Why This Approach Was Chosen
The original bash script already did HTML comparison:
```bash
if test "$test_diff"; then
    for xx in $(ls /tmp/run); do
        diff $test_dir/ref/$xx /tmp/run/$xx > /dev/null 2>&1
        # If HTML differs, test fails
    done
fi
```

The Python version **inherited this flawed approach** rather than improving it.

## Better Testing Strategies

### 1. Functional Testing Instead of HTML Comparison

**Current (Bad)**:
```python
# Test: "Does HTML output match exactly?"
assert html_content == reference_html  # Fragile!
```

**Better**:
```python
# Test: "Does the page contain expected data?"
assert "anthoine geruzet" in response.text
assert "Born: 1850" in response.text
assert response.status_code == 200
```

### 2. API-First Testing

**Instead of**: Testing HTML pages
**Test**: JSON/XML API responses
```python
# Test actual data, not presentation
response = requests.get(f"/api/person/{person_id}")
data = response.json()
assert data["name"] == "anthoine geruzet"
assert data["birth_year"] == 1850
```

### 3. Semantic HTML Testing

**Instead of**: Exact HTML matching
**Test**: Semantic content with CSS selectors
```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html_content, 'html.parser')
assert soup.select_one('.person-name').text == "anthoine geruzet"
assert soup.select_one('.birth-date').text == "1850"
```

### 4. Component-Level Testing (for Vue.js)

**Future Vue.js tests**:
```javascript
// Test Vue components directly
import { mount } from '@vue/test-utils'
import PersonDisplay from '@/components/PersonDisplay.vue'

test('displays person information', () => {
  const wrapper = mount(PersonDisplay, {
    props: { person: { name: "anthoine geruzet", birthYear: 1850 } }
  })

  expect(wrapper.text()).toContain("anthoine geruzet")
  expect(wrapper.text()).toContain("1850")
})
```

## Recommended Refactoring

### 1. Split Into Multiple Files

**Current**: One 850-line file
**Proposed**:
```
test/
├── geneweb_test_runner.py          # Main entry point (100 lines)
├── config/
│   ├── __init__.py
│   └── test_configuration.py       # TestConfiguration class
├── scenarios/
│   ├── __init__.py
│   ├── test_scenario.py            # TestScenario class
│   └── scenario_definitions.py     # All test scenarios
├── runners/
│   ├── __init__.py
│   ├── base_runner.py              # Abstract base
│   ├── functional_runner.py        # Functional tests
│   └── golden_master_runner.py     # Legacy HTML comparison
└── utils/
    ├── __init__.py
    ├── server_manager.py           # GWD server lifecycle
    └── http_client.py              # HTTP request handling
```

### 2. Implement Better Testing Strategy

**Phase 1**: Keep current HTML tests for compatibility
**Phase 2**: Add functional tests alongside HTML tests
**Phase 3**: Replace HTML tests with functional tests
**Phase 4**: Remove HTML golden master entirely

### 3. Example Functional Test

```python
class FunctionalTestRunner:
    def test_person_search(self):
        """Test person search functionality."""
        response = self.client.get("/search", params={
            "m": "S",
            "n": "anthoine+geruzet"
        })

        # Test functionality, not HTML
        assert response.status_code == 200
        assert "anthoine geruzet" in response.text.lower()
        assert "search results" in response.text.lower()

    def test_person_display(self):
        """Test person display functionality."""
        response = self.client.get(f"/person/{self.test_person_id}")

        assert response.status_code == 200
        assert self.test_person_name in response.text
        # Could also parse HTML and check for specific elements
        soup = BeautifulSoup(response.text, 'html.parser')
        assert soup.select_one('[data-testid="person-name"]')
```

## Conclusions

### The Golden Master Problem Is Real

1. **HTML comparison is fragile** and breaks with any frontend change
2. **Vue.js migration will invalidate all golden master files**
3. **Current approach creates more problems than it solves**

### Recommendations

1. **Keep the Python structure** - it's better organized than bash
2. **Split into multiple files** - 850 lines is too much for one file
3. **Gradually replace HTML golden master** with functional testing
4. **Focus on testing behavior, not presentation**
5. **Prepare for Vue.js migration** by testing data/functionality, not HTML structure

### Next Steps

1. Create the modular file structure
2. Implement functional testing alongside current HTML tests
3. Gradually migrate tests from HTML comparison to functional validation
4. Eventually remove golden master HTML comparison entirely

The Python rewrite was a good step for code organization, but the testing strategy needs to evolve beyond fragile HTML comparison to be truly useful for a modern web application.
