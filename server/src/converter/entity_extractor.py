"""
Entity extraction utilities for GeneWeb converter.

Handles extraction of entities from parsed GeneWeb data.
"""

from typing import Dict, Any
from uuid import uuid4
from .field_ensurer import ensure_person_fields, ensure_event_fields
from .family_extractor import (
    extract_marriage_date_from_family_data,
    extract_marriage_place_from_family_data,
    extract_family_notes_from_family_data,
)


def extract_entities(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract entities from parsed GeneWeb data.

    Args:
        parsed: Parsed GeneWeb data dictionary

    Returns:
        Dictionary containing extracted persons, families, events, and children
    """
    persons, families, events, children = [], [], [], []

    for fam in parsed.get("families", []):
        family_id = fam.get("id") or str(uuid4())

        # Extract husband and wife
        husband_id, wife_id = _extract_spouses(fam, persons, family_id)

        # Extract family data
        family_data = _build_family_data(fam, family_id, husband_id, wife_id)
        families.append(family_data)

        # Extract children
        _extract_children(fam, persons, children, family_id)

        # Extract family events
        _extract_family_events(fam, events, family_id)

    # Process person events (pevt blocks) - AFTER all families are processed
    _extract_person_events(parsed, persons, events)

    # Process person notes
    _extract_person_notes(parsed, persons)

    # Create persons for any people mentioned in pevt blocks but not in families
    _create_missing_persons_from_events(parsed, persons, events)

    return {
        "persons": persons,
        "families": families,
        "events": events,
        "children": children,
    }


def _extract_spouses(fam: Dict[str, Any], persons: list, family_id: str) -> tuple:
    """Extract husband and wife from family data."""
    husband_id = _ensure_spouse_and_get_id(fam.get("husband"), "male", persons)
    wife_id = _ensure_spouse_and_get_id(fam.get("wife"), "female", persons)
    return husband_id, wife_id


def _ensure_spouse_and_get_id(
    spouse: Dict[str, Any] | None, gender: str, persons: list
):
    if not spouse:
        return None
    spouse["gender"] = gender
    spouse_data = ensure_person_fields(spouse)
    full_name = _full_name(spouse_data)
    existing_id = _find_person_by_name(persons, full_name)
    if existing_id:
        return existing_id
    persons.append(spouse_data)
    return spouse_data.get("id")


def _build_family_data(
    fam: Dict[str, Any], family_id: str, husband_id: str, wife_id: str
) -> Dict[str, Any]:
    """Build family data dictionary."""
    marriage_date = extract_marriage_date_from_family_data(fam)
    marriage_place = extract_marriage_place_from_family_data(fam)
    family_notes = extract_family_notes_from_family_data(fam)

    family_data = {
        k: v
        for k, v in fam.items()
        if k not in ["husband", "wife", "children", "events"]
    }
    family_data.update(
        {
            "id": family_id,
            "husband_id": husband_id,
            "wife_id": wife_id,
            "marriage_date": marriage_date,
            "marriage_place": marriage_place,
            "notes": family_notes,
        }
    )

    return family_data


def _extract_children(
    fam: Dict[str, Any], persons: list, children: list, family_id: str
) -> None:
    """Extract children from family data."""
    for child in fam.get("children", []):
        c = child.get("person")
        if c:
            if "gender" in child:
                c["gender"] = child["gender"]

            child_data = ensure_person_fields(c)
            persons.append(child_data)
            children.append({"family_id": family_id, "child_id": child_data.get("id")})


def _extract_family_events(fam: Dict[str, Any], events: list, family_id: str) -> None:
    """Extract family events."""
    for evt in fam.get("events", []):
        event_data = ensure_event_fields(evt)
        events.append({"family_id": family_id, **event_data})


def _extract_person_events(parsed: Dict[str, Any], persons: list, events: list) -> None:
    """Extract person events from pevt blocks and link them to persons."""
    for person_data in parsed.get("people", []):
        person_name = (person_data.get("person") or "").strip()
        person_events = person_data.get("events") or []
        if not person_name or not person_events:
            continue
        person_id = _find_person_by_name(persons, person_name)
        if not person_id:
            continue
        for event in person_events:
            event_data = ensure_event_fields(event)
            events.append({"person_id": person_id, **event_data})


def _extract_person_notes(parsed: Dict[str, Any], persons: list) -> None:
    """Extract person notes and append them to matching persons."""
    for note_data in parsed.get("notes", []):
        person_name = (note_data.get("person") or "").strip()
        note_text = (note_data.get("text") or "").strip()
        if not person_name or not note_text:
            continue
        person = _find_person_by_name(persons, person_name, return_person=True)
        if not person:
            continue
        existing_notes = person.get("notes", "")
        person["notes"] = (
            f"{existing_notes}\n\n{note_text}" if existing_notes else note_text
        )


def _find_person_by_name(persons: list, name: str, return_person: bool = False):
    """Find person by name, return ID or person object."""
    normalized_name = name.lower().strip()
    for person in persons:
        if _full_name(person).lower() == normalized_name or (
            person.get("name", "").strip().lower() == normalized_name
        ):
            return person if return_person else person.get("id")
    return None


def _full_name(person: Dict[str, Any]) -> str:
    return f"{person.get('first_name', '')} {person.get('last_name', '')}".strip()


def _create_missing_persons_from_events(
    parsed: Dict[str, Any], persons: list, events: list
) -> None:
    """Create persons for people mentioned in pevt blocks but not in families."""
    for person_data in parsed.get("people", []):
        person_name = person_data.get("person", "").strip()
        person_events = person_data.get("events", [])

        if not person_name or not person_events:
            continue

        # Check if person already exists
        if _find_person_by_name(persons, person_name):
            continue

        # Create person from name
        name_parts = person_name.split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:])
        else:
            first_name = person_name
            last_name = ""

        # Create person data
        person_data_dict = {
            "id": str(uuid4()),
            "first_name": first_name,
            "last_name": last_name,
            "sex": "U",  # Unknown gender by default
            "name": person_name,
            "raw": person_name,
        }

        persons.append(person_data_dict)

        # Link their events
        person_id = person_data_dict["id"]
        for event in person_events:
            event_data = ensure_event_fields(event)
            events.append({"person_id": person_id, **event_data})
