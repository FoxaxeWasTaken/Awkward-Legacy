from src.converter.entity_extractor import (
    _create_missing_persons_from_events,
    _extract_person_events,
    _extract_person_notes,
)


def test_create_missing_persons_from_events_creates_person_and_links_events():
    parsed = {
        "people": [
            {
                "person": "New Person",
                "events": [
                    {"type": "birt", "date": "1999-09-09"},
                    {"type": "occu", "description": "Developer"},
                ],
            }
        ]
    }
    persons = []
    events = []
    _create_missing_persons_from_events(parsed, persons, events)

    assert any(
        p
        for p in persons
        if p.get("first_name") == "New" and p.get("last_name") == "Person"
    )
    assert any(e for e in events if e.get("person_id") and e.get("type") == "birt")


def test_extract_person_events_and_notes_skip_missing():
    parsed = {
        "people": [{"person": "", "events": []}],
        "notes": [{"person": "", "text": ""}],
    }
    persons = []
    events = []
    _extract_person_events(parsed, persons, events)
    _extract_person_notes(parsed, persons)
    assert events == []
