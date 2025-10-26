from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from ..constants import FAMILY_NOT_FOUND
from ..crud.family import family_crud
from ..db import get_session
from ..models.family import (
    Family,
    FamilyCreate,
    FamilyRead,
    FamilyUpdate,
    FamilySearchResult,
    FamilyDetailResult,
)

router = APIRouter(prefix="/api/v1/families", tags=["families"])


def _validate_spouse_exists(session: Session, spouse_id: UUID, role: str) -> None:
    """Helper function to validate that a spouse exists."""
    from ..crud.person import person_crud

    if spouse_id:
        spouse = person_crud.get(session, spouse_id)
        if not spouse:
            raise HTTPException(
                status_code=404, detail=f"{role.capitalize()} not found"
            )


def _get_spouse_data(session: Session, spouse_id: UUID):
    """Helper function to get spouse data if spouse_id exists."""
    from ..crud.person import person_crud

    return person_crud.get(session, spouse_id) if spouse_id else None


def _validate_family_relationships_and_dates(
    session: Session, family: FamilyCreate
) -> None:
    """Helper function to validate family relationships and dates."""
    from ..validators import (
        validate_family_dates,
        validate_family_spouses,
        FamilyDateData,
    )

    validate_family_spouses(family.husband_id, family.wife_id)

    _validate_spouse_exists(session, family.husband_id, "husband")
    _validate_spouse_exists(session, family.wife_id, "wife")

    husband = _get_spouse_data(session, family.husband_id)
    wife = _get_spouse_data(session, family.wife_id)

    family_data = FamilyDateData(
        marriage_date=family.marriage_date,
        divorce_date=None,
        husband_birth_date=husband.birth_date if husband else None,
        wife_birth_date=wife.birth_date if wife else None,
        husband_death_date=husband.death_date if husband else None,
        wife_death_date=wife.death_date if wife else None,
    )
    validate_family_dates(family_data)


def _validate_family_update_relationships(
    session: Session, family_update: FamilyUpdate
) -> None:
    """Helper function to validate family update relationships."""
    _validate_spouse_exists(session, family_update.husband_id, "husband")
    _validate_spouse_exists(session, family_update.wife_id, "wife")


def _get_effective_spouse_id(update_id: UUID, current_id: UUID) -> UUID:
    """Helper function to get the effective spouse ID for patch operations."""
    return update_id if update_id is not None else current_id


def _get_effective_marriage_date(update_date, current_date):
    """Helper function to get the effective marriage date for patch operations."""
    return update_date if update_date is not None else current_date


def _validate_patch_family_relationships_and_dates(
    session: Session, family_update: FamilyUpdate, current_family: Family
) -> None:
    """Helper function to validate patch family relationships and dates."""
    from ..validators import (
        validate_family_dates,
        validate_family_spouses,
        FamilyDateData,
    )

    update_data = family_update.model_dump(exclude_unset=True)
    husband_id = update_data.get("husband_id", current_family.husband_id)
    wife_id = update_data.get("wife_id", current_family.wife_id)

    validate_family_spouses(husband_id, wife_id)

    _validate_spouse_exists(session, family_update.husband_id, "husband")
    _validate_spouse_exists(session, family_update.wife_id, "wife")

    effective_husband_id = _get_effective_spouse_id(
        family_update.husband_id, current_family.husband_id
    )
    effective_wife_id = _get_effective_spouse_id(
        family_update.wife_id, current_family.wife_id
    )

    husband = _get_spouse_data(session, effective_husband_id)
    wife = _get_spouse_data(session, effective_wife_id)

    marriage_date = _get_effective_marriage_date(
        family_update.marriage_date, current_family.marriage_date
    )

    family_data = FamilyDateData(
        marriage_date=marriage_date,
        divorce_date=None,
        husband_birth_date=husband.birth_date if husband else None,
        wife_birth_date=wife.birth_date if wife else None,
        husband_death_date=husband.death_date if husband else None,
        wife_death_date=wife.death_date if wife else None,
    )
    validate_family_dates(family_data)


def _prevent_duplicate_couple(session: Session, family: FamilyCreate) -> None:
    """Raise 409 if the same couple already exists (order-indifferent)."""
    if not (family.husband_id and family.wife_id):
        return
    if family_crud.exists_same_couple(session, family.husband_id, family.wife_id):
        raise HTTPException(
            status_code=409, detail="Family with same spouses already exists"
        )


@router.post("/", response_model=FamilyRead, status_code=201)
def create_family(
    family: FamilyCreate,
    session: Session = Depends(get_session),
):
    """Create a new family."""
    _validate_family_relationships_and_dates(session, family)
    _prevent_duplicate_couple(session, family)
    return family_crud.create(session, family)


@router.get("/search", response_model=List[FamilySearchResult])
def search_families(
    q: Optional[str] = Query(None, description="Search query for family names"),
    family_id: Optional[UUID] = Query(
        None, description="Specific family ID to retrieve"
    ),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    session: Session = Depends(get_session),
):
    """
    Search families by name or get a specific family by ID.

    - **q**: Search query to find families by spouse names (fuzzy search)
    - **family_id**: Get a specific family by its ID
    - **limit**: Maximum number of results to return (1-100)

    Returns a list of family summaries with basic information.
    """
    if (not q or not q.strip()) and not family_id:
        raise HTTPException(
            status_code=400,
            detail="Either 'q' (search query) or 'family_id' parameter is required",
        )

    results = family_crud.search_families(
        session, query=q, family_id=family_id, limit=limit
    )

    if not results:
        raise HTTPException(
            status_code=404, detail="No families found matching the search criteria"
        )

    return results


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
        raise HTTPException(status_code=404, detail=FAMILY_NOT_FOUND)
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
        raise HTTPException(status_code=404, detail=FAMILY_NOT_FOUND)
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
        raise HTTPException(status_code=404, detail=FAMILY_NOT_FOUND)

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
        raise HTTPException(status_code=404, detail=FAMILY_NOT_FOUND)


@router.get("/{family_id}/detail", response_model=FamilyDetailResult)
def get_family_detail(
    family_id: UUID,
    session: Session = Depends(get_session),
):
    """
    Get detailed information about a family including spouses, children, and events.

    Returns complete family data with all related information.
    """
    family_detail = family_crud.get_family_detail(session, family_id)
    if not family_detail:
        raise HTTPException(status_code=404, detail=FAMILY_NOT_FOUND)

    return family_detail
