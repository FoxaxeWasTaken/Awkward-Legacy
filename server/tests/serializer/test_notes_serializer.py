import pytest
from serializer.notes_serializer import serialize_notes_db, serialize_notes


def test_serialize_notes_db_basic():
    notes_db = {"text": "This is a test notes DB."}
    result = serialize_notes_db(notes_db)
    lines = result.splitlines()

    assert lines[0] == "notes-db"
    assert "  text=This is a test notes DB." in lines


def test_serialize_notes_db_multiple_keys():
    notes_db = {"text": "Test", "author": "John Doe"}
    result = serialize_notes_db(notes_db)
    lines = result.splitlines()

    assert lines[0] == "notes-db"
    assert "  text=Test" in lines
    assert "  author=John Doe" in lines


def test_serialize_notes_db_empty():
    result = serialize_notes_db({})
    assert result == "notes-db"


def test_serialize_notes_basic():
    notes = [
        {"person": "John_Doe", "text": "First line\nSecond line"}
    ]
    result = serialize_notes(notes)
    lines = result.splitlines()

    assert lines[0] == "notes John_Doe"
    assert lines[1] == "beg"
    assert "First line" in lines
    assert "Second line" in lines
    assert lines[-1] == "end notes"


def test_serialize_notes_multiple_notes():
    notes = [
        {"person": "John_Doe", "text": "Line 1"},
        {"person": "Jane_Doe", "text": "Line A\nLine B"}
    ]
    result = serialize_notes(notes)
    blocks = result.split("notes ")

    assert len(blocks) == 3  # split creates extra empty block before first note
    assert "John_Doe" in blocks[1]
    assert "Jane_Doe" in blocks[2]
    assert "Line A" in result
    assert "Line B" in result


def test_serialize_notes_empty_text():
    notes = [{"person": "John_Doe", "text": ""}]
    result = serialize_notes(notes)
    lines = result.splitlines()

    assert "notes John_Doe" in lines
    assert "beg" in lines
    assert "end notes" in lines


def test_serialize_notes_missing_text():
    notes = [{"person": "John_Doe"}]
    result = serialize_notes(notes)
    lines = result.splitlines()

    assert "notes John_Doe" in lines
    assert "beg" in lines
    assert "end notes" in lines


def test_serialize_notes_empty_list():
    result = serialize_notes([])
    assert result == ""


def test_serialize_notes_db_non_string_values():
    notes_db = {"count": 5, "valid": True}
    result = serialize_notes_db(notes_db)
    assert "  count=5" in result
    assert "  valid=True" in result
