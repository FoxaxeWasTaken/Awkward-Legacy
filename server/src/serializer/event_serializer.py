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

    # Raw event line
    if event.get("raw"):
        lines.append(event["raw"])
    else:
        # Build event line from individual fields
        event_type = event.get("type", "")
        date = event.get("date", "")
        place = event.get("place", "")
        description = event.get("description", "")

        # Convert date to string if it's a date object
        if hasattr(date, "strftime"):
            date = date.strftime("%Y-%m-%d")

        if event_type:
            event_parts = [event_type]
            if date:
                event_parts.append(str(date))
            if place:
                event_parts.append(f"#pl {place}")
            if description:
                event_parts.append(f"#desc {description}")

            event_line = " ".join(event_parts)
            lines.append(event_line)

    # Notes attached to event
    if "notes" in event:
        for note in event["notes"]:
            lines.append(f"note {note}")

    return "\n".join(lines)
