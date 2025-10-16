"""
person_serializer.py

GeneWeb person serializer.

Design goals:
- Convert a person dictionary into a GeneWeb-compatible person string
- Support raw format output and structured output with tags and dates
- Serialize person events into `.gw` pevt blocks

Functions:
    - serialize_person: Serializes basic person information into GeneWeb format
    - serialize_person_events: Serializes a person's events into GeneWeb `.gw` format
"""

from typing import Dict, Any

from .event_serializer import serialize_event
from .utils import serialize_tags, serialize_dates


def serialize_person(person: Dict[str, Any], raw=False) -> str:
    """
    Serialize a person's basic information into a GeneWeb-compatible string.

    Args:
        person (Dict[str, Any]): Person dictionary containing name, tags, and dates.
        raw (bool): If True, return raw stored string without formatting.

    Returns:
        str: GeneWeb-formatted person line.
    """
    if raw:
        return person.get("raw", "")

    parts = [person.get("name", "")]
    parts.extend(serialize_tags(person.get("tags", {})))
    parts.extend(serialize_dates(person.get("dates", [])))
    return " ".join(parts)


def serialize_person_events(person: Dict[str, Any]) -> str:
    """
    Serialize events associated with a person into a GeneWeb `.gw` pevt block.

    Args:
        person (Dict[str, Any]): Person dictionary containing name and events.

    Returns:
        str: GeneWeb-formatted pevt block or empty string if no events.
    """
    lines = []
    if "events" in person and person["events"]:
        lines.append(f"pevt {person['name']}")
        for event in person["events"]:
            lines.append(serialize_event(event))
        lines.append("end pevt")
    return "\n".join(lines)
