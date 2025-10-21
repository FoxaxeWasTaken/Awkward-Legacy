# GWDiff - GeneWeb Database Diff Tool

A tool for comparing GeneWeb genealogy databases and identifying differences between individuals and their descendants.

## Features

- Compare individuals between two GeneWeb databases
- Recursive descendant comparison
- Multiple output formats (plain text, HTML)
- Flexible matching of persons across databases
- Detailed difference reporting

## Installation

```bash
# Requires Python 3.7+
# Clone the repository or download the files
```

Dependencies

    gw_parser.py - GeneWeb file parser (must be in the same directory)

Usage
Basic Syntax
```bash

python gwdiff.py BASE1.gw BASE2.gw -1 FIRST_NAME OCCURRENCE SURNAME -2 FIRST_NAME OCCURRENCE SURNAME [OPTIONS]
```
Required Arguments

    BASE1.gw - Reference database file

    BASE2.gw - Destination database file

    -1 FN OCC LN - Person in base1 (First name, Occurrence, Last name)

    -2 FN OCC LN - Person in base2 (First name, Occurrence, Last name)

Options

    -d - Check descendants (recursive comparison)

    -ad - Check descendants of all ascendants

    -html ROOT - HTML output format with root URL

Examples
```bash

# Compare two individuals
python gwdiff.py base1.gw base2.gw -1 "Jean" "0" "DUPONT" -2 "Jean" "0" "DUPONT"

# Compare with descendants
python gwdiff.py base1.gw base2.gw -1 "Jean" "0" "DUPONT" -2 "Jean" "0" "DUPONT" -d

# Debug mode
python gwdiff.py base1.gw base2.gw -1 "Jean" "0" "DUPONT" -2 "Jean" "0" "DUPONT" -d --debug
```

The tool reports differences in these categories:

    Personal information: First name, surname, sex, occupation

    Vital events: Birth date/place, death date/place

    Family relationships: Parents, spouses, children

    Marriage information: Marriage date/place, divorce

Difference Messages

    first name - Different first names

    surname - Different last names

    sex - Different genders

    birth date - Different birth dates

    death date - Different death dates

    child missing - Child present in base1 but not base2

    spouse missing - Spouse present in base1 but not base2

    And more...

How It Works

    Parsing: Both GW files are parsed into person and family objects

    Matching: Starting persons are located in each database

    Comparison: Persons are compared field by field

    Recursion: If -d option used, descendants are compared recursively

    Reporting: Differences are reported with clear messages

Matching Algorithm

    Persons are matched by first name, last name, and occurrence number

    Light matching uses only name fields for initial family matching

    Full matching compares all available personal information

    The tool handles cases where multiple persons match the criteria

Testing

Run the test suite:
```bash

python test_gwdiff.py
```
Tests cover:

    Person and family object creation

    Comparison logic

    Data builder functionality

    Person lookup

    Various comparison scenarios

File Structure

    gwdiff.py - Main diff tool

    test_gwdiff.py - Unit tests

    gw_parser.py - GeneWeb file parser (required)

Notes

    Names with spaces should be quoted on command line

    HTML output generates clickable links to GeneWeb individual pages

    The tool only reports differences, identical data produces no output