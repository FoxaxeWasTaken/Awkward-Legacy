from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from ..crud.family import family_crud
from ..db import get_session
from ..models.family import Family, FamilyCreate, FamilyRead, FamilyUpdate

router = APIRouter(prefix="/api/v1/families", tags=["families"])


def _validate_family_relationships_and_dates(
    session: Session, family: FamilyCreate
) -> None:
    """Helper function to validate family relationships and dates."""
    from ..validators import validate_family_dates, validate_family_spouses
    from ..crud.person import person_crud

    validate_family_spouses(family.husband_id, family.wife_id)

    if family.husband_id:
        husband = person_crud.get(session, family.husband_id)
        if not husband:
            raise HTTPException(status_code=404, detail="Husband not found")

    if family.wife_id:
        wife = person_crud.get(session, family.wife_id)
        if not wife:
            raise HTTPException(status_code=404, detail="Wife not found")

    husband = person_crud.get(session, family.husband_id) if family.husband_id else None
    wife = person_crud.get(session, family.wife_id) if family.wife_id else None

    validate_family_dates(
        marriage_date=family.marriage_date,
        divorce_date=None,
        husband_birth_date=husband.birth_date if husband else None,
        wife_birth_date=wife.birth_date if wife else None,
        husband_death_date=husband.death_date if husband else None,
        wife_death_date=wife.death_date if wife else None,
    )


def _validate_family_update_relationships(
    session: Session, family_update: FamilyUpdate
) -> None:
    """Helper function to validate family update relationships."""
    from ..crud.person import person_crud

    if family_update.husband_id:
        husband = person_crud.get(session, family_update.husband_id)
        if not husband:
            raise HTTPException(status_code=404, detail="Husband not found")

    if family_update.wife_id:
        wife = person_crud.get(session, family_update.wife_id)
        if not wife:
            raise HTTPException(status_code=404, detail="Wife not found")


def _validate_patch_family_relationships_and_dates(
    session: Session, family_update: FamilyUpdate, current_family: Family
) -> None:
    """Helper function to validate patch family relationships and dates."""
    from ..validators import validate_family_dates, validate_family_spouses
    from ..crud.person import person_crud

    update_data = family_update.model_dump(exclude_unset=True)
    husband_id = update_data.get("husband_id", current_family.husband_id)
    wife_id = update_data.get("wife_id", current_family.wife_id)

    validate_family_spouses(husband_id, wife_id)

    if family_update.husband_id:
        husband = person_crud.get(session, family_update.husband_id)
        if not husband:
            raise HTTPException(status_code=404, detail="Husband not found")

    if family_update.wife_id:
        wife = person_crud.get(session, family_update.wife_id)
        if not wife:
            raise HTTPException(status_code=404, detail="Wife not found")

    husband = (
        person_crud.get(session, family_update.husband_id)
        if family_update.husband_id
        else (
            person_crud.get(session, current_family.husband_id)
            if current_family.husband_id
            else None
        )
    )
    wife = (
        person_crud.get(session, family_update.wife_id)
        if family_update.wife_id
        else (
            person_crud.get(session, current_family.wife_id)
            if current_family.wife_id
            else None
        )
    )

    marriage_date = (
        family_update.marriage_date
        if family_update.marriage_date is not None
        else current_family.marriage_date
    )

    validate_family_dates(
        marriage_date=marriage_date,
        divorce_date=None,
        husband_birth_date=husband.birth_date if husband else None,
        wife_birth_date=wife.birth_date if wife else None,
        husband_death_date=husband.death_date if husband else None,
        wife_death_date=wife.death_date if wife else None,
    )


@router.post("/", response_model=FamilyRead, status_code=201)
def create_family(
    family: FamilyCreate,
    session: Session = Depends(get_session),
):
    """Create a new family."""
    _validate_family_relationships_and_dates(session, family)
    return family_crud.create(session, family)


@router.get("/", response_model=List[FamilyRead])
def get_all_families(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session),
):
    """Get all families with pagination."""
    return family_crud.get_all(session, skip=skip, limit=limit)


@router.get("/{family_id}", response_model=FamilyRead)
def get_family(
    family_id: UUID,
    session: Session = Depends(get_session),
):
    """Get a family by ID."""
    family = family_crud.get(session, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    return family


@router.get("/by-husband/{husband_id}", response_model=List[FamilyRead])
def get_families_by_husband(
    husband_id: UUID,
    session: Session = Depends(get_session),
):
    """Get all families where a person is the husband."""
    return family_crud.get_by_husband(session, husband_id)


@router.get("/by-wife/{wife_id}", response_model=List[FamilyRead])
def get_families_by_wife(
    wife_id: UUID,
    session: Session = Depends(get_session),
):
    """Get all families where a person is the wife."""
    return family_crud.get_by_wife(session, wife_id)


@router.get("/by-spouse/{spouse_id}", response_model=List[FamilyRead])
def get_families_by_spouse(
    spouse_id: UUID,
    session: Session = Depends(get_session),
):
    """Get all families where a person is either husband or wife."""
    return family_crud.get_by_spouse(session, spouse_id)


@router.put("/{family_id}", response_model=FamilyRead)
def update_family(
    family_id: UUID,
    family_update: FamilyUpdate,
    session: Session = Depends(get_session),
):
    """Update a family."""
    _validate_family_update_relationships(session, family_update)

    family = family_crud.update(session, family_id, family_update)
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    return family


@router.patch("/{family_id}", response_model=FamilyRead)
def patch_family(
    family_id: UUID,
    family_update: FamilyUpdate,
    session: Session = Depends(get_session),
):
    """Partially update a family."""
    current_family = family_crud.get(session, family_id)
    if not current_family:
        raise HTTPException(status_code=404, detail="Family not found")

    _validate_patch_family_relationships_and_dates(
        session, family_update, current_family
    )

    family = family_crud.update(session, family_id, family_update)
    return family


@router.delete("/{family_id}", status_code=204)
def delete_family(
    family_id: UUID,
    session: Session = Depends(get_session),
):
    """Delete a family."""
    success = family_crud.delete(session, family_id)
    if not success:
        raise HTTPException(status_code=404, detail="Family not found")
