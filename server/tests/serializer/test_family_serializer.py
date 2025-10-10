import pytest
from serializer.family_serializer import serialize_family


@pytest.fixture
def basic_family():
    return {
        "raw_header": "Smith John + Doe Jane",
        "sources": {
            "family_source": ["source1"],
            "children_source": ["source2"]
        },
        "events": [
            {"raw": "#marr 1900"},
            {"raw": "#div 1920"}
        ],
        "children": [
            {"gender": "male", "person": {"raw": "Smith Junior"}},
            {"gender": "female", "person": {"raw": "Smith Anna"}}
        ]
    }


def test_family_basic(basic_family):
    result = serialize_family(basic_family)
    assert result.startswith("fam Smith John + Doe Jane")
    assert "src source1" in result
    assert "csrc source1" in result
    assert "csources source2" in result
    assert "fevt" in result
    assert "#marr 1900" in result
    assert "#div 1920" in result
    assert "end fevt" in result
    assert "- h Smith Junior" in result
    assert "- f Smith Anna" in result
    assert result.strip().endswith("end")


def test_family_no_sources():
    family = {
        "raw_header": "Smith John + Doe Jane",
        "events": [{"raw": "#marr 1900"}],
        "children": []
    }
    result = serialize_family(family)
    assert "src" not in result
    assert "fevt" in result
    assert "#marr 1900" in result
    assert "beg" in result
    assert "end" in result


def test_family_no_events():
    family = {
        "raw_header": "Smith John + Doe Jane",
        "sources": {"family_source": ["src1"]},
        "children": [{"gender": "male", "person": {"raw": "Smith Junior"}}]
    }
    result = serialize_family(family)
    assert "fevt" not in result
    assert "src src1" in result
    assert "- h Smith Junior" in result


def test_family_no_children():
    family = {
        "raw_header": "Smith John + Doe Jane",
        "sources": {"family_source": ["src1"]},
        "events": [{"raw": "#marr 1900"}]
    }
    result = serialize_family(family)
    assert "beg" in result
    assert "end" in result
    assert "- " not in result


def test_family_empty_fields():
    family = {"raw_header": ""}
    result = serialize_family(family)
    assert result.startswith("fam ")
    assert "beg" in result
    assert "end" in result


def test_family_missing_gender():
    family = {
        "raw_header": "Smith John + Doe Jane",
        "children": [{"person": {"raw": "Smith Unknown"}}]
    }
    result = serialize_family(family)
    assert "- h Smith Unknown" in result


def test_family_unknown_gender():
    family = {
        "raw_header": "Smith John + Doe Jane",
        "children": [{"gender": "other", "person": {"raw": "Smith X"}}]
    }
    result = serialize_family(family)
    assert "- other Smith X" in result


def test_family_multiple_children_same_gender():
    family = {
        "raw_header": "Smith John + Doe Jane",
        "children": [
            {"gender": "female", "person": {"raw": "Smith A"}},
            {"gender": "female", "person": {"raw": "Smith B"}}
        ]
    }
    result = serialize_family(family)
    assert "- f Smith A" in result
    assert "- f Smith B" in result
