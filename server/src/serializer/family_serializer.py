"""
family_serializer.py

GeneWeb family serializer.

Converts a family dictionary from JSON format back into a
GeneWeb-compatible family block.

Design goals:
- Preserve raw header structure
- Serialize family sources, events, and children
- Maintain GeneWeb .gw block structure
"""

from typing import Dict, Any
from .person_serializer import serialize_person
from .event_serializer import serialize_event
from .sources_serializer import serialize_sources


def serialize_family(family: Dict[str, Any]) -> str:
    """
    Serialize a single family block.

    Args:
        family (Dict[str, Any]): Family data containing raw header, sources,
                                    events, and children.

    Returns:
        str: GeneWeb-formatted family block.
    """
    lines = []

    # Family header
    lines.append(f"fam {family['raw_header']}")

    # Add sources if present
    _add_family_sources(lines, family)
    
    # Add events if present
    _add_family_events(lines, family)
    
    # Add children
    _add_family_children(lines, family)

    return "\n".join(lines)


def _add_family_sources(lines: list, family: Dict[str, Any]) -> None:
    """Add family sources to the output lines."""
    if "sources" in family and family["sources"]:
        sources_output = serialize_sources(family["sources"])
        if sources_output.strip():
            lines.append(sources_output)


def _add_family_events(lines: list, family: Dict[str, Any]) -> None:
    """Add family events to the output lines."""
    if "events" in family and family["events"]:
        lines.append("fevt")
        for event in family["events"]:
            lines.append(serialize_event(event))
        lines.append("end fevt")


def _add_family_children(lines: list, family: Dict[str, Any]) -> None:
    """Add family children to the output lines."""
    lines.append("beg")
    for child in family.get("children", []):
        gender = child.get("gender", "h")
        prefix = _get_child_prefix(gender)
        lines.append(f"- {prefix} {serialize_person(child['person'], raw=True)}")
    lines.append("end")


def _get_child_prefix(gender: str) -> str:
    """Get the appropriate prefix for a child based on gender."""
    if gender == "male":
        return "h"
    elif gender == "female":
        return "f"
    else:
        return gender
