from src.converter.entity_extractor import (
    _ensure_spouse_and_get_id,
    _find_person_by_name,
    _extract_person_events,
    _extract_person_notes,
)


def test_ensure_spouse_and_get_id_creates_and_dedups():
    persons = []
    # First insertion creates
    hid = _ensure_spouse_and_get_id(
        {"first_name": "John", "last_name": "Doe"}, "male", persons
    )
    assert hid is not None
    assert len(persons) == 1
    # Duplicate by name returns same id
    hid2 = _ensure_spouse_and_get_id(
        {"first_name": "John", "last_name": "Doe"}, "male", persons
    )
    assert hid2 == hid
    assert len(persons) == 1


def test_find_person_by_name_matches_full_and_raw():
    persons = [
        {"id": "1", "first_name": "Jane", "last_name": "Roe"},
        {"id": "2", "name": "Alpha Beta", "first_name": "", "last_name": ""},
    ]
    assert _find_person_by_name(persons, "Jane Roe") == "1"
    assert _find_person_by_name(persons, "Alpha Beta") == "2"


def test_extract_person_events_and_notes_linking():
    parsed = {
        "people": [
            {
                "person": "Foo Bar",
                "events": [{"type": "birt", "date": "2000-01-01"}],
            }
        ],
        "notes": [{"person": "Foo Bar", "text": "Note1"}],
    }
    persons = [{"id": "p1", "first_name": "Foo", "last_name": "Bar"}]
    events = []

    _extract_person_events(parsed, persons, events)
    assert len(events) == 1
    assert events[0]["person_id"] == "p1"

    _extract_person_notes(parsed, persons)
    assert persons[0]["notes"].startswith("Note1")
