from datetime import date
from typing import Optional

from fastapi import HTTPException


def validate_person_dates(
    birth_date: Optional[date] = None,
    death_date: Optional[date] = None,
) -> None:
    """Validate person birth and death dates."""
    today = date.today()
    if birth_date and birth_date > today:
        raise HTTPException(
            status_code=400, detail="Birth date cannot be in the future"
        )

    if death_date and death_date > today:
        raise HTTPException(
            status_code=400, detail="Death date cannot be in the future"
        )

    if birth_date and death_date and death_date < birth_date:
        raise HTTPException(
            status_code=400, detail="Death date cannot be before birth date"
        )


def validate_family_dates(
    marriage_date: Optional[date] = None,
    divorce_date: Optional[date] = None,
    husband_birth_date: Optional[date] = None,
    wife_birth_date: Optional[date] = None,
    husband_death_date: Optional[date] = None,
    wife_death_date: Optional[date] = None,
) -> None:
    """Validate family dates."""
    today = date.today()

    if marriage_date and marriage_date > today:
        raise HTTPException(
            status_code=400, detail="Marriage date cannot be in the future"
        )

    if divorce_date and divorce_date > today:
        raise HTTPException(
            status_code=400, detail="Divorce date cannot be in the future"
        )

    if marriage_date and divorce_date and divorce_date < marriage_date:
        raise HTTPException(
            status_code=400, detail="Divorce date cannot be before marriage date"
        )

    if marriage_date and husband_birth_date and marriage_date < husband_birth_date:
        raise HTTPException(
            status_code=400,
            detail="Marriage date cannot be before husband's birth date",
        )

    if marriage_date and wife_birth_date and marriage_date < wife_birth_date:
        raise HTTPException(
            status_code=400, detail="Marriage date cannot be before wife's birth date"
        )

    if marriage_date and husband_death_date and marriage_date > husband_death_date:
        raise HTTPException(
            status_code=400, detail="Marriage date cannot be after husband's death date"
        )

    if marriage_date and wife_death_date and marriage_date > wife_death_date:
        raise HTTPException(
            status_code=400, detail="Marriage date cannot be after wife's death date"
        )


def validate_event_dates(
    event_date: Optional[date] = None,
    person_birth_date: Optional[date] = None,
    person_death_date: Optional[date] = None,
) -> None:
    """Validate event dates."""
    today = date.today()

    if event_date and event_date > today:
        raise HTTPException(
            status_code=400, detail="Event date cannot be in the future"
        )

    if event_date and person_birth_date and event_date < person_birth_date:
        raise HTTPException(
            status_code=400, detail="Event date cannot be before person's birth date"
        )

    if event_date and person_death_date and event_date > person_death_date:
        raise HTTPException(
            status_code=400, detail="Event date cannot be after person's death date"
        )


def validate_person_names(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> None:
    """Validate person names."""
    if first_name is not None and first_name.strip() == "":
        raise HTTPException(status_code=422, detail="First name cannot be empty")

    if last_name is not None and last_name.strip() == "":
        raise HTTPException(status_code=422, detail="Last name cannot be empty")


def validate_family_spouses(
    husband_id: Optional[str] = None,
    wife_id: Optional[str] = None,
) -> None:
    """Validate family spouse relationships."""
    if husband_id and wife_id and husband_id == wife_id:
        raise HTTPException(
            status_code=400, detail="Same person cannot be both husband and wife"
        )

    if not husband_id and not wife_id:
        raise HTTPException(
            status_code=422,
            detail="At least one spouse (husband or wife) must be provided",
        )


def validate_event_relationships(
    person_id: Optional[str] = None,
    family_id: Optional[str] = None,
) -> None:
    """Validate event relationships."""
    if person_id and family_id:
        raise HTTPException(
            status_code=400,
            detail="Event cannot be associated with both a person and a family",
        )

    if not person_id and not family_id:
        raise HTTPException(
            status_code=400,
            detail="Event must be associated with either a person or a family",
        )
