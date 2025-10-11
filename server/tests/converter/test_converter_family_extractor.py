"""
Tests for converter family extractor.
"""

import pytest
from datetime import date
from src.converter.family_extractor import (
    extract_marriage_date_from_family_data,
    extract_marriage_place_from_family_data,
    extract_family_notes_from_family_data
)


class TestExtractMarriageDateFromFamilyData:
    """Test extract_marriage_date_from_family_data function."""
    
    def test_extract_marriage_date_from_events(self):
        """Test extracting marriage date from events."""
        family_data = {
            "events": [
                {"type": "marriage", "date": {"value": "2023-06-15"}}
            ]
        }
        result = extract_marriage_date_from_family_data(family_data)
        assert result == date(2023, 6, 15)
    
    def test_extract_marriage_date_no_data(self):
        """Test extracting marriage date with no data."""
        family_data = {}
        result = extract_marriage_date_from_family_data(family_data)
        assert result is None


class TestExtractMarriagePlaceFromFamilyData:
    """Test extract_marriage_place_from_family_data function."""
    
    def test_extract_marriage_place_from_events(self):
        """Test extracting marriage place from events."""
        family_data = {
            "events": [
                {"type": "marriage", "place_raw": "Paris"}
            ]
        }
        result = extract_marriage_place_from_family_data(family_data)
        assert result == "Paris"
    
    def test_extract_marriage_place_no_data(self):
        """Test extracting marriage place with no data."""
        family_data = {}
        result = extract_marriage_place_from_family_data(family_data)
        assert result is None


class TestExtractFamilyNotesFromFamilyData:
    """Test extract_family_notes_from_family_data function."""
    
    def test_extract_family_notes_from_events_list(self):
        """Test extracting family notes from events with list notes."""
        family_data = {
            "events": [
                {"notes": ["Note 1", "Note 2"]}
            ]
        }
        result = extract_family_notes_from_family_data(family_data)
        assert result == "Note 1 | Note 2"
    
    def test_extract_family_notes_from_events_string(self):
        """Test extracting family notes from events with string notes."""
        family_data = {
            "events": [
                {"notes": "Single note"}
            ]
        }
        result = extract_family_notes_from_family_data(family_data)
        assert result == "Single note"
    
    def test_extract_family_notes_no_data(self):
        """Test extracting family notes with no data."""
        family_data = {}
        result = extract_family_notes_from_family_data(family_data)
        assert result is None
