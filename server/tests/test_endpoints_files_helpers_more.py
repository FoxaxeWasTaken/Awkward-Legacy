from src.endpoints.files import _build_children_data, _sex_to_letter


def test_build_children_data_produces_gender_and_person_raw():
    raw_data = {
        "persons": [
            {"id": "c1", "first_name": "Kid", "last_name": "One", "sex": "M"},
            {"id": "c2", "first_name": "Kid", "last_name": "Two", "sex": "F"},
        ],
        "children": [
            {"family_id": "fam1", "child_id": "c1"},
            {"family_id": "fam1", "child_id": "c2"},
        ],
    }

    children = _build_children_data(raw_data, "fam1")
    assert len(children) == 2
    male = next(c for c in children if c["person"]["raw"] == "Kid One")
    female = next(c for c in children if c["person"]["raw"] == "Kid Two")
    assert male["gender"] == "male"
    assert female["gender"] == "female"
    assert male["raw"].startswith("- h Kid One")
    assert female["raw"].startswith("- f Kid Two")


def test_sex_to_letter_default_is_h():
    assert _sex_to_letter(None) == "h"
    assert _sex_to_letter("X") == "h"
