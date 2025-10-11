"""
Tests for parsing date parser.
"""

import pytest
from src.parsing.date_parser import parse_date_token, normalize_underscores


class TestNormalizeUnderscores:
    """Test normalize_underscores function."""
    
    def test_basic_replacement(self):
        """Test basic underscore replacement."""
        result = normalize_underscores("Jean_Baptiste")
        assert result == "Jean Baptiste"
    
    def test_preserve_punctuation(self):
        """Test preserving punctuation."""
        result = normalize_underscores("Jean_Baptiste_Laurent")
        assert result == "Jean Baptiste Laurent"
    
    def test_strip_spaces(self):
        """Test stripping spaces."""
        result = normalize_underscores("  Jean_Baptiste  ")
        assert result == "Jean Baptiste"


class TestParseDateToken:
    """Test parse_date_token function."""
    
    def test_plain_date(self):
        """Test parsing plain date."""
        result = parse_date_token("1814")
        assert result == {"raw": "1814", "value": "1814"}
    
    def test_qualifiers(self):
        """Test parsing date with qualifiers."""
        result = parse_date_token("<1849")
        assert result == {"raw": "<1849", "qualifier": "before", "value": "1849"}
        
        result = parse_date_token("~1750")
        assert result == {"raw": "~1750", "qualifier": "approx", "value": "1750"}
        
        result = parse_date_token(">1900")
        assert result == {"raw": ">1900", "qualifier": "after", "value": "1900"}
    
    def test_literal_date(self):
        """Test parsing literal date."""
        result = parse_date_token("0(5_Mai_1990)")
        assert result == {"raw": "0(5_Mai_1990)", "literal": "5 Mai 1990"}
    
    def test_range(self):
        """Test parsing date range."""
        result = parse_date_token("1800..1850")
        assert result == {"raw": "1800..1850", "between": ["1800", "1850"]}
    
    def test_alternatives(self):
        """Test parsing date alternatives."""
        result = parse_date_token("10/5/1990|1991")
        assert result == {"raw": "10/5/1990|1991", "alternatives": ["10/5/1990", "1991"]}
    
    def test_empty_string(self):
        """Test parsing empty string."""
        result = parse_date_token("")
        assert result == {"raw": ""}
    
    def test_no_match(self):
        """Test parsing string with no date pattern."""
        result = parse_date_token("invalid")
        assert result == {"raw": "invalid"}
