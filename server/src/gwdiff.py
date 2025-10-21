#!/usr/bin/env python3

import argparse
import sys
from typing import List, Dict, Any, Optional, Tuple, Set
from enum import Enum
from dataclasses import dataclass

# Import des classes depuis consang.py
try:
    from consang import Person, Family, GenealogyDataBuilder
except ImportError:
    # Fallback si consang.py n'est pas disponible
    @dataclass
    class Person:
        id: str
        first_name: str
        last_name: str
        sex: str = "U"
        occ: int = 0
        birth_date: Optional[str] = None
        death_date: Optional[str] = None
        father_id: Optional[str] = None
        mother_id: Optional[str] = None
        families: List[str] = None
        
        def __post_init__(self):
            self.families = self.families or []

    @dataclass
    class Family:
        id: str
        husband_id: Optional[str] = None
        wife_id: Optional[str] = None
        children: List[str] = None
        
        def __post_init__(self):
            self.children = self.children or []

    class GenealogyDataBuilder:
        def __init__(self):
            self.persons: Dict[str, Person] = {}
            self.families: Dict[str, Family] = {}
            self._counters = {'person': 0, 'family': 0}
            
        def build_from_gw_parser(self, parser_result: Dict) -> None:
            for family_data in parser_result.get("families", []):
                self._process_family(family_data)
            self._link_families()
        
        def _process_family(self, family_data: Dict) -> None:
            family_id = f"F{self._counters['family']}"
            self._counters['family'] += 1
            
            family = Family(id=family_id)
            
            # Process spouses
            for role, sex in [('husband', 'M'), ('wife', 'F')]:
                if person_data := family_data.get(role):
                    person_id = self._get_or_create_person(person_data, sex)
                    setattr(family, f'{role}_id', person_id)
                    self.persons[person_id].families.append(family_id)
            
            # Process children
            for child_data in family_data.get("children", []):
                if child_person := child_data.get("person"):
                    sex = self._get_child_sex(child_data)
                    child_id = self._get_or_create_person(child_person, sex)
                    family.children.append(child_id)
                    self.persons[child_id].families.append(family_id)
            
            self.families[family_id] = family
        
        def _get_or_create_person(self, person_data: Dict, sex: str) -> str:
            first_name = person_data.get("first_name", "").strip()
            last_name = person_data.get("last_name", "").strip()
            
            # Extract occurrence
            occ = 0
            if '.' in first_name:
                name_parts = first_name.split('.')
                if len(name_parts) > 1 and name_parts[1].isdigit():
                    first_name, occ = name_parts[0], int(name_parts[1])
            
            # Generate ID
            if first_name or last_name:
                person_id = f"{last_name} {first_name}.{occ}" if occ > 0 else f"{last_name} {first_name}"
            else:
                self._counters['person'] += 1
                person_id = f"UNKNOWN_{self._counters['person']}"
            
            # Create person if needed
            if person_id not in self.persons:
                self.persons[person_id] = Person(
                    id=person_id,
                    first_name=first_name.replace("_", " "),
                    last_name=last_name.replace("_", " "),
                    sex=person_data.get("sex") or sex,
                    occ=occ
                )
            
            return person_id
        
        def _get_child_sex(self, child_data: Dict) -> str:
            return {'male': 'M', 'female': 'F'}.get(child_data.get("gender", ""), 'U')
        
        def _link_families(self) -> None:
            """Link parents to children"""
            for family in self.families.values():
                for child_id in family.children:
                    if child := self.persons.get(child_id):
                        if family.husband_id:
                            child.father_id = family.husband_id
                        if family.wife_id:
                            child.mother_id = family.wife_id


class DiffMessage(Enum):
    """Difference message types"""
    BAD_CHILD = 1
    BIRTH_DATE = 2
    BIRTH_PLACE = 3
    CHILD_MISSING = 4
    CHILDREN = 5
    DEATH_DATE = 6
    DEATH_PLACE = 7
    DIVORCE = 8
    FIRST_NAME = 9
    OCCUPATION = 10
    PARENTS_MISSING = 11
    MARRIAGE_DATE = 12
    MARRIAGE_PLACE = 13
    SEX = 14
    SPOUSE_MISSING = 15
    SPOUSES = 16
    SURNAME = 17


@dataclass
class ComparisonConfig:
    """Comparison configuration"""
    html: bool = False
    root: str = ""
    d_mode: bool = False
    ad_mode: bool = False


class GWDiff:
    """GeneWeb diff tool"""
    
    def __init__(self, config: ComparisonConfig):
        self.config = config
        self.cr = "<BR>\n" if config.html else "\n"
        self._message_strings = {
            DiffMessage.BAD_CHILD: "can not isolate one child match: {}",
            DiffMessage.BIRTH_DATE: "birth date",
            DiffMessage.BIRTH_PLACE: "birth place", 
            DiffMessage.CHILD_MISSING: "child missing: {}",
            DiffMessage.CHILDREN: "more than one child match: {}",
            DiffMessage.DEATH_DATE: "death (status or date)",
            DiffMessage.DEATH_PLACE: "death place",
            DiffMessage.DIVORCE: "divorce",
            DiffMessage.FIRST_NAME: "first name",
            DiffMessage.OCCUPATION: "occupation",
            DiffMessage.PARENTS_MISSING: "parents missing",
            DiffMessage.MARRIAGE_DATE: "marriage date",
            DiffMessage.MARRIAGE_PLACE: "marriage place",
            DiffMessage.SEX: "sex",
            DiffMessage.SPOUSE_MISSING: "spouse missing: {}",
            DiffMessage.SPOUSES: "more than one spouse match: {}",
            DiffMessage.SURNAME: "surname"
        }
    
    def person_string(self, person: Person) -> str:
        """Get person display string"""
        if person.occ > 0:
            return f"{person.first_name}.{person.occ} {person.last_name}"
        return f"{person.first_name} {person.last_name}"
    
    def person_link(self, person: Person, bname: str, target: str) -> str:
        """Get person link (HTML or plain)"""
        if self.config.html:
            return f'<A HREF="{self.config.root}{bname}_w?i={person.id}" TARGET="{target}">{self.person_string(person)}</A>'
        return self.person_string(person)
    
    def print_message(self, base_name: str, person: Person, msg: DiffMessage, target: Person = None):
        """Print a difference message"""
        msg_str = self._message_strings[msg]
        if target and "{}" in msg_str:
            print(f" {msg_str.format(self.person_link(target, base_name, 'base1'))}{self.cr}", end="")
        else:
            print(f" {msg_str}{self.cr}", end="")
    
    def compatible_field(self, val1: Any, val2: Any) -> bool:
        """Check if fields are compatible"""
        if not val1:
            return True
        return bool(val2) and str(val1).lower() == str(val2).lower()
    
    def compatible_persons_light(self, p1: Person, p2: Person) -> List[DiffMessage]:
        """Light person comparison"""
        messages = []
        if not self.compatible_field(p1.first_name, p2.first_name):
            messages.append(DiffMessage.FIRST_NAME)
        if not self.compatible_field(p1.last_name, p2.last_name):
            messages.append(DiffMessage.SURNAME)
        return messages
    
    def compatible_persons(self, p1: Person, p2: Person) -> List[DiffMessage]:
        """Full person comparison"""
        messages = self.compatible_persons_light(p1, p2)
        
        if p1.sex != p2.sex:
            messages.append(DiffMessage.SEX)
        if not self.compatible_field(p1.birth_date, p2.birth_date):
            messages.append(DiffMessage.BIRTH_DATE)
        if not self.compatible_field(p1.death_date, p2.death_date):
            messages.append(DiffMessage.DEATH_DATE)
            
        return messages
    
    def find_compatible_persons(self, target: Person, candidates: List[Person], light: bool = False) -> List[Person]:
        """Find compatible persons"""
        compare_func = self.compatible_persons_light if light else self.compatible_persons
        return [p for p in candidates if not compare_func(target, p)]
    
    def person_diff(self, p1: Person, p2: Person, base1_data: Dict):
        """Compare and print person differences"""
        if messages := self.compatible_persons(p1, p2):
            print(f"{self.person_link(p1, 'base1', 'base1')} / {self.person_link(p2, 'base2', 'base2')}{self.cr}", end="")
            for msg in messages:
                self.print_message('base1', p1, msg)

    def descendants_diff(self, p1: Person, p2: Person, base1_data: Dict, base2_data: Dict, visited: Set[Tuple[str, str]]):
        """Compare descendants recursively - FIXED VERSION"""
        if (p1.id, p2.id) in visited:
            return
        visited.add((p1.id, p2.id))
        
        self.person_diff(p1, p2, base1_data)
        
        # Get families where they are spouses (only valid families)
        families1 = []
        for f in base1_data['families'].values():
            if p1.id in (f.husband_id, f.wife_id):
                # Vérifier que le conjoint existe et a un nom
                spouse_id = f.wife_id if p1.id == f.husband_id else f.husband_id
                spouse = base1_data['persons'].get(spouse_id)
                if spouse and spouse.first_name.strip():
                    families1.append(f)
        
        families2 = []
        for f in base2_data['families'].values():
            if p2.id in (f.husband_id, f.wife_id):
                spouse_id = f.wife_id if p2.id == f.husband_id else f.husband_id
                spouse = base2_data['persons'].get(spouse_id)
                if spouse and spouse.first_name.strip():
                    families2.append(f)
        
        for fam1 in families1:
            self._process_family_diff(p1, p2, fam1, families2, base1_data, base2_data, visited)

    def _process_family_diff(self, p1: Person, p2: Person, fam1: Family, families2: List[Family], 
                           base1_data: Dict, base2_data: Dict, visited: Set[Tuple[str, str]]):
        """Process family differences - FIXED VERSION"""
        # Find compatible families
        compatible_fams = []
        for fam2 in families2:
            spouse1_id = fam1.wife_id if p1.id == fam1.husband_id else fam1.husband_id
            spouse2_id = fam2.wife_id if p2.id == fam2.husband_id else fam2.husband_id
            
            # Check if spouses exist
            spouse1 = base1_data['persons'].get(spouse1_id)
            spouse2 = base2_data['persons'].get(spouse2_id)
            
            if not spouse1 or not spouse2:
                continue 
            if not spouse1.first_name.strip() or not spouse2.first_name.strip():
                continue
            if not self.compatible_persons_light(spouse1, spouse2):
                compatible_fams.append(fam2)
        
        if len(compatible_fams) == 1:
            fam2 = compatible_fams[0]
            
            # Compare spouses
            spouse1_id = fam1.wife_id if p1.id == fam1.husband_id else fam1.husband_id
            spouse2_id = fam2.wife_id if p2.id == fam2.husband_id else fam2.husband_id
            spouse1 = base1_data['persons'][spouse1_id]
            spouse2 = base2_data['persons'][spouse2_id]
            
            self.person_diff(spouse1, spouse2, base1_data)
            
            # Compare children (with valid names)
            children1 = [base1_data['persons'][cid] for cid in fam1.children 
                        if cid in base1_data['persons'] and base1_data['persons'][cid].first_name.strip()]
            children2 = [base2_data['persons'][cid] for cid in fam2.children 
                        if cid in base2_data['persons'] and base2_data['persons'][cid].first_name.strip()]
            
            for child1 in children1:
                self._process_child_diff(child1, children2, p1, p2, base1_data, base2_data, visited)
                
        elif not compatible_fams:
            spouse_id = fam1.wife_id if p1.id == fam1.husband_id else fam1.husband_id
            if spouse_id in base1_data['persons']:
                spouse = base1_data['persons'][spouse_id]
                if spouse.first_name.strip():  # Only report if spouse has a name
                    self.print_message('base1', p1, DiffMessage.SPOUSE_MISSING, spouse)
        else:
            spouse_id = fam1.wife_id if p1.id == fam1.husband_id else fam1.husband_id
            if spouse_id in base1_data['persons']:
                spouse = base1_data['persons'][spouse_id]
                if spouse.first_name.strip():  # Only report if spouse has a name
                    self.print_message('base1', p1, DiffMessage.SPOUSES, spouse)

    def _process_child_diff(self, child1: Person, children2: List[Person], p1: Person, p2: Person,
                          base1_data: Dict, base2_data: Dict, visited: Set[Tuple[str, str]]):
        """Process child differences"""
        # Filter les valid children in
        valid_children2 = [c for c in children2 if c.first_name.strip()]
        
        compatible = self.find_compatible_persons(child1, valid_children2, light=True)
        
        if not compatible:
            self.print_message('base1', p1, DiffMessage.CHILD_MISSING, child1)
        elif len(compatible) == 1:
            self.descendants_diff(child1, compatible[0], base1_data, base2_data, visited)
        else:
            compatible_full = self.find_compatible_persons(child1, compatible)
            if len(compatible_full) == 1:
                self.descendants_diff(child1, compatible_full[0], base1_data, base2_data, visited)
            elif not compatible_full:
                self.print_message('base1', p1, DiffMessage.BAD_CHILD, child1)
            else:
                self.print_message('base1', p1, DiffMessage.CHILDREN, child1)

    def compare_databases(self, base1_data: Dict, base2_data: Dict, p1_id: str, p2_id: str):
        """Main comparison function"""
        p1, p2 = base1_data['persons'][p1_id], base2_data['persons'][p2_id]
        visited = set()
        
        if self.config.ad_mode:
            print("Ancestor mode not fully implemented")
        
        self.descendants_diff(p1, p2, base1_data, base2_data, visited)


def find_person_by_key(base_data: Dict, first_name: str, last_name: str, occ: int) -> Optional[Person]:
    """Find person by key"""
    search_fn = first_name.replace("_", " ").strip()
    search_ln = last_name.replace("_", " ").strip()
    
    for person in base_data['persons'].values():
        # check matching name 
        if (person.first_name == search_ln and 
            person.last_name == search_fn and 
            person.occ == occ):
            return person
    
    for person in base_data['persons'].values():
        if (person.first_name == search_fn and 
            person.last_name == search_ln and 
            person.occ == occ):
            return person
    
    return None


def main():
    parser = argparse.ArgumentParser(description='GeneWeb Database Diff Tool')
    parser.add_argument('base1', help='Reference database file')
    parser.add_argument('base2', help='Destination database file')
    parser.add_argument('-1', '--person1', nargs=3, required=True, metavar=('FN', 'OCC', 'LN'), help='Person in base1')
    parser.add_argument('-2', '--person2', nargs=3, required=True, metavar=('FN', 'OCC', 'LN'), help='Person in base2')
    parser.add_argument('-d', action='store_true', help='Check descendants')
    parser.add_argument('-ad', action='store_true', help='Check descendants of all ascendants')
    parser.add_argument('-html', metavar='ROOT', help='HTML format')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    
    args = parser.parse_args()
    
    # DEBUG: Shows args
    if args.debug:
        print(f"DEBUG: Base1: {args.base1}", file=sys.stderr)
        print(f"DEBUG: Base2: {args.base2}", file=sys.stderr)
        print(f"DEBUG: Person1: {args.person1}", file=sys.stderr)
        print(f"DEBUG: Person2: {args.person2}", file=sys.stderr)
    
    # Load and parse databases
    base1_data_raw = GWParser(args.base1).parse()
    base2_data_raw = GWParser(args.base2).parse()
    
    if args.debug:
        print(f"DEBUG: Base1 raw - familles: {len(base1_data_raw.get('families', []))}", file=sys.stderr)
        print(f"DEBUG: Base2 raw - familles: {len(base2_data_raw.get('families', []))}", file=sys.stderr)
    
    # Build data structures
    builder1, builder2 = GenealogyDataBuilder(), GenealogyDataBuilder()
    builder1.build_from_gw_parser(base1_data_raw)
    builder2.build_from_gw_parser(base2_data_raw)
    
    base1_data = {'persons': builder1.persons, 'families': builder1.families}
    base2_data = {'persons': builder2.persons, 'families': builder2.families}
    
    if args.debug:
        print(f"DEBUG: Base1 processed - persons: {len(base1_data['persons'])}, familles: {len(base1_data['families'])}", file=sys.stderr)
        print(f"DEBUG: Base2 processed - persons: {len(base2_data['persons'])}, familles: {len(base2_data['families'])}", file=sys.stderr)
        print(f"DEBUG: Persons base1:", file=sys.stderr)
        for i, (pid, person) in enumerate(list(base1_data['persons'].items())[:5]):
            print(f"DEBUG:   {pid}: {person.first_name} {person.last_name} (occ={person.occ})", file=sys.stderr)
    
    # Find starting persons
    p1_fn, p1_occ, p1_sn = args.person1
    p2_fn, p2_occ, p2_sn = args.person2
    
    person1 = find_person_by_key(base1_data, p1_fn, p1_sn, int(p1_occ))
    person2 = find_person_by_key(base2_data, p2_fn, p2_sn, int(p2_occ))
    
    if args.debug:
        print(f"DEBUG: found Person1 : {person1}", file=sys.stderr)
        print(f"DEBUG: found Person2 : {person2}", file=sys.stderr)
    
    if not person1 or not person2:
        print(f"ERROR: Cannot find specified persons", file=sys.stderr)
        print(f"Person1: {p1_fn} {p1_sn}.{p1_occ} -> {person1}", file=sys.stderr)
        print(f"Person2: {p2_fn} {p2_sn}.{p2_occ} -> {person2}", file=sys.stderr)
        sys.exit(1)
    
    # Run comparison
    config = ComparisonConfig(html=bool(args.html), root=args.html or "", d_mode=args.d, ad_mode=args.ad)
    
    if config.html:
        print("<BODY>")
    
    if args.debug:
        print(f"DEBUG: comparing...", file=sys.stderr)
    
    GWDiff(config).compare_databases(base1_data, base2_data, person1.id, person2.id)
    
    if config.html:
        print("</BODY>")


if __name__ == '__main__':
    main()