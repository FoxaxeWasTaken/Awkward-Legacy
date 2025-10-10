from datetime import date
from typing import Optional

from fastapi import HTTPException


def _validate_date_not_future(date_value: Optional[date], field_name: str) -> None:
    """Helper function to validate that a date is not in the future."""
    if date_value and date_value > date.today():
        raise HTTPException(
            status_code=400, detail=f"{field_name} cannot be in the future"
        )


def _validate_death_after_birth(
    birth_date: Optional[date], death_date: Optional[date]
) -> None:
    """Helper function to validate that death date is after birth date."""
    if birth_date and death_date and death_date < birth_date:
        raise HTTPException(
            status_code=400, detail="Death date cannot be before birth date"
        )


def validate_person_dates(
    birth_date: Optional[date] = None,
    death_date: Optional[date] = None,
) -> None:
    """Validate person birth and death dates."""
    _validate_date_not_future(birth_date, "Birth date")
    _validate_date_not_future(death_date, "Death date")
    _validate_death_after_birth(birth_date, death_date)


def _validate_marriage_after_birth(
    marriage_date: Optional[date], birth_date: Optional[date], spouse_role: str
) -> None:
    """Helper function to validate that marriage is after birth."""
    if marriage_date and birth_date and marriage_date < birth_date:
        raise HTTPException(
            status_code=400,
            detail=f"Marriage date cannot be before {spouse_role}'s birth date",
        )


def _validate_marriage_before_death(
    marriage_date: Optional[date], death_date: Optional[date], spouse_role: str
) -> None:
    """Helper function to validate that marriage is before death."""
    if marriage_date and death_date and marriage_date > death_date:
        raise HTTPException(
            status_code=400,
            detail=f"Marriage date cannot be after {spouse_role}'s death date",
        )


def _validate_divorce_after_marriage(
    marriage_date: Optional[date], divorce_date: Optional[date]
) -> None:
    """Helper function to validate that divorce is after marriage."""
    if marriage_date and divorce_date and divorce_date < marriage_date:
        raise HTTPException(
            status_code=400, detail="Divorce date cannot be before marriage date"
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
    _validate_date_not_future(marriage_date, "Marriage date")
    _validate_date_not_future(divorce_date, "Divorce date")
    _validate_divorce_after_marriage(marriage_date, divorce_date)
    _validate_marriage_after_birth(marriage_date, husband_birth_date, "husband")
    _validate_marriage_after_birth(marriage_date, wife_birth_date, "wife")
    _validate_marriage_before_death(marriage_date, husband_death_date, "husband")
    _validate_marriage_before_death(marriage_date, wife_death_date, "wife")


def _validate_event_after_birth(
    event_date: Optional[date], person_birth_date: Optional[date]
) -> None:
    """Helper function to validate that event is after person's birth."""
    if event_date and person_birth_date and event_date < person_birth_date:
        raise HTTPException(
            status_code=400, detail="Event date cannot be before person's birth date"
        )


def _validate_event_before_death(
    event_date: Optional[date], person_death_date: Optional[date]
) -> None:
    """Helper function to validate that event is before person's death."""
    if event_date and person_death_date and event_date > person_death_date:
        raise HTTPException(
            status_code=400, detail="Event date cannot be after person's death date"
        )


def validate_event_dates(
    event_date: Optional[date] = None,
    person_birth_date: Optional[date] = None,
    person_death_date: Optional[date] = None,
) -> None:
    """Validate event dates."""
    _validate_date_not_future(event_date, "Event date")
    _validate_event_after_birth(event_date, person_birth_date)
    _validate_event_before_death(event_date, person_death_date)


def validate_person_names(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> None:
    """Validate person names."""
    if first_name is not None and first_name.strip() == "":
        raise HTTPException(status_code=422, detail="First name cannot be empty")

    if last_name is not None and last_name.strip() == "":
        raise HTTPException(status_code=422, detail="Last name cannot be empty")


def _validate_not_same_spouse(
    husband_id: Optional[str], wife_id: Optional[str]
) -> None:
    """Helper function to validate that husband and wife are not the same person."""
    if husband_id and wife_id and husband_id == wife_id:
        raise HTTPException(
            status_code=400, detail="Same person cannot be both husband and wife"
        )


def _validate_at_least_one_spouse(
    husband_id: Optional[str], wife_id: Optional[str]
) -> None:
    """Helper function to validate that at least one spouse is provided."""
    if not husband_id and not wife_id:
        raise HTTPException(
            status_code=422,
            detail="At least one spouse (husband or wife) must be provided",
        )


def validate_family_spouses(
    husband_id: Optional[str] = None,
    wife_id: Optional[str] = None,
) -> None:
    """Validate family spouse relationships."""
    _validate_not_same_spouse(husband_id, wife_id)
    _validate_at_least_one_spouse(husband_id, wife_id)


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
