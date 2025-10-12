"""
Tests for parsing family utils.
"""

import pytest
from src.parsing.family_utils import split_family_header, should_skip_empty_line


class TestSplitFamilyHeader:
    """Test split_family_header function."""

    def test_with_plus_spaces(self):
        """Test splitting with plus and spaces."""
        husband, wife = split_family_header("Jean Baptiste + Marie Dubois")
        assert husband == "Jean Baptiste"
        assert wife == "Marie Dubois"

    def test_with_plus_no_spaces(self):
        """Test splitting with plus and no spaces."""
        husband, wife = split_family_header("Jean+Marie")
        assert husband == "Jean"
        assert wife == "Marie"

    def test_no_separator(self):
        """Test splitting with no separator."""
        husband, wife = split_family_header("Jean Baptiste")
        assert husband == "Jean Baptiste"
        assert wife is None


class TestShouldSkipEmptyLine:
    """Test should_skip_empty_line function."""

    def test_empty_and_whitespace(self):
        """Test empty and whitespace lines."""
        assert should_skip_empty_line("") is True
        assert should_skip_empty_line("   ") is True
        assert should_skip_empty_line("\t") is True
        assert should_skip_empty_line("\n") is True

    def test_non_empty_line(self):
        """Test non-empty line."""
        assert should_skip_empty_line("Jean Baptiste") is False
        assert should_skip_empty_line("  Jean Baptiste  ") is False
