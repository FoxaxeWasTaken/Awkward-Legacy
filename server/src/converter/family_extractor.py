"""
Family data extraction utilities for GeneWeb converter.

Handles extraction of family-specific data from parsed GeneWeb data.
"""

from datetime import date
from typing import Dict, Any, Optional
from .date_utils import parse_date_dict_to_date, parse_date_string_to_date


def extract_marriage_date_from_family_data(
    family_data: Dict[str, Any],
) -> Optional[date]:
    """Extract marriage date from family data."""
    events = family_data.get("events", [])
    for event in events:
        if event.get("type") == "marriage" and "date" in event:
            return (
                parse_date_dict_to_date(event["date"])
                if isinstance(event["date"], dict)
                else parse_date_string_to_date(event["date"])
            )

    return None


def extract_marriage_place_from_family_data(
    family_data: Dict[str, Any],
) -> Optional[str]:
    """Extract marriage place from family data."""
    events = family_data.get("events", [])
    for event in events:
        if event.get("type") == "marriage" and "place_raw" in event:
            return event["place_raw"]

    return None


def extract_family_notes_from_family_data(family_data: Dict[str, Any]) -> Optional[str]:
    """Extract family notes from family data."""
    # First check for direct notes field
    direct_notes = _extract_direct_notes(family_data)
    if direct_notes:
        return direct_notes

    # Then check for notes in events
    event_notes = _extract_event_notes(family_data)
    if event_notes:
        return " | ".join(event_notes)

    return None


def _extract_direct_notes(family_data: Dict[str, Any]) -> Optional[str]:
    """Extract direct notes from family data."""
    if "notes" in family_data and family_data["notes"]:
        return str(family_data["notes"])
    return None


def _extract_event_notes(family_data: Dict[str, Any]) -> list:
    """Extract notes from family events."""
    events = family_data.get("events", [])
    event_notes = []
    for event in events:
        if "notes" in event and event["notes"]:
            if isinstance(event["notes"], list):
                event_notes.extend(event["notes"])
            else:
                event_notes.append(str(event["notes"]))
    return event_notes
