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
from typing import Any, Dict, List, Union

try:
    from .parsing.models import ParserResult
    from .parsing.header_parser import HeaderParser
    from .parsing.family_parser import FamilyParser
    from .parsing.block_parser import BlockParser
    from .parsing.family_utils import should_skip_empty_line
except ImportError:
    from parsing.models import ParserResult
    from parsing.header_parser import HeaderParser
    from parsing.family_parser import FamilyParser
    from parsing.block_parser import BlockParser
    from parsing.family_utils import should_skip_empty_line

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
            "raw_header": {"gwplus": False},
        }

        self._block_parsers = {
            "fam ": self._parse_family,
            "pevt ": self._parse_pevt,
            "notes-db": self._parse_notes_db,
            "notes ": self._parse_notes,
            "page-ext ": self._parse_page_ext,
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
        p.write_text(
            json.dumps(self.result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # ===== HEADER PARSING =====

    def _parse_headers(self) -> None:
        """Parse headers at the top of the file."""
        header_parser = HeaderParser(self.lines, self.pos)
        headers, new_pos = header_parser.parse_headers()
        self.result["raw_header"].update(headers)
        self.pos = new_pos

    # ===== MAIN BLOCK PARSING =====

    def _parse_main_blocks(self) -> None:
        """Parse the main content blocks in the file."""
        while self.pos < self.length:
            line = self._current().strip()
            if should_skip_empty_line(line):
                self._advance()
                continue

            if self._try_parse_block(line):
                continue

            self._handle_unrecognized_line(line)

    def _try_parse_block(self, line: str) -> bool:
        """Try to parse a recognized block type."""
        for prefix, parser in self._block_parsers.items():
            if line.startswith(prefix):
                data = parser()
                self._add_parsed_data(prefix, data)
                return True
        return False

    def _handle_unrecognized_line(self, line: str) -> None:
        """Handle lines that don't match any known block type."""
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

    def _parse_family(self) -> Dict[str, Any]:
        """Parse a family block starting at current position."""
        family_parser = FamilyParser(self.lines, self.pos)
        family, new_pos = family_parser.parse_family()
        self.pos = new_pos
        return family

    # ===== PERSON EVENTS =====

    def _parse_pevt(self) -> Dict[str, Any]:
        """Parse pevt block."""
        block_parser = BlockParser(self.lines, self.pos)
        data, new_pos = block_parser.parse_pevt()
        self.pos = new_pos
        return data

    # ===== NOTES =====

    def _parse_notes(self) -> Dict[str, Any]:
        """Parse notes block."""
        block_parser = BlockParser(self.lines, self.pos)
        data, new_pos = block_parser.parse_notes()
        self.pos = new_pos
        return data

    def _parse_notes_db(self) -> Dict[str, Any]:
        """Parse notes-db block."""
        block_parser = BlockParser(self.lines, self.pos)
        data, new_pos = block_parser.parse_notes_db()
        self.pos = new_pos
        return data

    # ===== EXTENDED PAGES =====

    def _parse_page_ext(self) -> Dict[str, Any]:
        """Parse page-ext block."""
        block_parser = BlockParser(self.lines, self.pos)
        data, new_pos = block_parser.parse_page_ext()
        self.pos = new_pos
        return data
