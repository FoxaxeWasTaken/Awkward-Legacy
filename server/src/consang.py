#!/usr/bin/env python3
"""
Consanguinity Calculator
"""

import sys
import os
import argparse
import signal
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from uuid import UUID


@dataclass
class Person:
    """Represents a person in the genealogy tree with database compatibility"""
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
        if self.families is None:
            self.families = []

    def designation(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @classmethod
    def from_db_person(cls, db_person) -> 'Person':
        """Create Person instance from database Person model"""
        return cls(
            id=str(db_person.id),
            first_name=db_person.first_name or "",
            last_name=db_person.last_name or "",
            sex=db_person.sex or "U",
            occ=0,
            birth_date=db_person.birth_date.isoformat() if db_person.birth_date else None,
            death_date=db_person.death_date.isoformat() if db_person.death_date else None,
            families=[]
        )


@dataclass
class Family:
    """Represents a family unit"""
    id: str
    husband_id: Optional[str] = None
    wife_id: Optional[str] = None
    children: List[str] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []


class GenealogyDataBuilder:
    """Builds genealogy data structure from GW parser output OR database"""
    
    def __init__(self):
        self.persons: Dict[str, Person] = {}
        self.families: Dict[str, Family] = {}
        self._person_counter = 0
        self._family_counter = 0
        
    def build_from_gw_parser(self, parser_result: Dict) -> None:
        """Build from GeneWeb parser output"""
        self._process_families(parser_result.get("families", []))
        self._link_families_and_persons()
    
    def build_from_database(self, db_session, starting_person_id: UUID = None) -> None:
        """
        Build genealogy data from database starting from a specific person.
        
        Args:
            db_session: SQLModel database session
            starting_person_id: Optional UUID to build tree from specific person
        """
        if starting_person_id:
            self._build_from_person(db_session, starting_person_id)
        else:
            self._build_complete_database(db_session)
    
    def _build_from_person(self, db_session, person_id: UUID) -> None:
        """Build genealogy tree starting from a specific person (recursive)"""
        # Avoid infinite recursion
        if str(person_id) in self.persons:
            return
            
        # Get person from database - CORRECTION: utiliser getattr pour éviter ImportError
        try:
            db_person = db_session.get(person_id)  # Supposons que db_session.get fonctionne directement
            if not db_person:
                return
        except Exception:
            # Si la session ne peut pas récupérer la personne, on abandonne
            return
            
        # Convert to our Person class - CORRECTION: utiliser les attributs directement
        try:
            person = Person(
                id=str(db_person.id),
                first_name=getattr(db_person, 'first_name', '') or '',
                last_name=getattr(db_person, 'last_name', '') or '',
                sex=getattr(db_person, 'sex', 'U') or 'U',
                occ=0
            )
            
            # Gérer les dates
            birth_date = getattr(db_person, 'birth_date', None)
            death_date = getattr(db_person, 'death_date', None)
            if birth_date:
                person.birth_date = birth_date.isoformat() if hasattr(birth_date, 'isoformat') else str(birth_date)
            if death_date:
                person.death_date = death_date.isoformat() if hasattr(death_date, 'isoformat') else str(death_date)
                
        except AttributeError:
            # Si les attributs nécessaires ne sont pas présents
            return
        
        self.persons[person.id] = person
        
        # Get person's families (as spouse) - CORRECTION: simplifier sans FamilyCRUD
        try:
            # Essayer de récupérer les familles via des méthodes directes
            if hasattr(db_person, 'families_as_spouse'):
                families_as_spouse = db_person.families_as_spouse
            elif hasattr(db_person, 'families'):
                families_as_spouse = db_person.families
            else:
                families_as_spouse = []
                
            for db_family in families_as_spouse:
                self._process_db_family(db_session, db_family)
        except (AttributeError, ImportError):
            # Si on ne peut pas récupérer les familles, continuer sans
            pass
            
        # Recursively process parents - CORRECTION: utiliser getattr
        father_id = getattr(db_person, 'father_id', None)
        mother_id = getattr(db_person, 'mother_id', None)
        
        if father_id:
            self._build_from_person(db_session, father_id)
            person.father_id = str(father_id)
            
        if mother_id:
            self._build_from_person(db_session, mother_id)
            person.mother_id = str(mother_id)
    
    def _build_complete_database(self, db_session) -> None:
        """Build complete genealogy data from all database records"""
        try:
            from models.person import Person as DBPerson
            from models.family import Family as DBFamily
            from sqlmodel import select
        except ImportError:
            # Database models not available
            return
        
        # Get all persons
        db_persons = db_session.exec(select(DBPerson)).all()
        for db_person in db_persons:
            person = Person.from_db_person(db_person)
            self.persons[person.id] = person
            
            # Set parent relationships
            if db_person.father_id:
                person.father_id = str(db_person.father_id)
            if db_person.mother_id:
                person.mother_id = str(db_person.mother_id)
        
        # Get all families and process them
        db_families = db_session.exec(select(DBFamily)).all()
        for db_family in db_families:
            self._process_db_family(db_session, db_family)
    
    def _process_db_family(self, db_session, db_family) -> None:
        """Process a database family and create Family object"""
        family_id = f"F{self._family_counter}"
        self._family_counter += 1
        
        family = Family(id=family_id)
        
        # Set spouses
        if db_family.husband_id:
            family.husband_id = str(db_family.husband_id)
            if family.husband_id in self.persons:
                self.persons[family.husband_id].families.append(family_id)
        
        if db_family.wife_id:
            family.wife_id = str(db_family.wife_id)
            if family.wife_id in self.persons:
                self.persons[family.wife_id].families.append(family_id)
        
        # Process children
        for child_relation in db_family.children:
            child_id = str(child_relation.child_id)
            family.children.append(child_id)
            
            if child_id in self.persons:
                self.persons[child_id].families.append(family_id)
                # Set parent relationships
                self.persons[child_id].father_id = family.husband_id
                self.persons[child_id].mother_id = family.wife_id
        
        self.families[family_id] = family
        
    def _process_families(self, families_data: List[Dict]) -> None:
        for family_data in families_data:
            self._process_family(family_data)
    
    def _process_family(self, family_data: Dict) -> None:
        family_id = f"F{self._family_counter}"
        self._family_counter += 1
        
        family = Family(id=family_id)
        
        # Process husband
        if "husband" in family_data and family_data["husband"]:
            husband_data = family_data["husband"]
            husband_id = self._get_or_create_person(husband_data, "M")
            family.husband_id = husband_id
            self.persons[husband_id].families.append(family_id)
        
        # Process wife
        if "wife" in family_data and family_data["wife"]:
            wife_data = family_data["wife"]
            wife_id = self._get_or_create_person(wife_data, "F")
            family.wife_id = wife_id
            self.persons[wife_id].families.append(family_id)
        
        # Process children
        if "children" in family_data:
            for child_data in family_data["children"]:
                if "person" in child_data and child_data["person"]:
                    child_person_data = child_data["person"]
                    sex = self._determine_child_sex(child_data)
                    child_id = self._get_or_create_person(child_person_data, sex)
                    family.children.append(child_id)
                    self.persons[child_id].families.append(family_id)
        
        self.families[family_id] = family
    
    def _get_or_create_person(self, person_data: Dict, default_sex: str = "U") -> str:
        first_name = person_data.get("first_name", "").strip()
        last_name = person_data.get("last_name", "").strip()
        
        # Extract occurrence
        occ = 0
        if '.' in first_name:
            name_parts = first_name.split('.')
            if len(name_parts) > 1 and name_parts[1].isdigit():
                first_name, occ = name_parts[0], int(name_parts[1])
        
        # Generate unique ID
        if first_name or last_name:
            person_id = f"{last_name} {first_name}".strip()
            if occ > 0:
                person_id = f"{last_name} {first_name}.{occ}"
        else:
            self._person_counter += 1
            person_id = f"UNKNOWN_{self._person_counter}"
        
        # Create person if doesn't exist
        if person_id not in self.persons:
            sex = self._determine_sex(person_data, default_sex)
            
            person = Person(
                id=person_id,
                first_name=first_name.replace("_", " "),
                last_name=last_name.replace("_", " "),
                sex=sex,
                occ=occ
            )
            
            self.persons[person_id] = person
        
        return person_id
    
    def _determine_sex(self, person_data: Dict, default_sex: str) -> str:
        sex = person_data.get("sex", "")
        if sex in ["M", "male"]:
            return "M"
        elif sex in ["F", "female"]:
            return "F"
        else:
            return default_sex
    
    def _determine_child_sex(self, child_data: Dict) -> str:
        gender = child_data.get("gender", "")
        if gender == "male":
            return "M"
        elif gender == "female":
            return "F"
        else:
            return "U"
    
    def _link_families_and_persons(self) -> None:
        """Establish parent-child relationships"""
        for family in self.families.values():
            for child_id in family.children:
                if child_id in self.persons:
                    child = self.persons[child_id]
                    if family.husband_id:
                        child.father_id = family.husband_id
                    if family.wife_id:
                        child.mother_id = family.wife_id


class ConsanguinityCalculator:
    """Calculates consanguinity coefficients"""
    
    def __init__(self):
        self.ancestors_cache: Dict[str, Set[str]] = {}
        self.consanguinity_cache: Dict[Tuple[str, str], float] = {}
        self.parents_cache: Dict[str, Tuple[Optional[str], Optional[str]]] = {}

    def build_parents_cache(self, persons: Dict[str, Person]) -> None:
        for person_id, person in persons.items():
            self.parents_cache[person_id] = (person.father_id, person.mother_id)

    def get_ancestors(self, person_id: str, depth: int = 0, max_depth: int = 15) -> Set[str]:
        if depth > max_depth or person_id not in self.parents_cache:
            return set()
            
        if person_id in self.ancestors_cache:
            return self.ancestors_cache[person_id]
            
        ancestors = set()
        father_id, mother_id = self.parents_cache[person_id]
        
        if father_id:
            ancestors.add(father_id)
            ancestors.update(self.get_ancestors(father_id, depth + 1, max_depth))
        if mother_id:
            ancestors.add(mother_id) 
            ancestors.update(self.get_ancestors(mother_id, depth + 1, max_depth))
            
        self.ancestors_cache[person_id] = ancestors
        return ancestors

    def calculate_consanguinity(self, person1_id: str, person2_id: str) -> float:
        if person1_id == person2_id:
            return 0.0
            
        cache_key = (min(person1_id, person2_id), max(person1_id, person2_id))
        if cache_key in self.consanguinity_cache:
            return self.consanguinity_cache[cache_key]
            
        ancestors1 = self.get_ancestors(person1_id)
        ancestors2 = self.get_ancestors(person2_id)
        common_ancestors = ancestors1.intersection(ancestors2)
        
        coefficient = 0.0
        
        for ancestor_id in common_ancestors:
            dist1 = self._calculate_generational_distance(person1_id, ancestor_id)
            dist2 = self._calculate_generational_distance(person2_id, ancestor_id)
            
            if dist1 is not None and dist2 is not None:
                coefficient += (0.5) ** (dist1 + dist2 + 1)
        
        self.consanguinity_cache[cache_key] = coefficient
        return coefficient

    def _calculate_generational_distance(self, descendant_id: str, ancestor_id: str,
                                      current_dist: int = 0, max_depth: int = 15) -> Optional[int]:
        if current_dist > max_depth or descendant_id not in self.parents_cache:
            return None
            
        if descendant_id == ancestor_id:
            return current_dist
            
        father_id, mother_id = self.parents_cache[descendant_id]
        
        dist_via_father = None
        dist_via_mother = None
        
        if father_id:
            dist_via_father = self._calculate_generational_distance(
                father_id, ancestor_id, current_dist + 1, max_depth
            )
        if mother_id:
            dist_via_mother = self._calculate_generational_distance(
                mother_id, ancestor_id, current_dist + 1, max_depth
            )
        
        if dist_via_father is not None and dist_via_mother is not None:
            return min(dist_via_father, dist_via_mother)
        elif dist_via_father is not None:
            return dist_via_father
        else:
            return dist_via_mother


class TopologicalSortError(Exception):
    def __init__(self, person: Person):
        self.person = person
        super().__init__(f"Genealogical loop detected: {person.designation()} is their own ancestor")


class ConsanguinityApp:
    """Main application class with database support"""
    
    def __init__(self):
        self.filename = ""
        self.db_session = None
        self.starting_person_id = None
        self.verbosity = 2
        self.output_file = None
        
    def setup_database(self, db_session, starting_person_id: UUID = None):
        """Configure database connection for consanguinity calculation"""
        self.db_session = db_session
        self.starting_person_id = starting_person_id
        
    def parse_arguments(self) -> None:
        parser = argparse.ArgumentParser(
            description="Calculate consanguinity coefficients in GeneWeb .gw database"
        )
        
        parser.add_argument(
            "-q", "--quiet",
            action="store_true",
            help="Quiet mode"
        )
        parser.add_argument(
            "-qq", "--very-quiet", 
            action="store_true",
            help="Very quiet mode"
        )
        parser.add_argument(
            "-v", "--verbose",
            action="store_true", 
            help="Verbose mode"
        )
        parser.add_argument(
            "-o", "--output",
            type=str,
            help="Output file for detailed results"
        )
        parser.add_argument(
            "filename",
            nargs="?",
            help="GeneWeb .gw database file (optional if using database)"
        )
        
        args = parser.parse_args()
        
        if args.very_quiet:
            self.verbosity = 0
        elif args.quiet:
            self.verbosity = 1
        elif args.verbose:
            self.verbosity = 3
            
        self.filename = args.filename
        self.output_file = args.output

    def validate_arguments(self) -> None:
        if self.filename and not os.path.exists(self.filename):
            print(f"Error: File {self.filename} does not exist", file=sys.stderr)
            sys.exit(2)

    def setup_signal_handlers(self) -> None:
        def signal_handler(signum, frame):
            print("\nCalculation interrupted by user")
            sys.exit(1)
            
        signal.signal(signal.SIGINT, signal_handler)

    def check_for_cycles(self, persons: Dict[str, Person], calculator: ConsanguinityCalculator) -> None:
        visited: Set[str] = set()
        recursion_stack: Set[str] = set()
        
        def visit(person_id: str) -> None:
            if person_id in recursion_stack:
                raise TopologicalSortError(persons[person_id])
            if person_id in visited:
                return
                
            visited.add(person_id)
            recursion_stack.add(person_id)
            
            father_id, mother_id = calculator.parents_cache.get(person_id, (None, None))
            if father_id and father_id in persons:
                visit(father_id)
            if mother_id and mother_id in persons:
                visit(mother_id)
                
            recursion_stack.remove(person_id)
        
        for person_id in persons:
            if person_id not in visited:
                visit(person_id)

    def compute_consanguinity(self) -> Dict[str, Any]:
        """Compute consanguinity from GeneWeb file"""
        if not self.filename:
            raise ValueError("No filename provided and no database configured")
            
        if self.verbosity > 0:
            print("Loading and parsing .gw file...")
        
        try:
            from gw_parser import GWParser
        except ImportError:
            print("Error: gw_parser module required", file=sys.stderr)
            sys.exit(1)
        
        gw_parser = GWParser(self.filename)
        parser_result = gw_parser.parse()
        
        data_builder = GenealogyDataBuilder()
        data_builder.build_from_gw_parser(parser_result)
        
        return self._compute_with_data_builder(data_builder)
    
    def compute_consanguinity_from_database(self) -> Dict[str, Any]:
        """Compute consanguinity coefficients from database records"""
        if not self.db_session:
            raise ValueError("Database session not configured. Call setup_database() first.")
            
        if self.verbosity > 0:
            print("Loading genealogy data from database...")
        
        data_builder = GenealogyDataBuilder()
        
        if self.starting_person_id:
            data_builder.build_from_database(self.db_session, self.starting_person_id)
            if self.verbosity > 0:
                print(f"Built tree starting from person {self.starting_person_id}")
        else:
            data_builder.build_from_database(self.db_session)
            
        return self._compute_with_data_builder(data_builder)
    
    def _compute_with_data_builder(self, data_builder: GenealogyDataBuilder) -> Dict[str, Any]:
        """Common computation logic for both file and database sources"""
        persons = data_builder.persons
        families = data_builder.families
        
        if self.verbosity > 0:
            print(f"Data loaded: {len(persons)} persons, {len(families)} families")
        
        calculator = ConsanguinityCalculator()
        calculator.build_parents_cache(persons)
        
        try:
            if self.verbosity > 0:
                print("Checking for genealogical loops...")
            self.check_for_cycles(persons, calculator)
        except TopologicalSortError as e:
            print(f"\nError: {e}")
            return {"error": str(e), "changes_made": False}
        
        if self.verbosity > 0:
            print("Calculating consanguinity coefficients...")
        
        person_ids = list(persons.keys())
        significant_relations = []
        changes_made = False
        
        for i, person1_id in enumerate(person_ids):
            if self.verbosity == 1 and i % 100 == 0:
                print(f"Progress: {i}/{len(person_ids)} persons")
            elif self.verbosity > 1 and i % 50 == 0:
                print(f"Progress: {i}/{len(person_ids)} persons")
                
            for person2_id in person_ids[i+1:]:
                coefficient = calculator.calculate_consanguinity(person1_id, person2_id)
                
                if coefficient > 0.0001:
                    person1 = persons[person1_id]
                    person2 = persons[person2_id]
                    
                    relation_info = {
                        "person1": person1.designation(),
                        "person2": person2.designation(),
                        "person1_id": person1_id,
                        "person2_id": person2_id,
                        "coefficient": coefficient,
                        "percentage": coefficient * 100
                    }
                    significant_relations.append(relation_info)
                    changes_made = True
        
        significant_relations.sort(key=lambda x: x["coefficient"], reverse=True)
        
        if self.verbosity > 0:
            print(f"\nCalculation complete - {len(significant_relations)} significant consanguinity relations found")
            
            if significant_relations:
                print("\nTop 10 most consanguineous relations:")
                for i, rel in enumerate(significant_relations[:10]):
                    print(f"  {i+1}. {rel['person1']} - {rel['person2']}: {rel['coefficient']:.6f} ({rel['percentage']:.4f}%)")
        
        if self.output_file:
            self._save_detailed_results(significant_relations, persons, families)
        
        return {
            "changes_made": changes_made,
            "total_relations": len(significant_relations),
            "significant_relations": significant_relations,
            "person_count": len(persons),
            "family_count": len(families)
        }

    def _save_detailed_results(self, relations: List[Dict], persons: Dict[str, Person], families: Dict[str, Family]) -> None:
        import datetime
        
        results = {
            "metadata": {
                "total_persons": len(persons),
                "total_families": len(families),
                "total_relations": len(relations),
                "calculation_date": str(datetime.datetime.now())
            },
            "relations": relations
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        if self.verbosity > 0:
            print(f"Detailed results saved to: {self.output_file}")

    def run(self) -> None:
        """Main entry point for command-line usage"""
        self.parse_arguments()
        
        if self.filename:
            self.validate_arguments()
            self.setup_signal_handlers()
            
            try:
                result = self.compute_consanguinity()
                self._handle_result(result)
            except KeyboardInterrupt:
                print("\nCalculation interrupted by user")
                sys.exit(1)
            except Exception as e:
                print(f"Error during calculation: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
                sys.exit(2)
        else:
            print("Error: No filename provided", file=sys.stderr)
            sys.exit(1)
    
    def _handle_result(self, result: Dict[str, Any]) -> None:
        """Handle computation result"""
        if result.get("changes_made", False):
            if self.verbosity > 0:
                print("Consanguinity calculation completed successfully")
        else:
            if self.verbosity > 0:
                print("No significant consanguinity detected")


# Utility functions for database integration - SANS VARIABLES GLOBALES
def _get_family_crud():
    """Get family_crud instance without global variable"""
    try:
        from crud.family import family_crud
        return family_crud
    except ImportError:
        return None

def analyze_family_consanguinity(db_session, family_id: UUID):
    """Analyze consanguinity within a specific family using FamilyCRUD"""
    family_crud = _get_family_crud()
    if family_crud is None:
        return None
        
    # Get family details using FamilyCRUD
    family_detail = family_crud.get_family_detail(db_session, family_id)
    if not family_detail:
        return None
    
    builder = GenealogyDataBuilder()
    
    # Build genealogy data focusing on this family
    if family_detail.husband_id:
        builder.build_from_database(db_session, family_detail.husband_id)
    if family_detail.wife_id:
        builder.build_from_database(db_session, family_detail.wife_id)
    
    calculator = ConsanguinityCalculator()
    calculator.build_parents_cache(builder.persons)
    
    # Calculate consanguinity between spouses
    if family_detail.husband_id and family_detail.wife_id:
        husband_id = str(family_detail.husband_id)
        wife_id = str(family_detail.wife_id)
        coefficient = calculator.calculate_consanguinity(husband_id, wife_id)
        
        return {
            "family_id": family_id,
            "husband": family_detail.husband["first_name"] + " " + family_detail.husband["last_name"],
            "wife": family_detail.wife["first_name"] + " " + family_detail.wife["last_name"],
            "consanguinity_coefficient": coefficient,
            "children_count": len(family_detail.children)
        }
    
    return None


def batch_consanguinity_analysis(db_session, search_query: str = None, limit: int = 50):
    """Perform consanguinity analysis on multiple families using FamilyCRUD search"""
    family_crud = _get_family_crud()
    if family_crud is None:
        return []
    
    # Use FamilyCRUD search to find families
    families = family_crud.search_families(db_session, query=search_query, limit=limit)
    
    results = []
    for family in families:
        result = analyze_family_consanguinity(db_session, family.id)
        if result and result["consanguinity_coefficient"] > 0.01:  # Only significant ones
            results.append(result)
    
    return sorted(results, key=lambda x: x["consanguinity_coefficient"], reverse=True)


def main():
    app = ConsanguinityApp()
    app.run()


if __name__ == "__main__":
    main()