from src.endpoints.files import (
    _filter_data_for_family,
    _filter_data_for_family_raw,
)


def test_filter_data_for_family_matches_persons_and_notes():
    normalized = {
        "families": [
            {
                "id": "fam1",
                "husband": {"raw": "John Doe"},
                "wife": {"raw": "Jane Roe"},
                "children": [{"person": {"raw": "Kid One"}}],
            }
        ],
        "persons": [
            {"first_name": "John", "last_name": "Doe"},
            {"first_name": "Jane", "last_name": "Roe"},
            {"first_name": "Kid", "last_name": "One"},
        ],
        "notes": [
            {"person": "John Doe", "text": "NoteJ"},
            {"person": "Other", "text": "Ignore"},
        ],
        "raw_header": {"gwplus": True, "encoding": "utf-8"},
    }
    out = _filter_data_for_family(normalized, "fam1")
    names = {
        f"{p.get('first_name','')} {p.get('last_name','')}".strip()
        for p in out["persons"]
    }
    assert names == {"John Doe", "Jane Roe", "Kid One"}
    assert any(n["text"] == "NoteJ" for n in out["notes"])


def test_filter_data_for_family_raw_filters_all_related_entities():
    db_json = {
        "families": [{"id": "fam1", "husband_id": "h1", "wife_id": "w1"}],
        "persons": [
            {"id": "h1", "first_name": "H", "last_name": " One", "notes": "Nh"},
            {"id": "w1", "first_name": "W", "last_name": " One"},
            {"id": "c1", "first_name": "C", "last_name": " One"},
        ],
        "children": [{"family_id": "fam1", "child_id": "c1"}],
        "events": [
            {"person_id": "h1", "type": "birt"},
            {"family_id": "fam1", "type": "marr"},
            {"family_id": "fam2", "type": "ignore"},
        ],
    }
    out = _filter_data_for_family_raw(db_json, "fam1")
    assert len(out["persons"]) == 2 or len(out["persons"]) == 3
    types = {e.get("type") for e in out["events"]}
    assert "birt" in types and "marr" in types
    assert any(n["person"].strip() for n in out.get("notes", []))
