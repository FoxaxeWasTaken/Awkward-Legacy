# GeneWeb Serializer Architecture and Documentation

## Overview

The GeneWeb Serializer is a modular system designed to take clean, structured GeneWeb structured JSON output and regenerate a valid `.gw` file.
Its goal is to preserve as much of the original file structure as possible, so the regenerated `.gw` can be parsed back to the **same JSON** with minimal differences.

This serializer is designed to be **modular, extensible, and robust**, and follows a clear separation of responsibilities for different block types.

The serialization order is designed to respect GeneWeb file structure conventions, ensuring the resulting `.gw` is syntactically correct and parseable.

---

## Architecture

The serializer directory contains separate modules for each GeneWeb block type, plus helper utilities.

```
server/src/
├── serializer/
│   ├── gw_serializer.py         # Main GWSerializer class
│   ├── family_serializer.py     # Handles family blocks
│   ├── person_serializer.py     # Handles person-specific events
│   ├── event_serializer.py      # Handles events formatting
│   ├── notes_serializer.py      # Handles notes formatting
│   ├── page_serializer.py       # Handles extended pages
│   ├── sources_serializer.py    # Handles source references
│   ├── pevt_serializer.py       # Handles person events
│   └── utils.py                 # Helper serialization functions

docs/serializer/
├── test_serializer.py           # Example/test script
├── galichet.gw                  # Example .gw file
├── galichet.json                # Example .json file
```

---

### Module Breakdown

#### 1. `gw_serializer.py`

Entry point for serialization.

**Responsibilities:**
- Top-level coordination of serialization.
- Ensuring correct block ordering.
- Writing serialized content to file.

**Key methods:**
- `serialize()`: Returns the `.gw` content as a string.
- `to_file(path)`: Writes serialized content to disk.

---

#### 2. `family_serializer.py`

**Responsibilities:**
- Writing family header lines.
- Serializing family events (`fevt`).
- Serializing children with correct gender codes.
- Adding sources.

**Key functions:**
- `serialize_family(family: Dict[str, Any])`

---

#### 3. `person_serializer.py`

**Responsibilities:**
- Writing person event blocks (`pevt`).
- Formatting events in chronological order.
- Preserving raw event details.

**Key functions:**
- `serialize_person(person: Dict[str, Any])`
- `serialize_person_events(person: Dict[str, Any])`

---

#### 4. `event_serializer.py`

**Responsibilities:**
- Formatting event details.
- Maintaining exact raw content where possible.
- Handling event notes.

**Key functions:**
- `serialize_event(event: Dict[str, Any])`

---

#### 5. `notes_serializer.py`

**Responsibilities:**
- Preserving multi-line notes.
- Maintaining correct `beg`/`end` syntax.

**Key functions:**
- `serialize_notes(notes: list[Dict[str, str]])`
- `serialize_notes_db(notes_db: Dict[str, str])`

---

#### 6. `sources_serializer.py`

**Responsibilities:**
- Preserving all source references.
- Ensuring correct placement inside family blocks.

**Key functions:**
- `serialize_sources(sources: Dict[str, List[str]])`

Sources are grouped based on:
- `family_source`: serialized as `src` and `csrc`
- `children_source`: serialized as `csources`

---

#### 7. `page_serializer.py`

**Responsibilities:**
- Preserving all metadata and content for extended pages.

**Key functions:**
- `serialize_pages(pages: Dict[str, Dict[str, str]])`

---

#### 8. `utils.py`

**Responsibilities:**
- Providing helper functions for indentation, string normalization, and event formatting.

---

## Serialization Process

1. **Families (`fam` blocks)**
2. **Sources (`src`, `csrc`, `csources` lines)**
3. **Person events (`pevt` blocks)**
4. **Database notes (`notes-db` blocks)**
5. **Notes (`notes` blocks)**
6. **Extended pages (`page-ext` blocks)**

---

### Family Block Serialization

For each family:
- Write the family header line (`fam ...`).
- Write `src`/`csrc` lines if present.
- Write `fevt` event blocks.
- Write children with gender codes and tags.

---

### Person Event Serialization

For each person:
- Write a `pevt` block containing all events.
- Preserve raw event text.
- Avoid extra indentation.

---

### Notes Serialization

Write notes blocks while preserving multi-line content and special characters:
```
notes Name
beg
Note text here...
end notes
```

---

### Sources Serialization

Write source references grouped appropriately based on `"family_source"` and `"children_source"`.

---

### Extended Pages Serialization

Write extended page blocks preserving metadata:
```
page-ext PageName
TITLE=...
TYPE=...
Page content
end page-ext
```

---

## Design Goals

1. **Exact Round-Trip**: `.gw` → JSON → `.gw` produces equivalent `.gw`.
2. **Minimal Formatting Changes**: Preserve original style and tag placement.
3. **Full Compatibility**: Support all GeneWeb block types.
4. **Extensibility**: Easy to extend with new serializers.
5. **Maintainability**: Modular design.

---

## Usage Example

### Direct Usage
```python
from parser.gw_parser import GWParser
from serializer.gw_serializer import GWSerializer

parser = GWParser("input.gw")
data = parser.parse()

serializer = GWSerializer(data)
serializer.to_file("output.gw")
```

### API Integration
The serializer is integrated into the REST API for file export:

```python
# Export via API
GET /api/v1/files/export
# Exports database data to .gw format and returns as downloadable file
```

We can also export as json.

---

## `test_serializer.py` - Example/Test Script

A ready-to-use command-line script that demonstrates how to use the parser:
```bash
python3 -m docs.serializer.test_serializer docs/serializer/galichet.json galichet.gw
```

---

## Error Handling

- Missing optional fields are ignored.
- Unknown tags are preserved raw.
- Events and notes maintain original structure.
- Sources written only if present.
- Logs warnings for invalid fields if logging is enabled.

---

## Limitations

- Assumes input JSON follows GWParser structure.
- Custom GeneWeb extensions require additional serializers.
- Comments and spacing outside recognized blocks may not be preserved.

---

## Extension Points

- Add new block serializers.
- Modify existing serializers without affecting unrelated blocks.
- Change serialization order by modifying `GWSerializer.serialize()`.