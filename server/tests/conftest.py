"""Test configuration and fixtures."""

import os
import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient

from src.main import app
from src.db import get_session
from src.models.person import Person, PersonCreate, Sex
from src.models.family import Family, FamilyCreate
from src.models.child import Child, ChildCreate
from src.models.event import Event, EventCreate


# Test database configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    os.getenv("DATABASE_URL", "sqlite:///./test.db")
)

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL, echo=False)

# Enable foreign key constraints for SQLite
if TEST_DATABASE_URL.startswith("sqlite"):
    from sqlalchemy import event
    
    @event.listens_for(test_engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test."""
    # Create all tables
    SQLModel.metadata.create_all(test_engine)
    
    # Create session
    with Session(test_engine) as session:
        yield session
    
    # Clean up - drop all tables
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with database dependency override."""
    def get_test_session():
        yield test_db
    
    app.dependency_overrides[get_session] = get_test_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_person_data():
    """Sample person data for testing."""
    return PersonCreate(
        first_name="John",
        last_name="Doe",
        sex=Sex.MALE,
        birth_date="1990-01-01",
        birth_place="New York",
        occupation="Engineer",
        notes="Test person"
    )


@pytest.fixture
def sample_person_data_2():
    """Second sample person data for testing."""
    return PersonCreate(
        first_name="Jane",
        last_name="Smith",
        sex=Sex.FEMALE,
        birth_date="1992-05-15",
        birth_place="Los Angeles",
        occupation="Doctor",
        notes="Test person 2"
    )


@pytest.fixture
def sample_family_data():
    """Sample family data for testing."""
    return FamilyCreate(
        marriage_date="2015-06-20",
        marriage_place="Las Vegas",
        notes="Test family"
    )


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return EventCreate(
        type="Birth",
        date="1990-01-01",
        place="New York",
        description="Birth event"
    )


@pytest.fixture
def sample_person(test_db, sample_person_data):
    """Create a sample person in the test database."""
    from src.crud.person import person_crud
    return person_crud.create(test_db, sample_person_data)


@pytest.fixture
def sample_person_2(test_db, sample_person_data_2):
    """Create a second sample person in the test database."""
    from src.crud.person import person_crud
    return person_crud.create(test_db, sample_person_data_2)


@pytest.fixture
def sample_family(test_db, sample_family_data, sample_person, sample_person_2):
    """Create a sample family in the test database."""
    from src.crud.family import family_crud
    
    # Update family data with person IDs
    family_data = FamilyCreate(
        husband_id=sample_person.id,
        wife_id=sample_person_2.id,
        marriage_date="2015-06-20",
        marriage_place="Las Vegas",
        notes="Test family"
    )
    
    return family_crud.create(test_db, family_data)


@pytest.fixture
def sample_child(test_db, sample_family, sample_person):
    """Create a sample child relationship in the test database."""
    from src.crud.child import child_crud
    
    child_data = ChildCreate(
        family_id=sample_family.id,
        child_id=sample_person.id
    )
    
    return child_crud.create(test_db, child_data)


@pytest.fixture
def sample_event(test_db, sample_event_data, sample_person):
    """Create a sample event in the test database."""
    from src.crud.event import event_crud
    
    event_data = EventCreate(
        person_id=sample_person.id,
        type="Birth",
        date="1990-01-01",
        place="New York",
        description="Birth event"
    )
    
    return event_crud.create(test_db, event_data)
