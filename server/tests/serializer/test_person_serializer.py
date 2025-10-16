import pytest
from serializer.person_serializer import serialize_person, serialize_person_events


# ==========================================================
# Tests for serialize_person
# ==========================================================


def test_serialize_person_basic():
    person = {"name": "John Doe"}
    result = serialize_person(person)
    assert result == "John Doe"


def test_serialize_person_with_tags_and_dates(monkeypatch):
    monkeypatch.setattr(
        "serializer.person_serializer.serialize_tags", lambda x: ["#tag1 a", "#tag2 b"]
    )
    monkeypatch.setattr(
        "serializer.person_serializer.serialize_dates",
        lambda x: ["2025-01-01", "2025-01-02"],
    )

    person = {
        "name": "Alice",
        "tags": {"tag1": ["a"], "tag2": ["b"]},
        "dates": ["2025-01-01", "2025-01-02"],
    }
    result = serialize_person(person)
    assert "Alice" in result
    assert "#tag1 a" in result
    assert "#tag2 b" in result
    assert "2025-01-01" in result
    assert "2025-01-02" in result


def test_serialize_person_raw_mode():
    person = {"raw": "raw_content_should_be_returned", "name": "ignored"}
    result = serialize_person(person, raw=True)
    assert result == "raw_content_should_be_returned"


def test_serialize_person_handles_missing_fields(monkeypatch):
    monkeypatch.setattr("serializer.person_serializer.serialize_tags", lambda x: [])
    monkeypatch.setattr("serializer.person_serializer.serialize_dates", lambda x: [])
    result = serialize_person({})
    assert isinstance(result, str)
    assert result == ""


def test_serialize_person_with_empty_tags_and_dates(monkeypatch):
    monkeypatch.setattr("serializer.person_serializer.serialize_tags", lambda x: [])
    monkeypatch.setattr("serializer.person_serializer.serialize_dates", lambda x: [])
    person = {"name": "Eve", "tags": {}, "dates": []}
    result = serialize_person(person)
    assert result.strip() == "Eve"


# ==========================================================
# Tests for serialize_person_events
# ==========================================================


def test_serialize_person_events_basic(monkeypatch):
    monkeypatch.setattr(
        "serializer.person_serializer.serialize_event", lambda e: f"event {e['type']}"
    )
    person = {"name": "Bob", "events": [{"type": "birth"}, {"type": "death"}]}
    result = serialize_person_events(person)
    lines = result.splitlines()

    assert lines[0] == "pevt Bob"
    assert "event birth" in result
    assert "event death" in result
    assert lines[-1] == "end pevt"


def test_serialize_person_events_empty_events():
    person = {"name": "Bob", "events": []}
    result = serialize_person_events(person)
    assert result == ""


def test_serialize_person_events_no_events_key():
    person = {"name": "Jane"}
    result = serialize_person_events(person)
    assert result == ""


def test_serialize_person_events_with_invalid_event(monkeypatch):
    monkeypatch.setattr(
        "serializer.person_serializer.serialize_event", lambda e: "event_invalid"
    )
    person = {"name": "Carl", "events": [None, {}]}
    result = serialize_person_events(person)
    assert result.count("event_invalid") == 2


def test_serialize_person_events_handles_strange_names(monkeypatch):
    monkeypatch.setattr(
        "serializer.person_serializer.serialize_event", lambda e: "event test"
    )
    person = {"name": "Jöhn Dœ #42", "events": [{"type": "birth"}]}
    result = serialize_person_events(person)
    assert "pevt Jöhn Dœ #42" in result
    assert "end pevt" in result
