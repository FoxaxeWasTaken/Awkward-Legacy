"""
Date parsing utilities for GeneWeb parser.

Handles parsing and interpretation of date tokens and qualifiers.
"""

import re
from typing import Dict, Any, Optional
from .models import DateDict


# ===== CONSTANTS =====

DATE_QUAL_RE = re.compile(r"^(?P<qual>[<>\?~]{0,2}|0\(|\|{0,2})(?P<val>.*)$")
DATE_TOKEN_PATTERN = re.compile(r"[0-9\/\<\>\~\?\|\.]")  # date-like tokens


def parse_date_token(date_token: str) -> DateDict:
    """
    Parse a GeneWeb date token into a structured DateDict.

    Examples:
        "1814" -> {"raw": "1814", "value": "1814"}
        "<1849" -> {"raw":"<1849","qualifier":"before","value":"1849"}
        "~1750" -> {"raw":"~1750","qualifier":"approx","value":"1750"}
        "0(5_Mai_1990)" -> {"raw":"0(5_Mai_1990)","literal":"5 Mai 1990"}
        "10/5/1990|1991" -> {"raw":"10/5/1990|1991","alternatives":["10/5/1990","1991"]}
    """
    token = date_token.strip()
    if not token:
        return {"raw": token}

    # Try different parsing strategies
    parsers = [
        _parse_literal_date,
        _parse_range_date,
        _parse_alternatives_date,
        _parse_qualifier_date,
    ]

    for parser in parsers:
        result = parser(token)
        if result is not None:
            return result

    return {"raw": token}


def _parse_literal_date(token: str) -> Optional[DateDict]:
    """Parse literal date format."""
    if token.startswith("0(") and token.endswith(")"):
        literal_text = token[2:-1]
        return {"raw": token, "literal": normalize_underscores(literal_text)}
    return None


def _parse_range_date(token: str) -> Optional[DateDict]:
    """Parse range date format."""
    if ".." in token:
        parts = [part.strip() for part in token.split("..", 1)]
        return {"raw": token, "between": parts}
    return None


def _parse_alternatives_date(token: str) -> Optional[DateDict]:
    """Parse alternatives date format."""
    if "|" in token:
        parts = [part.strip() for part in token.split("|")]
        return {"raw": token, "alternatives": parts}
    return None


def _parse_qualifier_date(token: str) -> Optional[DateDict]:
    """Parse qualifier date format."""
    match = DATE_QUAL_RE.match(token)
    if not match:
        return None

    qualifier = match.group("qual") or ""
    value = match.group("val").strip()
    date: DateDict = {"raw": token}

    qualifiers_map = {
        "<": "before",
        "<<": "before",
        ">": "after",
        ">>": "after",
        "~": "approx",
        "?": "uncertain",
    }

    if qualifier in qualifiers_map:
        date["qualifier"] = qualifiers_map[qualifier]
        date["value"] = value
    elif value and DATE_TOKEN_PATTERN.search(token):
        date["value"] = value

    return date


def normalize_underscores(s: str) -> str:
    """Replace underscores with spaces in a string, preserving punctuation."""
    return s.replace("_", " ").strip()
