from date import Date
from person import Person

class PersonalEvent:
    """Représente un événement personnel"""
    def __init__(self):
        self.event_type = ""  # #birt, #bapt, #deat, etc.
        self.date = None
        self.place = None
        self.source = None
        self.witnesses = []  # Liste de (type, Person)
        self.notes = []
    
    EVENT_TYPES = {
        '#birt': 'Birth',
        '#bapt': 'Baptism',
        '#deat': 'Death',
        '#buri': 'Burial',
        '#crem': 'Cremation',
        '#acco': 'Accomplishment',
        '#acqu': 'Acquisition',
        '#adhe': 'Adhesion',
        '#bapl': 'BaptismLDS',
        '#barm': 'BarMitzvah',
        '#basm': 'BatMitzvah',
        '#bles': 'Benediction',
        '#cens': 'Recensement',
        '#chgn': 'ChangeName',
        '#circ': 'Circumcision',
        '#conf': 'Confirmation',
        '#conl': 'ConfirmationLDS',
        '#degr': 'Diploma',
        '#awar': 'Decoration',
        '#demm': 'DemobilisationMilitaire',
        '#dist': 'Distinction',
        '#endl': 'Dotation',
        '#dotl': 'DotationLDS',
        '#educ': 'Education',
        '#elec': 'Election',
        '#emig': 'Emigration',
        '#exco': 'Excommunication',
        '#flkl': 'FamilyLinkLDS',
        '#fcom': 'FirstCommunion',
        '#fune': 'Funeral',
        '#grad': 'Graduate',
        '#hosp': 'Hospitalisation',
        '#illn': 'Illness',
        '#immi': 'Immigration',
        '#lpas': 'ListePassenger',
        '#mdis': 'MilitaryDistinction',
        '#mpro': 'MilitaryPromotion',
        '#mser': 'MilitaryService',
        '#mobm': 'MobilisationMilitaire',
        '#natu': 'Naturalisation',
        '#occu': 'Occupation',
        '#ordn': 'Ordination',
        '#prop': 'Property',
        '#resi': 'Residence',
        '#reti': 'Retired',
        '#slgc': 'ScellentChildLDS',
        '#slgp': 'ScellentParentLDS',
        '#slgs': 'ScellentSpouseLDS',
        '#vteb': 'VenteBien',
        '#will': 'Will'
    }

class FamilyEvent:
    """Représente un événement familial"""
    def __init__(self):
        self.event_type = ""  # #marr, #nmar, #enga, etc.
        self.date = None
        self.place = None
        self.source = None
        self.witnesses = []  # Liste de (type, Person)
        self.notes = []
    
    EVENT_TYPES = {
        '#marr': 'Marriage',
        '#nmar': 'NoMarriage',
        '#nmen': 'NoMention',
        '#enga': 'Engage',
        '#div': 'Divorce',
        '#sep': 'Separated',
        '#anul': 'Annulation',
        '#marb': 'MarriageBann',
        '#marc': 'MarriageContract',
        '#marl': 'MarriageLicense',
        '#pacs': 'PACS',
        '#resi': 'Residence'
    }