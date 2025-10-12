"""
Field ensuring utilities for GeneWeb converter.

Handles ensuring that objects have the required fields for database insertion.
"""

from datetime import date, datetime
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from .date_utils import parse_date_dict_to_date, parse_date_string_to_date


def ensure_person_fields(person_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure that a person object has the required fields for database insertion.

    Args:
        person_data: The person data dictionary

    Returns:
        Person data with required fields (id, first_name, last_name, sex, birth_date, death_date, etc.)
    """
    from .person_extractor import (
        extract_birth_date_from_person_data,
        extract_death_date_from_person_data,
        extract_birth_place_from_person_data,
        extract_death_place_from_person_data,
        extract_occupation_from_person_data,
        extract_notes_from_person_data,
    )

    first_name = person_data.get("first_name", "")
    last_name = person_data.get("last_name", "")
    gender = person_data.get("gender")
    if gender == "male":
        sex = "M"
    elif gender == "female":
        sex = "F"
    else:
        sex = "U"

    if _should_extract_name_from_full_name(first_name, last_name, person_data):
        from src.parsing.token_parser import split_name_into_parts

        first_name, last_name = split_name_into_parts(person_data["name"])

    birth_date = extract_birth_date_from_person_data(person_data)
    death_date = extract_death_date_from_person_data(person_data)
    birth_place = extract_birth_place_from_person_data(person_data)
    death_place = extract_death_place_from_person_data(person_data)
    occupation = extract_occupation_from_person_data(person_data)
    notes = extract_notes_from_person_data(person_data)

    result = person_data.copy()
    result["id"] = person_data.get("id") or str(uuid4())
    result["first_name"] = first_name
    result["last_name"] = last_name
    result["sex"] = sex
    result["birth_date"] = birth_date
    result["death_date"] = death_date
    result["birth_place"] = birth_place
    result["death_place"] = death_place
    result["occupation"] = occupation
    result["notes"] = notes

    return result


def ensure_event_fields(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure that an event object has the required fields for database insertion.

    Args:
        event_data: The event data dictionary

    Returns:
        Event data with required fields (date, place, description converted properly)
    """
    result = event_data.copy()

    _process_event_date(event_data, result)
    _process_event_place(event_data, result)
    _process_event_notes(event_data, result)
    _ensure_event_id(result)

    return result


def _process_event_date(event_data: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Process and convert event date."""
    if "date" in event_data and isinstance(event_data["date"], dict):
        date_dict = event_data["date"]
        parsed_date = parse_date_dict_to_date(date_dict)
        result["date"] = parsed_date
    elif "date" in event_data and isinstance(event_data["date"], str):
        parsed_date = parse_date_string_to_date(event_data["date"])
        result["date"] = parsed_date


def _process_event_place(event_data: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Process and convert event place."""
    if "place_raw" in event_data:
        result["place"] = event_data["place_raw"]
    elif "place" in event_data:
        result["place"] = event_data["place"]


def _process_event_notes(event_data: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Process and convert event notes to description."""
    if "notes" in event_data and event_data["notes"]:
        if isinstance(event_data["notes"], list):
            result["description"] = " | ".join(event_data["notes"])
        else:
            result["description"] = str(event_data["notes"])


def _ensure_event_id(result: Dict[str, Any]) -> None:
    """Ensure event has an ID."""
    if "id" not in result:
        result["id"] = str(uuid4())


def _should_extract_name_from_full_name(
    first_name: str, last_name: str, person_data: Dict[str, Any]
) -> bool:
    """Check if we should extract name from full name."""
    return not first_name and not last_name and person_data.get("name")
