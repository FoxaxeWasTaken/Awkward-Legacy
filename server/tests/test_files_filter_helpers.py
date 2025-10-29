from src.endpoints.files import (
    _filter_events_for_family,
    _collect_related_person_ids,
)


def test_collect_related_person_ids_gathers_spouses_and_children():
    db_json = {
        "children": [
            {"family_id": "fam1", "child_id": "c1"},
            {"family_id": "fam2", "child_id": "c2"},
        ]
    }
    fam = {"husband_id": "h1", "wife_id": "w1"}
    ids = _collect_related_person_ids(db_json, fam, "fam1")
    assert ids == {"h1", "w1", "c1"}


def test_filter_events_for_family_selects_person_and_family_events():
    events = [
        {"person_id": "p1", "family_id": None, "type": "birt"},
        {"person_id": "p2", "family_id": "fam1", "type": "marr"},
        {"person_id": None, "family_id": "fam2", "type": "marr"},
    ]
    filtered = _filter_events_for_family(events, {"p1"}, "fam1")
    types = {e["type"] for e in filtered}
    assert types == {"birt", "marr"}
