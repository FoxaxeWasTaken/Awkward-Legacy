"""
Tests for parsing person parser.
"""

import pytest
from src.parsing.person_parser import parse_person_segment


class TestParsePersonSegment:
    """Test parse_person_segment function."""
    
    def test_basic_person(self):
        """Test parsing basic person."""
        result = parse_person_segment("Jean Baptiste Laurent")
        assert result["name"] == "Jean Baptiste Laurent"
        assert result["first_name"] == "Jean"
        assert result["last_name"] == "Baptiste Laurent"
        assert result["display_name"] == "Jean Baptiste Laurent"
    
    def test_basic_person_with_date(self):
        """Test parsing person with date."""
        result = parse_person_segment("Jean Baptiste Laurent 1814")
        assert result["name"] == "Jean Baptiste Laurent"
        assert len(result["dates"]) == 1
        assert result["dates"][0]["value"] == "1814"
    
    def test_person_with_gender_tag(self):
        """Test parsing person with gender tag."""
        result = parse_person_segment("Jean Baptiste #gender M")
        assert result["name"] == "Jean Baptiste"
        assert result["sex"] == "male"
        assert "gender" in result["tags"]
    
    def test_person_with_occupation_tag(self):
        """Test parsing person with occupation tag."""
        result = parse_person_segment("Jean Baptiste #occu Engineer")
        assert result["name"] == "Jean Baptiste"
        assert "occu" in result["tags"]
        assert result["tags"]["occu"] == ["Engineer"]
    
    def test_person_with_braces(self):
        """Test parsing person with braces."""
        result = parse_person_segment("Jean-Baptiste {Jean-Baptiste_Laurent}")
        assert result["name"] == "Jean-Baptiste {Jean-Baptiste_Laurent}"
    
    def test_empty_segment(self):
        """Test parsing empty segment."""
        result = parse_person_segment("")
        assert result["raw"] == ""
        assert result["name"] == ""
    
    def test_person_with_multiple_tags(self):
        """Test parsing person with multiple tags."""
        result = parse_person_segment("Jean Baptiste #occu Engineer #src Registry")
        assert "occu" in result["tags"]
        assert "src" in result["tags"]
        assert result["tags"]["occu"] == ["Engineer"]
        assert result["tags"]["src"] == ["Registry"]
