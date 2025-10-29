"""
event_serializer.py

GeneWeb event serializer.

Converts event dictionaries from JSON format back into
GeneWeb-compatible event lines.

Design goals:
- Preserve raw event lines when possible
- Serialize associated notes
- Maintain GeneWeb .gw formatting for events
"""

from typing import Dict, Any


def serialize_event(event: Dict[str, Any]) -> str:
    """
    Serialize a single event.

    Args:
        event (Dict[str, Any]): Event data containing raw text and optional notes.

    Returns:
        str: GeneWeb-formatted event line(s).
    """
    lines = []

    # Add main event line
    event_line = _build_event_line(event)
    if event_line:
        lines.append(event_line)

    # Add event notes
    event_notes = _build_event_notes(event)
    lines.extend(event_notes)

    return "\n".join(lines)


def _build_event_line(event: Dict[str, Any]) -> str:
    """Build the main event line."""
    if event.get("raw"):
        return event["raw"]

    return _build_event_from_fields(event)


def _build_event_from_fields(event: Dict[str, Any]) -> str:
    """Build event line from individual fields."""
    event_type = event.get("type", "")
    if not event_type:
        return ""

    event_parts = [event_type]
    date = _format_event_date(event.get("date", ""))
    if date:
        event_parts.append(date)
    if event.get("place"):
        event_parts.append(f"#pl {event['place']}")
    if event.get("description"):
        event_parts.append(f"#desc {event['description']}")

    return " ".join(event_parts)


def _format_event_date(date) -> str:
    """Format event date to string."""
    if not date:
        return ""
    if hasattr(date, "strftime"):
        return date.strftime("%Y-%m-%d")
    return str(date)


def _build_event_notes(event: Dict[str, Any]) -> list:
    """Build event notes list."""
    notes = []
    if "notes" in event:
        for note in event["notes"]:
            notes.append(f"note {note}")
    return notes
