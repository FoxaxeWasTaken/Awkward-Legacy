import pytest
from serializer.sources_serializer import serialize_sources


def test_empty_sources():
    result = serialize_sources({})
    assert result == ""


def test_family_source_only():
    data = {"family_source": ["archives"]}
    result = serialize_sources(data).splitlines()
    assert result == ["src archives", "csrc archives"]


def test_multiple_family_sources():
    data = {"family_source": ["A", "B"]}
    result = serialize_sources(data).splitlines()
    assert result == [
        "src A",
        "src B",
        "csrc A",
        "csrc B",
    ]


def test_children_source_only():
    data = {"children_source": ["church_records"]}
    result = serialize_sources(data).splitlines()
    assert result == ["csources church_records"]


def test_multiple_children_sources():
    data = {"children_source": ["A", "B", "C"]}
    result = serialize_sources(data).splitlines()
    assert result == ["csources A", "csources B", "csources C"]


def test_family_and_children_sources():
    data = {
        "family_source": ["archives"],
        "children_source": ["registers"],
    }
    result = serialize_sources(data).splitlines()
    assert result == [
        "src archives",
        "csrc archives",
        "csources registers",
    ]


def test_invalid_keys_are_ignored():
    data = {"unknown_key": ["X"], "family_source": ["Y"]}
    result = serialize_sources(data)
    assert "unknown_key" not in result
    assert "Y" in result


def test_non_list_values_are_handled_gracefully():
    data = {"family_source": "string_instead_of_list"}
    result = serialize_sources(data)
    assert isinstance(result, str)
    assert result == "" or "src" not in result


def test_whitespace_and_order_preserved():
    data = {
        "family_source": ["A"],
        "children_source": ["B"],
    }
    result = serialize_sources(data)
    assert result.strip().endswith("csources B")
    assert "  " not in result
