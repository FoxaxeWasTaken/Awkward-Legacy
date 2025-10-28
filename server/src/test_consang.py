#!/usr/bin/env python3
"""
Unit tests for consang.py - CORRECTED VERSION
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
from uuid import UUID, uuid4
from unittest.mock import patch, MagicMock, Mock
from typing import List, Dict, Any

# Import the modules to test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from consang import (
    Person, Family, GenealogyDataBuilder, 
    ConsanguinityCalculator, ConsanguinityApp
)


class TestDatabaseIntegration(unittest.TestCase):
    """Test database integration features"""
    
    def setUp(self):
        self.db_session = MagicMock()
        self.builder = GenealogyDataBuilder()
        
    def test_person_from_db_person(self):
        """Test creating Person from database Person model"""
        # Mock database person
        db_person = MagicMock()
        db_person.id = UUID('12345678-1234-5678-1234-567812345678')
        db_person.first_name = "John"
        db_person.last_name = "Doe"
        db_person.sex = "M"
        db_person.birth_date = None
        db_person.death_date = None
        db_person.father_id = None
        db_person.mother_id = None
        
        # Convert to our Person class
        person = Person.from_db_person(db_person)
        
        self.assertEqual(person.id, "12345678-1234-5678-1234-567812345678")
        self.assertEqual(person.first_name, "John")
        self.assertEqual(person.last_name, "Doe")
        self.assertEqual(person.sex, "M")
        self.assertEqual(person.occ, 0)
        self.assertEqual(person.families, [])
    
    def test_person_from_db_person_with_dates(self):
        """Test creating Person from database Person with dates"""
        from datetime import date
        
        db_person = MagicMock()
        db_person.id = UUID('12345678-1234-5678-1234-567812345678')
        db_person.first_name = "Jane"
        db_person.last_name = "Smith"
        db_person.sex = "F"
        db_person.birth_date = date(1980, 5, 15)
        db_person.death_date = date(2020, 3, 10)
        db_person.father_id = UUID('11111111-1111-1111-1111-111111111111')
        db_person.mother_id = UUID('22222222-2222-2222-2222-222222222222')
        
        person = Person.from_db_person(db_person)
        
        self.assertEqual(person.birth_date, "1980-05-15")
        self.assertEqual(person.death_date, "2020-03-10")
    
    def test_builder_initial_state(self):
        """Test GenealogyDataBuilder initial state"""
        self.assertEqual(self.builder.persons, {})
        self.assertEqual(self.builder.families, {})
        self.assertEqual(self.builder._person_counter, 0)
        self.assertEqual(self.builder._family_counter, 0)


class TestDatabaseBuilders(unittest.TestCase):
    """Test database building functionality"""
    
    def setUp(self):
        self.db_session = MagicMock()
        self.builder = GenealogyDataBuilder()
        
    def test_build_from_person_basic(self):
        """Test basic building from person without complex imports"""
        # Mock a simple person object that our code can handle
        db_person = MagicMock()
        db_person.id = UUID('12345678-1234-5678-1234-567812345678')
        db_person.first_name = "John"
        db_person.last_name = "Doe"
        db_person.sex = "M"
        db_person.birth_date = None
        db_person.death_date = None
        db_person.father_id = None
        db_person.mother_id = None
        
        self.db_session.get.return_value = db_person
        
        person_id = UUID('12345678-1234-5678-1234-567812345678')
        
        self.builder.build_from_database(self.db_session, person_id)
        
        self.assertGreaterEqual(len(self.builder.persons), 1)
    
    def test_process_db_family(self):
        """Test processing a database family"""
        # Create a proper mock family
        db_family = MagicMock()
        db_family.husband_id = UUID('11111111-1111-1111-1111-111111111111')
        db_family.wife_id = UUID('22222222-2222-2222-2222-222222222222')
        
        # Mock child relationship
        child_relation = MagicMock()
        child_relation.child_id = UUID('33333333-3333-3333-3333-333333333333')
        db_family.children = [child_relation]
        
        # Add persons to builder first
        husband_id = str(db_family.husband_id)
        wife_id = str(db_family.wife_id)
        child_id = str(db_family.children[0].child_id)
        
        self.builder.persons[husband_id] = Person(husband_id, "John", "Doe", "M")
        self.builder.persons[wife_id] = Person(wife_id, "Jane", "Smith", "F")
        self.builder.persons[child_id] = Person(child_id, "Bob", "Doe", "M")
        
        # Process family
        self.builder._process_db_family(self.db_session, db_family)
        
        # Verify family was created
        self.assertEqual(len(self.builder.families), 1)
        family = list(self.builder.families.values())[0]
        
        self.assertEqual(family.husband_id, husband_id)
        self.assertEqual(family.wife_id, wife_id)
        self.assertEqual(family.children, [child_id])
        
        # Verify person-family relationships
        self.assertIn(family.id, self.builder.persons[husband_id].families)
        self.assertIn(family.id, self.builder.persons[wife_id].families)
        self.assertIn(family.id, self.builder.persons[child_id].families)
        
        # Verify parent-child relationships
        child = self.builder.persons[child_id]
        self.assertEqual(child.father_id, husband_id)
        self.assertEqual(child.mother_id, wife_id)


class TestConsanguinityAppDatabase(unittest.TestCase):
    """Test ConsanguinityApp database functionality"""
    
    def setUp(self):
        self.app = ConsanguinityApp()
        self.db_session = MagicMock()
    
    def test_setup_database(self):
        """Test database setup"""
        person_id = UUID('12345678-1234-5678-1234-567812345678')
        
        self.app.setup_database(self.db_session, person_id)
        
        self.assertEqual(self.app.db_session, self.db_session)
        self.assertEqual(self.app.starting_person_id, person_id)
    
    def test_setup_database_no_person(self):
        """Test database setup without starting person"""
        self.app.setup_database(self.db_session)
        
        self.assertEqual(self.app.db_session, self.db_session)
        self.assertIsNone(self.app.starting_person_id)
    
    def test_compute_consanguinity_from_database_no_session(self):
        """Test computing consanguinity without database session"""
        with self.assertRaises(ValueError) as context:
            self.app.compute_consanguinity_from_database()
        
        self.assertIn("Database session not configured", str(context.exception))


class TestBasicFunctionality(unittest.TestCase):
    """Test basic consanguinity calculator functionality"""
    
    def test_person_creation(self):
        """Test basic person creation"""
        person = Person("id1", "John", "Doe", "M")
        self.assertEqual(person.first_name, "John")
        self.assertEqual(person.last_name, "Doe")
        self.assertEqual(person.sex, "M")
    
    def test_family_creation(self):
        """Test basic family creation"""
        family = Family("F1", "H1", "W1", ["C1", "C2"])
        self.assertEqual(family.id, "F1")
        self.assertEqual(family.husband_id, "H1")
        self.assertEqual(family.wife_id, "W1")
        self.assertEqual(family.children, ["C1", "C2"])
    
    def test_consanguinity_calculator(self):
        """Test basic consanguinity calculation"""
        calculator = ConsanguinityCalculator()
        
        # Create test persons
        persons = {
            "p1": Person("p1", "John", "Doe", "M"),
            "p2": Person("p2", "Jane", "Smith", "F"),
        }
        
        calculator.build_parents_cache(persons)
        coefficient = calculator.calculate_consanguinity("p1", "p2")
        
        # Unrelated persons should have coefficient 0.0
        self.assertEqual(coefficient, 0.0)


if __name__ == '__main__':
    unittest.main(verbosity=2)