"""
pevt_serializer.py

GeneWeb person events serializer.

Design goals:
- Convert person events in JSON format to GeneWeb `.gw` event blocks
- Support multiple persons
- Produce clean, human-readable `.gw` pevt blocks

Functions:
    - serialize_pevts: Serializes a dictionary of person events into GeneWeb format
"""

from typing import Any, Dict, List

from .event_serializer import serialize_event


def serialize_pevts(pevts: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Serialize person events (pevts) into GeneWeb `.gw` pevt blocks.

    Args:
        pevts (Dict[str, List[Dict[str, Any]]]):
            Dictionary where keys are person names and values are lists of event dictionaries.

    Returns:
        str: GeneWeb-formatted pevt blocks.
    """
    lines = []
    for person_name, events in pevts.items():
        lines.append(f"pevt {person_name}")
        for event in events:
            event_str = serialize_event(event)
            lines.append(event_str)
        lines.append("end pevt")
    return "\n".join(lines)
