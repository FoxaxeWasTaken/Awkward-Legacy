"""Tests for database integration."""

import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool

from ..db import get_session
from ..models.person import Person, PersonCreate, Sex
from ..models.family import Family, FamilyCreate
from ..models.child import Child, ChildCreate
from ..models.event import Event, EventCreate
from ..crud.person import person_crud
from ..crud.family import family_crud
from ..crud.child import child_crud
from ..crud.event import event_crud


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_create_person(session: Session):
    """Test creating a person."""
    person_data = PersonCreate(
        first_name="John",
        last_name="Doe",
        sex=Sex.MALE,
        birth_place="New York",
        occupation="Engineer",
    )
    person = person_crud.create(session, person_data)

    assert person.first_name == "John"
    assert person.last_name == "Doe"
    assert person.sex == Sex.MALE
    assert person.birth_place == "New York"
    assert person.occupation == "Engineer"
    assert person.id is not None


def test_create_family(session: Session):
    """Test creating a family."""
    # First create two people
    husband_data = PersonCreate(first_name="John", last_name="Doe", sex=Sex.MALE)
    wife_data = PersonCreate(first_name="Jane", last_name="Smith", sex=Sex.FEMALE)
    husband = person_crud.create(session, husband_data)
    wife = person_crud.create(session, wife_data)

    # Create family
    family_data = FamilyCreate(
        husband_id=husband.id, wife_id=wife.id, marriage_place="New York"
    )
    family = family_crud.create(session, family_data)

    assert family.husband_id == husband.id
    assert family.wife_id == wife.id
    assert family.marriage_place == "New York"
    assert family.id is not None


def test_create_child_relationship(session: Session):
    """Test creating a child relationship."""
    # Create family
    family_data = FamilyCreate()
    family = family_crud.create(session, family_data)

    # Create child
    child_data = PersonCreate(first_name="Child", last_name="Doe", sex=Sex.MALE)
    child = person_crud.create(session, child_data)

    # Create child relationship
    child_rel_data = ChildCreate(family_id=family.id, child_id=child.id)
    child_rel = child_crud.create(session, child_rel_data)

    assert child_rel.family_id == family.id
    assert child_rel.child_id == child.id


def test_create_event(session: Session):
    """Test creating an event."""
    # Create person
    person_data = PersonCreate(first_name="John", last_name="Doe", sex=Sex.MALE)
    person = person_crud.create(session, person_data)

    # Create event
    event_data = EventCreate(
        person_id=person.id,
        type="birth",
        place="New York",
        description="Born in New York",
    )
    event = event_crud.create(session, event_data)

    assert event.person_id == person.id
    assert event.type == "birth"
    assert event.place == "New York"
    assert event.description == "Born in New York"
    assert event.id is not None


def test_search_persons_by_name(session: Session):
    """Test searching persons by name."""
    # Create test persons
    person1_data = PersonCreate(first_name="John", last_name="Doe", sex=Sex.MALE)
    person2_data = PersonCreate(first_name="Jane", last_name="Doe", sex=Sex.FEMALE)
    person3_data = PersonCreate(first_name="John", last_name="Smith", sex=Sex.MALE)

    person_crud.create(session, person1_data)
    person_crud.create(session, person2_data)
    person_crud.create(session, person3_data)

    # Search by first name
    results = person_crud.search_by_name(session, "John")
    assert len(results) == 2

    # Search by last name
    results = person_crud.search_by_name(session, "Doe")
    assert len(results) == 2
