import json
from pathlib import Path
import pytest
from gw_parser import GWParser


@pytest.fixture
def gw_file_path():
    return Path(__file__).parent / "galichet.gw"


@pytest.fixture
def parser(gw_file_path):
    return GWParser(gw_file_path)


def test_parser_runs(parser):
    result = parser.parse()
    assert isinstance(result, dict)
    assert "families" in result
    assert "people" in result
    assert "notes" in result
    assert "database_notes" in result
    assert "raw_header" in result


def test_header_parsing(parser):
    result = parser.parse()
    assert result["raw_header"]["encoding"].lower() == "utf-8"
    assert result["raw_header"]["gwplus"] is True


def test_family_parsing(parser):
    result = parser.parse()
    assert len(result["families"]) > 0

    for fam in result["families"]:
        assert "husband" in fam
        assert "events" in fam
        assert "children" in fam


def test_events_parsing(parser):
    result = parser.parse()
    found_event = False

    for fam in result["families"]:
        if fam["events"]:
            found_event = True
            for evt in fam["events"]:
                assert "type" in evt
                assert any(k in evt for k in ("date", "notes", "raw"))
    assert found_event, "No events found — check test data."


def test_children_parsing(parser):
    result = parser.parse()

    for fam in result["families"]:
        for child in fam["children"]:
            assert "gender" in child or "raw_line" in child
            assert "person" in child or "raw_line" in child


def test_notes_parsing(parser):
    result = parser.parse()
    assert len(result["notes"]) > 0
    for note in result["notes"]:
        assert "person" in note
        assert "text" in note
        assert isinstance(note["text"], str)


def test_person_events_parsing(parser):
    result = parser.parse()
    assert len(result["people"]) > 0
    for pevt in result["people"]:
        assert "person" in pevt
        assert isinstance(pevt["events"], list)
        for evt in pevt["events"]:
            assert "type" in evt


def test_notes_db_parsing(parser):
    result = parser.parse()
    assert result["database_notes"] is not None
    assert "text" in result["database_notes"]
    assert "Ceci est une base de test." in result["database_notes"]["text"]


def test_extended_pages_parsing(parser):
    result = parser.parse()
    assert len(result["extended_pages"]) > 0
    for page in result["extended_pages"]:
        assert "name" in page
        assert "title" in page or page["title"] is None


def test_to_json(tmp_path, parser):
    parser.parse()
    out_file = tmp_path / "out.json"
    parser.to_json(out_file)

    assert out_file.exists()
    loaded = json.loads(out_file.read_text(encoding="utf-8"))
    assert "families" in loaded
    assert "people" in loaded
    assert "notes" in loaded
