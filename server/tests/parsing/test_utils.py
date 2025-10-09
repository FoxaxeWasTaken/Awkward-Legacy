# tests/test_utils.py

import re
import pytest
from parsing import utils

class TestNormalizeUnderscores:
    def test_basic_replacement(self):
        assert utils.normalize_underscores("Jean_Pierre") == "Jean Pierre"
        assert utils.normalize_underscores("A_B_C") == "A B C"

    def test_preserve_punctuation(self):
        assert utils.normalize_underscores("Hello_World!") == "Hello World!"
        assert utils.normalize_underscores("Test_123.") == "Test 123."

    def test_strip_spaces(self):
        assert utils.normalize_underscores("  test_string  ") == "test string"
        assert utils.normalize_underscores("") == ""


class TestParseDateToken:
    def test_plain_date(self):
        result = utils.parse_date_token("1814")
        assert result == {"raw": "1814", "value": "1814"}

    def test_qualifiers(self):
        assert utils.parse_date_token("<1849") == {"raw": "<1849", "qualifier": "before", "value": "1849"}
        assert utils.parse_date_token("<<1849") == {"raw": "<<1849", "qualifier": "before", "value": "1849"}
        assert utils.parse_date_token(">1849") == {"raw": ">1849", "qualifier": "after", "value": "1849"}
        assert utils.parse_date_token("~1750") == {"raw": "~1750", "qualifier": "approx", "value": "1750"}
        assert utils.parse_date_token("?1750") == {"raw": "?1750", "qualifier": "uncertain", "value": "1750"}

    def test_literal_date(self):
        assert utils.parse_date_token("0(5_Mai_1990)") == {"raw": "0(5_Mai_1990)", "literal": "5 Mai 1990"}

    def test_range(self):
        assert utils.parse_date_token("1814..1820") == {"raw": "1814..1820", "between": ["1814", "1820"]}

    def test_alternatives(self):
        assert utils.parse_date_token("10/5/1990|1991") == {"raw": "10/5/1990|1991", "alternatives": ["10/5/1990", "1991"]}

    def test_empty_string(self):
        assert utils.parse_date_token("") == {"raw": ""}

    def test_no_match(self):
        assert utils.parse_date_token("random") == {"raw": "random", "value": "random"}


class TestSplitFamilyHeader:
    def test_with_plus_spaces(self):
        assert utils.split_family_header("John + Jane") == ("John", "Jane")
        assert utils.split_family_header("John +Jane") == ("John", "Jane")
        assert utils.split_family_header("John+ Jane") == ("John", "Jane")
        assert utils.split_family_header("John+Jane") == ("John", "Jane")

    def test_no_separator(self):
        assert utils.split_family_header("John") == ("John", None)


class TestTokenizePreservingBraces:
    def test_basic_tokenization(self):
        assert utils.tokenize_preserving_braces("Jean Baptiste") == ["Jean", "Baptiste"]

    def test_preserve_braces(self):
        assert utils.tokenize_preserving_braces("Jean {Jean_Baptiste}") == ["Jean", "{Jean_Baptiste}"]

    def test_multiple_braces(self):
        assert utils.tokenize_preserving_braces("{A_B} C {D_E}") == ["{A_B}", "C", "{D_E}"]

    def test_empty_string(self):
        assert utils.tokenize_preserving_braces("") == []

    def test_spaces_inside_braces(self):
        assert utils.tokenize_preserving_braces("{A B}") == ["{A B}"]


class TestExtractTagsAndDatesFromTokens:
    def test_tags_extraction(self):
        tokens = ["#occu", "Marchand_de_bois", "#src", "source_text", "other"]
        tags, dates, others = utils.extract_tags_and_dates_from_tokens(tokens)
        assert tags == {"#occu": ["Marchand_de_bois"], "#src": ["source_text other"]}

    def test_dates_and_others(self):
        tokens = ["John", "10/5/1990", "extra"]
        tags, dates, others = utils.extract_tags_and_dates_from_tokens(tokens)
        assert dates == ["10/5/1990"]
        assert others == ["John", "extra"]

    def test_empty_tokens(self):
        tags, dates, others = utils.extract_tags_and_dates_from_tokens([])
        assert tags == {}
        assert dates == []
        assert others == []


class TestExtractNameTokens:
    def test_stops_on_tag(self):
        name_tokens, rest = utils.extract_name_tokens(["John", "Doe", "#occu", "Marchand"])
        assert name_tokens == ["John", "Doe"]
        assert rest == ["#occu", "Marchand"]

    def test_stops_on_date_token(self):
        name_tokens, rest = utils.extract_name_tokens(["John", "1814", "Doe"])
        assert name_tokens == ["John"]
        assert rest == ["1814", "Doe"]

    def test_all_name_tokens(self):
        name_tokens, rest = utils.extract_name_tokens(["John", "Doe"])
        assert name_tokens == ["John", "Doe"]
        assert rest == []


class TestParsePersonSegment:
    def test_basic_person(self):
        seg = "Jean_Pierre #occu Marchand_de_bois 1814"
        result = utils.parse_person_segment(seg)
        assert result["name"] == "Jean_Pierre"
        assert "occu" in result["tags"]
        assert "dates" not in result or not result["dates"] or result["dates"][0]["raw"] == "1814"

    def test_basic_person_with_date(self):
        seg = "Jean_Pierre 1814"
        result = utils.parse_person_segment(seg)
        assert result["dates"][0]["raw"] == "1814"

    def test_empty_segment(self):
        result = utils.parse_person_segment("")
        assert result == {"raw": ""}


class TestExtractDateFromParts:
    def test_extract_date(self):
        date, others = utils.extract_date_from_parts(["1814", "Paris"])
        assert date == "1814"
        assert others == ["Paris"]

    def test_no_date(self):
        date, others = utils.extract_date_from_parts(["Paris", "France"])
        assert date is None
        assert others == ["Paris", "France"]


class TestExtractPlaceAndSource:
    def test_place_and_sources(self):
        place, sources = utils.extract_place_and_source("#p Paris #s registry #s archive")
        assert place == "Paris"
        assert sources == ["registry", "archive"]

    def test_no_place(self):
        place, sources = utils.extract_place_and_source("#s registry")
        assert place is None
        assert sources == ["registry"]

    def test_no_sources(self):
        place, sources = utils.extract_place_and_source("#p Paris")
        assert place == "Paris"
        assert sources == []

    def test_empty_string(self):
        place, sources = utils.extract_place_and_source("")
        assert place is None
        assert sources == []


class TestParseEventLine:
    def test_basic_event(self):
        line = "#birt 1813 #p Paris #s registry"
        result = utils.parse_event_line(line, {"#birt": "birth"})
        assert result["type"] == "birth"
        assert result["date"]["raw"] == "1813"
        assert result["place_raw"] == "Paris"
        assert "registry" in result["source"]

    def test_event_without_content(self):
        result = utils.parse_event_line("#birt", {"#birt": "birth"})
        assert result["type"] == "birth"
        assert result["raw"] == "#birt"

    def test_event_unknown_tag(self):
        result = utils.parse_event_line("#unknown 1814", {})
        assert result["type"] == "unknown"


class TestParseNoteLine:
    def test_basic(self):
        assert utils.parse_note_line("note This is a note") == "This is a note"

    def test_no_note_prefix(self):
        assert utils.parse_note_line("Just text") == "Just text"


class TestShouldSkipEmptyLine:
    def test_empty_and_whitespace(self):
        assert utils.should_skip_empty_line("")
        assert utils.should_skip_empty_line("   ")

    def test_non_empty_line(self):
        assert not utils.should_skip_empty_line("Text")
