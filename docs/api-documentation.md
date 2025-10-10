# Genealogy API Documentation

A modern genealogy application API built with FastAPI and PostgreSQL, providing comprehensive endpoints for managing persons, families, children relationships, and events.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, no authentication is required. All endpoints are publicly accessible.

## API Version
All endpoints are prefixed with `/api/v1/`

## Data Models

### Person
- `id`: UUID (auto-generated)
- `first_name`: string (required)
- `last_name`: string (required)
- `sex`: string (M/F/U) (required)
- `birth_date`: date (optional)
- `birth_place`: string (optional)
- `death_date`: date (optional)
- `death_place`: string (optional)
- `notes`: string (optional)

### Family
- `id`: UUID (auto-generated)
- `husband_id`: UUID (optional, foreign key to Person)
- `wife_id`: UUID (optional, foreign key to Person)
- `marriage_date`: date (optional)
- `marriage_place`: string (optional)
- `notes`: string (optional)

### Child
- `family_id`: UUID (required, foreign key to Family)
- `child_id`: UUID (required, foreign key to Person)

### Event
- `id`: UUID (auto-generated)
- `person_id`: UUID (optional, foreign key to Person)
- `family_id`: UUID (optional, foreign key to Family)
- `type`: string (required)
- `date`: date (optional)
- `place`: string (optional)
- `description`: string (optional)

## Endpoints

## Person Endpoints

### Create Person
**POST** `/api/v1/persons`

Create a new person.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "sex": "M",
  "birth_date": "1980-01-01",
  "birth_place": "New York",
  "death_date": null,
  "death_place": null,
  "notes": "Sample person"
}
```

**Response:** `201 Created`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "first_name": "John",
  "last_name": "Doe",
  "sex": "M",
  "birth_date": "1980-01-01",
  "birth_place": "New York",
  "death_date": null,
  "death_place": null,
  "notes": "Sample person"
}
```

**Validation Rules:**
- `first_name` and `last_name` cannot be empty
- `sex` must be "M", "F", or "U"
- `birth_date` and `death_date` cannot be in the future
- `death_date` cannot be before `birth_date`

### Get All Persons
**GET** `/api/v1/persons`

Get all persons with pagination.

**Query Parameters:**
- `skip`: integer (default: 0, minimum: 0) - Number of records to skip
- `limit`: integer (default: 100, minimum: 1, maximum: 1000) - Number of records to return

**Response:** `200 OK`
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "first_name": "John",
    "last_name": "Doe",
    "sex": "M",
    "birth_date": "1980-01-01",
    "birth_place": "New York",
    "death_date": null,
    "death_place": null,
    "notes": "Sample person"
  }
]
```

### Search Persons by Name
**GET** `/api/v1/persons/search`

Search persons by first name or last name.

**Query Parameters:**
- `q`: string (required) - Search query
- `skip`: integer (default: 0, minimum: 0)
- `limit`: integer (default: 100, minimum: 1, maximum: 1000)

**Response:** `200 OK`
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "first_name": "John",
    "last_name": "Doe",
    "sex": "M",
    "birth_date": "1980-01-01",
    "birth_place": "New York",
    "death_date": null,
    "death_place": null,
    "notes": "Sample person"
  }
]
```

### Get Person by Exact Name
**GET** `/api/v1/persons/by-name`

Get person by exact first name and last name.

**Query Parameters:**
- `first_name`: string (required)
- `last_name`: string (required)

**Response:** `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "first_name": "John",
  "last_name": "Doe",
  "sex": "M",
  "birth_date": "1980-01-01",
  "birth_place": "New York",
  "death_date": null,
  "death_place": null,
  "notes": "Sample person"
}
```

### Get Person by ID
**GET** `/api/v1/persons/{person_id}`

Get a specific person by ID.

**Path Parameters:**
- `person_id`: UUID (required)

**Response:** `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "first_name": "John",
  "last_name": "Doe",
  "sex": "M",
  "birth_date": "1980-01-01",
  "birth_place": "New York",
  "death_date": null,
  "death_place": null,
  "notes": "Sample person"
}
```

**Error Responses:**
- `404 Not Found` - Person not found
- `422 Unprocessable Entity` - Invalid UUID format

### Update Person (Full)
**PUT** `/api/v1/persons/{person_id}`

Update a person with all fields.

**Path Parameters:**
- `person_id`: UUID (required)

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "sex": "F",
  "birth_date": "1985-05-15",
  "birth_place": "Boston",
  "death_date": null,
  "death_place": null,
  "notes": "Updated person"
}
```

**Response:** `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "first_name": "Jane",
  "last_name": "Smith",
  "sex": "F",
  "birth_date": "1985-05-15",
  "birth_place": "Boston",
  "death_date": null,
  "death_place": null,
  "notes": "Updated person"
}
```

### Update Person (Partial)
**PATCH** `/api/v1/persons/{person_id}`

Partially update a person.

**Path Parameters:**
- `person_id`: UUID (required)

**Request Body:**
```json
{
  "first_name": "Jane",
  "notes": "Updated notes only"
}
```

**Response:** `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "first_name": "Jane",
  "last_name": "Doe",
  "sex": "M",
  "birth_date": "1980-01-01",
  "birth_place": "New York",
  "death_date": null,
  "death_place": null,
  "notes": "Updated notes only"
}
```

### Delete Person
**DELETE** `/api/v1/persons/{person_id}`

Delete a person.

**Path Parameters:**
- `person_id`: UUID (required)

**Response:** `204 No Content`

**Error Responses:**
- `404 Not Found` - Person not found

## Family Endpoints

### Create Family
**POST** `/api/v1/families`

Create a new family.

**Request Body:**
```json
{
  "husband_id": "123e4567-e89b-12d3-a456-426614174000",
  "wife_id": "123e4567-e89b-12d3-a456-426614174001",
  "marriage_date": "2005-06-20",
  "marriage_place": "New York City",
  "notes": "First marriage"
}
```

**Response:** `201 Created`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",
  "husband_id": "123e4567-e89b-12d3-a456-426614174000",
  "wife_id": "123e4567-e89b-12d3-a456-426614174001",
  "marriage_date": "2005-06-20",
  "marriage_place": "New York City",
  "notes": "First marriage"
}
```

**Validation Rules:**
- At least one spouse (husband_id or wife_id) must be provided
- Same person cannot be both husband and wife
- Marriage date cannot be in the future
- Marriage date must be after both spouses' birth dates
- Marriage date must be before both spouses' death dates (if applicable)
- Referenced persons must exist

### Get All Families
**GET** `/api/v1/families`

Get all families with pagination.

**Query Parameters:**
- `skip`: integer (default: 0, minimum: 0)
- `limit`: integer (default: 100, minimum: 1, maximum: 1000)

**Response:** `200 OK`
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174002",
    "husband_id": "123e4567-e89b-12d3-a456-426614174000",
    "wife_id": "123e4567-e89b-12d3-a456-426614174001",
    "marriage_date": "2005-06-20",
    "marriage_place": "New York City",
    "notes": "First marriage"
  }
]
```

### Get Family by ID
**GET** `/api/v1/families/{family_id}`

Get a specific family by ID.

**Path Parameters:**
- `family_id`: UUID (required)

**Response:** `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",
  "husband_id": "123e4567-e89b-12d3-a456-426614174000",
  "wife_id": "123e4567-e89b-12d3-a456-426614174001",
  "marriage_date": "2005-06-20",
  "marriage_place": "New York City",
  "notes": "First marriage"
}
```

### Update Family (Full)
**PUT** `/api/v1/families/{family_id}`

Update a family with all fields.

**Path Parameters:**
- `family_id`: UUID (required)

**Request Body:**
```json
{
  "husband_id": "123e4567-e89b-12d3-a456-426614174000",
  "wife_id": "123e4567-e89b-12d3-a456-426614174001",
  "marriage_date": "2005-06-20",
  "marriage_place": "Updated City",
  "notes": "Updated notes"
}
```

### Update Family (Partial)
**PATCH** `/api/v1/families/{family_id}`

Partially update a family.

**Path Parameters:**
- `family_id`: UUID (required)

**Request Body:**
```json
{
  "marriage_place": "Updated City",
  "notes": "Updated notes only"
}
```

### Delete Family
**DELETE** `/api/v1/families/{family_id}`

Delete a family.

**Path Parameters:**
- `family_id`: UUID (required)

**Response:** `204 No Content`

## Child Endpoints

### Create Child Relationship
**POST** `/api/v1/children`

Create a new child relationship between a family and a person.

**Request Body:**
```json
{
  "family_id": "123e4567-e89b-12d3-a456-426614174002",
  "child_id": "123e4567-e89b-12d3-a456-426614174003"
}
```

**Response:** `201 Created`
```json
{
  "family_id": "123e4567-e89b-12d3-a456-426614174002",
  "child_id": "123e4567-e89b-12d3-a456-426614174003"
}
```

**Validation Rules:**
- Family must exist
- Person must exist
- Person cannot be a parent in the same family (prevents circular relationships)
- Relationship must not already exist

### Get All Child Relationships
**GET** `/api/v1/children`

Get all child relationships with pagination.

**Query Parameters:**
- `skip`: integer (default: 0, minimum: 0)
- `limit`: integer (default: 100, minimum: 1, maximum: 1000)

**Response:** `200 OK`
```json
[
  {
    "family_id": "123e4567-e89b-12d3-a456-426614174002",
    "child_id": "123e4567-e89b-12d3-a456-426614174003"
  }
]
```

### Get Children by Family
**GET** `/api/v1/children/by-family/{family_id}`

Get all children of a specific family.

**Path Parameters:**
- `family_id`: UUID (required)

**Response:** `200 OK`
```json
[
  {
    "family_id": "123e4567-e89b-12d3-a456-426614174002",
    "child_id": "123e4567-e89b-12d3-a456-426614174003"
  }
]
```

### Get Families by Child
**GET** `/api/v1/children/by-child/{child_id}`

Get all families where a person is a child.

**Path Parameters:**
- `child_id`: UUID (required)

**Response:** `200 OK`
```json
[
  {
    "family_id": "123e4567-e89b-12d3-a456-426614174002",
    "child_id": "123e4567-e89b-12d3-a456-426614174003"
  }
]
```

### Get Specific Child Relationship
**GET** `/api/v1/children/{family_id}/{child_id}`

Get a specific child relationship.

**Path Parameters:**
- `family_id`: UUID (required)
- `child_id`: UUID (required)

**Response:** `200 OK`
```json
{
  "family_id": "123e4567-e89b-12d3-a456-426614174002",
  "child_id": "123e4567-e89b-12d3-a456-426614174003"
}
```

### Delete All Children by Family
**DELETE** `/api/v1/children/by-family/{family_id}`

Delete all child relationships for a family.

**Path Parameters:**
- `family_id`: UUID (required)

**Response:** `200 OK`
```json
{
  "deleted_count": 2
}
```

### Delete All Families by Child
**DELETE** `/api/v1/children/by-child/{child_id}`

Delete all child relationships for a child.

**Path Parameters:**
- `child_id`: UUID (required)

**Response:** `200 OK`
```json
{
  "deleted_count": 1
}
```

### Delete Specific Child Relationship
**DELETE** `/api/v1/children/{family_id}/{child_id}`

Delete a specific child relationship.

**Path Parameters:**
- `family_id`: UUID (required)
- `child_id`: UUID (required)

**Response:** `204 No Content`

## Event Endpoints

### Create Event
**POST** `/api/v1/events`

Create a new event.

**Request Body:**
```json
{
  "person_id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "Birth",
  "date": "1980-01-01",
  "place": "New York Hospital",
  "description": "Born in New York Hospital"
}
```

**Response:** `201 Created`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174004",
  "person_id": "123e4567-e89b-12d3-a456-426614174000",
  "family_id": null,
  "type": "Birth",
  "date": "1980-01-01",
  "place": "New York Hospital",
  "description": "Born in New York Hospital"
}
```

**Validation Rules:**
- Must be associated with either a person OR a family (not both, not neither)
- Event date cannot be in the future
- Event date must be after person's birth date (if person event)
- Event date must be before person's death date (if person event)
- Referenced person/family must exist

### Get All Events
**GET** `/api/v1/events`

Get all events with pagination.

**Query Parameters:**
- `skip`: integer (default: 0, minimum: 0)
- `limit`: integer (default: 100, minimum: 1, maximum: 1000)

**Response:** `200 OK`
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174004",
    "person_id": "123e4567-e89b-12d3-a456-426614174000",
    "family_id": null,
    "type": "Birth",
    "date": "1980-01-01",
    "place": "New York Hospital",
    "description": "Born in New York Hospital"
  }
]
```

### Search Events by Type
**GET** `/api/v1/events/search`

Search events by type.

**Query Parameters:**
- `q`: string (required) - Search query
- `skip`: integer (default: 0, minimum: 0)
- `limit`: integer (default: 100, minimum: 1, maximum: 1000)

**Response:** `200 OK`
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174004",
    "person_id": "123e4567-e89b-12d3-a456-426614174000",
    "family_id": null,
    "type": "Birth",
    "date": "1980-01-01",
    "place": "New York Hospital",
    "description": "Born in New York Hospital"
  }
]
```

### Get Events by Type
**GET** `/api/v1/events/by-type`

Get events by specific type.

**Query Parameters:**
- `type`: string (required) - Event type
- `skip`: integer (default: 0, minimum: 0)
- `limit`: integer (default: 100, minimum: 1, maximum: 1000)

**Response:** `200 OK`
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174004",
    "person_id": "123e4567-e89b-12d3-a456-426614174000",
    "family_id": null,
    "type": "Birth",
    "date": "1980-01-01",
    "place": "New York Hospital",
    "description": "Born in New York Hospital"
  }
]
```

### Get Events by Person
**GET** `/api/v1/events/by-person/{person_id}`

Get all events for a specific person.

**Path Parameters:**
- `person_id`: UUID (required)

**Response:** `200 OK`
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174004",
    "person_id": "123e4567-e89b-12d3-a456-426614174000",
    "family_id": null,
    "type": "Birth",
    "date": "1980-01-01",
    "place": "New York Hospital",
    "description": "Born in New York Hospital"
  }
]
```

### Get Events by Family
**GET** `/api/v1/events/by-family/{family_id}`

Get all events for a specific family.

**Path Parameters:**
- `family_id`: UUID (required)

**Response:** `200 OK`
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174005",
    "person_id": null,
    "family_id": "123e4567-e89b-12d3-a456-426614174002",
    "type": "Marriage",
    "date": "2005-06-20",
    "place": "New York City",
    "description": "Wedding ceremony"
  }
]
```

### Get Event by ID
**GET** `/api/v1/events/{event_id}`

Get a specific event by ID.

**Path Parameters:**
- `event_id`: UUID (required)

**Response:** `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174004",
  "person_id": "123e4567-e89b-12d3-a456-426614174000",
  "family_id": null,
  "type": "Birth",
  "date": "1980-01-01",
  "place": "New York Hospital",
  "description": "Born in New York Hospital"
}
```

### Update Event (Full)
**PUT** `/api/v1/events/{event_id}`

Update an event with all fields.

**Path Parameters:**
- `event_id`: UUID (required)

**Request Body:**
```json
{
  "person_id": "123e4567-e89b-12d3-a456-426614174000",
  "family_id": null,
  "type": "Updated Event",
  "date": "1980-01-01",
  "place": "Updated Place",
  "description": "Updated description"
}
```

### Update Event (Partial)
**PATCH** `/api/v1/events/{event_id}`

Partially update an event.

**Path Parameters:**
- `event_id`: UUID (required)

**Request Body:**
```json
{
  "type": "Updated Event",
  "description": "Updated description only"
}
```

### Delete Event
**DELETE** `/api/v1/events/{event_id}`

Delete an event.

**Path Parameters:**
- `event_id`: UUID (required)

**Response:** `204 No Content`

## System Endpoints

### Health Check
**GET** `/health`

Check the health of the API and database connection.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Root Endpoint
**GET** `/`

Get basic information about the API.

**Response:** `200 OK`
```json
{
  "Hello": "World",
  "message": "Genealogy API is running!",
  "docs": "/docs",
  "health": "/health"
}
```

## Error Responses

### Common Error Codes

- `400 Bad Request` - Invalid request data or business logic validation failed
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists (e.g., duplicate child relationship)
- `422 Unprocessable Entity` - Validation error (e.g., invalid UUID format, missing required fields)
- `500 Internal Server Error` - Server error

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Interactive API Documentation

The API includes interactive documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Running the API

### Prerequisites
- Docker and Docker Compose
- Make (optional, for convenience commands)

### Start the API
```bash
# Using Docker Compose
docker-compose -f docker-compose.dev.yml up

# Using Make (if available)
make dev
```

### Run Tests
```bash
# Using Docker Compose
docker-compose -f docker-compose.dev.yml exec server-dev python -m pytest tests/

# Using Make (if available)
make test-server
```

## Database Schema

The API uses PostgreSQL with the following main tables:
- `persons` - Stores person information
- `families` - Stores family relationships
- `children` - Junction table for child relationships
- `events` - Stores events associated with persons or families

All tables use UUID primary keys and include proper foreign key constraints for data integrity.
