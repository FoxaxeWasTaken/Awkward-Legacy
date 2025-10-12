"""
models.py

Data structures, constants, and type definitions for the GeneWeb parser.

Contains:
- Event type mappings for families and persons
- Type hints and data structures used throughout the parser
- Constants for parsing and interpretation
"""

from __future__ import annotations
from typing import TypedDict, Literal, Dict, List, Union

# ===== FAMILY EVENT TAGS =====
FEVT_MAP: Dict[str, str] = {
    "#marr": "marriage",
    "#nmar": "no_marriage",
    "#nmen": "no_mention",
    "#enga": "engagement",
    "#div": "divorce",
    "#sep": "separated",
    "#anul": "annulation",
    "#marb": "marriage_bann",
    "#marc": "marriage_contract",
    "#marl": "marriage_license",
    "#pacs": "pacs",
    "#resi": "residence",
    # generic: if unknown tag, keep raw
}

# ===== PERSON EVENT TAGS =====
PEVT_MAP: Dict[str, str] = {
    "#birt": "birth",
    "#bapt": "baptism",
    "#deat": "death",
    "#buri": "burial",
    "#crem": "cremation",
    "#occu": "occupation",
    "#cens": "census",
    "#resi": "residence",
    "#immig": "immigration",
    "#strng": "name_string",
}

# ===== TYPES =====

# Precise tag types (optional for stricter checking)
FamilyEventTag = Literal[
    "#marr",
    "#nmar",
    "#nmen",
    "#enga",
    "#div",
    "#sep",
    "#anul",
    "#marb",
    "#marc",
    "#marl",
    "#pacs",
    "#resi",
]

PersonEventTag = Literal[
    "#birt",
    "#bapt",
    "#deat",
    "#buri",
    "#crem",
    "#occu",
    "#cens",
    "#resi",
    "#immig",
    "#strng",
]


# Date representation type
class DateDict(TypedDict, total=False):
    raw: str
    qualifier: str
    value: str
    between: List[str]
    alternatives: List[str]
    literal: str


# Event representation type
class EventDict(TypedDict, total=False):
    type: str
    date: DateDict
    place_raw: str
    source: str
    notes: List[str]
    raw: str


# Person representation type
class PersonDict(TypedDict, total=False):
    name: str
    first_name: str
    last_name: str
    sex: str
    tags: List[str]
    events: List[EventDict]
    notes: List[str]


# Family representation type
class FamilyDict(TypedDict, total=False):
    husband: PersonDict
    wife: PersonDict
    children: List[PersonDict]
    events: List[EventDict]
    notes: List[str]


# Tags mapping
TagsDict = Dict[str, List[str]]

# Parser result structure
ParserResult = Dict[str, Union[List[FamilyDict], List[PersonDict], Dict[str, str]]]
