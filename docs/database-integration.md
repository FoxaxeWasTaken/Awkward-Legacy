# Database Integration Documentation

## Overview

This document describes the PostgreSQL database integration for the Genealogy API, which modernizes the legacy GeneWeb file-based system with a proper relational database using SQLModel (SQLAlchemy + Pydantic).

## Architecture

### Database Schema

The database schema is inspired by the GeneWeb legacy data model and includes four core entities:

#### Person
- **id**: UUID (Primary Key)
- **first_name**: String (Given name)
- **last_name**: String (Surname)
- **sex**: Enum('M','F','U') (Biological sex / unknown)
- **birth_date**: Date (nullable)
- **death_date**: Date (nullable)
- **birth_place**: String (nullable)
- **death_place**: String (nullable)
- **occupation**: String (nullable)
- **notes**: Text (nullable)

#### Family
- **id**: UUID (Primary Key)
- **husband_id**: UUID (Foreign Key → Person.id, nullable)
- **wife_id**: UUID (Foreign Key → Person.id, nullable)
- **marriage_date**: Date (nullable)
- **marriage_place**: String (nullable)
- **notes**: Text (nullable)

#### Child (Association Table)
- **family_id**: UUID (Foreign Key → Family.id, Primary Key)
- **child_id**: UUID (Foreign Key → Person.id, Primary Key)

#### Event
- **id**: UUID (Primary Key)
- **person_id**: UUID (Foreign Key → Person.id, nullable)
- **family_id**: UUID (Foreign Key → Family.id, nullable)
- **type**: String (e.g., "birth", "baptism", "death", "marriage")
- **date**: Date (nullable)
- **place**: String (nullable)
- **description**: Text (nullable)

## Technology Stack

- **Database**: PostgreSQL 15
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Connection**: psycopg2-binary
- **Environment**: python-dotenv

## Setup Instructions

### 1. Environment Configuration

Create a `.env` file in the project root (copy from `env.example`):

```bash
# Database Configuration
DATABASE_URL=postgresql://genealogy_user:genealogy_password@localhost:5432/genealogy_db

# PostgreSQL Configuration
POSTGRES_DB=genealogy_db
POSTGRES_USER=genealogy_user
POSTGRES_PASSWORD=genealogy_password

# Application Configuration
NODE_ENV=development
```

### 2. Development Setup

Start the development environment:

```bash
# Start all services including PostgreSQL
docker-compose -f docker-compose.dev.yml up --build

# Or start only the database
docker-compose -f docker-compose.dev.yml up postgres-dev
```

### 3. Production Setup

Deploy the production environment:

```bash
# Start production services
docker-compose -f docker-compose.prod.yml up --build -d
```

## API Usage

### Database Connection

The database connection is automatically initialized when the FastAPI application starts. The connection URL is read from the `DATABASE_URL` environment variable.

### CRUD Operations

The application provides comprehensive CRUD operations for all entities:

#### Person Operations
- `create()`: Create a new person
- `get()`: Get person by ID
- `get_all()`: Get all persons with pagination
- `get_by_name()`: Get persons by exact first and last name
- `search_by_name()`: Search persons by name (partial match)
- `update()`: Update person information
- `delete()`: Delete a person

#### Family Operations
- `create()`: Create a new family
- `get()`: Get family by ID
- `get_all()`: Get all families with pagination
- `get_by_husband()`: Get families by husband ID
- `get_by_wife()`: Get families by wife ID
- `get_by_spouse()`: Get families by spouse ID (either husband or wife)
- `update()`: Update family information
- `delete()`: Delete a family

#### Child Operations
- `create()`: Create a child relationship
- `get()`: Get child relationship by family and child IDs
- `get_by_family()`: Get all children of a family
- `get_by_child()`: Get all families where a person is a child
- `get_all()`: Get all child relationships with pagination
- `delete()`: Delete a child relationship
- `delete_by_family()`: Delete all child relationships for a family
- `delete_by_child()`: Delete all family relationships for a child

#### Event Operations
- `create()`: Create a new event
- `get()`: Get event by ID
- `get_all()`: Get all events with pagination
- `get_by_person()`: Get all events for a person
- `get_by_family()`: Get all events for a family
- `get_by_type()`: Get all events of a specific type
- `search_by_type()`: Search events by type (partial match)
- `update()`: Update event information
- `delete()`: Delete an event

## Health Check

The API provides a health check endpoint at `/health` that verifies database connectivity:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Testing

Run the database tests:

```bash
# Run all tests
pytest server/src/tests/test_database.py

# Run with coverage
pytest server/src/tests/test_database.py --cov=server/src
```

## Migration from Legacy System

This database integration provides the foundation for importing legacy GeneWeb `.gw` files. Future import scripts will:

1. Parse `.gw` files
2. Extract genealogical data
3. Transform data to match the new schema
4. Import data using the CRUD operations

## Security Considerations

- Database credentials are managed through environment variables
- Default credentials are provided for development only
- Production deployments should use strong, unique passwords
- Database connections use SSL in production environments

## Performance Considerations

- UUID primary keys provide good distribution and avoid sequential bottlenecks
- Indexes are automatically created on foreign key columns
- Pagination is implemented for all list operations
- Connection pooling is handled by SQLAlchemy

## Future Enhancements

- Database migrations using Alembic
- Full-text search capabilities
- Advanced querying with GraphQL
- Data validation and constraints
- Audit logging for data changes
- Backup and recovery procedures
