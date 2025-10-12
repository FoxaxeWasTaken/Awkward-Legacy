from pathlib import Path
import pytest
import sys

from serializer.pevt_serializer import serialize_pevts


@pytest.fixture
def mock_serialize_event(monkeypatch):
    monkeypatch.setattr(
        "serializer.pevt_serializer.serialize_event",
        lambda e: f"EVENT:{e.get('type', 'unknown')}",
    )
    return None


def test_single_person_single_event(mock_serialize_event):
    pevts = {"john": [{"type": "birth"}]}
    result = serialize_pevts(pevts)
    expected = "pevt john\nEVENT:birth\nend pevt"
    assert result.strip() == expected


def test_single_person_multiple_events(mock_serialize_event):
    pevts = {"alice": [{"type": "birth"}, {"type": "death"}]}
    result = serialize_pevts(pevts)
    expected = "pevt alice\nEVENT:birth\nEVENT:death\nend pevt"
    assert result.strip() == expected


def test_multiple_persons(mock_serialize_event):
    pevts = {
        "john": [{"type": "birth"}],
        "mary": [{"type": "marriage"}, {"type": "death"}],
    }
    result = serialize_pevts(pevts)
    assert "pevt john" in result
    assert "pevt mary" in result
    assert result.count("end pevt") == 2


def test_empty_event_list(mock_serialize_event):
    pevts = {"empty": []}
    result = serialize_pevts(pevts)
    expected = "pevt empty\nend pevt"
    assert result.strip() == expected


def test_empty_input(mock_serialize_event):
    pevts = {}
    result = serialize_pevts(pevts)
    assert result.strip() == ""
