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

    # Family sources
    if "sources" in family:
        lines.append(serialize_sources(family["sources"]))

    # Family events
    if "events" in family:
        lines.append("fevt")
        for event in family["events"]:
            lines.append(serialize_event(event))
        lines.append("end fevt")

    # Children block
    lines.append("beg")
    for child in family.get("children", []):
        gender = child.get("gender", "h")
        prefix = "h" if gender == "male" else "f" if gender == "female" else gender
        lines.append(f"- {prefix} {serialize_person(child['person'], raw=True)}")
    lines.append("end")

    return "\n".join(lines)
