#!/usr/bin/env python3
"""
Unit tests for gwdiff.py
"""

import unittest
import tempfile
import os
from gwdiff import (
    Person, Family, GWDiff, ComparisonConfig, 
    DiffMessage, find_person_by_key, GenealogyDataBuilder
)


class TestPerson(unittest.TestCase):
    def test_person_creation(self):
        person = Person("id1", "John", "Doe", "M", 0)
        self.assertEqual(person.id, "id1")
        self.assertEqual(person.first_name, "John")
        self.assertEqual(person.last_name, "Doe")
        self.assertEqual(person.sex, "M")
        self.assertEqual(person.occ, 0)
        self.assertEqual(person.families, [])

    def test_person_with_families(self):
        person = Person("id2", "Jane", "Smith", "F", 1, families=["F1", "F2"])
        self.assertEqual(person.families, ["F1", "F2"])


class TestFamily(unittest.TestCase):
    def test_family_creation(self):
        family = Family("F1", "H1", "W1", ["C1", "C2"])
        self.assertEqual(family.id, "F1")
        self.assertEqual(family.husband_id, "H1")
        self.assertEqual(family.wife_id, "W1")
        self.assertEqual(family.children, ["C1", "C2"])

    def test_family_default_children(self):
        family = Family("F2")
        self.assertEqual(family.children, [])


class TestGWDiff(unittest.TestCase):
    def setUp(self):
        self.config = ComparisonConfig(html=False, root="", d_mode=False, ad_mode=False)
        self.gwdiff = GWDiff(self.config)

    def test_person_string(self):
        person = Person("id1", "John", "Doe", "M", 0)
        self.assertEqual(self.gwdiff.person_string(person), "John Doe")

    def test_person_string_with_occ(self):
        person = Person("id1", "John", "Doe", "M", 1)
        self.assertEqual(self.gwdiff.person_string(person), "John.1 Doe")

    def test_compatible_field(self):
        self.assertTrue(self.gwdiff.compatible_field("", "test"))
        self.assertTrue(self.gwdiff.compatible_field("same", "same"))
        self.assertTrue(self.gwdiff.compatible_field("SAME", "same"))
        self.assertFalse(self.gwdiff.compatible_field("diff", "different"))

    def test_compatible_persons_light(self):
        p1 = Person("id1", "John", "Doe", "M", 0)
        p2 = Person("id2", "John", "Doe", "M", 0)
        p3 = Person("id3", "Jane", "Doe", "F", 0)
        
        messages = self.gwdiff.compatible_persons_light(p1, p2)
        self.assertEqual(messages, [])
        
        messages = self.gwdiff.compatible_persons_light(p1, p3)
        self.assertEqual(messages, [DiffMessage.FIRST_NAME])

    def test_compatible_persons_full(self):
        p1 = Person("id1", "John", "Doe", "M", 0, "1900", "1980")
        p2 = Person("id2", "John", "Doe", "M", 0, "1900", "1980")
        p3 = Person("id3", "John", "Doe", "F", 0, "1901", "1980")
        
        messages = self.gwdiff.compatible_persons(p1, p2)
        self.assertEqual(messages, [])
        
        messages = self.gwdiff.compatible_persons(p1, p3)
        self.assertIn(DiffMessage.SEX, messages)
        self.assertIn(DiffMessage.BIRTH_DATE, messages)

    def test_find_compatible_persons(self):
        target = Person("t1", "John", "Doe", "M", 0)
        candidates = [
            Person("c1", "John", "Doe", "M", 0),
            Person("c2", "Jane", "Doe", "F", 0),
            Person("c3", "John", "Smith", "M", 0)
        ]
        
        compatible = self.gwdiff.find_compatible_persons(target, candidates, light=True)
        self.assertEqual(len(compatible), 1)
        self.assertEqual(compatible[0].id, "c1")


class TestGenealogyDataBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = GenealogyDataBuilder()

    def test_build_from_empty_data(self):
        empty_data = {"families": []}
        self.builder.build_from_gw_parser(empty_data)
        self.assertEqual(len(self.builder.persons), 0)
        self.assertEqual(len(self.builder.families), 0)

    def test_build_simple_family(self):
        test_data = {
            "families": [{
                "husband": {"first_name": "John", "last_name": "Doe", "sex": "M"},
                "wife": {"first_name": "Jane", "last_name": "Smith", "sex": "F"},
                "children": [
                    {"person": {"first_name": "Bob", "last_name": "Doe"}, "gender": "male"}
                ]
            }]
        }
        
        self.builder.build_from_gw_parser(test_data)
        
        self.assertEqual(len(self.builder.families), 1)
        self.assertEqual(len(self.builder.persons), 3)
        
        family = list(self.builder.families.values())[0]
        self.assertIsNotNone(family.husband_id)
        self.assertIsNotNone(family.wife_id)
        self.assertEqual(len(family.children), 1)

    def test_person_linking(self):
        test_data = {
            "families": [{
                "husband": {"first_name": "John", "last_name": "Doe"},
                "wife": {"first_name": "Jane", "last_name": "Smith"},
                "children": [
                    {"person": {"first_name": "Child", "last_name": "Doe"}, "gender": "male"}
                ]
            }]
        }
        
        self.builder.build_from_gw_parser(test_data)
        
        child_id = list(self.builder.families.values())[0].children[0]
        child = self.builder.persons[child_id]
        
        family = list(self.builder.families.values())[0]
        self.assertEqual(child.father_id, family.husband_id)
        self.assertEqual(child.mother_id, family.wife_id)


class TestFindPersonByKey(unittest.TestCase):
    def setUp(self):
        self.builder = GenealogyDataBuilder()
        test_data = {
            "families": [{
                "husband": {"first_name": "John", "last_name": "Doe", "sex": "M"},
                "wife": {"first_name": "Jane", "last_name": "Smith", "sex": "F"}
            }]
        }
        self.builder.build_from_gw_parser(test_data)
        self.base_data = {'persons': self.builder.persons, 'families': self.builder.families}

    def test_find_existing_person(self):
        person = find_person_by_key(self.base_data, "John", "Doe", 0)
        self.assertIsNotNone(person)
        # Fix: names are NOT swapped in the current implementation
        self.assertEqual(person.first_name, "John")
        self.assertEqual(person.last_name, "Doe")

    def test_find_nonexistent_person(self):
        person = find_person_by_key(self.base_data, "Nonexistent", "Person", 0)
        self.assertIsNone(person)

    def test_find_person_with_occ(self):
        test_data = {
            "families": [{
                "husband": {"first_name": "John.1", "last_name": "Doe", "sex": "M"}
            }]
        }
        builder = GenealogyDataBuilder()
        builder.build_from_gw_parser(test_data)
        base_data = {'persons': builder.persons, 'families': builder.families}
        
        person = find_person_by_key(base_data, "John", "Doe", 1)
        self.assertIsNotNone(person)
        self.assertEqual(person.occ, 1)


class TestComparisonScenarios(unittest.TestCase):
    def test_identical_persons_no_diff(self):
        config = ComparisonConfig()
        gwdiff = GWDiff(config)
        
        p1 = Person("id1", "John", "Doe", "M", 0, "1900", "1980")
        p2 = Person("id2", "John", "Doe", "M", 0, "1900", "1980")
        
        messages = gwdiff.compatible_persons(p1, p2)
        self.assertEqual(messages, [])

    def test_different_names_diff(self):
        config = ComparisonConfig()
        gwdiff = GWDiff(config)
        
        p1 = Person("id1", "John", "Doe", "M", 0)
        p2 = Person("id2", "Jonathan", "Doe", "M", 0)
        
        messages = gwdiff.compatible_persons_light(p1, p2)
        self.assertIn(DiffMessage.FIRST_NAME, messages)

    def test_different_sex_diff(self):
        config = ComparisonConfig()
        gwdiff = GWDiff(config)
        
        p1 = Person("id1", "John", "Doe", "M", 0)
        p2 = Person("id2", "John", "Doe", "F", 0)
        
        messages = gwdiff.compatible_persons(p1, p2)
        self.assertIn(DiffMessage.SEX, messages)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)