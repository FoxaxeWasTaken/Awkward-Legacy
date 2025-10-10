import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from family import Family
from person import Person
from date import Date
from events import FamilyEvent

class TestFamily(unittest.TestCase):
    
    def test_family_creation(self):
        family = Family()
        family.husband = Person()
        family.husband.parse_from_string("CORNO Joseph")
        family.wife = Person()
        family.wife.parse_from_string("THOMAS Marie")
        
        self.assertEqual(str(family.husband), "CORNO Joseph")
        self.assertEqual(str(family.wife), "THOMAS Marie")
    
    def test_family_with_wedding_info(self):
        family = Family()
        family.wedding_date = Date("25/11/1728")
        family.wedding_place = "Ile-aux-Moines"
        family.wedding_source = "Registre paroissial"
        
        self.assertEqual(str(family.wedding_date), "25/11/1728")
        self.assertEqual(family.wedding_place, "Ile-aux-Moines")
        self.assertEqual(family.wedding_source, "Registre paroissial")
    
    def test_family_with_children(self):
        family = Family()
        
        child1 = Person()
        child1.parse_from_string("CORNO Alain")
        family.children.append(child1)
        
        child2 = Person()
        child2.parse_from_string("CORNO Sophie")
        family.children.append(child2)
        
        self.assertEqual(len(family.children), 2)
        self.assertEqual(str(family.children[0]), "CORNO Alain")
        self.assertEqual(str(family.children[1]), "CORNO Sophie")
    
    def test_family_events(self):
        family = Family()
        
        event = FamilyEvent()
        event.event_type = "#marr"
        event.date = Date("25/11/1728")
        family.family_events.append(event)
        
        self.assertEqual(len(family.family_events), 1)
        self.assertEqual(family.family_events[0].event_type, "#marr")
    
    def test_str_representation(self):
        family = Family()
        family.husband = Person()
        family.husband.parse_from_string("CORNO Joseph")
        family.wife = Person()
        family.wife.parse_from_string("THOMAS Marie")
        
        self.assertEqual(str(family), "Famille: CORNO Joseph + THOMAS Marie")

if __name__ == '__main__':
    unittest.main()