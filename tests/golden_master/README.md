# Geneweb Test Suite

This directory contains the modernized Python-based test suite for Geneweb, replacing the legacy shell script `run_gw_test.sh` with clean, maintainable Python code.

## Overview

The test suite provides:
- **Clean test scenarios** with descriptive names and categories
- **Golden master testing** with reference file capture and comparison
- **Better error handling** and reporting
- **Modular design** following clean code principles
- **Easy configuration** and extensibility

## Golden Master Files & Git Strategy

### How Comparison Works
- **Capture mode** (`--capture`): Generates outputs and saves to both `golden_master_outputs/references/` and `ref/`
- **Compare mode** (`--compare`): Generates outputs to `/tmp/run/` and compares against files in `ref/`
- **Reference files**: Comparison always uses files from `ref/` directory

### Developer Setup Requirements
Each developer needs:
1. **Core reference files**: Essential `.txt` files in `ref/` directory
2. **Local generation**: Run `python3 geneweb_test_runner.py --capture` to generate full reference set

### Git strategy

**Minimal Git Storage**
```bash
# Only commit essential reference files
# Use .gitignore to exclude most generated files
# Developers generate full reference sets locally
```

## Files

- `tests/golden_master/features` - Detailed GIVEN-WHEN-THEN scenario descriptions.
- `geneweb_test_runner.py` - Main test runner (replaces `run_gw_test.sh`)
- `ref/` - Reference files (legacy compatibility + new clean names)
- `outputs/` - Clean golden master structure
  - `references/` - Golden master reference files (clean names)
  - `diffs/` - Comparison differences (when using --compare)
- `../../.gitignore` - Repository-level exclusions for generated test files

## Quick Start

### Basic Testing
```bash
# Run all tests
python3 test/geneweb_test_runner.py

# Run tests for specific database
python3 test/geneweb_test_runner.py galichet

# Run with debug output
python3 test/geneweb_test_runner.py --debug
```

### Category-based Testing
```bash
# List available categories
python3 test/geneweb_test_runner.py --list-categories

# List all test scenarios
python3 test/geneweb_test_runner.py --list-scenarios

# List scenarios in specific category
python3 test/geneweb_test_runner.py --list-scenarios --category ancestry

# Run only ancestry tests
python3 test/geneweb_test_runner.py --category ancestry

# Run only search tests
python3 test/geneweb_test_runner.py --category search
```

### Golden Master Testing
```bash
# Capture new reference files
python3 test/geneweb_test_runner.py --capture

# Compare against references
python3 test/geneweb_test_runner.py --compare

# Capture for specific category
python3 test/geneweb_test_runner.py --capture --category person
```

## Test Categories

The test suite is organized into logical categories:

- **page_modules** - Individual page module tests (individu, parents, unions, etc.)
- **search** - Search functionality tests
- **person** - Person display and access tests
- **ancestry** - Ancestry tree and timeline tests
- **descendants** - Descendants display tests
- **relationships** - Cousins and family relationship tests
- **navigation** - Site navigation and menu tests
- **admin** - Administrative interface tests
- **modification** - Data modification tests (may fail on read-only databases)
- **calendar** - Calendar functionality tests

## Configuration

### Default Configuration
The test runner uses sensible defaults that work with a standard Geneweb setup:

- Database: `galichet`
- Test person ID: `26` (anthoine geruzet)
- Test family ID: `13`
- Server: `localhost:2317`

### Custom Configuration
Create or modify `test-gw-vars.txt` to override defaults:

```bash
DBNAME=my_database
ID=123
FID=456
FN=john
SN=doe
```

Use a custom configuration file:
```bash
python3 test/geneweb_test_runner.py --config my-config.txt
```

## Test Scenarios

Each test scenario has:
- **Descriptive name** (e.g., `ancestry_tree_basic`)
- **Clear description** (e.g., "Display basic ancestry tree")
- **Category** for organization
- **Expected result** (pass/fail/skip)

### Adding New Test Scenarios

To add a new test scenario, edit `geneweb_test_runner.py` and add to the `get_test_scenarios()` method:

```python
TestScenario(
    name="my_new_test",
    description="Description of what this tests",
    url_params="m=MY_MODE&param=value",
    category="my_category"
)
```

## Output and Results

### Console Output
The test runner provides clear progress and results:
```
Starting Geneweb tests for database 'galichet'
Running 37 test scenarios...
[  1/37] ✓ search_person
[  2/37] ✓ display_person_basic
[  3/37] ✗ modify_children_order
...

Test Summary:
  Total:  37
  Passed: 35
  Failed: 2
  Skipped: 0
```

### Reference Files
- **Capture mode**: Saves files to both `golden_master_outputs/references/` (clean names) and `ref/` (backward compatibility)
- **Compare mode**: Shows differences between current and reference outputs
- **Dual storage**: New clean structure + legacy compatibility

## Migration from Shell Script

### Key Improvements
1. **Clean naming**: `search_person.txt` instead of `m_S_n_anthoine+geruzet_p_.txt`
2. **Categories**: Tests are organized by functionality
3. **Better error handling**: Clearer error messages and reporting
4. **Extensible**: Easy to add new tests and categories
5. **Maintainable**: Python code is easier to understand and modify

### Running Legacy Tests
The original shell script is still available:
```bash
# From main directory
./test/run_gw_test.sh

# Original golden master mode
./test/run_gw_test.sh -r  # Record
./test/run_gw_test.sh -t  # Test
```

## Utilities

All utility functions are now integrated into the main test runner:

```bash
# List categories
python3 test/geneweb_test_runner.py --list-categories

# List scenarios
python3 test/geneweb_test_runner.py --list-scenarios
python3 test/geneweb_test_runner.py --list-scenarios --category ancestry
```

## Prerequisites

- Python 3.6+
- `requests` library (usually pre-installed)
- Running Geneweb setup with the test database

## Troubleshooting

### Server Connection Issues
- Ensure Geneweb daemon is startable
- Check that the database exists in `distribution/bases/`
- Verify port 2317 is available

### Test Failures
- Use `--debug` flag for detailed output
- Check the Geneweb log file: `distribution/gw/gwd.log`
- Ensure test data (images, etc.) is properly set up

### Configuration Issues
- Verify configuration file syntax
- Check database name and paths
- Ensure test person/family IDs exist in the database

## Examples

### Continuous Integration
```bash
# Quick smoke test
python3 test/geneweb_test_runner.py --category search

# Full regression test
python3 test/geneweb_test_runner.py --compare

# Generate new baselines after changes
python3 test/geneweb_test_runner.py --capture

# Files are automatically saved to both locations:
# - golden_master_outputs/references/ (clean names)
# - ref/ (backward compatibility)
```

### Development Workflow
```bash
# Test specific functionality while developing
python3 test/geneweb_test_runner.py --category ancestry --debug

# Capture new references after implementing features
python3 test/geneweb_test_runner.py --capture --category person

# Files are saved to both golden_master_outputs/references/ and ref/
```

This modernized test suite provides a solid foundation for maintaining and extending Geneweb's test coverage while following clean code principles.
