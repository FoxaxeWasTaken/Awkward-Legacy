from family import Family
from relation import Relation
from events import PersonalEvent

class GeneWebData:
    """Main container"""
    def __init__(self):
        self.encoding = "iso-8859-1"
        self.gwplus = False
        self.families = []
        self.personal_notes = {}
        self.relations = []  
        self.personal_events = []
        self.database_notes = None
        self.extended_pages = {}
        self.wizard_notes = {}
    
    def add_family(self, family: Family):
        self.families.append(family)
    
    def __str__(self):
        return (f"GeneWebData: {len(self.families)} families, "
                f"{len(self.relations)} relations, "
                f"{len(self.personal_events)} personnal events")