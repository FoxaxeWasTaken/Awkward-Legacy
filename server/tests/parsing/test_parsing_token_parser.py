"""
Tests for parsing token parser.
"""

import pytest
from src.parsing.token_parser import (
    tokenize_preserving_braces,
    extract_tags_and_dates_from_tokens,
    extract_name_tokens,
    split_name_into_parts,
)


class TestTokenizePreservingBraces:
    """Test tokenize_preserving_braces function."""

    def test_basic_tokenization(self):
        """Test basic tokenization."""
        result = tokenize_preserving_braces("Jean Baptiste Laurent")
        assert result == ["Jean", "Baptiste", "Laurent"]

    def test_preserve_braces(self):
        """Test preserving braces."""
        result = tokenize_preserving_braces(
            "Jean-Baptiste {Jean-Baptiste_Laurent} #occu"
        )
        assert result == ["Jean-Baptiste", "{Jean-Baptiste_Laurent}", "#occu"]

    def test_multiple_braces(self):
        """Test multiple braces."""
        result = tokenize_preserving_braces("{first} {second}")
        assert result == ["{first}", "{second}"]

    def test_empty_string(self):
        """Test empty string."""
        result = tokenize_preserving_braces("")
        assert result == []

    def test_spaces_inside_braces(self):
        """Test spaces inside braces."""
        result = tokenize_preserving_braces("{Jean Baptiste Laurent}")
        assert result == ["{Jean Baptiste Laurent}"]


class TestExtractTagsAndDatesFromTokens:
    """Test extract_tags_and_dates_from_tokens function."""

    def test_tags_extraction(self):
        """Test extracting tags."""
        tokens = ["#occu", "Engineer", "#src", "Registry"]
        tags, dates, others = extract_tags_and_dates_from_tokens(tokens)
        assert tags == {"#occu": ["Engineer"], "#src": ["Registry"]}
        assert dates == []
        assert others == []

    def test_dates_and_others(self):
        """Test extracting dates and other tokens."""
        tokens = ["Jean", "Baptiste", "1814", "Paris"]
        tags, dates, others = extract_tags_and_dates_from_tokens(tokens)
        assert tags == {}
        assert dates == ["1814"]
        assert others == ["Jean", "Baptiste", "Paris"]

    def test_empty_tokens(self):
        """Test empty tokens."""
        tags, dates, others = extract_tags_and_dates_from_tokens([])
        assert tags == {}
        assert dates == []
        assert others == []


class TestExtractNameTokens:
    """Test extract_name_tokens function."""

    def test_stops_on_tag(self):
        """Test stopping on tag."""
        tokens = ["Jean", "Baptiste", "#occu", "Engineer"]
        name_tokens, remaining = extract_name_tokens(tokens)
        assert name_tokens == ["Jean", "Baptiste"]
        assert remaining == ["#occu", "Engineer"]

    def test_stops_on_date_token(self):
        """Test stopping on date token."""
        tokens = ["Jean", "Baptiste", "1814", "Paris"]
        name_tokens, remaining = extract_name_tokens(tokens)
        assert name_tokens == ["Jean", "Baptiste"]
        assert remaining == ["1814", "Paris"]

    def test_all_name_tokens(self):
        """Test all tokens are name tokens."""
        tokens = ["Jean", "Baptiste", "Laurent"]
        name_tokens, remaining = extract_name_tokens(tokens)
        assert name_tokens == ["Jean", "Baptiste", "Laurent"]
        assert remaining == []


class TestSplitNameIntoParts:
    """Test split_name_into_parts function."""

    def test_full_name(self):
        """Test splitting full name."""
        first, last = split_name_into_parts("Jean Baptiste Laurent")
        assert first == "Jean"
        assert last == "Baptiste Laurent"

    def test_single_name(self):
        """Test single name."""
        first, last = split_name_into_parts("Jean")
        assert first == "Jean"
        assert last == ""

    def test_empty_name(self):
        """Test empty name."""
        first, last = split_name_into_parts("")
        assert first == ""
        assert last == ""

    def test_whitespace_name(self):
        """Test whitespace name."""
        first, last = split_name_into_parts("   ")
        assert first == ""
        assert last == ""
