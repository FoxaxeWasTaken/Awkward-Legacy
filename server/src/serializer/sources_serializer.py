"""
sources_serializer.py

GeneWeb sources serializer.

Design goals:
- Convert JSON sources into GeneWeb `.gw` source block strings
- Support family-level and children-level source serialization
- Maintain modular serialization for integration with GWSerializer

Functions:
    - serialize_sources: Converts sources dictionary into GeneWeb source strings
"""

from typing import Dict, List


def serialize_sources(sources: Dict[str, List[str]]) -> str:
    """
    Serialize source references for families and children into GeneWeb `.gw` format.

    GeneWeb uses:
        src <source_name>    → family-level sources
        csrc <source_name>   → children-level sources
        csources <source_name> → children source references

    Args:
        sources (Dict[str, List[str]]): Dictionary with keys 'family_source' and/or 'children_source'.

    Returns:
        str: GeneWeb-formatted source block string.
    """
    lines = []

    _serialize_family_sources(lines, sources)
    _serialize_children_sources(lines, sources)

    return "\n".join(lines)


def _serialize_family_sources(lines: list, sources: Dict[str, List[str]]) -> None:
    """Serialize family-level sources."""
    family_sources = sources.get("family_source")
    if isinstance(family_sources, list):
        for src in family_sources:
            lines.append(f"src {src}")
        for csrc in family_sources:
            lines.append(f"csrc {csrc}")


def _serialize_children_sources(lines: list, sources: Dict[str, List[str]]) -> None:
    """Serialize children-level sources."""
    children_sources = sources.get("children_source")
    if isinstance(children_sources, list):
        for csrc in children_sources:
            lines.append(f"csources {csrc}")
