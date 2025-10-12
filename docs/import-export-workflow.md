# Import/Export Workflow Documentation

## Overview

This document explains the complete workflow for importing and exporting GeneWeb data, including the parsing, conversion, and serialization processes.

## Data Flow Architecture

```
GeneWeb File (.gw) → Parser → Converter → Database
Database → Converter → Serializer → GeneWeb File (.gw)
```

## Import Workflow

### 1. File Upload (`POST /api/v1/files/import`)

**Input**: GeneWeb `.gw` or `.gwplus` file
**Process**:
1. Asynchronous file upload using `aiofiles`
2. Temporary file creation with `.gw` suffix
3. File content written to temporary location

### 2. Parsing Phase

**Parser**: `GWParser` class
**Components**:
- `HeaderParser`: File headers and metadata
- `FamilyParser`: Family blocks and relationships  
- `BlockParser`: Notes, events, extended pages
- `PersonParser`: Person data extraction
- `EventParser`: Event parsing and interpretation

**Output**: Structured `ParserResult` dictionary
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

### 3. Entity Extraction

**Converter**: `extract_entities()` function
**Process**:
1. Extract persons from family data
2. Build family relationships
3. Extract events and children
4. Generate unique IDs for entities

**Output**: Flat entity structure
```json
{
  "persons": [...],
  "families": [...],
  "events": [...],
  "children": [...]
}
```

### 4. Database Storage

**Function**: `json_to_db()`
**Process**:
1. Create person records
2. Create family records with relationships
3. Create event records
4. Create child relationship records

**Output**: Database entities with generated IDs

## Export Workflow

### 1. Database Query (`GET /api/v1/files/export`)

**Function**: `db_to_json()`
**Process**:
1. Query all persons, families, events, children
2. Build relationship maps
3. Convert to JSON structure

### 2. Data Normalization

**Function**: `normalize_db_json()`
**Process**:
1. Build person lookup tables
2. Group children by family
3. Create family structures
4. Prepare for serialization

### 3. Serialization Phase

**Serializer**: `GWSerializer` class
**Components**:
- `FamilySerializer`: Family blocks and relationships
- `PersonSerializer`: Person events and data
- `EventSerializer`: Event formatting
- `NotesSerializer`: Notes and database notes
- `PageSerializer`: Extended pages

**Output**: GeneWeb `.gw` file content

### 4. File Generation

**Process**:
1. Generate complete `.gw` file content
2. Set appropriate headers and metadata
3. Return as downloadable file

## Key Components

### Parser System (`src/parsing/`)
- **Modular Design**: Specialized parsers for different block types
- **Position-Based**: Uses line position tracking for navigation
- **Error Handling**: Graceful degradation for malformed data

### Converter System (`src/converter/`)
- **Entity Extraction**: Transform parsed data to database entities
- **Field Ensuring**: Ensure required fields are present
- **Data Normalization**: Prepare data for serialization

### Serializer System (`src/serializer/`)
- **Complete GeneWeb Support**: All block types and features
- **Round-Trip Compatibility**: Preserves data through import/export cycles
- **Format Compliance**: Generates valid GeneWeb files

## API Endpoints

### Import Endpoint
```http
POST /api/v1/files/import
Content-Type: multipart/form-data

Response:
{
  "message": "GeneWeb file imported successfully",
  "persons": 25,
  "families": 12, 
  "events": 45,
  "children": 18
}
```

### Export Endpoint
```http
GET /api/v1/files/export

Response: File download (geneweb_export.gw)
```

We can also import and export from/as json.

## Error Handling

- **File Processing**: Asynchronous I/O with proper cleanup
- **Parsing Errors**: Graceful handling of malformed GeneWeb files
- **Database Errors**: Transaction rollback on failures
- **Validation**: Input validation and error messages

## Performance Considerations

- **Asynchronous I/O**: Non-blocking file operations
- **Memory Efficiency**: Streaming file processing
- **Database Optimization**: Batch operations where possible
- **Temporary Files**: Proper cleanup of temporary files

## Testing

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Round-Trip Tests**: Import → Export → Import validation
- **Edge Cases**: Malformed data, missing fields, special characters

This workflow ensures reliable, efficient, and maintainable import/export functionality for GeneWeb data.
