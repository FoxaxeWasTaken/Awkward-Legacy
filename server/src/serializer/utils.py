"""
utils.py

GeneWeb tag and date serializer utilities.

Design goals:
- Convert internal JSON structures for tags and dates into GeneWeb-compatible strings
- Provide consistent, human-readable serialization for gender prefixes
- Maintain modular functions for reuse across serializers

Functions:
    - serialize_tags: Converts a tags dictionary into GeneWeb tag lines
    - serialize_dates: Converts date lists to GeneWeb date format
    - gender_prefix: Maps gender values to GeneWeb prefixes ('h' or 'f')
"""

from typing import Dict, List


def serialize_tags(tags: Dict[str, List[str]]) -> List[str]:
    """
    Convert a tags dictionary into a list of GeneWeb tag strings.

    Args:
        tags (Dict[str, List[str]]): Dictionary mapping tag names to lists of values.

    Returns:
        List[str]: List of GeneWeb-formatted tag strings.
    """
    parts = []
    for tag, values in tags.items():
        for value in values:
            parts.append(f"#{tag} {value}")
    return parts


def serialize_dates(dates: List[str]) -> List[str]:
    """
    Convert a list of date strings to GeneWeb-compatible date format.

    Currently passes through dates unchanged.
    Can be extended to format or normalize date values.

    Args:
        dates (List[str]): List of date strings.

    Returns:
        List[str]: Serialized date strings.
    """
    return dates


def gender_prefix(gender: str) -> str:
    """
    Map a JSON gender value to a GeneWeb-compatible prefix.

    GeneWeb uses:
        'h' → male
        'f' → female

    Args:
        gender (str): Gender value ("male", "female", "m", "f", etc.).

    Returns:
        str: GeneWeb gender prefix ('h' or 'f').
    """
    if not gender:
        return "h"
    gender = gender.lower()
    if gender in ["m", "male", "man", "homme", "h"]:
        return "h"
    elif gender in ["f", "female", "woman", "femme"]:
        return "f"
    return "h"
