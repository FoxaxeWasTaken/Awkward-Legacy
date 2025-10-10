import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from relation import Relation
from person import Person

class TestRelation(unittest.TestCase):
    
    def test_relation_creation(self):
        relation = Relation()
        relation.person = Person()
        relation.person.parse_from_string("CORNO Jean")
        
        father = Person()
        father.parse_from_string("CORNO Pierre")
        mother = Person()
        mother.parse_from_string("THOMAS Marie")
        
        relation.relations.append(("godp", father, mother))
        
        self.assertEqual(str(relation.person), "CORNO Jean")
        self.assertEqual(len(relation.relations), 1)
        self.assertEqual(relation.relations[0][0], "godp")
        self.assertEqual(str(relation.relations[0][1]), "CORNO Pierre")
        self.assertEqual(str(relation.relations[0][2]), "THOMAS Marie")
    
    def test_relation_types(self):
        self.assertEqual(Relation.RELATION_TYPES["adop"], "Adoption")
        self.assertEqual(Relation.RELATION_TYPES["godp"], "GodParent")
        self.assertEqual(Relation.RELATION_TYPES["fost"], "Foster")
    
    def test_relation_single_parent(self):
        relation = Relation()
        relation.person = Person()
        relation.person.parse_from_string("CORNO Jean")
        
        father = Person()
        father.parse_from_string("CORNO Pierre")
        
        relation.relations.append(("adop", father, None))
        
        self.assertEqual(relation.relations[0][0], "adop")
        self.assertEqual(str(relation.relations[0][1]), "CORNO Pierre")
        self.assertIsNone(relation.relations[0][2])
    
    def test_multiple_relations(self):
        relation = Relation()
        relation.person = Person()
        relation.person.parse_from_string("CORNO Jean")
        
        # Première relation
        father1 = Person()
        father1.parse_from_string("CORNO Pierre")
        mother1 = Person()
        mother1.parse_from_string("THOMAS Marie")
        relation.relations.append(("godp", father1, mother1))
        
        # Seconde relation
        father2 = Person()
        father2.parse_from_string("DUPONT Louis")
        relation.relations.append(("adop", father2, None))
        
        self.assertEqual(len(relation.relations), 2)
        self.assertEqual(relation.relations[0][0], "godp")
        self.assertEqual(relation.relations[1][0], "adop")

if __name__ == '__main__':
    unittest.main()