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

    return {
        "persons": persons,
        "families": families,
        "events": events,
        "children": children,
    }


def _extract_spouses(fam: Dict[str, Any], persons: list, family_id: str) -> tuple:
    """Extract husband and wife from family data."""
    husband = fam.get("husband")
    wife = fam.get("wife")

    husband_id = None
    wife_id = None

    if husband:
        husband_data = ensure_person_fields(husband)
        persons.append(husband_data)
        husband_id = husband_data.get("id")

    if wife:
        wife_data = ensure_person_fields(wife)
        persons.append(wife_data)
        wife_id = wife_data.get("id")

    return husband_id, wife_id


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
