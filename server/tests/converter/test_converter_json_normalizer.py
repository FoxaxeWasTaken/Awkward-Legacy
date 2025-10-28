"""
Tests for JSON normalizer module.
"""

import pytest
from datetime import date, datetime
from uuid import uuid4, UUID
from src.converter.json_normalizer import (
    convert_to_json_serializable,
    normalize_db_json,
    _build_person_lookup,
    _build_children_by_family,
    _build_families_list,
    _ensure_family_exists,
    _add_child_if_valid,
    _find_person_by_id,
    _create_child_data,
    _create_family_data,
)


class TestConvertToJsonSerializable:
    """Test the convert_to_json_serializable function."""

    def test_convert_simple_dict(self):
        """Test conversion of simple dictionary."""
        obj = {"key": "value", "number": 42}
        result = convert_to_json_serializable(obj)
        assert result == {"key": "value", "number": 42}

    def test_convert_dict_with_date(self):
        """Test conversion of dictionary with date."""
        test_date = date(2023, 1, 1)
        obj = {"date": test_date, "name": "test"}
        result = convert_to_json_serializable(obj)
        assert result["date"] == "2023-01-01"
        assert result["name"] == "test"

    def test_convert_dict_with_datetime(self):
        """Test conversion of dictionary with datetime."""
        test_datetime = datetime(2023, 1, 1, 12, 30, 45)
        obj = {"datetime": test_datetime, "name": "test"}
        result = convert_to_json_serializable(obj)
        assert result["datetime"] == "2023-01-01T12:30:45"
        assert result["name"] == "test"

    def test_convert_dict_with_uuid(self):
        """Test conversion of dictionary with UUID."""
        test_uuid = uuid4()
        obj = {"id": test_uuid, "name": "test"}
        result = convert_to_json_serializable(obj)
        assert result["id"] == str(test_uuid)
        assert result["name"] == "test"

    def test_convert_nested_dict(self):
        """Test conversion of nested dictionary."""
        test_date = date(2023, 1, 1)
        test_uuid = uuid4()
        obj = {
            "person": {"id": test_uuid, "birth_date": test_date, "name": "John"},
            "count": 1,
        }
        result = convert_to_json_serializable(obj)
        assert result["person"]["id"] == str(test_uuid)
        assert result["person"]["birth_date"] == "2023-01-01"
        assert result["person"]["name"] == "John"
        assert result["count"] == 1

    def test_convert_list(self):
        """Test conversion of list."""
        test_date = date(2023, 1, 1)
        test_uuid = uuid4()
        obj = [test_date, test_uuid, "string", 42]
        result = convert_to_json_serializable(obj)
        assert result == ["2023-01-01", str(test_uuid), "string", 42]

    def test_convert_nested_list(self):
        """Test conversion of nested list."""
        test_date = date(2023, 1, 1)
        obj = [{"date": test_date}, [test_date, "string"]]
        result = convert_to_json_serializable(obj)
        assert result == [{"date": "2023-01-01"}, ["2023-01-01", "string"]]

    def test_convert_primitive_types(self):
        """Test conversion of primitive types."""
        assert convert_to_json_serializable("string") == "string"
        assert convert_to_json_serializable(42) == 42
        assert convert_to_json_serializable(3.14) == 3.14
        assert convert_to_json_serializable(True) == True
        assert convert_to_json_serializable(None) == None


class TestBuildPersonLookup:
    """Test the _build_person_lookup function."""

    def test_build_person_lookup_empty(self):
        """Test building person lookup with empty data."""
        db_json = {"persons": []}
        result = _build_person_lookup(db_json)
        assert result == {}

    def test_build_person_lookup_single_person(self):
        """Test building person lookup with single person."""
        db_json = {
            "persons": [{"id": "person1", "first_name": "John", "last_name": "Doe"}]
        }
        result = _build_person_lookup(db_json)
        expected = {"person1": "John Doe"}
        assert result == expected

    def test_build_person_lookup_multiple_persons(self):
        """Test building person lookup with multiple persons."""
        db_json = {
            "persons": [
                {"id": "person1", "first_name": "John", "last_name": "Doe"},
                {"id": "person2", "first_name": "Jane", "last_name": "Smith"},
            ]
        }
        result = _build_person_lookup(db_json)
        expected = {"person1": "John Doe", "person2": "Jane Smith"}
        assert result == expected

    def test_build_person_lookup_missing_names(self):
        """Test building person lookup with missing names."""
        db_json = {
            "persons": [
                {
                    "id": "person1",
                    "first_name": "John",
                    # missing last_name
                },
                {
                    "id": "person2",
                    "last_name": "Smith",
                    # missing first_name
                },
                {
                    "id": "person3"
                    # missing both names
                },
            ]
        }
        result = _build_person_lookup(db_json)
        expected = {"person1": "John", "person2": "Smith", "person3": ""}
        assert result == expected


class TestBuildChildrenByFamily:
    """Test the _build_children_by_family function."""

    def test_build_children_by_family_empty(self):
        """Test building children by family with empty data."""
        db_json = {"children": []}
        person_lookup = {}
        result = _build_children_by_family(db_json, person_lookup)
        assert result == {}

    def test_build_children_by_family_single_child(self):
        """Test building children by family with single child."""
        db_json = {
            "children": [{"family_id": "family1", "child_id": "child1"}],
            "persons": [{"id": "child1", "sex": "M"}],
        }
        person_lookup = {"child1": "Child Name"}
        result = _build_children_by_family(db_json, person_lookup)

        assert "family1" in result
        assert len(result["family1"]) == 1
        child = result["family1"][0]
        assert child["gender"] == "male"
        assert child["person"]["raw"] == "Child Name"

    def test_build_children_by_family_multiple_children(self):
        """Test building children by family with multiple children."""
        db_json = {
            "children": [
                {"family_id": "family1", "child_id": "child1"},
                {"family_id": "family1", "child_id": "child2"},
            ],
            "persons": [{"id": "child1", "sex": "M"}, {"id": "child2", "sex": "F"}],
        }
        person_lookup = {"child1": "Child1 Name", "child2": "Child2 Name"}
        result = _build_children_by_family(db_json, person_lookup)

        assert "family1" in result
        assert len(result["family1"]) == 2

        genders = {child["gender"] for child in result["family1"]}
        assert "male" in genders
        assert "female" in genders

    def test_build_children_by_family_missing_person(self):
        """Test building children by family with missing person."""
        db_json = {
            "children": [{"family_id": "family1", "child_id": "child1"}],
            "persons": [],  # No persons
        }
        person_lookup = {"child1": "Child Name"}
        result = _build_children_by_family(db_json, person_lookup)

        assert result == {"family1": []}  # No children added due to missing person

    def test_build_children_by_family_missing_in_lookup(self):
        """Test building children by family with missing person in lookup."""
        db_json = {
            "children": [{"family_id": "family1", "child_id": "child1"}],
            "persons": [{"id": "child1", "sex": "M"}],
        }
        person_lookup = {}  # Empty lookup
        result = _build_children_by_family(db_json, person_lookup)

        assert result == {"family1": []}  # No children added due to missing in lookup


class TestBuildFamiliesList:
    """Test the _build_families_list function."""

    def test_build_families_list_empty(self):
        """Test building families list with empty data."""
        db_json = {"families": []}
        person_lookup = {}
        children_by_family = {}
        result = _build_families_list(db_json, person_lookup, children_by_family)
        assert result == []

    def test_build_families_list_single_family(self):
        """Test building families list with single family."""
        db_json = {
            "families": [
                {"id": "family1", "husband_id": "husband1", "wife_id": "wife1"}
            ]
        }
        person_lookup = {"husband1": "Husband Name", "wife1": "Wife Name"}
        children_by_family = {}
        result = _build_families_list(db_json, person_lookup, children_by_family)

        assert len(result) == 1
        family = result[0]
        assert family["id"] == "family1"
        assert family["husband"]["raw"] == "Husband Name"
        assert family["wife"]["raw"] == "Wife Name"

    def test_build_families_list_missing_spouses(self):
        """Test building families list with missing spouses."""
        db_json = {
            "families": [{"id": "family1", "husband_id": "husband1", "wife_id": None}]
        }
        person_lookup = {"husband1": "Husband Name"}
        children_by_family = {}
        result = _build_families_list(db_json, person_lookup, children_by_family)

        assert len(result) == 1
        family = result[0]
        assert family["id"] == "family1"
        assert family["husband"]["raw"] == "Husband Name"
        assert family["wife"] is None


class TestHelperFunctions:
    """Test helper functions."""

    def test_ensure_family_exists(self):
        """Test _ensure_family_exists function."""
        children_by_family = {}
        _ensure_family_exists(children_by_family, "family1")
        assert "family1" in children_by_family
        assert children_by_family["family1"] == []

    def test_ensure_family_exists_already_exists(self):
        """Test _ensure_family_exists with existing family."""
        children_by_family = {"family1": ["existing"]}
        _ensure_family_exists(children_by_family, "family1")
        assert children_by_family["family1"] == ["existing"]

    def test_find_person_by_id(self):
        """Test _find_person_by_id function."""
        db_json = {
            "persons": [
                {"id": "person1", "name": "John"},
                {"id": "person2", "name": "Jane"},
            ]
        }
        result = _find_person_by_id(db_json, "person1")
        assert result == {"id": "person1", "name": "John"}

    def test_find_person_by_id_not_found(self):
        """Test _find_person_by_id with non-existent person."""
        db_json = {"persons": []}
        result = _find_person_by_id(db_json, "person1")
        assert result is None

    def test_create_child_data(self):
        """Test _create_child_data function."""
        child_person = {"sex": "F"}
        child_name = "Child Name"
        result = _create_child_data(child_person, child_name)

        assert result["gender"] == "female"
        assert result["person"]["raw"] == "Child Name"

    def test_create_child_data_unknown_sex(self):
        """Test _create_child_data with unknown sex."""
        child_person = {"sex": "U"}
        child_name = "Child Name"
        result = _create_child_data(child_person, child_name)

        assert result["gender"] == "male"  # Default to male
        assert result["person"]["raw"] == "Child Name"

    def test_create_family_data(self):
        """Test _create_family_data function."""
        family = {
            "id": "family1",
            "husband_id": "husband1",
            "wife_id": "wife1",
            "marriage_date": "2020-01-01",
            "marriage_place": "Paris",
        }
        person_lookup = {"husband1": "Husband Name", "wife1": "Wife Name"}
        children_by_family = {}
        result = _create_family_data(family, person_lookup, children_by_family)

        assert result["id"] == "family1"
        assert result["marriage_date"] == "2020-01-01"
        assert result["marriage_place"] == "Paris"
        assert result["husband"]["raw"] == "Husband Name"
        assert result["wife"]["raw"] == "Wife Name"

    def test_create_family_data_missing_spouses(self):
        """Test _create_family_data with missing spouses."""
        family = {"id": "family1"}
        person_lookup = {}
        children_by_family = {}
        result = _create_family_data(family, person_lookup, children_by_family)

        assert result["id"] == "family1"
        assert result["husband"] is None
        assert result["wife"] is None


class TestNormalizeDbJson:
    """Test the normalize_db_json function."""

    def test_normalize_db_json_empty(self):
        """Test normalizing empty database JSON."""
        db_json = {"persons": [], "families": [], "children": [], "events": []}
        result = normalize_db_json(db_json)

        expected = {
            "persons": [],
            "families": [],
            "events": [],
            "notes": [],
            "extended_pages": {},
            "database_notes": None,
            "raw_header": {"gwplus": True, "encoding": "utf-8"},
        }
        assert result == expected

    def test_normalize_db_json_complete(self):
        """Test normalizing complete database JSON."""
        db_json = {
            "persons": [
                {"id": "person1", "first_name": "John", "last_name": "Doe", "sex": "M"}
            ],
            "families": [{"id": "family1", "husband_id": "person1", "wife_id": None}],
            "children": [],
            "events": [],
        }
        result = normalize_db_json(db_json)

        assert "persons" in result
        assert "families" in result
        assert "events" in result
        assert len(result["persons"]) == 1
        assert len(result["families"]) == 1
        assert len(result["events"]) == 0
