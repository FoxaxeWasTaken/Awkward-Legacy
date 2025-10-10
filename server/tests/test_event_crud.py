import pytest
from uuid import uuid4
from datetime import date

from src.crud.event import event_crud
from src.models.event import EventCreate, EventUpdate


class TestEventCRUD:
    """Test class for Event CRUD operations."""

    def test_create_event(self, test_db, sample_event_data, sample_person):
        """Test creating a new event."""
        event_data = EventCreate(
            person_id=sample_person.id,
            type="Birth",
            date="1990-01-01",
            place="New York",
            description="Birth event",
        )

        created_event = event_crud.create(test_db, event_data)

        assert created_event is not None
        assert created_event.id is not None
        assert created_event.person_id == sample_person.id
        assert created_event.family_id is None
        assert created_event.type == "Birth"
        assert created_event.date == date(1990, 1, 1)
        assert created_event.place == "New York"
        assert created_event.description == "Birth event"

    def test_create_event_minimal_data(self, test_db):
        """Test creating an event with minimal required data."""
        minimal_event = EventCreate(type="Test Event")

        created_event = event_crud.create(test_db, minimal_event)

        assert created_event is not None
        assert created_event.id is not None
        assert created_event.type == "Test Event"
        assert created_event.person_id is None
        assert created_event.family_id is None
        assert created_event.date is None
        assert created_event.place is None
        assert created_event.description is None

    def test_create_event_with_family(self, test_db, sample_family):
        """Test creating an event associated with a family."""
        event_data = EventCreate(
            family_id=sample_family.id,
            type="Marriage",
            date="2015-06-20",
            place="Las Vegas",
            description="Wedding ceremony",
        )

        created_event = event_crud.create(test_db, event_data)

        assert created_event is not None
        assert created_event.family_id == sample_family.id
        assert created_event.person_id is None
        assert created_event.type == "Marriage"
        assert created_event.date == date(2015, 6, 20)
        assert created_event.place == "Las Vegas"
        assert created_event.description == "Wedding ceremony"

    def test_create_event_with_both_person_and_family(
        self, test_db, sample_person, sample_family
    ):
        """Test creating an event associated with both person and family."""
        event_data = EventCreate(
            person_id=sample_person.id,
            family_id=sample_family.id,
            type="Birth",
            date="1990-01-01",
            place="New York",
            description="Birth in family context",
        )

        created_event = event_crud.create(test_db, event_data)

        assert created_event is not None
        assert created_event.person_id == sample_person.id
        assert created_event.family_id == sample_family.id
        assert created_event.type == "Birth"

    def test_get_event_by_id(self, test_db, sample_event):
        """Test getting an event by ID."""
        retrieved_event = event_crud.get(test_db, sample_event.id)

        assert retrieved_event is not None
        assert retrieved_event.id == sample_event.id
        assert retrieved_event.type == sample_event.type
        assert retrieved_event.person_id == sample_event.person_id

    def test_get_event_by_id_not_found(self, test_db):
        """Test getting an event by non-existent ID."""
        non_existent_id = uuid4()

        retrieved_event = event_crud.get(test_db, non_existent_id)

        assert retrieved_event is None

    def test_get_all_events_empty(self, test_db):
        """Test getting all events when database is empty."""
        events = event_crud.get_all(test_db)

        assert events == []

    def test_get_all_events_with_data(self, test_db, sample_event):
        """Test getting all events with data."""
        events = event_crud.get_all(test_db)

        assert len(events) == 1
        assert events[0].id == sample_event.id

    def test_get_all_events_with_pagination(self, test_db, sample_person):
        """Test getting all events with pagination."""
        for i in range(5):
            event_data = EventCreate(
                person_id=sample_person.id, type=f"Event{i}", date=f"199{i}-01-01"
            )
            event_crud.create(test_db, event_data)

        events = event_crud.get_all(test_db, skip=0, limit=3)

        assert len(events) == 3

        events = event_crud.get_all(test_db, skip=3, limit=2)

        assert len(events) == 2

    def test_get_by_person(self, test_db, sample_event, sample_person):
        """Test getting all events for a person."""
        events = event_crud.get_by_person(test_db, sample_person.id)

        assert len(events) == 1
        assert events[0].id == sample_event.id
        assert events[0].person_id == sample_person.id

    def test_get_by_person_multiple_events(self, test_db, sample_person):
        """Test getting multiple events for a person."""
        for i in range(3):
            event_data = EventCreate(
                person_id=sample_person.id, type=f"Event{i}", date=f"199{i}-01-01"
            )
            event_crud.create(test_db, event_data)

        events = event_crud.get_by_person(test_db, sample_person.id)

        assert len(events) == 3
        for event in events:
            assert event.person_id == sample_person.id

    def test_get_by_person_no_events(self, test_db, sample_person):
        """Test getting events for a person with no events."""
        events = event_crud.get_by_person(test_db, sample_person.id)

        assert events == []

    def test_get_by_person_non_existent(self, test_db):
        """Test getting events for a non-existent person."""
        non_existent_id = uuid4()

        events = event_crud.get_by_person(test_db, non_existent_id)

        assert events == []

    def test_get_by_family(self, test_db, sample_family):
        """Test getting all events for a family."""
        event_data = EventCreate(
            family_id=sample_family.id, type="Marriage", date="2015-06-20"
        )
        event = event_crud.create(test_db, event_data)

        events = event_crud.get_by_family(test_db, sample_family.id)

        assert len(events) == 1
        assert events[0].id == event.id
        assert events[0].family_id == sample_family.id

    def test_get_by_family_multiple_events(self, test_db, sample_family):
        """Test getting multiple events for a family."""
        for i in range(3):
            event_data = EventCreate(
                family_id=sample_family.id, type=f"FamilyEvent{i}", date=f"201{i}-01-01"
            )
            event_crud.create(test_db, event_data)

        events = event_crud.get_by_family(test_db, sample_family.id)

        assert len(events) == 3
        for event in events:
            assert event.family_id == sample_family.id

    def test_get_by_family_no_events(self, test_db, sample_family):
        """Test getting events for a family with no events."""
        events = event_crud.get_by_family(test_db, sample_family.id)

        assert events == []

    def test_get_by_family_non_existent(self, test_db):
        """Test getting events for a non-existent family."""
        non_existent_id = uuid4()

        events = event_crud.get_by_family(test_db, non_existent_id)

        assert events == []

    def test_get_by_type(self, test_db, sample_event):
        """Test getting all events of a specific type."""
        events = event_crud.get_by_type(test_db, "Birth")

        assert len(events) == 1
        assert events[0].id == sample_event.id
        assert events[0].type == "Birth"

    def test_get_by_type_multiple_events(self, test_db, sample_person):
        """Test getting multiple events of the same type."""
        for i in range(3):
            event_data = EventCreate(
                person_id=sample_person.id, type="Birth", date=f"199{i}-01-01"
            )
            event_crud.create(test_db, event_data)

        events = event_crud.get_by_type(test_db, "Birth")

        assert len(events) == 3
        for event in events:
            assert event.type == "Birth"

    def test_get_by_type_no_events(self, test_db):
        """Test getting events of a type that doesn't exist."""
        events = event_crud.get_by_type(test_db, "NonExistent")

        assert events == []

    def test_search_by_type(self, test_db, sample_person):
        """Test searching events by type with partial match."""
        event1_data = EventCreate(
            person_id=sample_person.id, type="Birth Certificate", date="1990-01-01"
        )
        event_crud.create(test_db, event1_data)

        event2_data = EventCreate(
            person_id=sample_person.id, type="Birth Registration", date="1990-01-02"
        )
        event_crud.create(test_db, event2_data)

        event3_data = EventCreate(
            person_id=sample_person.id, type="Death", date="2020-01-01"
        )
        event_crud.create(test_db, event3_data)

        events = event_crud.search_by_type(test_db, "Birth")

        assert len(events) == 2
        for event in events:
            assert "Birth" in event.type

    def test_search_by_type_no_matches(self, test_db, sample_person):
        """Test searching events by type with no matches."""
        event_data = EventCreate(
            person_id=sample_person.id, type="Birth", date="1990-01-01"
        )
        event_crud.create(test_db, event_data)

        events = event_crud.search_by_type(test_db, "Death")

        assert events == []

    def test_search_by_type_case_sensitive(self, test_db, sample_person):
        """Test that type search is case sensitive."""
        event_data = EventCreate(
            person_id=sample_person.id, type="Birth", date="1990-01-01"
        )
        event_crud.create(test_db, event_data)

        events = event_crud.search_by_type(test_db, "birth")

        assert events == []

    def test_update_event_full_update(
        self, test_db, sample_event, sample_person, sample_family
    ):
        """Test updating an event with all fields."""
        update_data = EventUpdate(
            person_id=sample_person.id,
            family_id=sample_family.id,
            type="Updated Event",
            date=date(2020, 1, 1),
            place="Updated Place",
            description="Updated description",
        )

        updated_event = event_crud.update(test_db, sample_event.id, update_data)

        assert updated_event is not None
        assert updated_event.id == sample_event.id
        assert updated_event.person_id == sample_person.id
        assert updated_event.family_id == sample_family.id
        assert updated_event.type == "Updated Event"
        assert updated_event.date == date(2020, 1, 1)
        assert updated_event.place == "Updated Place"
        assert updated_event.description == "Updated description"

    def test_update_event_partial_update(self, test_db, sample_event):
        """Test updating an event with only some fields."""
        update_data = EventUpdate(type="Updated Type", place="Updated Place")

        updated_event = event_crud.update(test_db, sample_event.id, update_data)

        assert updated_event is not None
        assert updated_event.id == sample_event.id
        assert updated_event.type == "Updated Type"
        assert updated_event.place == "Updated Place"
        assert updated_event.person_id == sample_event.person_id
        assert updated_event.family_id == sample_event.family_id
        assert updated_event.date == sample_event.date
        assert updated_event.description == sample_event.description

    def test_update_event_clear_fields(self, test_db, sample_event):
        """Test updating an event to clear some fields."""
        update_data = EventUpdate(
            person_id=None, family_id=None, place=None, description=None
        )

        updated_event = event_crud.update(test_db, sample_event.id, update_data)

        assert updated_event is not None
        assert updated_event.id == sample_event.id
        assert updated_event.person_id is None
        assert updated_event.family_id is None
        assert updated_event.place is None
        assert updated_event.description is None
        assert updated_event.type == sample_event.type
        assert updated_event.date == sample_event.date

    def test_update_event_not_found(self, test_db):
        """Test updating a non-existent event."""
        non_existent_id = uuid4()
        update_data = EventUpdate(type="Updated")

        updated_event = event_crud.update(test_db, non_existent_id, update_data)

        assert updated_event is None

    def test_delete_event(self, test_db, sample_event):
        """Test deleting an event."""
        result = event_crud.delete(test_db, sample_event.id)

        assert result is True

        deleted_event = event_crud.get(test_db, sample_event.id)
        assert deleted_event is None

    def test_delete_event_not_found(self, test_db):
        """Test deleting a non-existent event."""
        non_existent_id = uuid4()

        result = event_crud.delete(test_db, non_existent_id)

        assert result is False

    def test_event_relationships(self, test_db, sample_event):
        """Test that event relationships are properly established."""
        retrieved_event = event_crud.get(test_db, sample_event.id)

        assert retrieved_event is not None

    def test_event_date_validation(self, test_db, sample_person):
        """Test event date field validation."""
        from pydantic_core import ValidationError

        with pytest.raises(ValidationError):
            event_data = EventCreate(
                person_id=sample_person.id, type="Test Event", date="invalid-date"
            )

    def test_event_field_lengths(self, test_db, sample_person):
        """Test event field length constraints."""
        from pydantic_core import ValidationError

        long_type = "A" * 51

        with pytest.raises(ValidationError):
            event_data = EventCreate(person_id=sample_person.id, type=long_type)

    def test_event_foreign_key_constraints(self, test_db):
        """Test event foreign key constraints."""
        from sqlalchemy.exc import IntegrityError

        non_existent_person_id = uuid4()
        non_existent_family_id = uuid4()

        event_data = EventCreate(
            person_id=non_existent_person_id,
            family_id=non_existent_family_id,
            type="Test Event",
        )

        with pytest.raises(IntegrityError):
            event_crud.create(test_db, event_data)

    def test_event_type_validation(self, test_db, sample_person):
        """Test event type validation."""
        event_data = EventCreate(person_id=sample_person.id, type="")

        event = event_crud.create(test_db, event_data)
        assert event.type == ""

    def test_event_cascade_behavior(self, test_db, sample_person, sample_family):
        """Test cascade behavior when related entities are deleted."""
        person_event_data = EventCreate(person_id=sample_person.id, type="Person Event")
        person_event = event_crud.create(test_db, person_event_data)

        family_event_data = EventCreate(family_id=sample_family.id, type="Family Event")
        family_event = event_crud.create(test_db, family_event_data)

        from src.crud.person import person_crud

        person_crud.delete(test_db, sample_person.id)

        remaining_person_event = event_crud.get(test_db, person_event.id)
        assert remaining_person_event is None

        from src.crud.family import family_crud

        family_crud.delete(test_db, sample_family.id)

        remaining_family_event = event_crud.get(test_db, family_event.id)
        assert remaining_family_event is None
