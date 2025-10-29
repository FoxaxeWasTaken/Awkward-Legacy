"""Unit tests for json_normalizer person events logic.

Covers explicit event normalization and synthesized core events to raise
coverage on newly added code paths.
"""

from src.converter.json_normalizer import (
    _build_person_events,
    _serialize_event_raw,
)


def test_build_person_events_with_explicit_events():
    person = {
        "events": [
            {"type": "birt", "date": "1990-01-01", "place": "Paris"},
            {"type": "deat", "date": "2050-12-31", "place": "Lyon"},
        ]
    }

    events = _build_person_events(person)

    assert len(events) == 2
    assert events[0]["type"] == "birt"
    assert "raw" in events[0]
    assert events[1]["type"] == "deat"
    assert "raw" in events[1]


def test_build_person_events_synthesizes_birth_when_missing():
    person = {
        "events": [],
        "birth_date": "1980-05-05",
        "birth_place": "Boston,MA,USA",
    }

    events = _build_person_events(person)

    assert len(events) >= 1
    birth = next((e for e in events if e["type"] == "birt"), None)
    assert birth is not None
    assert birth["date"] == "1980-05-05"
    assert birth["place"] == "Boston,MA,USA"
    assert birth["raw"].startswith("#birt 1980-05-05")


def test_build_person_events_synthesizes_birth_and_death():
    person = {
        "events": None,
        "birth_date": "1970-01-02",
        "birth_place": "Nice",
        "death_date": "2020-03-04",
        "death_place": "Marseille",
    }

    events = _build_person_events(person)

    types = {e["type"] for e in events}
    assert {"birt", "deat"}.issubset(types)


def test_serialize_event_raw_formats_parts():
    raw = _serialize_event_raw("birt", "2000-02-02", "Berlin", "Note")
    assert raw.startswith("#birt 2000-02-02")
    assert "#p Berlin" in raw
    assert "note Note" in raw
