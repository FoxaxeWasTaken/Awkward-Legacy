import pytest
from fastapi import HTTPException
from src.endpoints.files import (
    _filter_data_for_family_fixed,
    _build_family_header,
    _find_target_family,
)


def _mk_person(pid, fn, ln, sex=None, notes=None):
    p = {"id": pid, "first_name": fn, "last_name": ln}
    if sex is not None:
        p["sex"] = sex
    if notes:
        p["notes"] = notes
    return p


def test_filter_data_for_family_fixed_builds_complete_structure():
    raw_data = {
        "persons": [
            _mk_person("h1", "John", "Doe", sex="M", notes="HNote"),
            _mk_person("w1", "Jane", "Roe", sex="F"),
            _mk_person("c1", "Kid", "One", sex="M"),
        ],
        "families": [
            {
                "id": "fam1",
                "husband_id": "h1",
                "wife_id": "w1",
                "marriage_date": "2000-01-02",
                "marriage_place": "Boston",
                "notes": "FNote",
            }
        ],
        "children": [{"family_id": "fam1", "child_id": "c1"}],
        "events": [
            {"person_id": "h1", "type": "birt", "date": "1970-01-01"},
            {"family_id": "fam1", "type": "marr", "date": "2000-01-02"},
        ],
    }

    normalized_stub = {"raw_header": {"gwplus": True, "encoding": "utf-8"}}
    out = _filter_data_for_family_fixed(normalized_stub, raw_data, "fam1")

    # persons include events
    assert any(p.get("events") for p in out["persons"])
    # fixed family exists with header, events and children
    fam = out["families"][0]
    assert fam["raw_header"].startswith("John Doe + Jane Roe")
    assert fam["events"]
    assert fam["children"] and fam["children"][0]["person"]["raw"] == "Kid One"
    # filtered notes contain person note
    assert (
        any(n["person"].startswith("John Doe") for n in out["notes"])
        or out["notes"] == []
    )


def test_build_family_header_variants():
    tf = {"marriage_date": "1999-09-09", "marriage_place": "NY"}
    both = _build_family_header("A B", "C D", tf)
    assert "A B + C D" in both and "#mp NY" in both
    only_h = _build_family_header("A B", "", tf)
    assert only_h.startswith("A B")
    only_w = _build_family_header("", "C D", tf)
    assert only_w.startswith("Unknown + C D") or only_w.startswith("C D")
    none = _build_family_header("", "", {})
    assert "Unknown" in none


def test_find_target_family_raises_on_missing():
    with pytest.raises(HTTPException):
        _find_target_family({"families": []}, "famX")
