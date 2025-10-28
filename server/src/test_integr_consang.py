#!/usr/bin/env python3
"""
Integration tests for consang.py database features with actual database models
"""

import unittest
import tempfile
import os
from uuid import UUID, uuid4
from unittest.mock import patch, MagicMock
from sqlmodel import Session, create_engine, SQLModel

# Import the modules to test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from consang import (
    Person, Family, GenealogyDataBuilder, 
    analyze_family_consanguinity, batch_consanguinity_analysis
)


class TestIntegrationWithDatabaseModels(unittest.TestCase):
    """Integration tests with actual database models"""
    
    def setUp(self):
        # Create in-memory database for testing
        self.engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        
    def tearDown(self):
        self.session.close()
    
    @patch('consang.family_crud')
    def test_integration_with_mock_models(self, mock_family_crud):
        """Test integration with mocked database models"""
        # Create mock database models that resemble real ones
        MockPerson = self._create_mock_person_class()
        MockFamily = self._create_mock_family_class()
        MockChild = self._create_mock_child_class()
        
        # Create test data
        husband = MockPerson(
            id=uuid4(),
            first_name="John",
            last_name="Doe",
            sex="M"
        )
        
        wife = MockPerson(
            id=uuid4(),
            first_name="Jane", 
            last_name="Smith",
            sex="F"
        )
        
        child = MockPerson(
            id=uuid4(),
            first_name="Bob",
            last_name="Doe",
            sex="M",
            father_id=husband.id,
            mother_id=wife.id
        )
        
        family = MockFamily(
            id=uuid4(),
            husband_id=husband.id,
            wife_id=wife.id
        )
        
        child_relation = MockChild(
            child_id=child.id
        )
        family.children = [child_relation]
        
        # Mock the family_crud responses
        mock_family_crud.get_family_detail.return_value = MagicMock(
            husband_id=husband.id,
            wife_id=wife.id,
            husband=husband,
            wife=wife,
            children=[child_relation]
        )
        
        # Mock session query
        self.session.get = MagicMock(side_effect=lambda model, id: {
            husband.id: husband,
            wife.id: wife,
            child.id: child
        }.get(id))
        
        # Test the analysis
        result = analyze_family_consanguinity(self.session, family.id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["husband"], "John Doe")
        self.assertEqual(result["wife"], "Jane Smith")
        self.assertEqual(result["children_count"], 1)
    
    def _create_mock_person_class(self):
        """Create a mock Person class that behaves like the database model"""
        class MockPerson:
            def __init__(self, id, first_name, last_name, sex, father_id=None, mother_id=None):
                self.id = id
                self.first_name = first_name
                self.last_name = last_name
                self.sex = sex
                self.father_id = father_id
                self.mother_id = mother_id
                self.birth_date = None
                self.death_date = None
            
            def model_dump(self):
                return {
                    "id": self.id,
                    "first_name": self.first_name,
                    "last_name": self.last_name,
                    "sex": self.sex,
                    "father_id": self.father_id,
                    "mother_id": self.mother_id
                }
        
        return MockPerson
    
    def _create_mock_family_class(self):
        """Create a mock Family class that behaves like the database model"""
        class MockFamily:
            def __init__(self, id, husband_id, wife_id, marriage_date=None, marriage_place=None):
                self.id = id
                self.husband_id = husband_id
                self.wife_id = wife_id
                self.marriage_date = marriage_date
                self.marriage_place = marriage_place
                self.children = []
                self.events = []
        
        return MockFamily
    
    def _create_mock_child_class(self):
        """Create a mock Child relation class"""
        class MockChild:
            def __init__(self, child_id):
                self.child_id = child_id
            
            def model_dump(self):
                return {"child_id": self.child_id}
        
        return MockChild


class TestPerformanceWithLargeDatasets(unittest.TestCase):
    """Performance tests for database integration"""
    
    def setUp(self):
        self.builder = GenealogyDataBuilder()
        self.db_session = MagicMock()
    
    @patch('consang.family_crud')
    def test_build_large_family_tree(self, mock_family_crud):
        """Test building a large family tree from database"""
        # Mock a large family structure
        persons = {}
        families = []
        
        # Create 3 generations
        for gen in range(3):
            for i in range(2**gen):  # Exponential growth
                person_id = uuid4()
                persons[person_id] = self._create_mock_db_person(person_id, f"Gen{gen}_Person{i}")
                
                if gen > 0:  # Create families for non-root generation
                    family_id = uuid4()
                    family = self._create_mock_db_family(family_id)
                    families.append(family)
        
        # Mock database responses
        def mock_get_person(model, id):
            return persons.get(id)
        
        self.db_session.get.side_effect = mock_get_person
        mock_family_crud.get_by_spouse.return_value = families
        
        # Build from root person
        root_person_id = list(persons.keys())[0]
        self.builder._build_from_person(self.db_session, root_person_id)
        
        # Should have built substantial tree
        self.assertGreater(len(self.builder.persons), 0)
        self.assertGreater(len(self.builder.families), 0)
    
    def _create_mock_db_person(self, person_id, name):
        """Helper to create mock database person"""
        db_person = MagicMock()
        db_person.id = person_id
        db_person.first_name = name
        db_person.last_name = "Test"
        db_person.sex = "M"
        db_person.birth_date = None
        db_person.death_date = None
        db_person.father_id = None
        db_person.mother_id = None
        return db_person
    
    def _create_mock_db_family(self, family_id):
        """Helper to create mock database family"""
        db_family = MagicMock()
        db_family.id = family_id
        db_family.husband_id = uuid4()
        db_family.wife_id = uuid4()
        db_family.children = []
        return db_family


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)