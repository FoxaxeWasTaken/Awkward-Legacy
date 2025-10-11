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
    place_raw = _extract_place_from_text(text)
    sources = _extract_sources_from_text(text)
    return place_raw, sources


def _extract_place_from_text(text: str) -> Optional[str]:
    """Extract place from text."""
    # Look for explicit #p place tag
    place_match = re.search(r"#p\s*([^#]+)", text)
    if place_match:
        return place_match.group(1).strip()
    
    # If no #p tag, treat text before any # tags as place
    first_hash = text.find('#')
    if first_hash > 0:
        return text[:first_hash].strip()
    
    # If no tags at all, treat the whole text as place
    if not any(tag in text for tag in ['#s', '#p']) and text.strip():
        return text.strip()
    
    return None


def _extract_sources_from_text(text: str) -> List[str]:
    """Extract sources from text."""
    source_matches = re.findall(r"#s\s*([^#]+)", text)
    return [s.strip() for s in source_matches]


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
        _parse_event_content(content, parsed)

    return parsed


def _parse_event_content(content: str, parsed: EventDict) -> None:
    """Parse event content and add to parsed dict."""
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


def parse_note_line(line: str) -> str:
    """Extract note text, removing 'note' prefix."""
    return line.strip()[5:].strip() if line.strip().startswith("note ") else line.strip()
