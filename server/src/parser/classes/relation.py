from person import Person

class Relation:
    """Special relationships (adoption, parraining, etc.)"""
    def __init__(self):
        self.person = None
        self.relations = []
    
    RELATION_TYPES = {
        'adop': 'Adoption',
        'reco': 'Recognition',
        'cand': 'Candidate',
        'godp': 'GodParent',
        'fost': 'Foster'
    }