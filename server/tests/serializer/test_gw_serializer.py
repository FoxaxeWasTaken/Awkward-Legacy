import pytest
from serializer.gw_serializer import GWSerializer


@pytest.fixture
def minimal_data():
    return {
        "families": [],
        "persons": [],
        "notes": [],
        "notes_db": {},
        "sources": {},
        "extended_pages": {},
    }


@pytest.fixture
def populated_data():
    return {
        "families": [
            {
                "raw_header": "fam Test",
                "sources": {"family_source": ["source1"]},
                "events": [{"raw": "#marr 1900"}],
                "children": [
                    {
                        "gender": "male",
                        "person": {"name": "Child One", "raw": "raw_child"},
                    }
                ],
            }
        ],
        "sources": {"family_source": ["source1"], "children_source": ["source2"]},
        "persons": [
            {"name": "Person One", "events": [{"raw": "#birt 1900"}]},
            {"name": "Person Two", "events": []},
        ],
        "notes_db": {"text": "Database notes"},
        "notes": [{"person": "Person One", "text": "A note"}],
        "extended_pages": {"Page1": {"TITLE": "Title1", "TYPE": "type1"}},
    }


def test_serialize_empty(minimal_data):
    serializer = GWSerializer(minimal_data)
    result = serializer.serialize()
    assert isinstance(result, str)
    assert "notes-db" in result or result.strip() == ""


def test_serialize_populated(populated_data):
    serializer = GWSerializer(populated_data)
    result = serializer.serialize()
    assert isinstance(result, str)
    assert "fam Test" in result
    assert "src source1" in result or "csrc source1" in result
    assert "pevt Person One" in result
    assert "A note" in result
    assert "page-ext Page1" in result


def test_to_file(tmp_path, populated_data):
    serializer = GWSerializer(populated_data)
    file_path = tmp_path / "output.gw"
    serializer.to_file(str(file_path))
    assert file_path.exists()
    content = file_path.read_text(encoding="utf-8")
    assert "fam Test" in content


def test_missing_sections(minimal_data):
    del minimal_data["notes_db"]
    del minimal_data["notes"]
    del minimal_data["extended_pages"]
    serializer = GWSerializer(minimal_data)
    result = serializer.serialize()
    assert isinstance(result, str)


def test_people_without_events():
    data = {"families": [], "persons": [{"name": "No Events", "events": []}]}
    serializer = GWSerializer(data)
    result = serializer.serialize()
    assert "pevt No Events" in result and result.strip().endswith("end pevt")


def test_handles_missing_keys():
    data = {}
    serializer = GWSerializer(data)
    result = serializer.serialize()
    assert isinstance(result, str)


def test_database_notes_only():
    data = {"families": [], "persons": [], "notes_db": {"text": "Only database notes"}}
    serializer = GWSerializer(data)
    result = serializer.serialize()
    assert "Only database notes" in result


def test_order_of_sections(populated_data):
    serializer = GWSerializer(populated_data)
    result = serializer.serialize()
    sections = [
        "fam Test",
        "src source1",
        "pevt Person One",
        "notes",
        "page-ext Page1",
        "notes-db",
    ]
    indices = [result.find(s) for s in sections if s in result]
    assert indices == sorted(indices), "Sections are not in the correct order"
