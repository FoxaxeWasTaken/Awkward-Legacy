Overview

The GeneWeb Diff Tool compares two genealogy databases and identifies differences between individuals and families. It builds upon the core classes from consang.py for data representation.
Core Dependencies
Shared Classes from consang.py

This tool reuses the core data structures from the consanguinity calculator:

    Person - Represents individuals (see consang.md for detailed documentation)

    Family - Represents family units (see consang.md for detailed documentation)

    GenealogyDataBuilder - Builds genealogy data from GW parser output (see consang.md for detailed documentation)

Usage Example:
```python

from consang import Person, Family, GenealogyDataBuilder

# Reuse the same data structures
builder = GenealogyDataBuilder()
builder.build_from_gw_parser(parser_result)
persons = builder.persons  # Dict[str, Person]
families = builder.families  # Dict[str, Family]

```
Diff-Specific Classes
DiffMessage Enum
Purpose: Defines the types of differences that can be detected between genealogy records.
```python

class DiffMessage(Enum):
    BAD_CHILD = 1           # Cannot isolate one child match
    BIRTH_DATE = 2          # Birth date difference
    BIRTH_PLACE = 3         # Birth place difference
    CHILD_MISSING = 4       # Child missing in target database
    CHILDREN = 5            # Multiple child matches
    DEATH_DATE = 6          # Death date difference  
    DEATH_PLACE = 7         # Death place difference
    DIVORCE = 8             # Divorce information difference
    FIRST_NAME = 9          # First name difference
    OCCUPATION = 10         # Occupation difference
    PARENTS_MISSING = 11    # Parents missing
    MARRIAGE_DATE = 12      # Marriage date difference
    MARRIAGE_PLACE = 13     # Marriage place difference
    SEX = 14                # Gender difference
    SPOUSE_MISSING = 15     # Spouse missing in target database
    SPOUSES = 16            # Multiple spouse matches
    SURNAME = 17            # Last name difference
```
ComparisonConfig Class

Purpose: Configuration settings for the diff operation.
```python

@dataclass
class ComparisonConfig:
    html: bool = False      # Output in HTML format
    root: str = ""          # Root path for HTML links
    d_mode: bool = False    # Check descendants mode
    ad_mode: bool = False   # Check descendants of all ascendants mode
```
Usage Example:
```python

config = ComparisonConfig(
    html=True,
    root="/genealogy/",
    d_mode=True
)
```
Main Diff Engine
GWDiff Class

Purpose: Core diff engine that performs comparison between two genealogy databases.
Initialization
```python

gwdiff = GWDiff(config)

```
Key Methods
person_string(person: Person) -> str
Formats a person's name for display, including occurrence number.
```python

person = Person("id1", "John", "Doe", "M", occ=0)
print(gwdiff.person_string(person))  # "John Doe"

person2 = Person("id2", "John", "Doe", "M", occ=1)  
print(gwdiff.person_string(person2)) # "John.1 Doe"

```
compatible_field(val1: Any, val2: Any) -> bool
Checks if two field values are compatible (case-insensitive comparison).
```python

gwdiff.compatible_field("John", "john")    # True
gwdiff.compatible_field("John", "Jane")    # False
gwdiff.compatible_field("", "anything")    # True (empty considered compatible)
```
compatible_persons_light(p1: Person, p2: Person) -> List
[DiffMessage]

Light comparison checking only names.
```python

p1 = Person("id1", "John", "Doe", "M")
p2 = Person("id2", "Jonathan", "Doe", "M")

messages = gwdiff.compatible_persons_light(p1, p2)
# Returns [DiffMessage.FIRST_NAME]

compatible_persons(p1: Person, p2: Person) -> List[DiffMessage]

Full comparison checking all person attributes.
python

p1 = Person("id1", "John", "Doe", "M", birth_date="1900")
p2 = Person("id2", "John", "Doe", "F", birth_date="1901")

messages = gwdiff.compatible_persons(p1, p2)
# Returns [DiffMessage.SEX, DiffMessage.BIRTH_DATE]
```
find_compatible_persons(target: Person, candidates: List[Person], light: bool = False) -> List[Person]

Finds persons compatible with the target from a candidate list.
```python

target = Person("t1", "John", "Doe", "M")
candidates = [
    Person("c1", "John", "Doe", "M"),      # Compatible
    Person("c2", "Jane", "Doe", "F"),      # Not compatible
    Person("c3", "John", "Smith", "M")     # Not compatible
]

compatible = gwdiff.find_compatible_persons(target, candidates, light=True)
# Returns [c1]
```
compare_databases(base1_data: Dict, base2_data: Dict, p1_id: str, p2_id: str)

Main comparison method that initiates the diff process.
```python

gwdiff.compare_databases(
    base1_data,  # {'persons': persons1, 'families': families1}
    base2_data,  # {'persons': persons2, 'families': families2} 
    "Doe John",  # Starting person ID in base1
    "Doe John"   # Starting person ID in base2
)

Recursive Comparison Methods
descendants_diff(p1: Person, p2: Person, base1_data: Dict, base2_data: Dict, visited: Set[Tuple[str, str]])

Recursively compares descendants of two persons, tracking visited pairs to avoid cycles.
_process_family_diff(p1: Person, p2: Person, fam1: Family, families2: List[Family], base1_data: Dict, base2_data: Dict, visited: Set[Tuple[str, str]])

Compares families between two persons, finding compatible spouse matches.
_process_child_diff(child1: Person, children2: List[Person], p1: Person, p2: Person, base1_data: Dict, base2_data: Dict, visited: Set[Tuple[str, str]])

Compares children between families, handling multiple match scenarios.
Utility Functions
```
find_person_by_key(base_data: Dict, first_name: str, last_name: str, occ: int) -> Optional[Person]

Finds a person by name and occurrence in the database.
```python

person = find_person_by_key(
    base_data,    # {'persons': persons_dict, 'families': families_dict}
    "John",       # First name
    "Doe",        # Last name  
    0             # Occurrence
)
```
Complete Workflow Example
```python

from gwdiff import GWDiff, ComparisonConfig, find_person_by_key
from consang import GenealogyDataBuilder
from gw_parser import GWParser

# Load and parse both databases
parser1 = GWParser("database1.gw")
parser2 = GWParser("database2.gw")

# Build data structures using shared GenealogyDataBuilder
builder1 = GenealogyDataBuilder()
builder2 = GenealogyDataBuilder()
builder1.build_from_gw_parser(parser1.parse())
builder2.build_from_gw_parser(parser2.parse())

base1_data = {'persons': builder1.persons, 'families': builder1.families}
base2_data = {'persons': builder2.persons, 'families': builder2.families}

# Find starting persons
person1 = find_person_by_key(base1_data, "John", "Doe", 0)
person2 = find_person_by_key(base2_data, "John", "Doe", 0)

# Configure and run diff
config = ComparisonConfig(html=False, d_mode=True)
gwdiff = GWDiff(config)

gwdiff.compare_databases(base1_data, base2_data, person1.id, person2.id)
```
Output Formats
Plain Text Output
```text

John Doe / John Doe
 first name
 death (status or date)
```
HTML Output
```html

<BODY>
<A HREF="/base1_w?i=Doe John" TARGET="base1">John Doe</A> / <A HREF="/base2_w?i=Doe John" TARGET="base2">John Doe</A><BR>
 first name<BR>
 death (status or date)<BR>
</BODY>
```
Integration with Other Tools

The diff tool can be integrated with other genealogy applications:
```python

from gwdiff import GWDiff, DiffMessage
from consang import GenealogyDataBuilder

class GenealogyQualityChecker:
    def __init__(self):
        self.gwdiff = GWDiff(ComparisonConfig())
    
    def check_data_quality(self, persons):
        """Check for internal consistency within a single database"""
        issues = []
        for person in persons.values():
            # Use diff comparison methods for quality checks
            if not person.first_name.strip():
                issues.append(f"Empty first name: {person.id}")
        return issues
```
Error Handling

The tool includes robust error handling for:

    Missing persons in either database

    Circular family relationships

    Invalid person references

    Malformed genealogy data

This modular design allows the diff functionality to be reused in other genealogy applications while maintaining consistency with the core data structures from consang.py.