import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from person import Person
from date import Date

class TestPerson(unittest.TestCase):
    
    def test_parse_basic_person(self):
        person = Person()
        person.parse_from_string("CORNO Joseph_Marie_Vincent")
        self.assertEqual(person.last_name, "CORNO")
        self.assertEqual(person.first_name, "Joseph Marie Vincent")
        self.assertIsNone(person.occurence)
    
    def test_parse_person_with_occurence(self):
        person = Person()
        person.parse_from_string("CORNO Alain.1")
        self.assertEqual(person.last_name, "CORNO")
        self.assertEqual(person.first_name, "Alain")
        self.assertEqual(person.occurence, 1)
    
    def test_parse_complex_name(self):
        person = Person()
        person.parse_from_string("DE_LA_VALLEE Jean_Pierre")
        self.assertEqual(person.last_name, "DE_LA_VALLEE")
        self.assertEqual(person.first_name, "Jean Pierre")
    
    def test_str_representation(self):
        person = Person()
        person.last_name = "CORNO"
        person.first_name = "Alain"
        self.assertEqual(str(person), "CORNO Alain")
        
        person.occurence = 1
        self.assertEqual(str(person), "CORNO Alain.1")
    
    def test_person_with_dates(self):
        person = Person()
        person.birth_date = Date("10/05/1990")
        person.birth_place = "Paris"
        person.death_date = Date("15/08/2020")
        person.death_place = "Lyon"
        
        self.assertEqual(str(person.birth_date), "10/05/1990")
        self.assertEqual(person.birth_place, "Paris")
        self.assertEqual(str(person.death_date), "15/08/2020")

if __name__ == '__main__':
    unittest.main()