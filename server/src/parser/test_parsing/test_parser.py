import unittest
import sys
import os
import tempfile
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser import GeneWebParser

class TestGeneWebParser(unittest.TestCase):
    
    def create_test_file(self, content):
        """Crée un fichier temporaire avec le contenu donné"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gw', delete=False, encoding='utf-8') as f:
            f.write(content)
            return f.name
    
    def test_parse_encoding(self):
        content = """encoding: utf-8

fam CORNO Joseph + THOMAS Marie"""
        
        filename = self.create_test_file(content)
        try:
            parser = GeneWebParser()
            data = parser.parse_file(filename)
            
            self.assertEqual(data.encoding, "utf-8")
            self.assertEqual(len(data.families), 1)
        finally:
            os.unlink(filename)
    
    def test_parse_simple_family(self):
        content = """fam CORNO Joseph + THOMAS Marie"""
        
        filename = self.create_test_file(content)
        try:
            parser = GeneWebParser()
            data = parser.parse_file(filename)
            
            self.assertEqual(len(data.families), 1)
            family = data.families[0]
            self.assertEqual(str(family.husband), "CORNO Joseph")
            self.assertEqual(str(family.wife), "THOMAS Marie")
        finally:
            os.unlink(filename)
    
    def test_parse_family_with_wedding_info(self):
        content = """fam CORNO Alain +25/11/1728 #mp Ile-aux-Moines CAUZIC Marie"""
        
        filename = self.create_test_file(content)
        try:
            parser = GeneWebParser()
            data = parser.parse_file(filename)
            
            self.assertEqual(len(data.families), 1)
            family = data.families[0]
            self.assertEqual(str(family.wedding_date), "25/11/1728")
            self.assertEqual(family.wedding_place, "Ile-aux-Moines")
            self.assertEqual(str(family.wife), "CAUZIC Marie")
        finally:
            os.unlink(filename)
    
    def test_parse_family_with_children(self):
        content = """fam CORNO Joseph + THOMAS Marie
beg
- CORNO Alain
- CORNO Sophie
end"""
        
        filename = self.create_test_file(content)
        try:
            parser = GeneWebParser()
            data = parser.parse_file(filename)
            
            family = data.families[0]
            self.assertEqual(len(family.children), 2)
            self.assertEqual(str(family.children[0]), "CORNO Alain")
            self.assertEqual(str(family.children[1]), "CORNO Sophie")
        finally:
            os.unlink(filename)
    
    def test_parse_personal_notes(self):
        content = """notes CORNO Alain
beg
Note personnelle pour Alain CORNO.
Il était un grand voyageur.
end notes"""
        
        filename = self.create_test_file(content)
        try:
            parser = GeneWebParser()
            data = parser.parse_file(filename)
            
            self.assertIn("CORNO Alain", data.personal_notes)
            self.assertIn("grand voyageur", data.personal_notes["CORNO Alain"])
        finally:
            os.unlink(filename)
    
    def test_parse_relations(self):
        content = """rel CORNO Jean
    beg
    - godp: CORNO Pierre + THOMAS Marie
    end"""
        
        filename = self.create_test_file(content)
        try:
            parser = GeneWebParser()
            data = parser.parse_file(filename)
            
            self.assertEqual(len(data.relations), 1)
            relation = data.relations[0]
            self.assertEqual(str(relation.person), "CORNO Jean")
            self.assertEqual(len(relation.relations), 1)
            self.assertEqual(relation.relations[0][0], "godp")
        finally:
            os.unlink(filename)
    
    def test_parse_database_notes(self):
        content = """notes-db
  Note de présentation de la base.
  Contient des informations généalogiques.
end notes-db"""
        
        filename = self.create_test_file(content)
        try:
            parser = GeneWebParser()
            data = parser.parse_file(filename)
            
            self.assertIsNotNone(data.database_notes)
            self.assertIn("informations généalogiques", data.database_notes)
        finally:
            os.unlink(filename)
    
    def test_parse_complex_file(self):
        content = """encoding: utf-8

fam CORNO Joseph + THOMAS Marie
beg
- CORNO Alain
end

notes CORNO Alain
beg
Note importante.
end notes

notes-db
  Base de test.
end notes-db"""
        
        filename = self.create_test_file(content)
        try:
            parser = GeneWebParser()
            data = parser.parse_file(filename)
            
            self.assertEqual(data.encoding, "utf-8")
            self.assertEqual(len(data.families), 1)
            self.assertEqual(len(data.personal_notes), 1)
            self.assertIsNotNone(data.database_notes)
        finally:
            os.unlink(filename)

if __name__ == '__main__':
    unittest.main()