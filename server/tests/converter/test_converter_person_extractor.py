"""
Tests for converter person extractor.
"""

import pytest
from datetime import date
from src.converter.person_extractor import (
    extract_birth_date_from_person_data,
    extract_death_date_from_person_data,
    extract_birth_place_from_person_data,
    extract_death_place_from_person_data,
    extract_occupation_from_person_data,
    extract_notes_from_person_data
)


class TestExtractBirthDateFromPersonData:
    """Test extract_birth_date_from_person_data function."""
    
    def test_extract_birth_date_from_events(self):
        """Test extracting birth date from events."""
        person_data = {
            "events": [
                {"type": "birth", "date": {"value": "2023-01-01"}}
            ]
        }
        result = extract_birth_date_from_person_data(person_data)
        assert result == date(2023, 1, 1)
    
    def test_extract_birth_date_from_dates(self):
        """Test extracting birth date from dates."""
        person_data = {
            "dates": [{"value": "2023-01-01"}]
        }
        result = extract_birth_date_from_person_data(person_data)
        assert result == date(2023, 1, 1)
    
    def test_extract_birth_date_from_tags(self):
        """Test extracting birth date from tags."""
        person_data = {
            "tags": {"birth": ["2023-01-01"]}
        }
        result = extract_birth_date_from_person_data(person_data)
        assert result == date(2023, 1, 1)
    
    def test_extract_birth_date_no_data(self):
        """Test extracting birth date with no data."""
        person_data = {}
        result = extract_birth_date_from_person_data(person_data)
        assert result is None


class TestExtractDeathDateFromPersonData:
    """Test extract_death_date_from_person_data function."""
    
    def test_extract_death_date_from_events(self):
        """Test extracting death date from events."""
        person_data = {
            "events": [
                {"type": "death", "date": {"value": "2023-12-31"}}
            ]
        }
        result = extract_death_date_from_person_data(person_data)
        assert result == date(2023, 12, 31)
    
    def test_extract_death_date_from_dates(self):
        """Test extracting death date from dates."""
        person_data = {
            "dates": [{"value": "2023-01-01"}, {"value": "2023-12-31"}]
        }
        result = extract_death_date_from_person_data(person_data)
        assert result == date(2023, 12, 31)
    
    def test_extract_death_date_no_data(self):
        """Test extracting death date with no data."""
        person_data = {}
        result = extract_death_date_from_person_data(person_data)
        assert result is None


class TestExtractBirthPlaceFromPersonData:
    """Test extract_birth_place_from_person_data function."""
    
    def test_extract_birth_place_from_events(self):
        """Test extracting birth place from events."""
        person_data = {
            "events": [
                {"type": "birth", "place_raw": "Paris"}
            ]
        }
        result = extract_birth_place_from_person_data(person_data)
        assert result == "Paris"
    
    def test_extract_birth_place_from_tags(self):
        """Test extracting birth place from tags."""
        person_data = {
            "tags": {"birth_place": ["Paris"]}
        }
        result = extract_birth_place_from_person_data(person_data)
        assert result == "Paris"
    
    def test_extract_birth_place_no_data(self):
        """Test extracting birth place with no data."""
        person_data = {}
        result = extract_birth_place_from_person_data(person_data)
        assert result is None


class TestExtractDeathPlaceFromPersonData:
    """Test extract_death_place_from_person_data function."""
    
    def test_extract_death_place_from_events(self):
        """Test extracting death place from events."""
        person_data = {
            "events": [
                {"type": "death", "place_raw": "London"}
            ]
        }
        result = extract_death_place_from_person_data(person_data)
        assert result == "London"
    
    def test_extract_death_place_no_data(self):
        """Test extracting death place with no data."""
        person_data = {}
        result = extract_death_place_from_person_data(person_data)
        assert result is None


class TestExtractOccupationFromPersonData:
    """Test extract_occupation_from_person_data function."""
    
    def test_extract_occupation_from_tags_occu(self):
        """Test extracting occupation from occu tag."""
        person_data = {
            "tags": {"occu": ["Engineer"]}
        }
        result = extract_occupation_from_person_data(person_data)
        assert result == "Engineer"
    
    def test_extract_occupation_from_tags_occupation(self):
        """Test extracting occupation from occupation tag."""
        person_data = {
            "tags": {"occupation": ["Doctor"]}
        }
        result = extract_occupation_from_person_data(person_data)
        assert result == "Doctor"
    
    def test_extract_occupation_from_events(self):
        """Test extracting occupation from events."""
        person_data = {
            "events": [
                {"type": "occupation", "description": "Teacher"}
            ]
        }
        result = extract_occupation_from_person_data(person_data)
        assert result == "Teacher"
    
    def test_extract_occupation_no_data(self):
        """Test extracting occupation with no data."""
        person_data = {}
        result = extract_occupation_from_person_data(person_data)
        assert result is None


class TestExtractNotesFromPersonData:
    """Test extract_notes_from_person_data function."""
    
    def test_extract_notes_from_notes(self):
        """Test extracting notes from notes field."""
        person_data = {
            "notes": ["Note 1", "Note 2"]
        }
        result = extract_notes_from_person_data(person_data)
        assert result == "Note 1 | Note 2"
    
    def test_extract_notes_from_tags_src(self):
        """Test extracting notes from src tag."""
        person_data = {
            "tags": {"src": ["Source 1", "Source 2"]}
        }
        result = extract_notes_from_person_data(person_data)
        assert result == "Source 1 | Source 2"
    
    def test_extract_notes_from_events(self):
        """Test extracting notes from events."""
        person_data = {
            "events": [
                {"notes": ["Event note 1", "Event note 2"]}
            ]
        }
        result = extract_notes_from_person_data(person_data)
        assert result == "Event note 1 | Event note 2"
    
    def test_extract_notes_no_data(self):
        """Test extracting notes with no data."""
        person_data = {}
        result = extract_notes_from_person_data(person_data)
        assert result is None
