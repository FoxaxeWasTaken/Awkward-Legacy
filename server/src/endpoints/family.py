from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from ..crud.family import family_crud
from ..db import get_session
from ..models.family import Family, FamilyCreate, FamilyRead, FamilyUpdate

router = APIRouter(prefix="/api/v1/families", tags=["families"])


@router.post("/", response_model=FamilyRead, status_code=201)
def create_family(
    family: FamilyCreate,
    session: Session = Depends(get_session),
):
    """Create a new family."""
    from ..validators import validate_family_dates, validate_family_spouses

    validate_family_spouses(family.husband_id, family.wife_id)

    husband = None
    if family.husband_id:
        from ..crud.person import person_crud

        husband = person_crud.get(session, family.husband_id)
        if not husband:
            raise HTTPException(status_code=404, detail="Husband not found")

    wife = None
    if family.wife_id:
        from ..crud.person import person_crud

        wife = person_crud.get(session, family.wife_id)
        if not wife:
            raise HTTPException(status_code=404, detail="Wife not found")

    validate_family_dates(
        marriage_date=family.marriage_date,
        divorce_date=None,
        husband_birth_date=husband.birth_date if husband else None,
        wife_birth_date=wife.birth_date if wife else None,
        husband_death_date=husband.death_date if husband else None,
        wife_death_date=wife.death_date if wife else None,
    )

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
    if family_update.husband_id:
        from ..crud.person import person_crud

        husband = person_crud.get(session, family_update.husband_id)
        if not husband:
            raise HTTPException(status_code=404, detail="Husband not found")

    if family_update.wife_id:
        from ..crud.person import person_crud

        wife = person_crud.get(session, family_update.wife_id)
        if not wife:
            raise HTTPException(status_code=404, detail="Wife not found")

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
    from ..validators import validate_family_dates, validate_family_spouses

    current_family = family_crud.get(session, family_id)
    if not current_family:
        raise HTTPException(status_code=404, detail="Family not found")

    update_data = family_update.model_dump(exclude_unset=True)
    husband_id = update_data.get("husband_id", current_family.husband_id)
    wife_id = update_data.get("wife_id", current_family.wife_id)

    validate_family_spouses(husband_id, wife_id)

    husband = None
    if family_update.husband_id:
        from ..crud.person import person_crud

        husband = person_crud.get(session, family_update.husband_id)
        if not husband:
            raise HTTPException(status_code=404, detail="Husband not found")
    elif current_family.husband_id:
        from ..crud.person import person_crud

        husband = person_crud.get(session, current_family.husband_id)

    wife = None
    if family_update.wife_id:
        from ..crud.person import person_crud

        wife = person_crud.get(session, family_update.wife_id)
        if not wife:
            raise HTTPException(status_code=404, detail="Wife not found")
    elif current_family.wife_id:
        from ..crud.person import person_crud

        wife = person_crud.get(session, current_family.wife_id)

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
