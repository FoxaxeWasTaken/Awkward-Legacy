import pytest
from serializer.event_serializer import serialize_event


def test_event_with_raw_only():
    event = {"raw": "#birt 1900"}
    result = serialize_event(event)
    assert result == "#birt 1900"


def test_event_with_notes_only():
    event = {"notes": ["Note one", "Note two"]}
    result = serialize_event(event)
    lines = result.splitlines()
    assert "note Note one" in lines
    assert "note Note two" in lines
    assert len(lines) == 2


def test_event_with_raw_and_notes():
    event = {"raw": "#birt 1900", "notes": ["Note one", "Note two"]}
    result = serialize_event(event)
    lines = result.splitlines()
    assert lines[0] == "#birt 1900"
    assert "note Note one" in lines
    assert "note Note two" in lines
    assert len(lines) == 3


def test_event_empty():
    event = {}
    result = serialize_event(event)
    assert result == ""


def test_event_with_empty_notes():
    event = {"raw": "#birt 1900", "notes": []}
    result = serialize_event(event)
    assert result == "#birt 1900"


def test_event_with_none_raw():
    event = {"raw": None, "notes": ["Note one"]}
    result = serialize_event(event)
    assert "note Note one" in result
    assert "#birt" not in result


def test_event_with_non_string_notes():
    event = {"raw": "#birt 1900", "notes": [123, None, "Note"]}
    result = serialize_event(event)
    assert "note 123" in result
    assert "note None" in result
    assert "note Note" in result


def test_event_with_multiline_note():
    event = {"raw": "#note", "notes": ["Line one\nLine two"]}
    result = serialize_event(event)
    assert "note Line one\nLine two" in result
