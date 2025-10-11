"""
Family parsing utilities for GeneWeb parser.

Handles parsing of family blocks and related structures.
"""

from typing import Dict, Any, List, Optional, Tuple
from .event_parser import parse_event_line, parse_note_line
from .person_parser import parse_person_segment
from .family_utils import split_family_header, should_skip_empty_line
from .models import FEVT_MAP, FamilyDict, EventDict


class FamilyParser:
    """Handles parsing of family blocks and related structures."""
    
    def __init__(self, lines: List[str], pos: int):
        self.lines = lines
        self.pos = pos
        self.length = len(lines)
        
    def parse_family(self) -> tuple[FamilyDict, int]:
        """
        Parse a family block starting at current position.
        
        Returns:
            Tuple of (family_data, new_position)
        """
        line = self.lines[self.pos].strip()
        assert line.startswith("fam ")
        raw_header = line[len("fam "):].strip()
        current_pos = self.pos + 1

        husband_segment, wife_segment = split_family_header(raw_header)
        husband = parse_person_segment(husband_segment)
        wife = parse_person_segment(wife_segment) if wife_segment else None

        family: FamilyDict = {
            "raw_header": raw_header,
            "husband": husband,
            "wife": wife,
            "events": [],
            "children": [],
            "sources": {},
        }

        while current_pos < self.length:
            line = self.lines[current_pos].strip()
            if not line:
                current_pos += 1
                continue

            if self._parse_family_sources(family, line):
                current_pos += 1
                continue
            if self._parse_family_events(family, line, current_pos):
                current_pos += 1
                continue
            if self._is_block_start(line):
                break

            family.setdefault("raw_lines", []).append(line)
            current_pos += 1

        return family, current_pos

    def _parse_family_sources(self, family: FamilyDict, line: str) -> bool:
        """Parse family source lines."""
        source_map = {
            "src": "family_source",
            "csrc": "children_source",
        }

        for key, field in source_map.items():
            if line.startswith(f"{key} "):
                family["sources"].setdefault(field, []).append(line[len(f"{key} "):].strip())
                return True
        return False

    def _parse_family_events(self, family: FamilyDict, line: str, pos: int) -> bool:
        """Parse family event lines."""
        if line == "fevt":
            events = self._parse_fevt(pos)
            family["events"].extend(events)
            return True
        if line == "beg":
            children = self._parse_beg(pos)
            family["children"].extend(children)
            return True
        return False

    def _parse_fevt(self, start_pos: int) -> List[EventDict]:
        """Parse fevt ... end fevt block."""
        assert self.lines[start_pos].strip() == "fevt"
        return self._parse_event_block(start_pos + 1, "end fevt", FEVT_MAP)

    def _parse_event_block(self, start_pos: int, end_marker: str, event_map: Dict[str, str]) -> List[EventDict]:
        """Common logic to parse events in fevt and pevt blocks."""
        events: List[EventDict] = []
        current_pos = start_pos
        
        while current_pos < self.length:
            line = self.lines[current_pos].rstrip()
            if should_skip_empty_line(line):
                current_pos += 1
                continue
            if line.startswith(end_marker):
                current_pos += 1
                break
            if line.startswith("#"):
                events.append(parse_event_line(line, event_map))
                current_pos += 1
                continue
            if line.startswith("note "):
                note = parse_note_line(line)
                if not events:
                    events.append({"type": "note", "notes": [note]})
                else:
                    events[-1].setdefault("notes", []).append(note)
                current_pos += 1
                continue
            events.append({"type": "raw", "raw": line})
            current_pos += 1
            
        return events

    def _parse_beg(self, start_pos: int) -> List[Dict[str, Any]]:
        """Parse beg ... end block containing children."""
        assert self.lines[start_pos].strip() == "beg"
        children: List[Dict[str, Any]] = []
        current_pos = start_pos + 1

        while current_pos < self.length:
            line = self.lines[current_pos].rstrip()
            if not line:
                current_pos += 1
                continue
            if line == "end":
                current_pos += 1
                break
            if line.startswith("- "):
                raw_child = line[2:].strip()
                gender, remainder = self._extract_gender(raw_child)
                person = parse_person_segment(remainder)
                children.append({"raw": raw_child, "gender": gender, "person": person})
                current_pos += 1
                continue
            children.append({"raw_line": line})
            current_pos += 1
            
        return children

    def _extract_gender(self, text: str) -> Tuple[Optional[str], str]:
        """Extract gender prefix from child line."""
        parts = text.split(None, 1)
        if parts and parts[0] in ("h", "f"):
            return ("male" if parts[0] == "h" else "female", parts[1] if len(parts) > 1 else "")
        return None, text

    def _is_block_start(self, line: str) -> bool:
        """Check if line starts a new block."""
        block_parsers = ["fam ", "pevt ", "notes-db", "notes ", "page-ext "]
        return any(line.startswith(p) for p in block_parsers)

