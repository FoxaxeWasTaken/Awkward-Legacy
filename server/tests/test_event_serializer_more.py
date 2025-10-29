from datetime import date
from src.serializer.event_serializer import serialize_event


def test_serialize_event_with_raw_takes_precedence():
    ev = {"raw": "#birt 2000-01-01 #pl Paris"}
    out = serialize_event(ev)
    assert out.strip() == "#birt 2000-01-01 #pl Paris"


def test_serialize_event_with_fields_builds_line():
    ev = {
        "type": "birt",
        "date": "1990-05-05",
        "place": "Berlin",
        "description": "Note",
    }
    out = serialize_event(ev)
    assert out.startswith("birt 1990-05-05")
    assert "#pl Berlin" in out
    assert "#desc Note" in out


def test_serialize_event_converts_date_object():
    ev = {"type": "birt", "date": date(2010, 2, 3), "place": "NY"}
    out = serialize_event(ev)
    assert "2010-02-03" in out


def test_serialize_event_with_notes_appends_lines():
    ev = {"raw": "#birt 2000-01-01", "notes": ["line1", "line2"]}
    out = serialize_event(ev)
    lines = out.splitlines()
    assert lines[0] == "#birt 2000-01-01"
    assert "note line1" in lines[1]
    assert "note line2" in lines[2]
