import pytest
from typing import List, Dict
from serializer.utils import serialize_tags, serialize_dates, gender_prefix


def test_serialize_tags_basic():
    tags = {"birt": ["1813"], "p": ["Paris"]}
    result = serialize_tags(tags)
    assert isinstance(result, list)
    assert "#birt 1813" in result
    assert "#p Paris" in result


def test_serialize_tags_multiple_values():
    tags = {"birt": ["1813", "1814"], "p": ["Paris", "Lyon"]}
    result = serialize_tags(tags)
    assert len(result) == 4
    assert "#birt 1813" in result
    assert "#birt 1814" in result
    assert "#p Paris" in result
    assert "#p Lyon" in result


def test_serialize_tags_empty_dict():
    tags = {}
    result = serialize_tags(tags)
    assert result == []


def test_serialize_tags_empty_values():
    tags = {"birt": []}
    result = serialize_tags(tags)
    assert result == []


def test_serialize_tags_non_string_values():
    tags = {"year": [1813, 1814]}
    result = serialize_tags(tags)
    assert "#year 1813" in result
    assert "#year 1814" in result


def test_serialize_dates_basic():
    dates = ["1813", "1814"]
    result = serialize_dates(dates)
    assert isinstance(result, list)
    assert result == dates


def test_serialize_dates_empty_list():
    dates: List[str] = []
    result = serialize_dates(dates)
    assert result == []


def test_serialize_dates_non_string_values():
    dates = ["1813", 1814, None]
    result = serialize_dates(dates)
    assert result == dates


@pytest.mark.parametrize("gender,input_value,expected", [
    ("male", "male", "h"),
    ("male", "m", "h"),
    ("male", "man", "h"),
    ("male", "homme", "h"),
    ("male", "h", "h"),
    ("female", "female", "f"),
    ("female", "f", "f"),
    ("female", "woman", "f"),
    ("female", "femme", "f"),
    ("male", "unknown", "h"),
    ("male", "", "h"),
    ("male", None, "h"),
])
def test_gender_prefix(gender, input_value, expected):
    result = gender_prefix(input_value if input_value is not None else "")
    assert result == expected


def test_gender_prefix_case_insensitive():
    assert gender_prefix("Male") == "h"
    assert gender_prefix("FEMALE") == "f"
    assert gender_prefix("HoMmE") == "h"
    assert gender_prefix("FeMmE") == "f"


def test_gender_prefix_none_or_empty():
    assert gender_prefix("") == "h"
    assert gender_prefix(None) == "h"
