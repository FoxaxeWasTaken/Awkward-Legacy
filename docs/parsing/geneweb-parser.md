# GeneWeb Parser Architecture and Documentation

## Overview

The GeneWeb parser is a modular system designed to parse legacy GeneWeb `.gw` files and convert them into clean, nested, human-friendly JSON objects. The parser has been refactored into a modular architecture for better maintainability and clarity.

## Architecture

The parser is organized into a clean, minimal structure:

```
server/src/
├── gw_parser.py         # Main GWParser class (ready-to-use)
└── parsing/
    ├── __init__.py      # Empty package file
    ├── models.py        # Data structures and constants
    └── utils.py         # All utility and parsing functions
docs/parsing/
├── test_parser.py       # Example/test script
├── galichet.gw          # example .gw file
├── galichetjson         # example .json file

```

### Module Breakdown

#### 1. `gw_parser.py` - Main Parser Class

The main `GWParser` class that we use directly:
- **File Management**: Reads and prepares `.gw` files for parsing
- **State Management**: Tracks current position and parsing context
- **Block Parsing**: Handles different block types (families, events, notes, etc.)
- **Output Generation**: Produces structured JSON output

#### 2. `parsing/models.py` - Data Structures and Constants

Contains:
- **Event Type Mappings**: Maps GeneWeb event tags to human-readable names
  - `FEVT_MAP`: Family event mappings (`#marr` → `"marriage"`, etc.)
  - `PEVT_MAP`: Person event mappings (`#birt` → `"birth"`, etc.)
- **Type Definitions**: Type hints for better code documentation and IDE support
  - `PersonDict`, `FamilyDict`, `EventDict`, `DateDict`, etc.

#### 3. `parsing/utils.py` - All Utility and Parsing Functions

Contains all helper functions in one place:

- **Text Normalization**:
  - `normalize_underscores()`: Converts underscores to spaces

- **Date Parsing**:
  - `parse_date_token()`: Handles complex date formats with qualifiers
    - Supports qualifiers: `<` (before), `>` (after), `~` (approximate), `?` (uncertain)
    - Handles ranges: `1850..1860`
    - Handles alternatives: `1850|1851`
    - Handles literal dates: `0(5_Mai_1990)`

- **Text Processing**:
  - `split_family_header()`: Splits husband/wife segments in family headers
  - `tokenize_preserving_braces()`: Tokenizes while preserving `{...}` blocks

- **Person Parsing**:
  - `parse_person_segment()`: Parses person information (name, tags, dates)
  - Extracts display names, tags, dates, and other metadata

- **Event Parsing**:
  - `parse_event_line()`: Parses event lines with dates, places, and sources
  - `parse_note_line()`: Extracts note text from note lines

#### 4. `test_parser.py` - Example/Test Script

A ready-to-use command-line script that demonstrates how to use the parser:
```bash
python3 test_parser.py input.gw output.json
```

## Parsing Process

### 1. File Structure Detection

The parser first detects optional header information:
- `encoding:` declarations
- `gwplus` format indicators

### 2. Block-Based Parsing

The parser processes different block types in sequence:

#### Family Blocks (`fam`)
```
fam LastName FirstName + LastName FirstName
src family_source_reference
csrc children_source_reference
fevt
  #marr 1850 #p Paris #s registry
  note Marriage note
end fevt
beg
  - h ChildLastName ChildFirst #birt 1851
  - f ChildLastName ChildFirst #birt 1853
end
```

#### Person Event Blocks (`pevt`)
```
pevt LastName FirstName
#birt 1820 #p London #s birth_registry
#deat >1890 #p London
note Person biographical note
end pevt
```

#### Notes Blocks
```
notes PersonName
beg
Biographical information about the person...
end notes
```

#### Extended Pages (`page-ext`)
```
page-ext PageName
TITLE=Page Title
TYPE=page_type
Content of the page...
end page-ext
```

### 3. Data Structure Generation

The parser creates a structured output with:

```json
{
  "families": [...],
  "people": [...],
  "notes": [...],
  "extended_pages": [...],
  "database_notes": {...},
  "raw_header": {...}
}
```

## Date Parsing Features

The parser handles sophisticated date formats commonly found in genealogical data:

### Basic Dates
- `1850` → `{"raw": "1850", "value": "1850"}`

### Qualified Dates
- `<1849` → `{"raw": "<1849", "qualifier": "before", "value": "1849"}`
- `~1750` → `{"raw": "~1750", "qualifier": "approx", "value": "1750"}`
- `?1800` → `{"raw": "?1800", "qualifier": "uncertain", "value": "1800"}`

### Date Ranges
- `1850..1860` → `{"raw": "1850..1860", "between": ["1850", "1860"]}`
- `1850|1851` → `{"raw": "1850|1851", "alternatives": ["1850", "1851"]}`

### Literal Dates
- `0(5_Mai_1990)` → `{"raw": "0(5_Mai_1990)", "literal": "5 Mai 1990"}`

## Event Processing

### Family Events
Events within family contexts are mapped from GeneWeb tags to readable names:
- `#marr` → `marriage`
- `#div` → `divorce`
- `#enga` → `engagement`
- etc.

### Person Events
Individual person events include:
- `#birt` → `birth`
- `#deat` → `death`
- `#bapt` → `baptism`
- `#occu` → `occupation`
- etc.

### Event Structure
Each event includes:
- `type`: Human-readable event type
- `date`: Parsed date information (if present)
- `place_raw`: Location information (from `#p` tags)
- `source`: Source references (from `#s` tags)
- `notes`: Associated notes
- `raw`: Original unparsed text

## Usage Examples

### Basic Usage
```python
from parsing import GWParser

# Parse a .gw file
parser = GWParser("family_tree.gw")
data = parser.parse()

# Output to JSON
parser.to_json("output.json")
```

### API Integration
The parser is integrated into the REST API for file import/export:

```python
# Import via API
POST /api/v1/files/import
# Uploads .gw file, parses it, and stores in database

# Export via API  
GET /api/v1/files/export
# Exports database data back to .gw format
```

We can also import and export from/as json.

### Backward Compatibility
```python
# The original import still works
from gw_parser import GWParser

parser = GWParser("family_tree.gw")
data = parser.parse()
```

## Design Goals

The parser implements several key design goals:

1. **Human-Readable Output**: Uses clear field names like `husband`, `wife`, `children`, `events`
2. **Nested Structure**: Organizes families and people in logical hierarchies
3. **Tag Interpretation**: Converts cryptic tags (`#marr`) to readable names (`marriage`)
4. **Date Intelligence**: Sophisticated parsing of genealogical date formats
5. **Data Preservation**: Maintains raw values when interpretation might lose information
6. **JSON Ready**: Produces Python dictionaries ready for JSON serialization

## Error Handling

The parser is designed to be robust:
- Unknown tags are preserved with their raw values
- Parsing errors don't halt the entire process
- Raw data is always preserved alongside interpreted data
- Flexible parsing accommodates variations in file format

## Extension Points

The modular architecture makes it easy to extend:
- Add new event types by updating the mapping dictionaries
- Add new parsing functions in `parsers.py`
- Extend date parsing capabilities in `utils.py`
- Add new block types by extending the main parser class

This architecture ensures the parser remains maintainable, testable, and extensible while preserving all the functionality of the original monolithic implementation.