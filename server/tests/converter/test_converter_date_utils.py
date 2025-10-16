"""
Tests for converter date utilities.
"""

import pytest
from datetime import date
from src.converter.date_utils import parse_date_dict_to_date, parse_date_string_to_date


class TestParseDateDictToDate:
    """Test parse_date_dict_to_date function."""

    def test_parse_date_dict_with_value(self):
        """Test parsing date dict with value."""
        date_dict = {"value": "2023-01-01"}
        result = parse_date_dict_to_date(date_dict)
        assert result == date(2023, 1, 1)

    def test_parse_date_dict_with_raw(self):
        """Test parsing date dict with raw value."""
        date_dict = {"raw": "2023-01-01"}
        result = parse_date_dict_to_date(date_dict)
        assert result == date(2023, 1, 1)

    def test_parse_date_dict_empty(self):
        """Test parsing empty date dict."""
        date_dict = {}
        result = parse_date_dict_to_date(date_dict)
        assert result is None

    def test_parse_date_dict_none(self):
        """Test parsing None date dict."""
        result = parse_date_dict_to_date(None)
        assert result is None


class TestParseDateStringToDate:
    """Test parse_date_string_to_date function."""

    def test_parse_date_string_iso_format(self):
        """Test parsing ISO date string."""
        result = parse_date_string_to_date("2023-01-01")
        assert result == date(2023, 1, 1)

    def test_parse_date_string_md_format(self):
        """Test parsing MM/DD/YYYY format."""
        result = parse_date_string_to_date("01/01/2023")
        assert result == date(2023, 1, 1)

    def test_parse_date_string_dm_format(self):
        """Test parsing DD/MM/YYYY format."""
        result = parse_date_string_to_date("01/01/2023")
        assert result == date(2023, 1, 1)

    def test_parse_date_string_year_only(self):
        """Test parsing year only."""
        result = parse_date_string_to_date("2023")
        assert result == date(2023, 1, 1)

    def test_parse_date_string_invalid(self):
        """Test parsing invalid date string."""
        result = parse_date_string_to_date("invalid")
        assert result is None

    def test_parse_date_string_empty(self):
        """Test parsing empty date string."""
        result = parse_date_string_to_date("")
        assert result is None

    def test_parse_date_string_none(self):
        """Test parsing None date string."""
        result = parse_date_string_to_date(None)
        assert result is None
