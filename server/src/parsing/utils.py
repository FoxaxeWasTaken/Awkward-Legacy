"""
utils.py

Utility and parsing functions for GeneWeb parser.

Contains helper functions for:
- Text normalization
- Date parsing and interpretation
- Token parsing and manipulation
- Family header splitting
- Person segment parsing
- Event parsing
"""

import re
from typing import Dict, List, Optional, Tuple

from .models import DateDict, EventDict, PersonDict, TagsDict

# ===== CONSTANTS =====

DATE_QUAL_RE = re.compile(r"^(?P<qual>[<>\?~]{0,2}|0\(|\|{0,2})(?P<val>.*)$")
DATE_TOKEN_PATTERN = re.compile(r"[0-9\/\<\>\~\?\|\.]")  # date-like tokens

# ===== TEXT NORMALIZATION =====

def normalize_underscores(s: str) -> str:
    """Replace underscores with spaces in a string, preserving punctuation."""
    return s.replace("_", " ").strip()

# ===== DATE PARSING =====

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

    # Handle literal dates
    if token.startswith("0(") and token.endswith(")"):
        literal_text = token[2:-1]
        return {"raw": token, "literal": normalize_underscores(literal_text)}

    # Handle ranges
    if ".." in token:
        parts = [part.strip() for part in token.split("..", 1)]
        return {"raw": token, "between": parts}

    # Handle alternatives
    if "|" in token:
        parts = [part.strip() for part in token.split("|")]
        return {"raw": token, "alternatives": parts}

    # Handle qualifiers
    match = DATE_QUAL_RE.match(token)
    if not match:
        return {"raw": token}

    qualifier = match.group("qual") or ""
    value = match.group("val").strip()
    date: DateDict = {"raw": token}

    qualifiers_map = {
        "<": "before", "<<": "before",
        ">": "after", ">>": "after",
        "~": "approx",
        "?": "uncertain"
    }

    if qualifier in qualifiers_map:
        date["qualifier"] = qualifiers_map[qualifier]
        date["value"] = value
    else:
        date["value"] = value

    return date

# ===== TOKENIZATION =====

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

def tokenize_preserving_braces(text: str) -> List[str]:
    """
    Tokenize text by whitespace but preserve content inside braces.

    Example:
        "Jean-Baptiste {Jean-Baptiste_Laurent} #occu ..."
        → keeps "{...}" together.
    """
    tokens, i = [], 0
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue
        if text[i] == "{":
            start = i
            i += 1
            while i < len(text) and text[i] != "}":
                i += 1
            if i < len(text):
                i += 1
            tokens.append(text[start:i])
        else:
            start = i
            while i < len(text) and not text[i].isspace():
                i += 1
            tokens.append(text[start:i])
    return tokens

# ===== TAG EXTRACTION =====

def extract_tags_and_dates_from_tokens(tokens: List[str]) -> Tuple[TagsDict, List[str], List[str]]:
    """
    Extract tags, date tokens, and other tokens from a list of tokens.

    Returns:
        Tuple: (tags_dict, date_tokens, other_tokens)
    """
    tags: TagsDict = {}
    date_tokens: List[str] = []
    other_tokens: List[str] = []

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token.startswith("#"):
            tag_key = token
            value_parts = []
            i += 1
            while i < len(tokens) and not tokens[i].startswith("#"):
                value_parts.append(tokens[i])
                i += 1
            tags.setdefault(tag_key, []).append(" ".join(value_parts).strip())
            continue

        if DATE_TOKEN_PATTERN.search(token):
            date_tokens.append(token)
        else:
            other_tokens.append(token)
        i += 1

    return tags, date_tokens, other_tokens

def extract_name_tokens(tokens: List[str]) -> Tuple[List[str], List[str]]:
    """
    Extract name tokens from token list until a tag or date token is encountered.

    Returns:
        Tuple: (name_tokens, remaining_tokens)
    """
    name_tokens = []
    i = 0
    while i < len(tokens):
        tk = tokens[i]
        if tk.startswith("#") or DATE_TOKEN_PATTERN.match(tk):
            break
        name_tokens.append(tk)
        i += 1
    return name_tokens, tokens[i:]

# ===== PERSON SEGMENT PARSING =====

def parse_person_segment(segment: str) -> PersonDict:
    """
    Parse a person segment from a family or child line.

    Returns:
        PersonDict with:
        - name, display_name, tags, dates, raw, other
    """
    tokens = tokenize_preserving_braces(segment)
    if not tokens:
        return {"raw": segment}

    name_tokens, remaining_tokens = extract_name_tokens(tokens)
    tags, date_tokens, other_tokens = extract_tags_and_dates_from_tokens(remaining_tokens)

    return {
        "raw": segment,
        "name": " ".join(name_tokens),
        "display_name": normalize_underscores(" ".join(name_tokens)) or None,
        "tags": {k.lstrip("#"): [normalize_underscores(v) for v in vs] for k, vs in tags.items()},
        "dates": [parse_date_token(t) for t in date_tokens],
        **({"other": other_tokens} if other_tokens else {})
    }

# ===== EVENT PARSING =====

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

    place_match = re.search(r"#p\s*([^#]+)", text)
    if place_match:
        place_raw = place_match.group(1).strip()

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

# ===== NOTES AND UTILITIES =====

def parse_note_line(line: str) -> str:
    """Extract note text, removing 'note' prefix."""
    return line.strip()[5:].strip() if line.strip().startswith("note ") else line.strip()

def should_skip_empty_line(line: str) -> bool:
    """Return True if the line is empty or contains only whitespace."""
    return not line.strip()
