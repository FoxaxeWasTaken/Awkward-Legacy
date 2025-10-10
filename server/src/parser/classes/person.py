import re
from date import Date

class Person:
    def __init__(self):
        self.last_name = ""
        self.first_name = ""
        self.occurence = None
        self.public_name = None
        self.nickname = None
        self.first_name_alias = None
        self.surname_alias = None
        self.alias = None
        self.titles = []
        self.access = None  # 'public' or 'private'
        self.image_path = None
        self.occupation = None
        self.source = None
        
        # Dates
        self.birth_date = None
        self.birth_place = None
        self.birth_source = None
        
        self.baptism_date = None
        self.baptism_place = None
        self.baptism_source = None
        
        self.death_date = None
        self.death_place = None
        self.death_source = None
        self.death_type = None  # k: killed, m: murdered, etc.
        self.obviously_dead = False
        self.dead_in_infancy = False
        
        self.burial_date = None
        self.burial_place = None
        self.burial_source = None
        self.cremation = False
    
    def parse_from_string(self, person_str: str):
        # pattern with name and surname with optional occurences
        pattern = r'^(\w+)\s+([\w_]+)(?:\.(\d+))?'
        match = re.match(pattern, person_str)
        if match:
            self.last_name = match.group(1)
            self.first_name = match.group(2).replace('_', ' ')
            if match.group(3):
                self.occurence = int(match.group(3))
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}" + (f".{self.occurence}" if self.occurence else "")