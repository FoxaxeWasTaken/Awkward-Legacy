Parse Structure

```text

parser/
├── classes/date.py              # Date handling with modifiers and calendars
├── classes/person.py            # Person representation
├── classes/family.py            # Family structures
├── classes/events.py            # Personal and family events
├── classes/relation.py          # Special relationships (adoption, godparents, etc.)
├── classes/data.py              # Main data container
├── parser.py            # Core parser implementation
├── test.py              # Main usage example
├── test_parsing/run_all_tests.py     # Test runner
├── test_parsing/test_*.py           # Individual unit tests
└── requirements.txt     # Dependencies
```
Key Features
Supported Format Elements

    Families (fam): Husband, wife, children, wedding information

    Personal Information: Names, dates, occupations, sources

    Events: Birth, marriage, death, baptism, and custom events

    Relations: Adoption, godparents, foster relationships

    Notes: Personal notes and database notes

    Extended Pages: Wiki-style extended content

    Wizard Notes: Administrator notes

Date Handling

date formats with:

    Modifiers: ~ (about), ? (maybe), < (before), > (after)

    Calendars: Gregorian (default), Julian (J), French Republican (F), Hebrew (H)

    Text dates: 0(5_Mai_1990)

    Date ranges: 10/5/1990..1991

Usage

Basic Parsing

```python

from parser import GeneWebParser

# Parse a .gw file
parser = GeneWebParser()
data = parser.parse_file("family_tree.gw")

# Access the parsed data
print(f"Found {len(data.families)} families")
for family in data.families:
    print(f"Family: {family.husband} + {family.wife}")
    if family.wedding_date:
        print(f"  Married: {family.wedding_date}")
```
Working with Parsed Data

```python
# Access specific information
first_family = data.families[0]

# Person information
print(f"Husband: {first_family.husband.first_name} {first_family.husband.last_name}")
print(f"Wife: {first_family.wife.first_name} {first_family.wife.last_name}")

# Wedding information
if first_family.wedding_date:
    print(f"Wedding: {first_family.wedding_date} in {first_family.wedding_place}")

# Children
for child in first_family.children:
    print(f"Child: {child.first_name} {child.last_name}")

# Personal notes
if "CORNO Alain" in data.personal_notes:
    print(f"Notes for Alain: {data.personal_notes['CORNO Alain']}")
```
Creating Data Programmatically
```python

from family import Family
from person import Person
from date import Date

# Create a family
family = Family()

# Create persons
husband = Person()
husband.last_name = "CORNO"
husband.first_name = "Alain"
husband.occurence = 1

wife = Person() 
wife.last_name = "CAUZIC"
wife.first_name = "Marie"

# Set family relationships
family.husband = husband
family.wife = wife
family.wedding_date = Date("25/11/1728")
family.wedding_place = "Ile-aux-Moines"

# Add to data container
from data import GeneWebData
data = GeneWebData()
data.add_family(family)
```
Data Model
Core Classes

    Date: Handles date formats with modifiers and calendars

    Person: Individual with personal information, events, and relationships

    Family: Family unit with spouses, children, and marriage information

    PersonalEvent: Life events (birth, death, baptism, etc.)

    FamilyEvent: Family events (marriage, divorce, etc.)

    Relation: Special relationships (adoption, godparents)

    GeneWebData: Main container for all parsed data

Example .gw File Structure
```gw

encoding: utf-8

fam CORNO Joseph_Marie_Vincent + THOMAS Marie_Julienne
beg
- CORNO Alain
- CORNO Sophie
end

fam CORNO Alain.1 +25/11/1728 #mp Ile-aux-Moines CAUZIC Marie
beg
- CORNO Jean
- CORNO Pierre
end

notes CORNO Alain
beg
Note personnelle pour Alain CORNO.
Il était un grand voyageur.
end notes

rel CORNO Jean
beg
- godp: CORNO Pierre + THOMAS Marie
end
```

Testing

Run all unit tests:
bash
```sh
python run_all_tests.py
```
Run specific test files:
```sh

python test_parser.py
python test_date.py
python test_person.py
```

API Reference
GeneWebParser

    parse_file(filename: str) -> GeneWebData: Parse a .gw file

    parse_lines(lines: List[str]) -> GeneWebData: Parse from text lines

GeneWebData Properties

    families: List[Family]: All family definitions

    personal_notes: Dict[str, str]: Personal notes by person reference

    relations: List[Relation]: Special relationships

    personal_events: List[PersonalEvent]: Personal life events

    database_notes: str: Database presentation notes

    extended_pages: Dict[str, str]: Extended wiki pages

    wizard_notes: Dict[str, str]: Wizard administration notes

Supported GW Format Features

    Basic family structures

    Personal information with dates

    Marriage information with places and sources

    Children definitions

    Personal and family events (GWPlus)

    Special relationships (adoption, godparents)

    Personal and database notes

    Extended pages

    Wizard notes

    Encoding specification

    GWPlus format extensions