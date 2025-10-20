from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from ..constants import EVENT_NOT_FOUND, FAMILY_NOT_FOUND, PERSON_NOT_FOUND
from ..crud.event import event_crud
from ..db import get_session
from ..models.event import Event, EventCreate, EventRead, EventUpdate, EventType

router = APIRouter(prefix="/api/v1/events", tags=["events"])


def _validate_person_exists(session: Session, person_id: UUID) -> None:
    """Helper function to validate that a person exists."""
    from ..crud.person import person_crud

    person = person_crud.get(session, person_id)
    if not person:
        raise HTTPException(status_code=404, detail=PERSON_NOT_FOUND)


def _validate_family_exists(session: Session, family_id: UUID) -> None:
    """Helper function to validate that a family exists."""
    from ..crud.family import family_crud

    family = family_crud.get(session, family_id)
    if not family:
        raise HTTPException(status_code=404, detail=FAMILY_NOT_FOUND)


def _get_person_for_event(session: Session, person_id: UUID) -> object:
    """Helper function to get person for event validation."""
    from ..crud.person import person_crud

    return person_crud.get(session, person_id) if person_id else None


def _validate_event_relationships_and_dates(
    session: Session, event: EventCreate
) -> None:
    """Helper function to validate event relationships and dates."""
    from ..validators import validate_event_dates, validate_event_relationships

    validate_event_relationships(event.person_id, event.family_id)

    if event.person_id:
        _validate_person_exists(session, event.person_id)

    if event.family_id:
        _validate_family_exists(session, event.family_id)

    person = _get_person_for_event(session, event.person_id)
    validate_event_dates(
        event_date=event.date,
        person_birth_date=person.birth_date if person else None,
        person_death_date=person.death_date if person else None,
    )


def _validate_event_update_relationships(
    session: Session, event_update: EventUpdate
) -> None:
    """Helper function to validate event update relationships."""
    if event_update.person_id:
        _validate_person_exists(session, event_update.person_id)

    if event_update.family_id:
        _validate_family_exists(session, event_update.family_id)


def _get_person_for_patch_event(
    session: Session, event_update: EventUpdate, current_event: Event
) -> object:
    """Helper function to get person for patch event validation."""
    from ..crud.person import person_crud

    if event_update.person_id:
        return person_crud.get(session, event_update.person_id)
    elif current_event.person_id:
        return person_crud.get(session, current_event.person_id)
    return None


def _validate_patch_event_relationships_and_dates(
    session: Session, event_update: EventUpdate, current_event: Event
) -> None:
    """Helper function to validate patch event relationships and dates."""
    from ..validators import validate_event_dates, validate_event_relationships

    update_data = event_update.model_dump(exclude_unset=True)
    person_id = update_data.get("person_id", current_event.person_id)
    family_id = update_data.get("family_id", current_event.family_id)

    validate_event_relationships(person_id, family_id)

    if event_update.person_id:
        _validate_person_exists(session, event_update.person_id)

    if event_update.family_id:
        _validate_family_exists(session, event_update.family_id)

    person = _get_person_for_patch_event(session, event_update, current_event)
    event_date = (
        event_update.date if event_update.date is not None else current_event.date
    )

    validate_event_dates(
        event_date=event_date,
        person_birth_date=person.birth_date if person else None,
        person_death_date=person.death_date if person else None,
    )


@router.get("/types", response_model=List[str])
def get_event_types():
    """Get all available event types."""
    return [event_type.value for event_type in EventType]


@router.post("/", response_model=EventRead, status_code=201)
def create_event(
    event: EventCreate,
    session: Session = Depends(get_session),
):
    """Create a new event."""
    _validate_event_relationships_and_dates(session, event)
    return event_crud.create(session, event)


@router.get("/", response_model=List[EventRead])
def get_all_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session),
):
    """Get all events with pagination."""
    return event_crud.get_all(session, skip=skip, limit=limit)


@router.get("/search", response_model=List[EventRead])
def search_events_by_type(
    type: str = Query(..., description="Event type to search for"),
    session: Session = Depends(get_session),
):
    """Search events by type (partial match)."""
    return event_crud.search_by_type(session, type)


@router.get("/by-person/{person_id}", response_model=List[EventRead])
def get_events_by_person(
    person_id: UUID,
    session: Session = Depends(get_session),
):
    """Get all events for a person."""
    return event_crud.get_by_person(session, person_id)


@router.get("/by-family/{family_id}", response_model=List[EventRead])
def get_events_by_family(
    family_id: UUID,
    session: Session = Depends(get_session),
):
    """Get all events for a family."""
    return event_crud.get_by_family(session, family_id)


@router.get("/by-type", response_model=List[EventRead])
def get_events_by_type(
    type: str = Query(..., description="Event type to filter by"),
    session: Session = Depends(get_session),
):
    """Get all events of a specific type."""
    return event_crud.get_by_type(session, type)


@router.get("/{event_id}", response_model=EventRead)
def get_event(
    event_id: UUID,
    session: Session = Depends(get_session),
):
    """Get an event by ID."""
    event = event_crud.get(session, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=EVENT_NOT_FOUND)
    return event


@router.put("/{event_id}", response_model=EventRead)
def update_event(
    event_id: UUID,
    event_update: EventUpdate,
    session: Session = Depends(get_session),
):
    """Update an event."""
    _validate_event_update_relationships(session, event_update)

    event = event_crud.update(session, event_id, event_update)
    if not event:
        raise HTTPException(status_code=404, detail=EVENT_NOT_FOUND)
    return event


@router.patch("/{event_id}", response_model=EventRead)
def patch_event(
    event_id: UUID,
    event_update: EventUpdate,
    session: Session = Depends(get_session),
):
    """Partially update an event."""
    current_event = event_crud.get(session, event_id)
    if not current_event:
        raise HTTPException(status_code=404, detail=EVENT_NOT_FOUND)

    _validate_patch_event_relationships_and_dates(session, event_update, current_event)

    event = event_crud.update(session, event_id, event_update)
    return event


@router.delete("/{event_id}", status_code=204)
def delete_event(
    event_id: UUID,
    session: Session = Depends(get_session),
):
    """Delete an event."""
    success = event_crud.delete(session, event_id)
    if not success:
        raise HTTPException(status_code=404, detail=EVENT_NOT_FOUND)
