"""
Family parsing utilities for GeneWeb parser.

Handles parsing of family-related data.
"""

from typing import Tuple, Optional


def split_family_header(header: str) -> Tuple[str, Optional[str]]:
    """
    Split a family header into husband and wife segments.

    Args:
        header: Text after 'fam' keyword

    Returns:
        Tuple: (husband_segment, wife_segment or None)
    """
    for sep in (" + ", " +", "+ ", "+"):
        if sep in header:
            husband, wife = header.split(sep, 1)
            return husband.strip(), wife.strip()
    return header.strip(), None


def should_skip_empty_line(line: str) -> bool:
    """Return True if the line is empty or contains only whitespace."""
    return not line.strip()
