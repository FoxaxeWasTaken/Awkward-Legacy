"""
Token parsing utilities for GeneWeb parser.

Handles tokenization and parsing of text segments.
"""

import re
from typing import List, Tuple
from .models import TagsDict
from .date_parser import DATE_TOKEN_PATTERN, normalize_underscores


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
            token, i = _extract_braced_token(text, i)
        else:
            token, i = _extract_regular_token(text, i)

        tokens.append(token)
    return tokens


def _extract_braced_token(text: str, start: int) -> Tuple[str, int]:
    """Extract token inside braces."""
    i = start + 1
    while i < len(text) and text[i] != "}":
        i += 1
    if i < len(text):
        i += 1
    return text[start:i], i


def _extract_regular_token(text: str, start: int) -> Tuple[str, int]:
    """Extract regular token (not in braces)."""
    i = start
    while i < len(text) and not text[i].isspace():
        i += 1
    return text[start:i], i


def extract_tags_and_dates_from_tokens(
    tokens: List[str],
) -> Tuple[TagsDict, List[str], List[str]]:
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


def split_name_into_parts(full_name: str) -> Tuple[str, str]:
    """
    Split a full name into first name and last name.

    Args:
        full_name: The full name string

    Returns:
        Tuple of (first_name, last_name)
    """
    if not full_name or not full_name.strip():
        return "", ""

    name_parts = full_name.strip().split()

    if len(name_parts) == 0:
        return "", ""
    elif len(name_parts) == 1:
        return name_parts[0], ""
    else:
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:])
        return first_name, last_name
