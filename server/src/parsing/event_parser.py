"""
Event parsing utilities for GeneWeb parser.

Handles parsing of events and related data.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .models import EventDict
from .date_parser import parse_date_token, DATE_TOKEN_PATTERN


def extract_date_from_parts(parts: List[str]) -> Tuple[Optional[str], List[str]]:
    """Extract first date-like token and return remaining parts."""
    date_candidate, others = None, []
    for part in parts:
        if DATE_TOKEN_PATTERN.search(part) and date_candidate is None:
            date_candidate = part
        else:
            others.append(part)
    return date_candidate, others


def extract_place_and_source(text: str) -> Tuple[Optional[str], List[str]]:
    """
    Extract place (#p) and source (#s) from event content.

    Returns:
        Tuple: (place_raw, list_of_sources)
    """
    place_raw, sources = None, []

    # Look for explicit #p place tag
    place_match = re.search(r"#p\s*([^#]+)", text)
    if place_match:
        place_raw = place_match.group(1).strip()
    else:
        # If no #p tag, treat text before any # tags as place
        first_hash = text.find('#')
        if first_hash > 0:
            place_raw = text[:first_hash].strip()
        elif not any(tag in text for tag in ['#s', '#p']) and text.strip():
            # If no tags at all, treat the whole text as place
            place_raw = text.strip()
        else:
            place_raw = None

    source_matches = re.findall(r"#s\s*([^#]+)", text)
    sources.extend(s.strip() for s in source_matches)

    return place_raw, sources


def parse_event_line(event_line: str, event_type_mapping: Dict[str, str]) -> EventDict:
    """
    Parse an event line into structured EventDict.

    Example:
        "#birt 1813 #p Paris #s registry"
    """
    parts = event_line.strip().split(maxsplit=1)
    tag = parts[0]
    content = parts[1] if len(parts) > 1 else ""
    event_type = event_type_mapping.get(tag, tag.lstrip("#"))

    parsed: EventDict = {"type": event_type, "raw": event_line.strip()}

    if content:
        tokens = content.split()
        date_token, rest_tokens = extract_date_from_parts(tokens)
        if date_token:
            parsed["date"] = parse_date_token(date_token)
        if rest_tokens:
            place, sources = extract_place_and_source(" ".join(rest_tokens))
            if place:
                parsed["place_raw"] = place
            if sources:
                parsed["source"] = sources

    return parsed


def parse_note_line(line: str) -> str:
    """Extract note text, removing 'note' prefix."""
    return line.strip()[5:].strip() if line.strip().startswith("note ") else line.strip()
