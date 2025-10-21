Overview

The calculator uses a modular class structure that can be reused for other genealogy applications. Here's how each class works:
Core Data Classes
Person Class

Purpose: Represents an individual in the genealogy tree with all necessary attributes.
```python

@dataclass
class Person:
    id: str                    # Unique identifier (e.g., "Doe John")
    first_name: str           # First name
    last_name: str            # Last name  
    sex: str = "U"            # Gender: "M", "F", or "U" (unknown)
    occ: int = 0              # Occurrence number for same names (e.g., John.1, John.2)
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    father_id: Optional[str] = None    # Reference to father's ID
    mother_id: Optional[str] = None    # Reference to mother's ID
    families: List[str] = None         # List of family IDs where person appears

    def designation(self) -> str:
        return f"{self.first_name} {self.last_name}"
```
Usage Example:
```python

# Create a person
person = Person(
    id="Doe John",
    first_name="John",
    last_name="Doe", 
    sex="M",
    occ=0,
    father_id="Doe Robert",
    mother_id="Smith Mary"
)

# Get display name
print(person.designation())  # "John Doe"
```
Family Class

Purpose: Represents a family unit connecting spouses and their children.
```python

@dataclass  
class Family:
    id: str                          # Unique family ID (e.g., "F1")
    husband_id: Optional[str] = None # Reference to husband's Person ID
    wife_id: Optional[str] = None    # Reference to wife's Person ID  
    children: List[str] = None       # List of children Person IDs
```
Usage Example:
```python

# Create a family
family = Family(
    id="F1",
    husband_id="Doe John",
    wife_id="Smith Jane", 
    children=["Doe Bob", "Doe Alice"]
)
```
Data Builder Class
GenealogyDataBuilder Class

Purpose: Converts raw GeneWeb parser output into structured Person and Family objects.

Key Methods:
build_from_gw_parser(parser_result: Dict)

Main method that processes the entire GeneWeb data structure.
```python

builder = GenealogyDataBuilder()
builder.build_from_gw_parser(gw_parser_output)

# Access results
persons = builder.persons      # Dict[str, Person] 
families = builder.families    # Dict[str, Family]
```
_get_or_create_person(person_data: Dict, default_sex: str) -> str

Creates or retrieves a Person object from raw data, handling:

    Name parsing and occurrence extraction (e.g., "John.1" → first_name="John", occ=1)

    Sex determination from tags

    Unique ID generation

_process_family(family_data: Dict)

Processes a single family, creating:

    Husband and wife Person objects

    Child Person objects

    Family object linking them all

_link_families_and_persons()

Establishes parent-child relationships by setting father_id and mother_id on children.

Complete Usage Example:
```python

from gw_parser import GWParser
from consang import GenealogyDataBuilder

# Parse GeneWeb file
gw_parser = GWParser("family_tree.gw")
parser_result = gw_parser.parse()

# Build structured data
builder = GenealogyDataBuilder()
builder.build_from_gw_parser(parser_result)

# Access the genealogy data
persons = builder.persons
families = builder.families

# Find a specific person
john_doe = persons["Doe John"]
print(f"John's father: {persons[john_doe.father_id].designation()}")
```
Calculator Class
ConsanguinityCalculator Class

Purpose: Calculates consanguinity coefficients between individuals using ancestor analysis.

Key Methods:
build_parents_cache(persons: Dict[str, Person])

Precomputes parent relationships for efficient ancestor lookup.
get_ancestors(person_id: str) -> Set[str]

Returns all ancestors of a person (recursive up to 15 generations).
calculate_consanguinity(person1_id: str, person2_id: str) -> float

Computes consanguinity coefficient using the formula:
```text

coefficient = Σ (0.5)^(d1 + d2 + 1)
```
Where d1, d2 are generational distances from common ancestors.

Usage Example:
```python

calculator = ConsanguinityCalculator()
calculator.build_parents_cache(persons)

# Calculate consanguinity between two people
coef = calculator.calculate_consanguinity("Doe John", "Smith Jane")
print(f"Consanguinity coefficient: {coef}")
``` 
Application Class
ConsanguinityApp Class

Purpose: Main application class handling command-line interface and workflow.

Key Methods:
compute_consanguinity() -> Dict

Main workflow:

    Parses GeneWeb file

    Builds data structure

    Checks for genealogical loops

    Calculates all pairwise coefficients

    Returns results

check_for_cycles(persons, calculator)

Detects circular relationships that would break calculations.
Data Flow
```text

GeneWeb File (.gw)
    ↓
GWParser → Raw JSON
    ↓  
GenealogyDataBuilder → Persons & Families Dicts
    ↓
ConsanguinityCalculator → Coefficients
    ↓
ConsanguinityApp → Results & Reports
```
Reuse Patterns
For New Genealogy Applications

    Basic Person/Family Structure:

```python

from consang import Person, Family, GenealogyDataBuilder

# Reuse the data model for any genealogy app
builder = GenealogyDataBuilder()
builder.build_from_gw_parser(your_data)
```
    Ancestor Analysis:

```python

from consang import ConsanguinityCalculator

calculator = ConsanguinityCalculator()
calculator.build_parents_cache(persons)

# Find common ancestors
ancestors1 = calculator.get_ancestors("person1")
ancestors2 = calculator.get_ancestors("person2") 
common_ancestors = ancestors1.intersection(ancestors2)
```
    Family Relationship Queries:

```python

def get_siblings(person_id, families):
    siblings = []
    for family in families.values():
        if person_id in family.children:
            siblings.extend([c for c in family.children if c != person_id])
    return siblings
```
Integration Example
```python

from consang import GenealogyDataBuilder, ConsanguinityCalculator

class MyGenealogyApp:
    def __init__(self, gw_file):
        self.builder = GenealogyDataBuilder()
        self.calculator = ConsanguinityCalculator()
        self.load_data(gw_file)
    
    def load_data(self, gw_file):
        from gw_parser import GWParser
        parser_result = GWParser(gw_file).parse()
        self.builder.build_from_gw_parser(parser_result)
        self.calculator.build_parents_cache(self.builder.persons)
    
    def find_relations(self, person1_name, person2_name):
        # Your custom relationship logic using the shared classes
        pass
```
This modular design allows easy extension for other genealogy analyses like relationship finding, pedigree charts, or genetic inheritance patterns.

Limitations

    Maximum generational depth: 15 (configurable)

    Performance may vary with very large datasets

    Requires valid GeneWeb .gw file format