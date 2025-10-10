import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from events import PersonalEvent, FamilyEvent
from date import Date
from person import Person

class TestEvents(unittest.TestCase):
    
    def test_personal_event_creation(self):
        event = PersonalEvent()
        event.event_type = "#birt"
        event.date = Date("10/05/1990")
        event.place = "Paris"
        
        self.assertEqual(event.event_type, "#birt")
        self.assertEqual(str(event.date), "10/05/1990")
        self.assertEqual(event.place, "Paris")
    
    def test_family_event_creation(self):
        event = FamilyEvent()
        event.event_type = "#marr"
        event.date = Date("25/11/1728")
        event.place = "Ile-aux-Moines"
        
        self.assertEqual(event.event_type, "#marr")
        self.assertEqual(str(event.date), "25/11/1728")
        self.assertEqual(event.place, "Ile-aux-Moines")
    
    def test_event_types_mapping(self):
        self.assertEqual(PersonalEvent.EVENT_TYPES["#birt"], "Birth")
        self.assertEqual(PersonalEvent.EVENT_TYPES["#deat"], "Death")
        self.assertEqual(FamilyEvent.EVENT_TYPES["#marr"], "Marriage")
        self.assertEqual(FamilyEvent.EVENT_TYPES["#div"], "Divorce")
    
    def test_event_with_witnesses(self):
        event = PersonalEvent()
        witness = Person()
        witness.parse_from_string("CORNO Alain")
        event.witnesses.append(("godp", witness))
        
        self.assertEqual(len(event.witnesses), 1)
        self.assertEqual(event.witnesses[0][0], "godp")
        self.assertEqual(str(event.witnesses[0][1]), "CORNO Alain")
    
    def test_event_notes(self):
        event = PersonalEvent()
        event.notes.append("Note importante")
        event.notes.append("Seconde note")
        
        self.assertEqual(len(event.notes), 2)
        self.assertEqual(event.notes[0], "Note importante")

if __name__ == '__main__':
    unittest.main()