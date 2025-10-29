"""Family parsing utilities for GeneWeb parser."""

import re
from typing import Tuple, Optional


def split_family_header(header: str) -> Tuple[str, Optional[str]]:
    """Split a family header into husband and wife segments."""
    marriage_date_pattern = r"\+\d{4}-\d{2}-\d{2}"
    match = re.search(marriage_date_pattern, header)

    if match:
        husband = header[: match.start()].strip()
        words = header[match.end() :].strip().split()

        wife = _extract_wife_from_complex_format(words)
        return husband, wife

    return _extract_wife_from_simple_format(header)


def _extract_wife_from_complex_format(words: list) -> Optional[str]:
    """Extract wife name from complex family format with marriage place."""
    try:
        mp_index = words.index("#mp")
    except ValueError:
        return _extract_wife_from_simple_format(" ".join(words))

    start_idx = _find_first_name_pair_after(words, mp_index + 1)
    if start_idx is None:
        # Fallback: simple split, but return only the wife segment (string)
        _, wife = _extract_wife_from_simple_format(" ".join(words))
        return wife
    return _extract_name_from_parts(words, start_idx)


def _find_first_name_pair_after(words: list, idx: int) -> Optional[int]:
    while idx < len(words) - 1:
        if _is_person_name_pair(words[idx], words[idx + 1], words, idx):
            return idx
        idx += 1
    return None


def _extract_wife_from_simple_format(header: str) -> Tuple[str, Optional[str]]:
    """Extract wife from simple family format."""
    for sep in (" + ", " +", "+ ", "+"):
        if sep in header:
            husband, wife = header.split(sep, 1)
            return husband.strip(), wife.strip()
    return header.strip(), None


def _is_person_name_pair(current: str, next_word: str, words: list, idx: int) -> bool:
    """Check if two words form a person name pair."""
    return (
        _is_valid_name_word(current)
        and _is_valid_name_word(next_word)
        and _has_tag_after(words, idx)
    )


def _is_valid_name_word(word: str) -> bool:
    """Check if a word is a valid name component."""
    return (
        "," not in word
        and not (word.isupper() and len(word) <= 3)
        and not word.startswith("#")
    )


def _has_tag_after(words: list, idx: int) -> bool:
    """Check if there's a tag after the current position."""
    return idx + 2 < len(words) and words[idx + 2].startswith("#")


def _extract_name_from_parts(words: list, start_idx: int) -> Optional[str]:
    """Extract name from word parts."""
    end_idx = len(words)
    for i in range(start_idx + 1, len(words)):
        if words[i].startswith("#"):
            end_idx = i
            break

    name_parts = words[start_idx:end_idx]
    if len(name_parts) >= 2:
        return " ".join(name_parts[:2])
    if len(name_parts) == 1:
        return name_parts[0]
    return None


def should_skip_empty_line(line: str) -> bool:
    """Return True if the line is empty or contains only whitespace."""
    return not line.strip()
