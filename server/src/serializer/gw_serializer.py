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
from family_serializer import serialize_family
from notes_serializer import serialize_notes_db, serialize_notes
from page_serializer import serialize_pages
from pevt_serializer import serialize_pevts
from sources_serializer import serialize_sources


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

        # Serialize families
        for family in self.data.get("families", []):
            output_lines.append(serialize_family(family))

        # Serialize sources
        if "sources" in self.data:
            output_lines.append(serialize_sources(self.data["sources"]))

        # Serialize person events
        if "people" in self.data:
            pevts_dict = {}
            for p in self.data["people"]:
                if "person" in p and "events" in p:
                    pevts_dict[p["person"]] = p["events"] or []
            output_lines.append(serialize_pevts(pevts_dict))

        # Serialize notes database
        if "notes_db" in self.data:
            output_lines.append(serialize_notes_db(self.data["notes_db"]))

        # Serialize individual notes
        if "notes" in self.data:
            output_lines.append(serialize_notes(self.data["notes"]))

        # Serialize extended pages
        if "pages" in self.data:
            output_lines.append(serialize_pages(self.data["pages"]))

        # Serialize database notes if present
        if "database_notes" in self.data:
            output_lines.append(serialize_notes_db(self.data["database_notes"]))

        return "\n\n".join(output_lines)

    def to_file(self, path: str) -> None:
        """
        Serialize and save to a file.

        Args:
            path (str): Path to save the `.gw` file.
        """
        serialized = self.serialize()
        with open(path, "w", encoding="utf-8") as f:
            f.write(serialized)
