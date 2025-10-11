"""
Tests for entity extractor module.
"""

import pytest
from datetime import date
from src.converter.entity_extractor import extract_entities


class TestExtractEntities:
    """Test the extract_entities function."""

    def test_extract_entities_empty_data(self):
        """Test extraction with empty data."""
        result = extract_entities({})
        expected = {
            "persons": [],
            "families": [],
            "events": [],
            "children": []
        }
        assert result == expected

    def test_extract_entities_no_families(self):
        """Test extraction with no families."""
        parsed = {"families": []}
        result = extract_entities(parsed)
        expected = {
            "persons": [],
            "families": [],
            "events": [],
            "children": []
        }
        assert result == expected

    def test_extract_entities_single_family_with_husband_only(self):
        """Test extraction with single family having only husband."""
        parsed = {
            "families": [{
                "id": "fam1",
                "husband": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": "male"
                }
            }]
        }
        result = extract_entities(parsed)
        
        assert len(result["persons"]) == 1
        assert len(result["families"]) == 1
        assert len(result["events"]) == 0
        assert len(result["children"]) == 0
        
        person = result["persons"][0]
        assert person["first_name"] == "John"
        assert person["last_name"] == "Doe"
        assert person["sex"] == "M"
        assert "id" in person
        
        family = result["families"][0]
        assert family["id"] == "fam1"
        assert family["husband_id"] == person["id"]
        assert family["wife_id"] is None

    def test_extract_entities_single_family_with_wife_only(self):
        """Test extraction with single family having only wife."""
        parsed = {
            "families": [{
                "id": "fam1",
                "wife": {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "gender": "female"
                }
            }]
        }
        result = extract_entities(parsed)
        
        assert len(result["persons"]) == 1
        assert len(result["families"]) == 1
        assert len(result["events"]) == 0
        assert len(result["children"]) == 0
        
        person = result["persons"][0]
        assert person["first_name"] == "Jane"
        assert person["last_name"] == "Smith"
        assert person["sex"] == "F"
        
        family = result["families"][0]
        assert family["id"] == "fam1"
        assert family["husband_id"] is None
        assert family["wife_id"] == person["id"]

    def test_extract_entities_single_family_with_both_spouses(self):
        """Test extraction with single family having both spouses."""
        parsed = {
            "families": [{
                "id": "fam1",
                "husband": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "sex": "M"
                },
                "wife": {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "sex": "F"
                }
            }]
        }
        result = extract_entities(parsed)
        
        assert len(result["persons"]) == 2
        assert len(result["families"]) == 1
        assert len(result["events"]) == 0
        assert len(result["children"]) == 0
        
        # Check that both persons are extracted
        person_names = {p["first_name"] for p in result["persons"]}
        assert "John" in person_names
        assert "Jane" in person_names
        
        family = result["families"][0]
        assert family["id"] == "fam1"
        assert family["husband_id"] is not None
        assert family["wife_id"] is not None
        assert family["husband_id"] != family["wife_id"]

    def test_extract_entities_family_with_children(self):
        """Test extraction with family having children."""
        parsed = {
            "families": [{
                "id": "fam1",
                "husband": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "sex": "M"
                },
                "wife": {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "sex": "F"
                },
                "children": [
                    {
                        "person": {
                            "first_name": "Child1",
                            "last_name": "Doe",
                            "sex": "M"
                        },
                        "gender": "male"
                    },
                    {
                        "person": {
                            "first_name": "Child2",
                            "last_name": "Doe",
                            "sex": "F"
                        }
                    }
                ]
            }]
        }
        result = extract_entities(parsed)
        
        assert len(result["persons"]) == 4  # 2 spouses + 2 children
        assert len(result["families"]) == 1
        assert len(result["events"]) == 0
        assert len(result["children"]) == 2
        
        # Check children relationships
        child_relationships = result["children"]
        assert all(rel["family_id"] == "fam1" for rel in child_relationships)
        assert len(set(rel["child_id"] for rel in child_relationships)) == 2

    def test_extract_entities_family_with_events(self):
        """Test extraction with family having events."""
        parsed = {
            "families": [{
                "id": "fam1",
                "husband": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "sex": "M"
                },
                "events": [
                    {
                        "type": "marriage",
                        "date": "2020-01-01",
                        "place": "Paris"
                    },
                    {
                        "type": "divorce",
                        "date": "2022-01-01"
                    }
                ]
            }]
        }
        result = extract_entities(parsed)
        
        assert len(result["persons"]) == 1
        assert len(result["families"]) == 1
        assert len(result["events"]) == 2
        assert len(result["children"]) == 0
        
        # Check events
        events = result["events"]
        assert all(evt["family_id"] == "fam1" for evt in events)
        event_types = {evt["type"] for evt in events}
        assert "marriage" in event_types
        assert "divorce" in event_types

    def test_extract_entities_family_without_id(self):
        """Test extraction with family without ID (should generate one)."""
        parsed = {
            "families": [{
                "husband": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "sex": "M"
                }
            }]
        }
        result = extract_entities(parsed)
        
        assert len(result["families"]) == 1
        family = result["families"][0]
        assert "id" in family
        assert family["id"] is not None

    def test_extract_entities_multiple_families(self):
        """Test extraction with multiple families."""
        parsed = {
            "families": [
                {
                    "id": "fam1",
                    "husband": {
                        "first_name": "John",
                        "last_name": "Doe",
                        "sex": "M"
                    }
                },
                {
                    "id": "fam2",
                    "wife": {
                        "first_name": "Jane",
                        "last_name": "Smith",
                        "sex": "F"
                    }
                }
            ]
        }
        result = extract_entities(parsed)
        
        assert len(result["persons"]) == 2
        assert len(result["families"]) == 2
        assert len(result["events"]) == 0
        assert len(result["children"]) == 0
        
        family_ids = {fam["id"] for fam in result["families"]}
        assert "fam1" in family_ids
        assert "fam2" in family_ids

    def test_extract_entities_child_with_gender_in_child(self):
        """Test extraction with child having gender in child object."""
        parsed = {
            "families": [{
                "id": "fam1",
                "husband": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "sex": "M"
                },
                "children": [
                    {
                        "person": {
                            "first_name": "Child1",
                            "last_name": "Doe",
                            "gender": "male"
                        }
                    }
                ]
            }]
        }
        result = extract_entities(parsed)
        
        assert len(result["persons"]) == 2  # husband + child
        assert len(result["children"]) == 1
        
        # Find the child person
        child_persons = [p for p in result["persons"] if p["first_name"] == "Child1"]
        assert len(child_persons) == 1
        child = child_persons[0]
        assert child["gender"] == "male"

    def test_extract_entities_child_with_gender_override(self):
        """Test extraction with child having gender override in child object."""
        parsed = {
            "families": [{
                "id": "fam1",
                "husband": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "sex": "M"
                },
                "children": [
                    {
                        "person": {
                            "first_name": "Child1",
                            "last_name": "Doe",
                            "gender": "male"
                        },
                        "gender": "female"  # This should override
                    }
                ]
            }]
        }
        result = extract_entities(parsed)
        
        # Find the child person
        child_persons = [p for p in result["persons"] if p["first_name"] == "Child1"]
        assert len(child_persons) == 1
        child = child_persons[0]
        assert child["gender"] == "female"  # Should be overridden

    def test_extract_entities_family_with_marriage_data(self):
        """Test extraction with family having marriage data."""
        parsed = {
            "families": [{
                "id": "fam1",
                "husband": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "sex": "M"
                },
                "wife": {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "sex": "F"
                },
                "events": [
                    {
                        "type": "marriage",
                        "date": "2020-01-01",
                        "place": "Paris"
                    }
                ]
            }]
        }
        result = extract_entities(parsed)
        
        family = result["families"][0]
        # The family should have marriage data extracted
        assert "marriage_date" in family
        assert "marriage_place" in family
        assert "notes" in family

    def test_extract_entities_complex_family(self):
        """Test extraction with complex family structure."""
        parsed = {
            "families": [{
                "id": "fam1",
                "husband": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": "male",
                    "birth_date": "1980-01-01"
                },
                "wife": {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "gender": "female",
                    "birth_date": "1985-01-01"
                },
                "children": [
                    {
                        "person": {
                            "first_name": "Child1",
                            "last_name": "Doe",
                            "sex": "M"
                        },
                        "gender": "male"
                    }
                ],
                "events": [
                    {
                        "type": "marriage",
                        "date": "2010-01-01",
                        "place": "Paris"
                    }
                ],
                "notes": "Family notes"
            }]
        }
        result = extract_entities(parsed)
        
        assert len(result["persons"]) == 3  # 2 spouses + 1 child
        assert len(result["families"]) == 1
        assert len(result["events"]) == 1
        assert len(result["children"]) == 1
        
        # Check family data
        family = result["families"][0]
        assert family["id"] == "fam1"
        assert family["husband_id"] is not None
        assert family["wife_id"] is not None
        assert family["notes"] == "Family notes"
        
        # Check event
        event = result["events"][0]
        assert event["family_id"] == "fam1"
        assert event["type"] == "marriage"
        
        # Check child relationship
        child_rel = result["children"][0]
        assert child_rel["family_id"] == "fam1"
        assert child_rel["child_id"] is not None
