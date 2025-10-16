"""
Block parsing utilities for GeneWeb parser.

Handles parsing of various block types (notes, pages, etc.).
"""

import json
from typing import Dict, Any, List
from .models import PEVT_MAP
from .event_block_utils import parse_event_block


class BlockParser:
    """Handles parsing of various block types."""

    def __init__(self, lines: List[str], pos: int):
        self.lines = lines
        self.pos = pos
        self.length = len(lines)

    def parse_pevt(self) -> tuple[Dict[str, Any], int]:
        """Parse pevt block."""
        assert self.lines[self.pos].strip().startswith("pevt ")
        payload = self.lines[self.pos].strip()[len("pevt ") :].strip()
        current_pos = self.pos + 1

        events = parse_event_block(self.lines, current_pos, "end pevt", PEVT_MAP)
        return {"person": payload, "events": events}, current_pos + len(events) + 1

    def parse_notes(self) -> tuple[Dict[str, Any], int]:
        """Parse notes block."""
        assert self.lines[self.pos].strip().startswith("notes ")
        subject = self.lines[self.pos].strip()[len("notes ") :].strip()
        current_pos = self.pos + 1

        if current_pos < self.length and self.lines[current_pos].strip() == "beg":
            current_pos += 1

        lines = []
        while current_pos < self.length:
            line = self.lines[current_pos].rstrip("\n")
            if line.strip().startswith("end notes"):
                current_pos += 1
                break
            lines.append(line)
            current_pos += 1

        return {
            "person": subject,
            "text": "\n".join(lines).strip(),
            "raw_lines": lines,
        }, current_pos

    def parse_notes_db(self) -> tuple[Dict[str, Any], int]:
        """Parse notes-db block."""
        current_pos = self.pos + 1
        lines = []

        while current_pos < self.length:
            line = self.lines[current_pos]
            if line.strip().startswith("end notes-db"):
                current_pos += 1
                break
            lines.append(line)
            current_pos += 1

        return {"text": "\n".join(lines).strip(), "raw_lines": lines}, current_pos

    def parse_page_ext(self) -> tuple[Dict[str, Any], int]:
        """Parse page-ext block."""
        assert self.lines[self.pos].strip().startswith("page-ext ")
        name = self.lines[self.pos].strip()[len("page-ext ") :].strip()
        current_pos = self.pos + 1

        title, ptype, content_lines = None, None, []
        while current_pos < self.length:
            line = self.lines[current_pos]
            stripped = line.strip()
            if stripped.startswith("end page-ext"):
                current_pos += 1
                break
            if stripped.startswith("TITLE="):
                title = stripped.split("=", 1)[1].strip()
            elif stripped.startswith("TYPE="):
                ptype = stripped.split("=", 1)[1].strip()
            else:
                content_lines.append(line)
            current_pos += 1

        content_text = "\n".join(content_lines).strip()
        try:
            content = (
                json.loads(content_text)
                if content_text.startswith("{") and content_text.endswith("}")
                else content_text
            )
        except (json.JSONDecodeError, ValueError):
            content = content_text

        return {
            "name": name,
            "title": title,
            "type": ptype,
            "content": content,
        }, current_pos
