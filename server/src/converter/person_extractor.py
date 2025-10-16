"""
Person data extraction utilities for GeneWeb converter.

Handles extraction of person-specific data from parsed GeneWeb data.
"""

from datetime import date
from typing import Dict, Any, Optional
from .date_utils import parse_date_dict_to_date, parse_date_string_to_date


def extract_birth_date_from_person_data(person_data: Dict[str, Any]) -> Optional[date]:
    """Extract birth date from person data."""
    return _extract_date_from_person_data(person_data, "birth", 0)


def _extract_date_from_person_data(
    person_data: Dict[str, Any], event_type: str, dates_index: int
) -> Optional[date]:
    """Generic function to extract date from person data using multiple strategies."""
    extractors = [
        lambda data: _extract_date_from_events(data, event_type),
        lambda data: _extract_date_from_dates_list(data, dates_index),
        lambda data: _extract_date_from_tags(data, event_type),
        lambda data: _extract_date_from_raw_string(data),
    ]

    for extractor in extractors:
        date_result = extractor(person_data)
        if date_result:
            return date_result

    return None


def _extract_date_from_events(
    person_data: Dict[str, Any], event_type: str
) -> Optional[date]:
    """Extract date from events by type."""
    events = person_data.get("events", [])
    for event in events:
        if event.get("type") == event_type and "date" in event:
            return _parse_date_value(event["date"])
    return None


def _extract_date_from_dates_list(
    person_data: Dict[str, Any], index: int = 0
) -> Optional[date]:
    """Extract date from dates list at specified index."""
    dates = person_data.get("dates", [])
    if len(dates) > index:
        return _parse_date_value(dates[index])
    return None


def _extract_date_from_tags(
    person_data: Dict[str, Any], tag_key: str
) -> Optional[date]:
    """Extract date from tags by key."""
    tags = person_data.get("tags", {})
    if tag_key in tags:
        tag_values = tags[tag_key]
        if tag_values:
            return parse_date_string_to_date(tag_values[0])
    return None


def _extract_date_from_raw_string(person_data: Dict[str, Any]) -> Optional[date]:
    """Extract date from raw string."""
    raw_string = person_data.get("raw", "")
    if raw_string:
        import re

        years = re.findall(r"\b(1[0-9]{3}|2[0-9]{3})\b", raw_string)
        if years:
            try:
                year = int(years[0])
                return date(year, 1, 1)
            except ValueError:
                pass
    return None


def _parse_date_value(date_value: Any) -> Optional[date]:
    """Parse a date value that could be a dict or string."""
    if isinstance(date_value, dict):
        return parse_date_dict_to_date(date_value)
    elif isinstance(date_value, str):
        return parse_date_string_to_date(date_value)
    return None


def extract_death_date_from_person_data(person_data: Dict[str, Any]) -> Optional[date]:
    """Extract death date from person data."""
    return _extract_date_from_person_data(person_data, "death", 1)


def extract_birth_place_from_person_data(person_data: Dict[str, Any]) -> Optional[str]:
    """Extract birth place from person data."""
    return _extract_place_from_person_data(person_data, "birth", "birth_place")


def extract_death_place_from_person_data(person_data: Dict[str, Any]) -> Optional[str]:
    """Extract death place from person data."""
    return _extract_place_from_person_data(person_data, "death", "death_place")


def _extract_place_from_person_data(
    person_data: Dict[str, Any], event_type: str, tag_key: str
) -> Optional[str]:
    """Extract place from person data by event type and tag key."""
    # Try events first
    place = _extract_place_from_events(person_data, event_type)
    if place:
        return place

    # Try tags
    return _extract_place_from_tags(person_data, tag_key)


def _extract_place_from_events(
    person_data: Dict[str, Any], event_type: str
) -> Optional[str]:
    """Extract place from events by type."""
    events = person_data.get("events", [])
    for event in events:
        if event.get("type") == event_type and "place_raw" in event:
            return event["place_raw"]
    return None


def _extract_place_from_tags(
    person_data: Dict[str, Any], tag_key: str
) -> Optional[str]:
    """Extract place from tags by key."""
    tags = person_data.get("tags", {})
    if tag_key in tags:
        places = tags[tag_key]
        if places:
            return places[0]
    return None


def extract_occupation_from_person_data(person_data: Dict[str, Any]) -> Optional[str]:
    """Extract occupation from person data."""
    # Try tags first
    occupation = _extract_occupation_from_tags(person_data)
    if occupation:
        return occupation

    # Try events
    return _extract_occupation_from_events(person_data)


def _extract_occupation_from_tags(person_data: Dict[str, Any]) -> Optional[str]:
    """Extract occupation from tags."""
    tags = person_data.get("tags", {})

    # Try "occu" tag first
    if "occu" in tags and tags["occu"]:
        return tags["occu"][0]

    # Try "occupation" tag
    if "occupation" in tags and tags["occupation"]:
        return tags["occupation"][0]

    return None


def _extract_occupation_from_events(person_data: Dict[str, Any]) -> Optional[str]:
    """Extract occupation from events."""
    events = person_data.get("events", [])
    for event in events:
        if event.get("type") == "occupation" and "description" in event:
            return event["description"]
    return None


def extract_notes_from_person_data(person_data: Dict[str, Any]) -> Optional[str]:
    """Extract notes from person data."""
    # Try direct notes first
    notes = _extract_notes_from_notes_field(person_data)
    if notes:
        return notes

    # Try tags
    notes = _extract_notes_from_tags(person_data)
    if notes:
        return notes

    # Try events
    return _extract_notes_from_events(person_data)


def _extract_notes_from_notes_field(person_data: Dict[str, Any]) -> Optional[str]:
    """Extract notes from notes field."""
    notes = person_data.get("notes", [])
    if notes:
        return " | ".join(notes)
    return None


def _extract_notes_from_tags(person_data: Dict[str, Any]) -> Optional[str]:
    """Extract notes from tags."""
    tags = person_data.get("tags", {})
    if "src" in tags and tags["src"]:
        return " | ".join(tags["src"])
    return None


def _extract_notes_from_events(person_data: Dict[str, Any]) -> Optional[str]:
    """Extract notes from events."""
    events = person_data.get("events", [])
    event_notes = []
    for event in events:
        if "notes" in event and event["notes"]:
            event_notes.extend(event["notes"])

    if event_notes:
        return " | ".join(event_notes)
    return None
