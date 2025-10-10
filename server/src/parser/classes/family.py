from person import Person
from events import FamilyEvent

class Family:
    def __init__(self):
        self.husband = None
        self.wife = None
        self.wedding_date = None
        self.wedding_place = None
        self.wedding_source = None
        self.marriage_type = None  # #nm, #eng, etc.
        self.separation = False
        self.divorce_date = None
        self.witnesses = []
        self.source = None
        self.comments = None
        self.common_birth_place = None
        self.common_children_source = None
        self.children = []
        self.family_events = []
    
    def __str__(self):
        return f"Famille: {self.husband} + {self.wife}"