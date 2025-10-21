GeneWeb Consanguinity Calculator
Overview

The Consanguinity Calculator analyzes GeneWeb genealogy database files (.gw) to compute consanguinity coefficients between individuals. It identifies and quantifies familial relationships to help understand genetic connections within a family tree.
Features

    Consanguinity Calculation: Computes consanguinity coefficients between all pairs of individuals

    Genealogical Loop Detection: Identifies and reports circular relationships in family trees

    Multiple Output Formats: Supports console output and detailed JSON reports

    Performance Optimized: Uses caching and efficient algorithms for large datasets

    Comprehensive Testing: Includes unit tests and integration tests

Requirements

    Python 3.6+

    GeneWeb parser module (gw_parser.py and dependencies)

Installation

    Ensure all required Python files are in your working directory:

        consang.py

        gw_parser.py

        All parser modules (block_parser.py, date_parser.py, event_parser.py, etc.)

Usage
Basic Command
```bash

python consang.py database.gw

Options

    -q, --quiet: Quiet mode (reduced output)

    -qq, --very-quiet: Very quiet mode (minimal output)

    -v, --verbose: Verbose mode (detailed output)

    -o, --output FILE: Save detailed results to JSON file
```
Examples
```bash

# Basic analysis
python consang.py family_tree.gw

# Save detailed results to file
python consang.py -o results.json family_tree.gw

# Quiet mode for large databases
python consang.py -q large_family.gw
```
Output

The tool provides:

    Summary statistics (number of persons, families, significant relations)

    Top 10 most consanguineous relationships

    Detailed JSON report with all relationships and coefficients (when using -o option)

Consanguinity coefficients range from 0.0 (unrelated) to higher values indicating closer familial relationships.
Testing

Run the test suite to verify functionality:

```bash

python test_consang.py
```
The test suite includes:

    Unit tests for data structures and algorithms

    Integration tests with sample genealogy files

    Cycle detection tests

    Performance validation

Algorithm

The calculator uses a recursive approach to:

    Build ancestor sets for each individual

    Identify common ancestors between pairs

    Calculate coefficients using generational distances

    Cache results for performance

Error Handling

    Detects and reports genealogical loops

    Handles missing or malformed data gracefully

    Provides clear error messages for common issues

Limitations

    Maximum generational depth: 15 (configurable)

    Performance may vary with very large datasets

    Requires valid GeneWeb .gw file format