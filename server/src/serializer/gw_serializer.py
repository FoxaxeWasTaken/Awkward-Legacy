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

        self._serialize_families(output_lines)
        self._serialize_sources(output_lines)
        self._serialize_people_events(output_lines)
        self._serialize_notes_db(output_lines)
        self._serialize_notes(output_lines)
        self._serialize_pages(output_lines)
        self._serialize_database_notes(output_lines)

        return "\n\n".join(output_lines)

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
        if "people" in self.data:
            pevts_dict = self._build_pevts_dict()
            output_lines.append(serialize_pevts(pevts_dict))

    def _build_pevts_dict(self) -> Dict[str, Any]:
        """Build person events dictionary."""
        pevts_dict = {}
        for p in self.data["people"]:
            if "person" in p and "events" in p:
                pevts_dict[p["person"]] = p["events"] or []
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
        if "pages" in self.data:
            output_lines.append(serialize_pages(self.data["pages"]))

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
