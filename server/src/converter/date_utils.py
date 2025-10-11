"""
Date utilities for GeneWeb converter.

Handles date parsing and conversion between different formats.
"""

from datetime import date, datetime
from typing import Dict, Any, Optional
import re


def parse_date_dict_to_date(date_dict: Dict[str, Any]) -> Optional[date]:
    """
    Convert a date dictionary from GeneWeb parsing to a proper date object.

    Args:
        date_dict: Dictionary with date information (e.g., {'raw': '3/3/1835', 'value': '3/3/1835'})

    Returns:
        Parsed date object or None if parsing fails
    """
    if not date_dict:
        return None

    date_str = date_dict.get("value") or date_dict.get("raw", "")

    if not date_str:
        return None

    return parse_date_string_to_date(date_str)


def parse_date_string_to_date(date_str: str) -> Optional[date]:
    """
    Parse a date string to a date object.

    Args:
        date_str: Date string in various formats (e.g., "3/3/1835", "1835-03-03", "1835")

    Returns:
        Parsed date object or None if parsing fails
    """
    if not date_str:
        return None

    date_formats = [
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%Y",
        "%m/%Y",
        "%Y-%m",
    ]

    for fmt in date_formats:
        try:
            parsed_datetime = datetime.strptime(date_str, fmt)
            return parsed_datetime.date()
        except ValueError:
            continue

    try:
        year_match = re.search(r'\b(1[0-9]{3}|2[0-9]{3})\b', date_str)
        if year_match:
            year = int(year_match.group(1))
            return date(year, 1, 1)
    except (ValueError, AttributeError):
        pass

    return None

