"""
notes_serializer.py

GeneWeb notes serializer.

Design goals:
- Serialize notes database and individual notes into GeneWeb `.gw` format
- Preserve structure of notes with proper block markers
- Ensure compatibility with GeneWeb parsing conventions

Functions:
    - serialize_notes_db: Serialize the notes database section
    - serialize_notes: Serialize individual notes blocks
"""

from typing import Dict


def serialize_notes_db(notes_db: Dict[str, str]) -> str:
    """
    Serialize the notes database metadata into a GeneWeb-compatible block.

    Args:
        notes_db (Dict[str, str]): Dictionary containing notes database metadata.

    Returns:
        str: GeneWeb `.gw` formatted notes-db block.
    """
    lines = ["notes-db"]
    for key, value in notes_db.items():
        lines.append(f"  {key}={value}")
    return "\n".join(lines)


def serialize_notes(notes: list[dict[str, str]]) -> str:
    """
    Serialize individual notes for multiple persons.

    Args:
        notes (list[dict[str, str]]): List of note dictionaries with 'person' and 'text'.

    Returns:
        str: GeneWeb `.gw` formatted notes blocks.
    """
    output = []
    for note in notes:
        output.append(f"notes {note['person']}")
        output.append("beg")
        if note.get("text"):
            output.extend(note["text"].splitlines())
        output.append("end notes")
    return "\n".join(output)
