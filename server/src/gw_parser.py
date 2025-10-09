"""
gw_parser.py

GeneWeb .gw / gwplus parser that converts a .gw file into a single,
clean, nested, human-friendly JSON object.

Design goals:
- Human-readable keys: husband, wife, children, events, notes, sources...
- Nested structure for families and people
- Interpretation of tags (#marr → type: "marriage", #birt → "birth", ...)
- Structured parsing of date qualifiers: <, >, ~, ?, .., |, parentheses 0(...)
- Preserve raw values when interpretation may lose info
- Produce a single dict ready for json.dump(..., ensure_ascii=False, indent=2)

Usage:
    from gw_parser import GWParser
    parser = GWParser("input.gw")
    data = parser.parse()
    parser.to_json("output.json")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from .parsing.models import FEVT_MAP, PEVT_MAP, EventDict, FamilyDict, ParserResult, PersonDict
    from .parsing.utils import (
        parse_event_line, parse_note_line, parse_person_segment, split_family_header,
        should_skip_empty_line
    )
except ImportError:
    from parsing.models import FEVT_MAP, PEVT_MAP, EventDict, FamilyDict, ParserResult, PersonDict
    from parsing.utils import (
        parse_event_line, parse_note_line, parse_person_segment, split_family_header,
        should_skip_empty_line
    )

# ===== MAIN PARSER CLASS =====

class GWParser:
    """
    Main GeneWeb parser.

    Reads a .gw or .gwplus file and returns a structured dict representing:
    families, people, notes, extended pages, database notes, and raw header data.
    """

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        self.lines: List[str] = []
        self.pos: int = 0
        self.length: int = 0

        self.result: ParserResult = {
            "families": [],
            "people": [],
            "notes": [],
            "extended_pages": [],
            "database_notes": None,
            "raw_header": {},
        }

        self._block_parsers = {
            "fam ": self._parse_family,
            "pevt ": self._parse_pevt,
            "notes-db": self._parse_notes_db,
            "notes ": self._parse_notes,
            "page-ext ": self._parse_page_ext,
        }

        self._header_parsers = {
            "encoding:": self._parse_encoding_header,
            "gwplus": self._parse_gwplus_header,
        }

    def _read(self) -> None:
        """Read the .gw file into self.lines."""
        self.lines = self.path.read_text(encoding="utf-8").splitlines()
        self.lines = [line.rstrip("\n").rstrip("\r") for line in self.lines]
        self.pos = 0
        self.length = len(self.lines)

    def _current(self) -> str:
        """Return current line or empty string if EOF."""
        return self.lines[self.pos] if self.pos < self.length else ""

    def _advance(self, count: int = 1) -> None:
        """Advance parsing position."""
        self.pos += count

    def _peek(self, offset: int = 1) -> str:
        """Peek ahead without advancing position."""
        idx = self.pos + offset
        return self.lines[idx] if 0 <= idx < self.length else ""

    def parse(self) -> ParserResult:
        """Parse the file and return the structured parser result."""
        self._read()
        self._parse_headers()
        self._parse_main_blocks()
        return self.result

    def to_json(self, output_path: Union[str, Path]) -> None:
        """Write parser result to a JSON file."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.result, ensure_ascii=False, indent=2), encoding="utf-8")

    # ===== HEADER PARSING =====

    def _parse_headers(self) -> None:
        """Parse headers at the top of the file."""
        while self.pos < self.length:
            line = self._current().strip()
            if should_skip_empty_line(line):
                self._advance()
                continue
            handled = False
            for prefix, parser in self._header_parsers.items():
                if (prefix == "gwplus" and line == prefix) or line.startswith(prefix):
                    parser(line)
                    handled = True
                    break
            if not handled:
                break

    def _parse_encoding_header(self, line: str) -> None:
        """Parse an encoding header line."""
        encoding = line.split(":", 1)[-1].strip()
        self.result["raw_header"]["encoding"] = encoding
        self._advance()

    def _parse_gwplus_header(self, _: str) -> None:
        """Parse gwplus header line."""
        self.result["raw_header"]["gwplus"] = True
        self._advance()

    # ===== MAIN BLOCK PARSING =====

    def _parse_main_blocks(self) -> None:
        """Parse the main content blocks in the file."""
        while self.pos < self.length:
            line = self._current().strip()
            if should_skip_empty_line(line):
                self._advance()
                continue
            handled = False
            for prefix, parser in self._block_parsers.items():
                if line.startswith(prefix):
                    data = parser()
                    self._add_parsed_data(prefix, data)
                    handled = True
                    break
            if not handled:
                self.result.setdefault("raw_header_extra", []).append(line)
                self._advance()

    def _add_parsed_data(self, prefix: str, data: Any) -> None:
        """Add parsed block data to the result dict."""
        if prefix == "fam ":
            self.result["families"].append(data)
        elif prefix == "pevt ":
            self.result["people"].append(data)
        elif prefix == "notes-db":
            self.result["database_notes"] = data
        elif prefix == "notes ":
            self.result["notes"].append(data)
        elif prefix == "page-ext ":
            self.result["extended_pages"].append(data)

    # ===== FAMILY BLOCK =====

    def _parse_family(self) -> FamilyDict:
        """Parse a family block starting at current position."""
        line = self._current().strip()
        assert line.startswith("fam ")
        raw_header = line[len("fam "):].strip()
        self._advance()

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

        while self.pos < self.length:
            line = self._current().strip()
            if not line:
                self._advance()
                continue

            if line.startswith("src "):
                family["sources"].setdefault("family_source", []).append(line[len("src "):].strip())
                self._advance()
                continue
            if line.startswith("csrc "):
                family["sources"].setdefault("children_source", []).append(line[len("csrc "):].strip())
                self._advance()
                continue
            if line == "fevt":
                family["events"].extend(self._parse_fevt())
                continue
            if line == "beg":
                family["children"].extend(self._parse_beg())
                continue
            if any(line.startswith(p) for p in self._block_parsers):
                break
            family.setdefault("raw_lines", []).append(line)
            self._advance()

        return family

    def _parse_fevt(self) -> List[EventDict]:
        """Parse fevt ... end fevt block."""
        assert self._current().strip() == "fevt"
        self._advance()
        return self._parse_event_block("end fevt", FEVT_MAP)

    def _parse_event_block(self, end_marker: str, event_map: Dict[str, str]) -> List[EventDict]:
        """Common logic to parse events in fevt and pevt blocks."""
        events: List[EventDict] = []
        while self.pos < self.length:
            line = self._current().rstrip()
            if should_skip_empty_line(line):
                self._advance()
                continue
            if line.startswith(end_marker):
                self._advance()
                break
            if line.startswith("#"):
                events.append(parse_event_line(line, event_map))
                self._advance()
                continue
            if line.startswith("note "):
                note = parse_note_line(line)
                if not events:
                    events.append({"type": "note", "notes": [note]})
                else:
                    events[-1].setdefault("notes", []).append(note)
                self._advance()
                continue
            events.append({"type": "raw", "raw": line})
            self._advance()
        return events

    def _parse_beg(self) -> List[Dict[str, Any]]:
        """Parse beg ... end block containing children."""
        assert self._current().strip() == "beg"
        self._advance()
        children: List[Dict[str, Any]] = []

        while self.pos < self.length:
            line = self._current().rstrip()
            if not line:
                self._advance()
                continue
            if line == "end":
                self._advance()
                break
            if line.startswith("- "):
                raw_child = line[2:].strip()
                gender, remainder = self._extract_gender(raw_child)
                person = parse_person_segment(remainder)
                children.append({"raw": raw_child, "gender": gender, "person": person})
                self._advance()
                continue
            children.append({"raw_line": line})
            self._advance()
        return children

    def _extract_gender(self, text: str) -> Tuple[Optional[str], str]:
        """Extract gender prefix from child line."""
        parts = text.split(None, 1)
        if parts and parts[0] in ("h", "f"):
            return ("male" if parts[0] == "h" else "female", parts[1] if len(parts) > 1 else "")
        return None, text

    # ===== PERSON EVENTS =====

    def _parse_pevt(self) -> PersonDict:
        """Parse pevt block."""
        assert self._current().strip().startswith("pevt ")
        payload = self._current().strip()[len("pevt "):].strip()
        self._advance()
        events = self._parse_event_block("end pevt", PEVT_MAP)
        return {"person": payload, "events": events}

    # ===== NOTES =====

    def _parse_notes(self) -> Dict[str, Any]:
        """Parse notes block."""
        assert self._current().strip().startswith("notes ")
        subject = self._current().strip()[len("notes "):].strip()
        self._advance()
        if self._current().strip() == "beg":
            self._advance()
        lines = []
        while self.pos < self.length:
            line = self._current().rstrip("\n")
            if line.strip().startswith("end notes"):
                self._advance()
                break
            lines.append(line)
            self._advance()
        return {"person": subject, "text": "\n".join(lines).strip(), "raw_lines": lines}

    def _parse_notes_db(self) -> Dict[str, Any]:
        """Parse notes-db block."""
        self._advance()
        lines = []
        while self.pos < self.length:
            line = self._current()
            if line.strip().startswith("end notes-db"):
                self._advance()
                break
            lines.append(line)
            self._advance()
        return {"text": "\n".join(lines).strip(), "raw_lines": lines}

    # ===== EXTENDED PAGES =====

    def _parse_page_ext(self) -> Dict[str, Any]:
        """Parse page-ext block."""
        assert self._current().strip().startswith("page-ext ")
        name = self._current().strip()[len("page-ext "):].strip()
        self._advance()

        title, ptype, content_lines = None, None, []
        while self.pos < self.length:
            line = self._current()
            stripped = line.strip()
            if stripped.startswith("end page-ext"):
                self._advance()
                break
            if stripped.startswith("TITLE="):
                title = stripped.split("=", 1)[1].strip()
            elif stripped.startswith("TYPE="):
                ptype = stripped.split("=", 1)[1].strip()
            else:
                content_lines.append(line)
            self._advance()

        content_text = "\n".join(content_lines).strip()
        try:
            content = json.loads(content_text) if content_text.startswith("{") and content_text.endswith("}") else content_text
        except Exception:
            content = content_text

        return {"name": name, "title": title, "type": ptype, "content": content}
