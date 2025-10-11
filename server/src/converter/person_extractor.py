"""
Person data extraction utilities for GeneWeb converter.

Handles extraction of person-specific data from parsed GeneWeb data.
"""

from datetime import date
from typing import Dict, Any, Optional
from .date_utils import parse_date_dict_to_date, parse_date_string_to_date


def extract_birth_date_from_person_data(person_data: Dict[str, Any]) -> Optional[date]:
    """Extract birth date from person data."""
    extractors = [
        _extract_birth_date_from_events,
        _extract_birth_date_from_dates,
        _extract_birth_date_from_tags,
        _extract_birth_date_from_raw_string
    ]
    
    for extractor in extractors:
        birth_date = extractor(person_data)
        if birth_date:
            return birth_date
    
    return None


def _extract_birth_date_from_events(person_data: Dict[str, Any]) -> Optional[date]:
    """Extract birth date from events."""
    events = person_data.get("events", [])
    for event in events:
        if event.get("type") == "birth" and "date" in event:
            return parse_date_dict_to_date(event["date"]) if isinstance(event["date"], dict) else parse_date_string_to_date(event["date"])
    return None


def _extract_birth_date_from_dates(person_data: Dict[str, Any]) -> Optional[date]:
    """Extract birth date from dates list."""
    dates = person_data.get("dates", [])
    if dates:
        first_date = dates[0]
        if isinstance(first_date, dict):
            return parse_date_dict_to_date(first_date)
        elif isinstance(first_date, str):
            return parse_date_string_to_date(first_date)
    return None


def _extract_birth_date_from_tags(person_data: Dict[str, Any]) -> Optional[date]:
    """Extract birth date from tags."""
    tags = person_data.get("tags", {})
    if "birth" in tags:
        birth_values = tags["birth"]
        if birth_values:
            return parse_date_string_to_date(birth_values[0])
    return None


def _extract_birth_date_from_raw_string(person_data: Dict[str, Any]) -> Optional[date]:
    """Extract birth date from raw string."""
    raw_string = person_data.get("raw", "")
    if raw_string:
        import re
        years = re.findall(r'\b(1[0-9]{3}|2[0-9]{3})\b', raw_string)
        if years:
            try:
                year = int(years[0])
                return date(year, 1, 1)
            except ValueError:
                pass
    return None


def extract_death_date_from_person_data(person_data: Dict[str, Any]) -> Optional[date]:
    """Extract death date from person data."""
    extractors = [
        _extract_death_date_from_events,
        _extract_death_date_from_dates,
        _extract_death_date_from_tags,
        _extract_death_date_from_raw_string
    ]
    
    for extractor in extractors:
        death_date = extractor(person_data)
        if death_date:
            return death_date
    
    return None


def _extract_death_date_from_events(person_data: Dict[str, Any]) -> Optional[date]:
    """Extract death date from events."""
    events = person_data.get("events", [])
    for event in events:
        if event.get("type") == "death" and "date" in event:
            return parse_date_dict_to_date(event["date"]) if isinstance(event["date"], dict) else parse_date_string_to_date(event["date"])
    return None


def _extract_death_date_from_dates(person_data: Dict[str, Any]) -> Optional[date]:
    """Extract death date from dates list."""
    dates = person_data.get("dates", [])
    if len(dates) >= 2:
        second_date = dates[1]
        if isinstance(second_date, dict):
            return parse_date_dict_to_date(second_date)
        elif isinstance(second_date, str):
            return parse_date_string_to_date(second_date)
    return None


def _extract_death_date_from_tags(person_data: Dict[str, Any]) -> Optional[date]:
    """Extract death date from tags."""
    tags = person_data.get("tags", {})
    if "death" in tags:
        death_values = tags["death"]
        if death_values:
            return parse_date_string_to_date(death_values[0])
    return None


def _extract_death_date_from_raw_string(person_data: Dict[str, Any]) -> Optional[date]:
    """Extract death date from raw string."""
    raw_string = person_data.get("raw", "")
    if raw_string:
        import re
        years = re.findall(r'\b(1[0-9]{3}|2[0-9]{3})\b', raw_string)
        if len(years) >= 2:
            try:
                year = int(years[1])
                return date(year, 1, 1)
            except ValueError:
                pass
    return None


def extract_birth_place_from_person_data(person_data: Dict[str, Any]) -> Optional[str]:
    """Extract birth place from person data."""
    events = person_data.get("events", [])
    for event in events:
        if event.get("type") == "birth" and "place_raw" in event:
            return event["place_raw"]

    tags = person_data.get("tags", {})
    if "birth_place" in tags:
        birth_places = tags["birth_place"]
        if birth_places:
            return birth_places[0]

    return None


def extract_death_place_from_person_data(person_data: Dict[str, Any]) -> Optional[str]:
    """Extract death place from person data."""
    events = person_data.get("events", [])
    for event in events:
        if event.get("type") == "death" and "place_raw" in event:
            return event["place_raw"]

    tags = person_data.get("tags", {})
    if "death_place" in tags:
        death_places = tags["death_place"]
        if death_places:
            return death_places[0]

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

