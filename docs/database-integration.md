# Database Integration Documentation

## Overview

This document describes the PostgreSQL database integration for the Genealogy API, which modernizes the legacy GeneWeb file-based system with a proper relational database using SQLModel (SQLAlchemy + Pydantic).

## Quick Start

To get started with the database integration:

1. Copy the environment configuration:
   ```bash
   cp env.example .env
   ```

2. Start the development environment:
   ```bash
   make up-dev
   ```

3. Access the API documentation at `http://localhost:8000/docs`

4. Run tests to verify everything works:
   ```bash
   make test-server
   ```

**Important:** Always use Makefile commands (`make <command>`) instead of running `docker-compose` directly. The Makefile provides a consistent interface and ensures proper configuration.

## Architecture

### System Components

The application consists of three main Docker services:

1. **postgres-dev** (PostgreSQL 16 Alpine)
   - Database server running on port 5432
   - Persistent data storage using Docker volumes
   - Configured via environment variables

2. **server-dev** (FastAPI Application)
   - Python FastAPI backend on port 8000
   - Connects to PostgreSQL database
   - Provides REST API endpoints
   - Auto-generates OpenAPI documentation

3. **client-dev** (Vue.js Application)
   - Frontend application on port 5173
   - Vue.js with TypeScript
   - Communicates with the FastAPI backend

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

- **Database**: PostgreSQL 16 (Alpine)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **API Framework**: FastAPI
- **Connection**: psycopg2-binary
- **Environment**: python-dotenv
- **Containerization**: Docker with Docker Compose

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

**Note for Docker Development**: When running in Docker, the `DATABASE_URL` hostname should be `postgres-dev` instead of `localhost`. The docker-compose configuration automatically sets this:
```bash
DATABASE_URL=postgresql://genealogy_user:genealogy_password@postgres-dev:5432/genealogy_db
```

### 2. Development Setup

Start the development environment using the Makefile:

```bash
# Start all services including PostgreSQL
make up-dev

# Stop development environment
make down-dev

# View logs
make logs-dev
```

**Note:** The Makefile wraps Docker Compose commands and provides a consistent interface for managing the application. Always use `make` commands instead of running `docker-compose` directly.

### 3. Production Setup

Deploy the production environment using the Makefile:

```bash
# Start production services
make up-prod

# Stop production services
make down-prod

# View logs
make logs-prod
```

## Implementation Details

### Database Connection

The database connection is managed in `server/src/db.py`:

- Connection URL is read from the `DATABASE_URL` environment variable
- SQLModel engine is created with connection pooling
- Tables are automatically created on application startup via the FastAPI lifespan context manager
- Database sessions are provided via dependency injection using `get_session()`

### Application Lifecycle

The FastAPI application (`server/src/main.py`) uses a lifespan context manager to:
1. Create database tables on startup if they don't exist
2. Ensure proper cleanup on shutdown

### Models

Models are defined in `server/src/models/` using SQLModel, which combines SQLAlchemy and Pydantic:

- Each entity has a base model (e.g., `Person`), a create model (e.g., `PersonCreate`), and an update model (e.g., `PersonUpdate`)
- Models include validation for field types, lengths, and constraints
- UUIDs are automatically generated for primary keys
- Enums are used for constrained fields (e.g., `Sex` enum for person gender)

### CRUD Operations

The application provides comprehensive CRUD operations for all entities through singleton CRUD instances in `server/src/crud/`:

#### Person Operations (`person_crud`)
- `create(db, person)`: Create a new person
- `get(db, person_id)`: Get person by UUID
- `get_all(db, skip, limit)`: Get all persons with pagination
- `get_by_name(db, first_name, last_name)`: Get persons by exact name match
- `search_by_name(db, name)`: Search persons by partial name (case-sensitive)
- `update(db, person_id, person_update)`: Update person information
- `delete(db, person_id)`: Delete a person

#### Family Operations (`family_crud`)
- `create(db, family)`: Create a new family
- `get(db, family_id)`: Get family by UUID
- `get_all(db, skip, limit)`: Get all families with pagination
- `get_by_husband(db, husband_id)`: Get families by husband UUID
- `get_by_wife(db, wife_id)`: Get families by wife UUID
- `get_by_spouse(db, spouse_id)`: Get families by spouse UUID (either husband or wife)
- `update(db, family_id, family_update)`: Update family information
- `delete(db, family_id)`: Delete a family

#### Child Operations (`child_crud`)
- `create(db, child)`: Create a child-family relationship
- `get(db, family_id, child_id)`: Get specific child relationship
- `get_by_family(db, family_id)`: Get all children of a family
- `get_by_child(db, child_id)`: Get all families where a person is a child
- `get_all(db, skip, limit)`: Get all child relationships with pagination
- `delete(db, family_id, child_id)`: Delete a child relationship
- `delete_by_family(db, family_id)`: Delete all child relationships for a family
- `delete_by_child(db, child_id)`: Delete all family relationships for a child

#### Event Operations (`event_crud`)
- `create(db, event)`: Create a new event
- `get(db, event_id)`: Get event by UUID
- `get_all(db, skip, limit)`: Get all events with pagination
- `get_by_person(db, person_id)`: Get all events for a person
- `get_by_family(db, family_id)`: Get all events for a family
- `get_by_type(db, event_type)`: Get all events of a specific type
- `search_by_type(db, event_type)`: Search events by type (partial match)
- `update(db, event_id, event_update)`: Update event information
- `delete(db, event_id)`: Delete an event

## Security Considerations

- Database credentials are managed through environment variables
- Default credentials are provided for development only
- Production deployments should use strong, unique passwords
- Database connections use SSL in production environments
- Never commit `.env` files to version control

## Performance Considerations

- UUID primary keys provide good distribution and avoid sequential bottlenecks
- Indexes are automatically created on foreign key columns
- Pagination is implemented for all list operations
- Connection pooling is handled by SQLAlchemy
