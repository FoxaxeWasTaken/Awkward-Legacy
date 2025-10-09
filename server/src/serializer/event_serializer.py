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

    # Notes attached to event
    if "notes" in event:
        for note in event["notes"]:
            lines.append(f"note {note}")

    return "\n".join(lines)
