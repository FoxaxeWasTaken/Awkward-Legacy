import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data import GeneWebData
from family import Family
from person import Person
from relation import Relation
from events import PersonalEvent

class TestGeneWebData(unittest.TestCase):
    
    def test_data_initialization(self):
        data = GeneWebData()
        self.assertEqual(data.encoding, "iso-8859-1")
        self.assertFalse(data.gwplus)
        self.assertEqual(len(data.families), 0)
        self.assertEqual(len(data.relations), 0)
        self.assertEqual(len(data.personal_events), 0)
    
    def test_add_families(self):
        data = GeneWebData()
        
        family1 = Family()
        family1.husband = Person()
        family1.husband.parse_from_string("CORNO Joseph")
        data.add_family(family1)
        
        family2 = Family()
        family2.husband = Person()
        family2.husband.parse_from_string("DUPONT Jean")
        data.add_family(family2)
        
        self.assertEqual(len(data.families), 2)
        self.assertEqual(str(data.families[0].husband), "CORNO Joseph")
        self.assertEqual(str(data.families[1].husband), "DUPONT Jean")
    
    def test_personal_notes(self):
        data = GeneWebData()
        data.personal_notes["CORNO Alain"] = "Note personnelle pour Alain"
        data.personal_notes["THOMAS Marie"] = "Note pour Marie"
        
        self.assertEqual(len(data.personal_notes), 2)
        self.assertEqual(data.personal_notes["CORNO Alain"], "Note personnelle pour Alain")
    
    def test_relations_storage(self):
        data = GeneWebData()
        
        relation = Relation()
        relation.person = Person()
        relation.person.parse_from_string("CORNO Jean")
        data.relations.append(relation)
        
        self.assertEqual(len(data.relations), 1)
        self.assertEqual(str(data.relations[0].person), "CORNO Jean")
    
    def test_personal_events_storage(self):
        data = GeneWebData()
        
        event = PersonalEvent()
        event.event_type = "#birt"
        data.personal_events.append(event)
        
        self.assertEqual(len(data.personal_events), 1)
        self.assertEqual(data.personal_events[0].event_type, "#birt")
    
    def test_extended_pages(self):
        data = GeneWebData()
        data.extended_pages["Histoire"] = "Page sur l'histoire de la famille"
        data.extended_pages["Lieux"] = "Page sur les lieux importants"
        
        self.assertEqual(len(data.extended_pages), 2)
        self.assertEqual(data.extended_pages["Histoire"], "Page sur l'histoire de la famille")
    
    def test_str_representation(self):
        data = GeneWebData()
        data.add_family(Family())
        data.relations.append(Relation())
        
        expected_str = "GeneWebData: 1 familles, 1 relations, 0 événements personnels"
        self.assertEqual(str(data), expected_str)

if __name__ == '__main__':
    unittest.main()