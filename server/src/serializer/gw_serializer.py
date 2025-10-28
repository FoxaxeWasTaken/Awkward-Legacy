"""
gw_serializer.py

GeneWeb .gw / gwplus serializer that converts a structured JSON object
back into a GeneWeb-compatible `.gw` file.

Design goals:
- Serialize families, people, events, notes, sources, and pages
- Maintain the original structure and ordering of .gw files
- Produce output fully compatible with GeneWeb parsing
- Preserve raw lines and tags where applicable

Classes:
    - GWSerializer: Main serializer for GeneWeb data
"""

from typing import Dict, Any
from .family_serializer import serialize_family
from .notes_serializer import serialize_notes_db, serialize_notes
from .page_serializer import serialize_pages
from .pevt_serializer import serialize_pevts
from .sources_serializer import serialize_sources


class GWSerializer:
    """
    Main GeneWeb serializer.

    Converts structured JSON into a GeneWeb `.gw` file format.
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Initialize the serializer with a JSON-like dictionary.

        Args:
            data (Dict[str, Any]): Parsed GeneWeb data structure
                                        containing families, people, notes, sources, etc.
        """
        self.data = data

    def serialize(self) -> str:
        """
        Serialize the internal JSON data into a GeneWeb `.gw` format string.

        Returns:
            str: Complete GeneWeb `.gw` file content.
        """
        output_lines = []

        # Serialize header first
        self._serialize_header(output_lines)

        # Serialize families
        self._serialize_families(output_lines)

        # Serialize person events (pevt blocks)
        self._serialize_people_events(output_lines)

        # Serialize notes
        self._serialize_notes(output_lines)

        # Serialize extended pages
        self._serialize_pages(output_lines)

        # Serialize database notes
        self._serialize_notes_db(output_lines)

        return "\n\n".join(output_lines)

    def _serialize_header(self, output_lines: list) -> None:
        """Serialize file header."""
        header_lines = []

        # Add encoding if specified
        if "raw_header" in self.data and self.data["raw_header"].get("encoding"):
            header_lines.append(f"encoding: {self.data['raw_header']['encoding']}")

        # Add gwplus if specified
        if "raw_header" in self.data and self.data["raw_header"].get("gwplus"):
            header_lines.append("gwplus")

        if header_lines:
            output_lines.append("\n".join(header_lines))

    def _serialize_families(self, output_lines: list) -> None:
        """Serialize families section."""
        for family in self.data.get("families", []):
            output_lines.append(serialize_family(family))

    def _serialize_sources(self, output_lines: list) -> None:
        """Serialize sources section."""
        if "sources" in self.data:
            output_lines.append(serialize_sources(self.data["sources"]))

    def _serialize_people_events(self, output_lines: list) -> None:
        """Serialize people events section."""
        if "persons" in self.data:
            pevts_dict = self._build_pevts_dict()
            if pevts_dict:
                output_lines.append(serialize_pevts(pevts_dict))

    def _build_pevts_dict(self) -> Dict[str, Any]:
        """Build person events dictionary."""
        pevts_dict = {}
        for person in self.data.get("persons", []):
            # Try to get name from different possible fields
            person_name = person.get("name", "")
            if not person_name:
                first_name = person.get("first_name", "")
                last_name = person.get("last_name", "")
                person_name = f"{first_name} {last_name}".strip()

            person_events = person.get("events", [])

            # Include person even if they have no events (for test compatibility)
            if person_name:
                pevts_dict[person_name] = person_events
        return pevts_dict

    def _serialize_notes_db(self, output_lines: list) -> None:
        """Serialize notes database section."""
        if "notes_db" in self.data:
            output_lines.append(serialize_notes_db(self.data["notes_db"]))

    def _serialize_notes(self, output_lines: list) -> None:
        """Serialize individual notes section."""
        if "notes" in self.data:
            output_lines.append(serialize_notes(self.data["notes"]))

    def _serialize_pages(self, output_lines: list) -> None:
        """Serialize extended pages section."""
        if "extended_pages" in self.data and self.data["extended_pages"]:
            output_lines.append(serialize_pages(self.data["extended_pages"]))

    def _serialize_database_notes(self, output_lines: list) -> None:
        """Serialize database notes section."""
        if "database_notes" in self.data:
            output_lines.append(serialize_notes_db(self.data["database_notes"]))

    def to_file(self, path: str) -> None:
        """
        Serialize and save to a file.

        Args:
            path (str): Path to save the `.gw` file.
        """
        serialized = self.serialize()
        with open(path, "w", encoding="utf-8") as f:
            f.write(serialized)
