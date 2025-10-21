#!/usr/bin/env python3
"""
Consanguinity Calculator - Optimized version using GW parser
"""

import sys
import os
import argparse
import signal
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class Person:
    """Represents a person in the genealogy tree"""
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
    """Builds genealogy data structure from GW parser output"""
    
    def __init__(self):
        self.persons: Dict[str, Person] = {}
        self.families: Dict[str, Family] = {}
        self._person_counter = 0
        self._family_counter = 0
        
    def build_from_gw_parser(self, parser_result: Dict) -> None:
        self._process_families(parser_result.get("families", []))
        self._link_families_and_persons()
        
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
    """Main application class"""
    
    def __init__(self):
        self.filename = ""
        self.verbosity = 2
        self.output_file = None
        
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
            help="GeneWeb .gw database file"
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
        if not os.path.exists(self.filename):
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
        
        persons = data_builder.persons
        families = data_builder.families
        
        if self.verbosity > 0:
            print(f"Database loaded: {len(persons)} persons, {len(families)} families")
        
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
        self.parse_arguments()
        self.validate_arguments()
        self.setup_signal_handlers()
        
        try:
            result = self.compute_consanguinity()
            
            if result.get("changes_made", False):
                if self.verbosity > 0:
                    print("Consanguinity calculation completed successfully")
            else:
                if self.verbosity > 0:
                    print("No significant consanguinity detected")
                    
        except KeyboardInterrupt:
            print("\nCalculation interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"Error during calculation: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(2)


def main():
    app = ConsanguinityApp()
    app.run()


if __name__ == "__main__":
    main()