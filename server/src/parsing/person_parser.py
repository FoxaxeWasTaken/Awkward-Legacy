"""
Person parsing utilities for GeneWeb parser.

Handles parsing of person segments and related data.
"""

from typing import Dict, Any, List, Tuple
from .models import PersonDict
from .token_parser import (
    tokenize_preserving_braces, extract_tags_and_dates_from_tokens,
    extract_name_tokens, split_name_into_parts
)
from .date_parser import parse_date_token, normalize_underscores


def parse_person_segment(segment: str) -> PersonDict:
    """
    Parse a person segment from a family or child line.

    Returns:
        PersonDict with:
        - name, first_name, last_name, sex, display_name, tags, dates, raw, other
    """
    tokens = tokenize_preserving_braces(segment)
    if not tokens:
        return {"raw": segment, "name": "", "first_name": "", "last_name": "", "sex": None, "display_name": None, "tags": {}, "dates": []}

    name_tokens, remaining_tokens = extract_name_tokens(tokens)
    tags, date_tokens, other_tokens = extract_tags_and_dates_from_tokens(remaining_tokens)

    full_name = " ".join(name_tokens)
    first_name, last_name = split_name_into_parts(full_name)

    gender_tag = tags.get("#gender")
    sex = None
    if gender_tag:
        g = gender_tag[0].upper()
        if g == "F":
            sex = "female"
        elif g == "M":
            sex = "male"
        else:
            sex = "Unknown"

    parsed_tags = {k.lstrip("#"): [normalize_underscores(v) for v in vs] for k, vs in tags.items()}

    return {
        "raw": segment,
        "name": full_name,
        "first_name": first_name,
        "last_name": last_name,
        "sex": sex,
        "display_name": normalize_underscores(full_name) or None,
        "tags": parsed_tags,
        "dates": [parse_date_token(t) for t in date_tokens],
        **({"other": other_tokens} if other_tokens else {})
    }
