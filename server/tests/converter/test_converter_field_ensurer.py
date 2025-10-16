"""
Tests for converter field ensurer.
"""

import pytest
from datetime import date
from src.converter.field_ensurer import ensure_person_fields, ensure_event_fields


class TestEnsurePersonFields:
    """Test ensure_person_fields function."""

    def test_ensure_person_fields_basic(self):
        """Test ensuring basic person fields."""
        person_data = {"first_name": "John", "last_name": "Doe", "gender": "male"}
        result = ensure_person_fields(person_data)
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["sex"] == "M"
        assert "id" in result

    def test_ensure_person_fields_female(self):
        """Test ensuring person fields for female."""
        person_data = {"first_name": "Jane", "last_name": "Doe", "gender": "female"}
        result = ensure_person_fields(person_data)
        assert result["sex"] == "F"

    def test_ensure_person_fields_unknown_gender(self):
        """Test ensuring person fields for unknown gender."""
        person_data = {"first_name": "Alex", "last_name": "Smith", "gender": "unknown"}
        result = ensure_person_fields(person_data)
        assert result["sex"] == "U"

    def test_ensure_person_fields_from_name(self):
        """Test ensuring person fields from name field."""
        person_data = {"name": "John Doe"}
        result = ensure_person_fields(person_data)
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"

    def test_ensure_person_fields_with_id(self):
        """Test ensuring person fields with existing ID."""
        person_data = {"id": "existing-id", "first_name": "John", "last_name": "Doe"}
        result = ensure_person_fields(person_data)
        assert result["id"] == "existing-id"


class TestEnsureEventFields:
    """Test ensure_event_fields function."""

    def test_ensure_event_fields_with_date_dict(self):
        """Test ensuring event fields with date dict."""
        event_data = {
            "type": "birth",
            "date": {"value": "2023-01-01"},
            "place_raw": "Paris",
        }
        result = ensure_event_fields(event_data)
        assert result["date"] == date(2023, 1, 1)
        assert result["place"] == "Paris"
        assert "id" in result

    def test_ensure_event_fields_with_date_string(self):
        """Test ensuring event fields with date string."""
        event_data = {"type": "death", "date": "2023-12-31", "place": "London"}
        result = ensure_event_fields(event_data)
        assert result["date"] == date(2023, 12, 31)
        assert result["place"] == "London"

    def test_ensure_event_fields_with_notes_list(self):
        """Test ensuring event fields with notes list."""
        event_data = {"type": "marriage", "notes": ["Note 1", "Note 2"]}
        result = ensure_event_fields(event_data)
        assert result["description"] == "Note 1 | Note 2"

    def test_ensure_event_fields_with_notes_string(self):
        """Test ensuring event fields with notes string."""
        event_data = {"type": "baptism", "notes": "Single note"}
        result = ensure_event_fields(event_data)
        assert result["description"] == "Single note"

    def test_ensure_event_fields_with_existing_id(self):
        """Test ensuring event fields with existing ID."""
        event_data = {"id": "existing-event-id", "type": "birth"}
        result = ensure_event_fields(event_data)
        assert result["id"] == "existing-event-id"
