"""
Header parsing utilities for GeneWeb parser.

Handles parsing of file headers and metadata.
"""

from typing import Dict, Any, List, Optional
from .family_utils import should_skip_empty_line


class HeaderParser:
    """Handles parsing of GeneWeb file headers."""
    
    def __init__(self, lines: List[str], pos: int):
        self.lines = lines
        self.pos = pos
        self.length = len(lines)

    def parse_headers(self) -> tuple[Dict[str, Any], int]:
        """
        Parse headers at the top of the file.
        
        Returns:
            Tuple of (parsed_headers, new_position)
        """
        headers = {"gwplus": False}
        current_pos = self.pos
        
        while current_pos < self.length:
            line = self.lines[current_pos].strip()

            if not _should_parse_line(line):
                current_pos += 1
                continue

            parser = _find_matching_parser(line, self)
            if parser:
                parser(line, headers)
                current_pos += 1
            else:
                break

        return headers, current_pos

    def _parse_encoding_header(self, line: str, headers: Dict[str, Any]) -> None:
        """Parse an encoding header line."""
        encoding = line.split(":", 1)[-1].strip()
        headers["encoding"] = encoding

    def _parse_gwplus_header(self, _: str, headers: Dict[str, Any]) -> None:
        """Parse gwplus header line."""
        headers["gwplus"] = True


def _should_parse_line(line: str) -> bool:
    """Return True if this line should be parsed as a header."""
    return not should_skip_empty_line(line)


def _find_matching_parser(line: str, parser_instance) -> Optional[callable]:
    """Return the parser for a matching header line, or None."""
    header_parsers = {
        "encoding:": parser_instance._parse_encoding_header,
        "gwplus": parser_instance._parse_gwplus_header,
    }
    
    for prefix, parser in header_parsers.items():
        if _matches_prefix(line, prefix):
            return parser
    return None


def _matches_prefix(line: str, prefix: str) -> bool:
    """Check if line matches the prefix."""
    if prefix == "gwplus":
        return line == prefix
    return line.startswith(prefix)