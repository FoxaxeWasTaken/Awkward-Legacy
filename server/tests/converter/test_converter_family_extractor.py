"""
Tests for family extractor functions.
"""

import pytest
from datetime import date
from src.converter.family_extractor import (
    extract_marriage_date_from_family_data,
    extract_marriage_place_from_family_data,
    extract_family_notes_from_family_data,
    _extract_direct_notes,
    _extract_event_notes
)


class TestExtractMarriageDateFromFamilyData:
    """Test the extract_marriage_date_from_family_data function."""

    def test_extract_marriage_date_from_events(self):
        """Test extracting marriage date from events."""
        family_data = {
            "events": [
                {
                    "type": "marriage",
                    "date": "2020-01-01"
                }
            ]
        }
        result = extract_marriage_date_from_family_data(family_data)
        assert result == date(2020, 1, 1)

    def test_extract_marriage_date_from_dict(self):
        """Test extracting marriage date from dict format."""
        family_data = {
            "events": [
                {
                    "type": "marriage",
                    "date": {"value": "2020-01-01"}
                }
            ]
        }
        result = extract_marriage_date_from_family_data(family_data)
        assert result == date(2020, 1, 1)

    def test_no_marriage_date(self):
        """Test when no marriage date is found."""
        family_data = {
            "events": [
                {
                    "type": "birth",
                    "date": "2020-01-01"
                }
            ]
        }
        result = extract_marriage_date_from_family_data(family_data)
        assert result is None

    def test_no_events(self):
        """Test when no events are present."""
        family_data = {}
        result = extract_marriage_date_from_family_data(family_data)
        assert result is None


class TestExtractMarriagePlaceFromFamilyData:
    """Test the extract_marriage_place_from_family_data function."""

    def test_extract_marriage_place_from_events(self):
        """Test extracting marriage place from events."""
        family_data = {
            "events": [
                {
                    "type": "marriage",
                    "place_raw": "Paris"
                }
            ]
        }
        result = extract_marriage_place_from_family_data(family_data)
        assert result == "Paris"

    def test_no_marriage_place(self):
        """Test when no marriage place is found."""
        family_data = {
            "events": [
                {
                    "type": "birth",
                    "place_raw": "Paris"
                }
            ]
        }
        result = extract_marriage_place_from_family_data(family_data)
        assert result is None

    def test_no_events(self):
        """Test when no events are present."""
        family_data = {}
        result = extract_marriage_place_from_family_data(family_data)
        assert result is None


class TestExtractFamilyNotesFromFamilyData:
    """Test the extract_family_notes_from_family_data function."""

    def test_extract_direct_notes(self):
        """Test extracting direct notes from family data."""
        family_data = {
            "notes": "Family notes"
        }
        result = extract_family_notes_from_family_data(family_data)
        assert result == "Family notes"

    def test_extract_notes_from_events(self):
        """Test extracting notes from events."""
        family_data = {
            "events": [
                {
                    "notes": "Event notes"
                }
            ]
        }
        result = extract_family_notes_from_family_data(family_data)
        assert result == "Event notes"

    def test_extract_notes_from_events_list(self):
        """Test extracting notes from events with list format."""
        family_data = {
            "events": [
                {
                    "notes": ["Note 1", "Note 2"]
                }
            ]
        }
        result = extract_family_notes_from_family_data(family_data)
        assert result == "Note 1 | Note 2"

    def test_extract_notes_from_multiple_events(self):
        """Test extracting notes from multiple events."""
        family_data = {
            "events": [
                {
                    "notes": "Event 1 notes"
                },
                {
                    "notes": "Event 2 notes"
                }
            ]
        }
        result = extract_family_notes_from_family_data(family_data)
        assert result == "Event 1 notes | Event 2 notes"

    def test_no_notes(self):
        """Test when no notes are found."""
        family_data = {}
        result = extract_family_notes_from_family_data(family_data)
        assert result is None

    def test_empty_notes(self):
        """Test when notes are empty."""
        family_data = {
            "notes": "",
            "events": [
                {
                    "notes": ""
                }
            ]
        }
        result = extract_family_notes_from_family_data(family_data)
        assert result is None


class TestExtractDirectNotes:
    """Test the _extract_direct_notes helper function."""

    def test_extract_direct_notes_present(self):
        """Test extracting direct notes when present."""
        family_data = {"notes": "Direct notes"}
        result = _extract_direct_notes(family_data)
        assert result == "Direct notes"

    def test_extract_direct_notes_missing(self):
        """Test extracting direct notes when missing."""
        family_data = {}
        result = _extract_direct_notes(family_data)
        assert result is None

    def test_extract_direct_notes_empty(self):
        """Test extracting direct notes when empty."""
        family_data = {"notes": ""}
        result = _extract_direct_notes(family_data)
        assert result is None


class TestExtractEventNotes:
    """Test the _extract_event_notes helper function."""

    def test_extract_event_notes_single(self):
        """Test extracting notes from single event."""
        family_data = {
            "events": [
                {
                    "notes": "Event notes"
                }
            ]
        }
        result = _extract_event_notes(family_data)
        assert result == ["Event notes"]

    def test_extract_event_notes_list(self):
        """Test extracting notes from event with list format."""
        family_data = {
            "events": [
                {
                    "notes": ["Note 1", "Note 2"]
                }
            ]
        }
        result = _extract_event_notes(family_data)
        assert result == ["Note 1", "Note 2"]

    def test_extract_event_notes_multiple_events(self):
        """Test extracting notes from multiple events."""
        family_data = {
            "events": [
                {
                    "notes": "Event 1 notes"
                },
                {
                    "notes": "Event 2 notes"
                }
            ]
        }
        result = _extract_event_notes(family_data)
        assert result == ["Event 1 notes", "Event 2 notes"]

    def test_extract_event_notes_no_events(self):
        """Test extracting notes when no events are present."""
        family_data = {}
        result = _extract_event_notes(family_data)
        assert result == []

    def test_extract_event_notes_empty_notes(self):
        """Test extracting notes when notes are empty."""
        family_data = {
            "events": [
                {
                    "notes": ""
                }
            ]
        }
        result = _extract_event_notes(family_data)
        assert result == []

    def test_extract_event_notes_missing_notes(self):
        """Test extracting notes when notes field is missing."""
        family_data = {
            "events": [
                {
                    "type": "marriage"
                }
            ]
        }
        result = _extract_event_notes(family_data)
        assert result == []