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
    import re
    
    marriage_date_pattern = r'\+\d{4}-\d{2}-\d{2}'
    
    match = re.search(marriage_date_pattern, header)
    if match:
        before_date = header[:match.start()].strip()
        after_date = header[match.end():].strip()
        
        husband = before_date

        words = after_date.split()
        wife_start_idx = 0
        
        mp_found = False
        for i, word in enumerate(words):
            if word == '#mp':
                mp_found = True

                wife_start_idx = i + 1

                while wife_start_idx < len(words) - 1:
                    current_word = words[wife_start_idx]
                    next_word = words[wife_start_idx + 1]

                    current_is_name_part = (',' not in current_word and 
                                          not (current_word.isupper() and len(current_word) <= 3) and
                                          not current_word.startswith('#'))
                    next_is_name_part = (',' not in next_word and 
                                       not (next_word.isupper() and len(next_word) <= 3) and
                                       not next_word.startswith('#'))

                    has_tag_after = (wife_start_idx + 2 < len(words) and 
                                   words[wife_start_idx + 2].startswith('#'))
                    
                    if current_is_name_part and next_is_name_part and has_tag_after:
                        break
                    wife_start_idx += 1
                break
        
        if mp_found and wife_start_idx < len(words):
            wife_end_idx = len(words)
            for i in range(wife_start_idx + 1, len(words)):
                if words[i].startswith('#'):
                    wife_end_idx = i
                    break
            
            wife_name_parts = words[wife_start_idx:wife_end_idx]
            
            if len(wife_name_parts) >= 2:
                wife = ' '.join(wife_name_parts[:2])
            elif len(wife_name_parts) == 1:
                wife = wife_name_parts[0]
            else:
                wife = None
        else:
            for i, word in enumerate(words):
                if not word.startswith('#'):
                    wife_start_idx = i
                    break
            
            if wife_start_idx < len(words):
                wife_end_idx = len(words)
                for i in range(wife_start_idx + 1, len(words)):
                    if words[i].startswith('#'):
                        wife_end_idx = i
                        break
                
                wife_name_parts = words[wife_start_idx:wife_end_idx]
                
                # Find the last two words that look like names (not places with commas)
                name_candidates = []
                for part in reversed(wife_name_parts):
                    if ',' not in part and len(part) < 20 and not part.isupper() and part.isalpha():
                        name_candidates.insert(0, part)
                        if len(name_candidates) >= 2:
                            break
                
                # Use the last 2 words as the wife name, or just 1 if that's all we have
                if len(name_candidates) >= 2:
                    wife = ' '.join(name_candidates[-2:])
                elif len(name_candidates) == 1:
                    wife = name_candidates[0]
                else:
                    wife = None
            else:
                wife = None
            
        return husband, wife
    
    # Fallback to original logic for simple cases
    for sep in (" + ", " +", "+ ", "+"):
        if sep in header:
            husband, wife = header.split(sep, 1)
            return husband.strip(), wife.strip()
    return header.strip(), None


def should_skip_empty_line(line: str) -> bool:
    """Return True if the line is empty or contains only whitespace."""
    return not line.strip()
