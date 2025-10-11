"""
Tests for parsing event parser.
"""

import pytest
from src.parsing.event_parser import (
    extract_date_from_parts,
    extract_place_and_source,
    parse_event_line,
    parse_note_line
)


class TestExtractDateFromParts:
    """Test extract_date_from_parts function."""
    
    def test_extract_date(self):
        """Test extracting date from parts."""
        parts = ["Jean", "Baptiste", "1814", "Paris"]
        date_candidate, others = extract_date_from_parts(parts)
        assert date_candidate == "1814"
        assert others == ["Jean", "Baptiste", "Paris"]
    
    def test_no_date(self):
        """Test no date in parts."""
        parts = ["Jean", "Baptiste", "Paris"]
        date_candidate, others = extract_date_from_parts(parts)
        assert date_candidate is None
        assert others == ["Jean", "Baptiste", "Paris"]


class TestExtractPlaceAndSource:
    """Test extract_place_and_source function."""
    
    def test_place_and_sources(self):
        """Test extracting place and sources."""
        text = "Paris #s registry #s church"
        place, sources = extract_place_and_source(text)
        assert place == "Paris"
        assert sources == ["registry", "church"]
    
    def test_no_place(self):
        """Test no place in text."""
        text = "#s registry"
        place, sources = extract_place_and_source(text)
        assert place is None
        assert sources == ["registry"]
    
    def test_no_sources(self):
        """Test no sources in text."""
        text = "Paris"
        place, sources = extract_place_and_source(text)
        assert place == "Paris"
        assert sources == []
    
    def test_empty_string(self):
        """Test empty string."""
        place, sources = extract_place_and_source("")
        assert place is None
        assert sources == []


class TestParseEventLine:
    """Test parse_event_line function."""
    
    def test_basic_event(self):
        """Test parsing basic event."""
        event_line = "#birt 1813 #p Paris #s registry"
        event_type_mapping = {"#birt": "birth"}
        result = parse_event_line(event_line, event_type_mapping)
        assert result["type"] == "birth"
        assert result["raw"] == "#birt 1813 #p Paris #s registry"
        assert result["date"]["value"] == "1813"
        assert result["place_raw"] == "Paris"
        assert result["source"] == ["registry"]
    
    def test_event_without_content(self):
        """Test parsing event without content."""
        event_line = "#birt"
        event_type_mapping = {"#birt": "birth"}
        result = parse_event_line(event_line, event_type_mapping)
        assert result["type"] == "birth"
        assert result["raw"] == "#birt"
    
    def test_event_unknown_tag(self):
        """Test parsing event with unknown tag."""
        event_line = "#unknown_tag content"
        event_type_mapping = {}
        result = parse_event_line(event_line, event_type_mapping)
        assert result["type"] == "unknown_tag"
        assert result["raw"] == "#unknown_tag content"


class TestParseNoteLine:
    """Test parse_note_line function."""
    
    def test_basic(self):
        """Test parsing basic note line."""
        result = parse_note_line("note This is a note")
        assert result == "This is a note"
    
    def test_no_note_prefix(self):
        """Test parsing line without note prefix."""
        result = parse_note_line("This is not a note")
        assert result == "This is not a note"
