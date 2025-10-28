"""Family parsing utilities for GeneWeb parser."""

import re
from typing import Tuple, Optional


def split_family_header(header: str) -> Tuple[str, Optional[str]]:
    """Split a family header into husband and wife segments."""
    marriage_date_pattern = r'\+\d{4}-\d{2}-\d{2}'
    match = re.search(marriage_date_pattern, header)

    if match:
        husband = header[:match.start()].strip()
        words = header[match.end():].strip().split()

        wife = _extract_wife_from_complex_format(words)
        return husband, wife

    return _extract_wife_from_simple_format(header)


def _extract_wife_from_complex_format(words: list) -> Optional[str]:
    """Extract wife name from complex family format with marriage place."""
    mp_found = False
    wife_start_idx = 0

    for i, word in enumerate(words):
        if word == '#mp':
            mp_found = True
            wife_start_idx = i + 1

            while wife_start_idx < len(words) - 1:
                current_word = words[wife_start_idx]
                next_word = words[wife_start_idx + 1]

                if _is_person_name_pair(current_word, next_word, words, wife_start_idx):
                    break
                wife_start_idx += 1
            break

    if mp_found and wife_start_idx < len(words):
        return _extract_name_from_parts(words, wife_start_idx)

    return _extract_wife_from_simple_format(' '.join(words))


def _extract_wife_from_simple_format(header: str) -> Tuple[str, Optional[str]]:
    """Extract wife from simple family format."""
    for sep in (" + ", " +", "+ ", "+"):
        if sep in header:
            husband, wife = header.split(sep, 1)
            return husband.strip(), wife.strip()
    return header.strip(), None


def _is_person_name_pair(current: str, next_word: str, words: list, idx: int) -> bool:
    """Check if two words form a person name pair."""
    current_valid = (',' not in current and
                    not (current.isupper() and len(current) <= 3) and
                    not current.startswith('#'))
    next_valid = (',' not in next_word and
                 not (next_word.isupper() and len(next_word) <= 3) and
                 not next_word.startswith('#'))
    has_tag_after = (idx + 2 < len(words) and words[idx + 2].startswith('#'))

    return current_valid and next_valid and has_tag_after


def _extract_name_from_parts(words: list, start_idx: int) -> Optional[str]:
    """Extract name from word parts."""
    end_idx = len(words)
    for i in range(start_idx + 1, len(words)):
        if words[i].startswith('#'):
            end_idx = i
            break

    name_parts = words[start_idx:end_idx]
    if len(name_parts) >= 2:
        return ' '.join(name_parts[:2])
    if len(name_parts) == 1:
        return name_parts[0]
    return None


def should_skip_empty_line(line: str) -> bool:
    """Return True if the line is empty or contains only whitespace."""
    return not line.strip()
