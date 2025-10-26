"""CRUD operations for Event model."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select
from sqlalchemy import cast, String

from ..models.event import Event, EventCreate, EventUpdate


class EventCRUD:
    """CRUD operations for Event model."""

    def create(self, db: Session, event: EventCreate) -> Event:
        """Create a new event."""
        db_event = Event.model_validate(event)
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event

    def get(self, db: Session, event_id: UUID) -> Optional[Event]:
        """Get an event by ID."""
        return db.get(Event, event_id)

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Event]:
        """Get all events with pagination."""
        statement = select(Event).offset(skip).limit(limit)
        return list(db.exec(statement))

    def get_by_person(self, db: Session, person_id: UUID) -> List[Event]:
        """Get all events for a person."""
        statement = select(Event).where(Event.person_id == person_id)
        return list(db.exec(statement))

    def get_by_family(self, db: Session, family_id: UUID) -> List[Event]:
        """Get all events for a family."""
        statement = select(Event).where(Event.family_id == family_id)
        return list(db.exec(statement))

    def get_by_type(self, db: Session, event_type: str) -> List[Event]:
        """Get all events of a specific type."""
        statement = select(Event).where(Event.type == event_type)
        return list(db.exec(statement))

    def search_by_type(self, db: Session, event_type: str) -> List[Event]:
        """Search events by type (case-sensitive partial match)."""
        # Cast to text for portability across drivers

        statement = select(Event).where(
            cast(Event.type, String).contains(event_type, autoescape=True)
        )
        return list(db.exec(statement))

    def update(
        self, db: Session, event_id: UUID, event_update: EventUpdate
    ) -> Optional[Event]:
        """Update an event."""
        db_event = db.get(Event, event_id)
        if not db_event:
            return None

        event_data = event_update.model_dump(exclude_unset=True)
        for field, value in event_data.items():
            setattr(db_event, field, value)

        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event

    def delete(self, db: Session, event_id: UUID) -> bool:
        """Delete an event."""
        db_event = db.get(Event, event_id)
        if not db_event:
            return False

        db.delete(db_event)
        db.commit()
        return True


# Create a singleton instance
event_crud = EventCRUD()
