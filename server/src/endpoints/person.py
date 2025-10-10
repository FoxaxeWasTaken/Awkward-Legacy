from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from ..crud.person import person_crud
from ..db import get_session
from ..models.person import Person, PersonCreate, PersonRead, PersonUpdate

router = APIRouter(prefix="/api/v1/persons", tags=["persons"])


@router.post("/", response_model=PersonRead, status_code=201)
def create_person(
    person: PersonCreate,
    session: Session = Depends(get_session),
):
    """Create a new person."""
    from ..validators import validate_person_dates, validate_person_names

    validate_person_names(person.first_name, person.last_name)
    validate_person_dates(person.birth_date, person.death_date)

    return person_crud.create(session, person)


@router.get("/", response_model=List[PersonRead])
def get_all_persons(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session),
):
    """Get all persons with pagination."""
    return person_crud.get_all(session, skip=skip, limit=limit)


@router.get("/search", response_model=List[PersonRead])
def search_persons(
    name: str = Query(..., description="Name to search for"),
    session: Session = Depends(get_session),
):
    """Search persons by name."""
    return person_crud.search_by_name(session, name)


@router.get("/by-name", response_model=List[PersonRead])
def get_persons_by_name(
    first_name: str = Query(..., description="First name"),
    last_name: str = Query(..., description="Last name"),
    session: Session = Depends(get_session),
):
    """Get persons by exact first and last name."""
    return person_crud.get_by_name(session, first_name, last_name)


@router.get("/{person_id}", response_model=PersonRead)
def get_person(
    person_id: UUID,
    session: Session = Depends(get_session),
):
    """Get a person by ID."""
    person = person_crud.get(session, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.put("/{person_id}", response_model=PersonRead)
def update_person(
    person_id: UUID,
    person_update: PersonUpdate,
    session: Session = Depends(get_session),
):
    """Update a person."""
    from ..validators import validate_person_dates, validate_person_names

    current_person = person_crud.get(session, person_id)
    if not current_person:
        raise HTTPException(status_code=404, detail="Person not found")

    validate_person_names(person_update.first_name, person_update.last_name)

    birth_date = (
        person_update.birth_date
        if person_update.birth_date is not None
        else current_person.birth_date
    )
    death_date = (
        person_update.death_date
        if person_update.death_date is not None
        else current_person.death_date
    )
    validate_person_dates(birth_date, death_date)

    person = person_crud.update(session, person_id, person_update)
    return person


@router.patch("/{person_id}", response_model=PersonRead)
def patch_person(
    person_id: UUID,
    person_update: PersonUpdate,
    session: Session = Depends(get_session),
):
    """Partially update a person."""
    from ..validators import validate_person_dates, validate_person_names

    current_person = person_crud.get(session, person_id)
    if not current_person:
        raise HTTPException(status_code=404, detail="Person not found")

    validate_person_names(person_update.first_name, person_update.last_name)

    birth_date = (
        person_update.birth_date
        if person_update.birth_date is not None
        else current_person.birth_date
    )
    death_date = (
        person_update.death_date
        if person_update.death_date is not None
        else current_person.death_date
    )
    validate_person_dates(birth_date, death_date)

    person = person_crud.update(session, person_id, person_update)
    return person


@router.delete("/{person_id}", status_code=204)
def delete_person(
    person_id: UUID,
    session: Session = Depends(get_session),
):
    """Delete a person."""
    success = person_crud.delete(session, person_id)
    if not success:
        raise HTTPException(status_code=404, detail="Person not found")
