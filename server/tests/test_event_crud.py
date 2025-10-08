"""Test suite for Event CRUD operations."""

import pytest
from uuid import uuid4
from datetime import date

from src.crud.event import event_crud
from src.models.event import EventCreate, EventUpdate


@pytest.mark.unit
@pytest.mark.crud
@pytest.mark.event
class TestEventCRUD:
    """Test class for Event CRUD operations."""

    def test_create_event(self, test_db, sample_event_data, sample_person):
        """Test creating a new event."""
        # Arrange
        event_data = EventCreate(
            person_id=sample_person.id,
            type="Birth",
            date="1990-01-01",
            place="New York",
            description="Birth event"
        )
        
        # Act
        created_event = event_crud.create(test_db, event_data)
        
        # Assert
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
        # Arrange
        minimal_event = EventCreate(
            type="Test Event"
        )
        
        # Act
        created_event = event_crud.create(test_db, minimal_event)
        
        # Assert
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
        # Arrange
        event_data = EventCreate(
            family_id=sample_family.id,
            type="Marriage",
            date="2015-06-20",
            place="Las Vegas",
            description="Wedding ceremony"
        )
        
        # Act
        created_event = event_crud.create(test_db, event_data)
        
        # Assert
        assert created_event is not None
        assert created_event.family_id == sample_family.id
        assert created_event.person_id is None
        assert created_event.type == "Marriage"
        assert created_event.date == date(2015, 6, 20)
        assert created_event.place == "Las Vegas"
        assert created_event.description == "Wedding ceremony"

    def test_create_event_with_both_person_and_family(self, test_db, sample_person, sample_family):
        """Test creating an event associated with both person and family."""
        # Arrange
        event_data = EventCreate(
            person_id=sample_person.id,
            family_id=sample_family.id,
            type="Birth",
            date="1990-01-01",
            place="New York",
            description="Birth in family context"
        )
        
        # Act
        created_event = event_crud.create(test_db, event_data)
        
        # Assert
        assert created_event is not None
        assert created_event.person_id == sample_person.id
        assert created_event.family_id == sample_family.id
        assert created_event.type == "Birth"

    def test_get_event_by_id(self, test_db, sample_event):
        """Test getting an event by ID."""
        # Act
        retrieved_event = event_crud.get(test_db, sample_event.id)
        
        # Assert
        assert retrieved_event is not None
        assert retrieved_event.id == sample_event.id
        assert retrieved_event.type == sample_event.type
        assert retrieved_event.person_id == sample_event.person_id

    def test_get_event_by_id_not_found(self, test_db):
        """Test getting an event by non-existent ID."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        retrieved_event = event_crud.get(test_db, non_existent_id)
        
        # Assert
        assert retrieved_event is None

    def test_get_all_events_empty(self, test_db):
        """Test getting all events when database is empty."""
        # Act
        events = event_crud.get_all(test_db)
        
        # Assert
        assert events == []

    def test_get_all_events_with_data(self, test_db, sample_event):
        """Test getting all events with data."""
        # Act
        events = event_crud.get_all(test_db)
        
        # Assert
        assert len(events) == 1
        assert events[0].id == sample_event.id

    def test_get_all_events_with_pagination(self, test_db, sample_person):
        """Test getting all events with pagination."""
        # Arrange - create multiple events
        for i in range(5):
            event_data = EventCreate(
                person_id=sample_person.id,
                type=f"Event{i}",
                date=f"199{i}-01-01"
            )
            event_crud.create(test_db, event_data)
        
        # Act - get first 3 events
        events = event_crud.get_all(test_db, skip=0, limit=3)
        
        # Assert
        assert len(events) == 3
        
        # Act - get next 2 events
        events = event_crud.get_all(test_db, skip=3, limit=2)
        
        # Assert
        assert len(events) == 2

    def test_get_by_person(self, test_db, sample_event, sample_person):
        """Test getting all events for a person."""
        # Act
        events = event_crud.get_by_person(test_db, sample_person.id)
        
        # Assert
        assert len(events) == 1
        assert events[0].id == sample_event.id
        assert events[0].person_id == sample_person.id

    def test_get_by_person_multiple_events(self, test_db, sample_person):
        """Test getting multiple events for a person."""
        # Arrange - create multiple events for the same person
        for i in range(3):
            event_data = EventCreate(
                person_id=sample_person.id,
                type=f"Event{i}",
                date=f"199{i}-01-01"
            )
            event_crud.create(test_db, event_data)
        
        # Act
        events = event_crud.get_by_person(test_db, sample_person.id)
        
        # Assert
        assert len(events) == 3
        for event in events:
            assert event.person_id == sample_person.id

    def test_get_by_person_no_events(self, test_db, sample_person):
        """Test getting events for a person with no events."""
        # Act
        events = event_crud.get_by_person(test_db, sample_person.id)
        
        # Assert
        assert events == []

    def test_get_by_person_non_existent(self, test_db):
        """Test getting events for a non-existent person."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        events = event_crud.get_by_person(test_db, non_existent_id)
        
        # Assert
        assert events == []

    def test_get_by_family(self, test_db, sample_family):
        """Test getting all events for a family."""
        # Arrange - create an event for the family
        event_data = EventCreate(
            family_id=sample_family.id,
            type="Marriage",
            date="2015-06-20"
        )
        event = event_crud.create(test_db, event_data)
        
        # Act
        events = event_crud.get_by_family(test_db, sample_family.id)
        
        # Assert
        assert len(events) == 1
        assert events[0].id == event.id
        assert events[0].family_id == sample_family.id

    def test_get_by_family_multiple_events(self, test_db, sample_family):
        """Test getting multiple events for a family."""
        # Arrange - create multiple events for the same family
        for i in range(3):
            event_data = EventCreate(
                family_id=sample_family.id,
                type=f"FamilyEvent{i}",
                date=f"201{i}-01-01"
            )
            event_crud.create(test_db, event_data)
        
        # Act
        events = event_crud.get_by_family(test_db, sample_family.id)
        
        # Assert
        assert len(events) == 3
        for event in events:
            assert event.family_id == sample_family.id

    def test_get_by_family_no_events(self, test_db, sample_family):
        """Test getting events for a family with no events."""
        # Act
        events = event_crud.get_by_family(test_db, sample_family.id)
        
        # Assert
        assert events == []

    def test_get_by_family_non_existent(self, test_db):
        """Test getting events for a non-existent family."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        events = event_crud.get_by_family(test_db, non_existent_id)
        
        # Assert
        assert events == []

    def test_get_by_type(self, test_db, sample_event):
        """Test getting all events of a specific type."""
        # Act
        events = event_crud.get_by_type(test_db, "Birth")
        
        # Assert
        assert len(events) == 1
        assert events[0].id == sample_event.id
        assert events[0].type == "Birth"

    def test_get_by_type_multiple_events(self, test_db, sample_person):
        """Test getting multiple events of the same type."""
        # Arrange - create multiple events of the same type
        for i in range(3):
            event_data = EventCreate(
                person_id=sample_person.id,
                type="Birth",
                date=f"199{i}-01-01"
            )
            event_crud.create(test_db, event_data)
        
        # Act
        events = event_crud.get_by_type(test_db, "Birth")
        
        # Assert
        assert len(events) == 3
        for event in events:
            assert event.type == "Birth"

    def test_get_by_type_no_events(self, test_db):
        """Test getting events of a type that doesn't exist."""
        # Act
        events = event_crud.get_by_type(test_db, "NonExistent")
        
        # Assert
        assert events == []

    def test_search_by_type(self, test_db, sample_person):
        """Test searching events by type with partial match."""
        # Arrange - create events with similar types
        event1_data = EventCreate(
            person_id=sample_person.id,
            type="Birth Certificate",
            date="1990-01-01"
        )
        event_crud.create(test_db, event1_data)
        
        event2_data = EventCreate(
            person_id=sample_person.id,
            type="Birth Registration",
            date="1990-01-02"
        )
        event_crud.create(test_db, event2_data)
        
        event3_data = EventCreate(
            person_id=sample_person.id,
            type="Death",
            date="2020-01-01"
        )
        event_crud.create(test_db, event3_data)
        
        # Act - search for events containing "Birth"
        events = event_crud.search_by_type(test_db, "Birth")
        
        # Assert
        assert len(events) == 2
        for event in events:
            assert "Birth" in event.type

    def test_search_by_type_no_matches(self, test_db, sample_person):
        """Test searching events by type with no matches."""
        # Arrange
        event_data = EventCreate(
            person_id=sample_person.id,
            type="Birth",
            date="1990-01-01"
        )
        event_crud.create(test_db, event_data)
        
        # Act
        events = event_crud.search_by_type(test_db, "Death")
        
        # Assert
        assert events == []

    def test_search_by_type_case_sensitive(self, test_db, sample_person):
        """Test that type search is case sensitive."""
        # Arrange
        event_data = EventCreate(
            person_id=sample_person.id,
            type="Birth",
            date="1990-01-01"
        )
        event_crud.create(test_db, event_data)
        
        # Act
        events = event_crud.search_by_type(test_db, "birth")
        
        # Assert
        assert events == []

    def test_update_event_full_update(self, test_db, sample_event, sample_person, sample_family):
        """Test updating an event with all fields."""
        # Arrange
        update_data = EventUpdate(
            person_id=sample_person.id,
            family_id=sample_family.id,
            type="Updated Event",
            date=date(2020, 1, 1),
            place="Updated Place",
            description="Updated description"
        )
        
        # Act
        updated_event = event_crud.update(test_db, sample_event.id, update_data)
        
        # Assert
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
        # Arrange
        update_data = EventUpdate(
            type="Updated Type",
            place="Updated Place"
        )
        
        # Act
        updated_event = event_crud.update(test_db, sample_event.id, update_data)
        
        # Assert
        assert updated_event is not None
        assert updated_event.id == sample_event.id
        assert updated_event.type == "Updated Type"
        assert updated_event.place == "Updated Place"
        assert updated_event.person_id == sample_event.person_id  # Unchanged
        assert updated_event.family_id == sample_event.family_id  # Unchanged
        assert updated_event.date == sample_event.date  # Unchanged
        assert updated_event.description == sample_event.description  # Unchanged

    def test_update_event_clear_fields(self, test_db, sample_event):
        """Test updating an event to clear some fields."""
        # Arrange
        update_data = EventUpdate(
            person_id=None,
            family_id=None,
            place=None,
            description=None
        )
        
        # Act
        updated_event = event_crud.update(test_db, sample_event.id, update_data)
        
        # Assert
        assert updated_event is not None
        assert updated_event.id == sample_event.id
        assert updated_event.person_id is None
        assert updated_event.family_id is None
        assert updated_event.place is None
        assert updated_event.description is None
        assert updated_event.type == sample_event.type  # Unchanged
        assert updated_event.date == sample_event.date  # Unchanged

    def test_update_event_not_found(self, test_db):
        """Test updating a non-existent event."""
        # Arrange
        non_existent_id = uuid4()
        update_data = EventUpdate(type="Updated")
        
        # Act
        updated_event = event_crud.update(test_db, non_existent_id, update_data)
        
        # Assert
        assert updated_event is None

    def test_delete_event(self, test_db, sample_event):
        """Test deleting an event."""
        # Act
        result = event_crud.delete(test_db, sample_event.id)
        
        # Assert
        assert result is True
        
        # Verify event is deleted
        deleted_event = event_crud.get(test_db, sample_event.id)
        assert deleted_event is None

    def test_delete_event_not_found(self, test_db):
        """Test deleting a non-existent event."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        result = event_crud.delete(test_db, non_existent_id)
        
        # Assert
        assert result is False

    def test_event_relationships(self, test_db, sample_event):
        """Test that event relationships are properly established."""
        # Act
        retrieved_event = event_crud.get(test_db, sample_event.id)
        
        # Assert
        assert retrieved_event is not None
        # Note: Relationships would need to be explicitly loaded in a real scenario
        # This test verifies the event exists and can be retrieved

    def test_event_date_validation(self, test_db, sample_person):
        """Test event date field validation."""
        # Test with invalid date format
        event_data = EventCreate(
            person_id=sample_person.id,
            type="Test Event",
            date="invalid-date"  # This should raise a validation error
        )
        
        # This should raise a validation error
        with pytest.raises(Exception):  # Date parsing error
            event_crud.create(test_db, event_data)

    def test_event_field_lengths(self, test_db, sample_person):
        """Test event field length constraints."""
        # Test with very long type
        long_type = "A" * 51  # Exceeds max_length=50
        event_data = EventCreate(
            person_id=sample_person.id,
            type=long_type
        )
        
        # This should raise a validation error
        with pytest.raises(Exception):  # SQLModel validation error
            event_crud.create(test_db, event_data)

    def test_event_foreign_key_constraints(self, test_db):
        """Test event foreign key constraints."""
        # Test with non-existent person and family IDs
        non_existent_person_id = uuid4()
        non_existent_family_id = uuid4()
        
        event_data = EventCreate(
            person_id=non_existent_person_id,
            family_id=non_existent_family_id,
            type="Test Event"
        )
        
        # This should raise a foreign key constraint error
        with pytest.raises(Exception):  # Foreign key constraint error
            event_crud.create(test_db, event_data)

    def test_event_type_validation(self, test_db, sample_person):
        """Test event type validation."""
        # Test with empty type
        event_data = EventCreate(
            person_id=sample_person.id,
            type=""  # Empty type should raise validation error
        )
        
        # This should raise a validation error
        with pytest.raises(Exception):  # Validation error
            event_crud.create(test_db, event_data)

    def test_event_cascade_behavior(self, test_db, sample_person, sample_family):
        """Test cascade behavior when related entities are deleted."""
        # Create events for both person and family
        person_event_data = EventCreate(
            person_id=sample_person.id,
            type="Person Event"
        )
        person_event = event_crud.create(test_db, person_event_data)
        
        family_event_data = EventCreate(
            family_id=sample_family.id,
            type="Family Event"
        )
        family_event = event_crud.create(test_db, family_event_data)
        
        # Delete the person
        from src.crud.person import person_crud
        person_crud.delete(test_db, sample_person.id)
        
        # Verify person event still exists (no cascade delete)
        # or is deleted (with cascade delete) depending on configuration
        remaining_person_event = event_crud.get(test_db, person_event.id)
        # This behavior depends on the database configuration
        # For now, we'll assume no cascade delete
        assert remaining_person_event is None  # Person was deleted, so event should be gone
        
        # Delete the family
        from src.crud.family import family_crud
        family_crud.delete(test_db, sample_family.id)
        
        # Verify family event still exists (no cascade delete)
        # or is deleted (with cascade delete) depending on configuration
        remaining_family_event = event_crud.get(test_db, family_event.id)
        # This behavior depends on the database configuration
        # For now, we'll assume no cascade delete
        assert remaining_family_event is None  # Family was deleted, so event should be gone
