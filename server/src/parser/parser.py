import re
from typing import List
from data import GeneWebData
from family import Family
from person import Person
from relation import Relation
from events import PersonalEvent, FamilyEvent
from date import Date

class GeneWebParser:
    """Parser pour les fichiers .gw de GeneWeb"""
    
    def __init__(self):
        self.data = GeneWebData()
        self.current_section = None
        self.current_content = []
        self.current_family = None
        self.current_relation = None
        self.current_personal_event = None
        self.current_person_ref = None
        self.current_page_name = None
        self.current_wizard_name = None
    
    def parse_file(self, filename: str) -> GeneWebData:
        """Parse un fichier .gw complet"""
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        return self.parse_lines(lines)
    
    def parse_lines(self, lines: List[str]) -> GeneWebData:
        """Parse une liste de lignes"""
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                self._parse_line(line)
            except Exception as e:
                print(f"Erreur ligne {line_num}: {line}")
                raise e
        
        # S'assurer que la dernière section est fermée
        if self.current_section:
            self._end_current_section()
        
        return self.data
    
    def _parse_line(self, line: str):
        """Parse une ligne individuelle"""
        # Sections principales
        if line.startswith('encoding:'):
            self.data.encoding = line.split(':', 1)[1].strip()
        
        elif line == 'gwplus':
            self.data.gwplus = True
        
        elif line.startswith('fam '):
            # Fermer la section précédente si elle existe
            if self.current_section:
                self._end_current_section()
            self._start_family_section(line[4:])
        
        elif line.startswith('notes ') and not line.startswith('notes-db'):
            if self.current_section:
                self._end_current_section()
            self._start_personal_notes_section(line[6:])
        
        elif line.startswith('rel '):
            if self.current_section:
                self._end_current_section()
            self._start_relation_section(line[4:])
        
        elif line.startswith('pevt '):
            if self.current_section:
                self._end_current_section()
            self._start_personal_event_section(line[5:])
        
        elif line.startswith('notes-db'):
            if self.current_section:
                self._end_current_section()
            self._start_database_notes_section()
        
        elif line.startswith('page-ext '):
            if self.current_section:
                self._end_current_section()
            self._start_extended_page_section(line[9:])
        
        elif line.startswith('wizard-note '):
            if self.current_section:
                self._end_current_section()
            self._start_wizard_note_section(line[12:])
        
        elif line in ('end', 'end notes', 'end rel', 'end pevt', 'end notes-db', 'end page-ext', 'end wizard-note', 'end fevt'):
            self._end_current_section()
        
        else:
            self._process_content_line(line)
    
    def _start_family_section(self, family_line: str):
        """Début d'une section famille"""
        self.current_section = 'family'
        self.current_family = Family()
        self._parse_family_header(family_line)  # Renommage de la méthode
    
    def _parse_family_header(self, family_line: str):
        """Parse la ligne de définition d'une famille"""
        # Séparation époux/épouse
        if ' + ' in family_line:
            parts = family_line.split(' + ', 1)
            husband_part = parts[0].strip()
            wife_part = parts[1].strip()
        else:
            husband_part = family_line
            wife_part = ""
        
        # Parse époux
        self._parse_family_husband(husband_part)
        
        # Parse épouse
        if wife_part:
            self._parse_family_wife(wife_part)
    
    def _parse_family_husband(self, husband_str: str):
        """Parse la partie époux d'une définition de famille"""
        # Nettoyer la chaîne des tags (les tags mariage sont dans la partie épouse)
        tag_pattern = r'#\w+\s+[^#\s]+(?:\s+[^#\s]+)*'
        clean_str = re.sub(tag_pattern, '', husband_str).strip()
        
        # Parser l'époux
        person = Person()
        person.parse_from_string(clean_str)
        self.current_family.husband = person
    
    def _parse_family_wife(self, wife_str: str):
        """Parse la partie épouse d'une définition de famille"""
        # Extraire les tags avec une regex
        tags = {}
        tag_pattern = r'#(\w+)\s+([^#\s]+(?:\s+[^#\s]+)*)'
        
        # Chercher les tags
        for match in re.finditer(tag_pattern, wife_str):
            tag_name, tag_value = match.groups()
            tags[tag_name] = tag_value.strip()
        
        # Nettoyer la chaîne des tags pour obtenir le nom et la date
        clean_str = re.sub(tag_pattern, '', wife_str).strip()
        
        # La partie épouse contient: [date] [nom_épouse]
        parts = clean_str.split()
        
        date_parts = []
        name_parts = []
        in_date = True
        
        for part in parts:
            if in_date and self._looks_like_date_part(part):
                date_parts.append(part)
            else:
                in_date = False
                name_parts.append(part)
        
        # Date de mariage
        if date_parts:
            wedding_date_str = ' '.join(date_parts)
            self.current_family.wedding_date = Date(wedding_date_str)
        
        # Nom de l'épouse
        if name_parts:
            wife_name = ' '.join(name_parts)
            person = Person()
            person.parse_from_string(wife_name)
            self.current_family.wife = person
        
        # Application des tags
        if 'mp' in tags:
            self.current_family.wedding_place = tags['mp']
        if 'ms' in tags:
            self.current_family.wedding_source = tags['ms']
        if 'nm' in tags:
            self.current_family.marriage_type = '#nm'
        if 'eng' in tags:
            self.current_family.marriage_type = '#eng'
    
    def _looks_like_date_part(self, part: str) -> bool:
        """Détermine si une partie ressemble à un élément de date"""
        # Les dates contiennent des chiffres ou des modificateurs de date
        date_indicators = ['~', '?', '<', '>', '|', '..']
        
        # Si c'est un modificateur de date
        if part in date_indicators:
            return True
        
        # Si ça contient des chiffres (format dd/mm/yyyy, yyyy, etc.)
        if any(c.isdigit() for c in part):
            return True
        
        # Si ça contient des séparateurs de date
        if '/' in part or '-' in part or '.' in part:
            return True
        
        return False
    
    def _start_personal_notes_section(self, person_ref: str):
        """Début d'une section de notes personnelles"""
        self.current_section = 'personal_notes'
        self.current_person_ref = person_ref.strip()
        self.current_content = []
    
    def _start_relation_section(self, person_ref: str):
        """Début d'une section de relations"""
        self.current_section = 'relation'
        self.current_relation = Relation()
        self.current_relation.person = Person()
        self.current_relation.person.parse_from_string(person_ref.strip())
    
    def _start_personal_event_section(self, person_ref: str):
        """Début d'une section d'événements personnels (gwplus)"""
        self.current_section = 'personal_event'
        self.current_personal_event = PersonalEvent()
        self.current_person_ref = person_ref.strip()
    
    def _start_database_notes_section(self):
        """Début d'une section de notes de base de données"""
        self.current_section = 'database_notes'
        self.current_content = []
    
    def _start_extended_page_section(self, page_name: str):
        """Début d'une section de page étendue"""
        self.current_section = 'extended_page'
        self.current_page_name = page_name.strip()
        self.current_content = []
    
    def _start_wizard_note_section(self, wizard_name: str):
        """Début d'une section de note de wizard"""
        self.current_section = 'wizard_note'
        self.current_wizard_name = wizard_name.strip()
        self.current_content = []
    
    def _end_current_section(self):
        """Termine la section courante"""
        if self.current_section == 'family' and self.current_family:
            self.data.add_family(self.current_family)
            self.current_family = None
        
        elif self.current_section == 'personal_notes' and self.current_person_ref:
            self.data.personal_notes[self.current_person_ref] = '\n'.join(self.current_content)
            self.current_person_ref = None
        
        elif self.current_section == 'relation' and self.current_relation:
            self.data.relations.append(self.current_relation)
            self.current_relation = None
        
        elif self.current_section == 'personal_event' and self.current_personal_event:
            self.data.personal_events.append(self.current_personal_event)
            self.current_personal_event = None
        
        elif self.current_section == 'database_notes':
            self.data.database_notes = '\n'.join(self.current_content)
        
        elif self.current_section == 'extended_page' and self.current_page_name:
            self.data.extended_pages[self.current_page_name] = '\n'.join(self.current_content)
            self.current_page_name = None
        
        elif self.current_section == 'wizard_note' and self.current_wizard_name:
            self.data.wizard_notes[self.current_wizard_name] = '\n'.join(self.current_content)
            self.current_wizard_name = None
        
        elif self.current_section == 'family_events':
            # Juste retour à la section famille
            self.current_section = 'family'
        
        self.current_section = None
        self.current_content = []
    
    def _process_content_line(self, line: str):
        """Traite une ligne de contenu selon la section courante"""
        if self.current_section in ['personal_notes', 'database_notes', 'extended_page', 'wizard_note']:
            self.current_content.append(line)
        
        elif self.current_section == 'relation' and line.startswith('- '):
            self._parse_relation_line(line[2:])
        
        elif self.current_section == 'family' and line.startswith('- '):
            self._parse_child_line(line[2:])
        
        elif self.current_section == 'family' and line.startswith('fevt'):
            self.current_section = 'family_events'
        
        elif self.current_section == 'family_events' and not line.startswith('end fevt'):
            self._parse_family_event_line(line)
        
        elif self.current_section == 'family' and line.startswith('src'):
            self.current_family.source = line[4:].strip()
        
        elif self.current_section == 'family' and line.startswith('comm'):
            self.current_family.comments = line[5:].strip()

    def _parse_family_event_line(self, line: str):
        """Parse une ligne d'événement familial"""
        if line.startswith('#'):
            # Nouvel événement
            event = FamilyEvent()
            parts = line.split()
            event.event_type = parts[0]
            
            # Parse date et autres informations
            for i, part in enumerate(parts[1:], 1):
                if part.startswith('#p'):
                    event.place = ' '.join(parts[i+1:])
                    break
                elif part.startswith('#s'):
                    event.source = ' '.join(parts[i+1:])
                    break
                elif not part.startswith('#'):
                    event.date = Date(part)
            
            self.current_family.family_events.append(event)

    def _parse_relation_line(self, relation_line: str):
        """Parse une ligne de relation"""
        if ':' in relation_line:
            rel_type, persons = relation_line.split(':', 1)
            rel_type = rel_type.strip()
            persons = persons.strip()
            
            # Séparation père/mère si présents
            if ' + ' in persons:
                father_str, mother_str = persons.split(' + ', 1)
                father = Person()
                father.parse_from_string(father_str.strip())
                mother = Person()
                mother.parse_from_string(mother_str.strip())
                self.current_relation.relations.append((rel_type, father, mother))
            else:
                person = Person()
                person.parse_from_string(persons.strip())
                self.current_relation.relations.append((rel_type, person, None))

    def _parse_child_line(self, child_line: str):
        """Parse une ligne d'enfant dans une famille"""
        child = Person()
        
        # Le premier mot après le '-' peut être h, f ou vide pour le sexe
        parts = child_line.split()
        if parts and parts[0] in ('h', 'f', ''):
            sex = parts[0]
            child_line = ' '.join(parts[1:])
        else:
            sex = None
        
        child.parse_from_string(child_line)
        self.current_family.children.append(child)