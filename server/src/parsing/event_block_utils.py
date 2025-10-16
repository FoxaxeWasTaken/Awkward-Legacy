"""
Event block parsing utilities for GeneWeb parser.

Shared utilities for parsing event blocks to eliminate code duplication.
"""

from typing import Dict, List
from .models import EventDict
from .event_parser import parse_event_line, parse_note_line
from .family_utils import should_skip_empty_line


def parse_event_block(
    lines: List[str], start_pos: int, end_marker: str, event_map: Dict[str, str]
) -> List[EventDict]:
    """
    Common logic to parse events in fevt and pevt blocks.

    Args:
        lines: List of file lines
        start_pos: Starting position in lines
        end_marker: Marker that indicates end of event block
        event_map: Mapping of event tags to event types

    Returns:
        List of parsed events
    """
    events: List[EventDict] = []
    current_pos = start_pos
    length = len(lines)

    while current_pos < length:
        line = lines[current_pos].rstrip()
        if should_skip_empty_line(line):
            current_pos += 1
            continue
        if line.startswith(end_marker):
            current_pos += 1
            break

        process_event_line(line, event_map, events)
        current_pos += 1

    return events


def process_event_line(
    line: str, event_map: Dict[str, str], events: List[EventDict]
) -> None:
    """
    Process a single event line and add to events list.

    Args:
        line: Event line to process
        event_map: Mapping of event tags to event types
        events: List to add processed event to
    """
    if line.startswith("#"):
        events.append(parse_event_line(line, event_map))
    elif line.startswith("note "):
        handle_note_line(line, events)
    else:
        events.append({"type": "raw", "raw": line})


def handle_note_line(line: str, events: List[EventDict]) -> None:
    """
    Handle note line by either creating new note event or adding to last event.

    Args:
        line: Note line to process
        events: List to add note to
    """
    note = parse_note_line(line)

    if not events:
        events.append({"type": "note", "notes": [note]})
    else:
        events[-1].setdefault("notes", []).append(note)
