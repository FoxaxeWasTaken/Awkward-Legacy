"""
JSON normalization utilities for GeneWeb converter.

Handles conversion between database JSON and GeneWeb format.
"""

from typing import Dict, Any
from datetime import date, datetime
from uuid import UUID


def convert_to_json_serializable(obj):
    """Recursively convert objects into JSON-serializable types."""
    if isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(v) for v in obj]
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, UUID):
        return str(obj)
    else:
        return obj


def normalize_db_json(db_json: dict) -> dict:
    """
    Transform DB JSON (from db_to_json) into the format expected by the GeneWeb serializers.
    """
    person_lookup = _build_person_lookup(db_json)
    persons = _build_persons_list(db_json)
    children_by_family = _build_children_by_family(db_json, person_lookup)
    families = _build_families_list(db_json, person_lookup, children_by_family)

    return {"persons": persons, "families": families, "events": []}


def _build_person_lookup(db_json: dict) -> Dict[str, str]:
    """Build person lookup dictionary."""
    person_lookup = {}
    for p in db_json.get("persons", []):
        person_id = str(p.get("id"))
        name = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
        person_lookup[person_id] = name
    return person_lookup


def _build_persons_list(db_json: dict) -> list:
    """Build persons list from database JSON."""
    persons = []
    for p in db_json.get("persons", []):
        raw = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()

        tags = {}
        if occ := p.get("occupation"):
            tags["occu"] = [occ]
        if notes := p.get("notes"):
            tags["note"] = [notes]

        dates = []
        if p.get("birth_date"):
            dates.append(str(p.get("birth_date")))
        if p.get("death_date"):
            dates.append(str(p.get("death_date")))

        persons.append({
            "name": raw,
            "raw": raw,
            "tags": tags,
            "dates": dates,
            "events": [],
        })
    return persons


def _build_children_by_family(db_json: dict, person_lookup: Dict[str, str]) -> Dict[str, list]:
    """Build children by family dictionary."""
    children_by_family = {}
    for c in db_json.get("children", []):
        family_id = str(c.get("family_id"))
        child_id = str(c.get("child_id"))
        
        _ensure_family_exists(children_by_family, family_id)
        _add_child_if_valid(db_json, children_by_family, family_id, child_id, person_lookup)
    
    return children_by_family


def _ensure_family_exists(children_by_family: Dict[str, list], family_id: str) -> None:
    """Ensure family exists in children_by_family dictionary."""
    if family_id not in children_by_family:
        children_by_family[family_id] = []


def _add_child_if_valid(db_json: dict, children_by_family: Dict[str, list], family_id: str, child_id: str, person_lookup: Dict[str, str]) -> None:
    """Add child to family if valid."""
    child_person = _find_person_by_id(db_json, child_id)
    if child_person and child_id in person_lookup:
        child_data = _create_child_data(child_person, person_lookup[child_id])
        children_by_family[family_id].append(child_data)


def _find_person_by_id(db_json: dict, person_id: str) -> dict:
    """Find person by ID in the database JSON."""
    for p in db_json.get("persons", []):
        if str(p.get("id")) == person_id:
            return p
    return None


def _create_child_data(child_person: dict, child_name: str) -> dict:
    """Create child data structure."""
    sex = child_person.get("sex", "M")
    gender = "male" if sex == "M" else "female" if sex == "F" else "male"
    
    return {
        "gender": gender,
        "person": {
            "raw": child_name
        }
    }


def _build_families_list(db_json: dict, person_lookup: Dict[str, str], children_by_family: Dict[str, list]) -> list:
    """Build families list from database JSON."""
    families = []
    for f in db_json.get("families", []):
        family_data = _create_family_data(f, person_lookup, children_by_family)
        families.append(family_data)
    return families


def _create_family_data(family: dict, person_lookup: Dict[str, str], children_by_family: Dict[str, list]) -> dict:
    """Create family data structure."""
    husband_id = str(family.get("husband_id", "")) if family.get("husband_id") else ""
    wife_id = str(family.get("wife_id", "")) if family.get("wife_id") else ""

    husband_name = person_lookup.get(husband_id, "")
    wife_name = person_lookup.get(wife_id, "")

    header = _build_family_header(husband_name, wife_name)
    fam_events = _build_family_events(family)
    sources = {}
    family_id = str(family.get("id"))
    family_children = children_by_family.get(family_id, [])

    return {
        "raw_header": header,
        "sources": sources,
        "events": fam_events,
        "children": family_children,
    }


def _build_family_header(husband_name: str, wife_name: str) -> str:
    """Build family header string."""
    if husband_name and wife_name:
        return f"{husband_name} + {wife_name}"
    elif husband_name:
        return husband_name
    elif wife_name:
        return wife_name
    else:
        return "Unknown + Unknown"


def _build_family_events(f: dict) -> list:
    """Build family events list."""
    fam_events = []
    if f.get("marriage_date") or f.get("marriage_place"):
        marriage_parts = ["#marr"]
        if f.get("marriage_date"):
            marriage_parts.append(str(f.get("marriage_date")))
        if f.get("marriage_place"):
            marriage_parts.append(f.get("marriage_place"))

        fam_events.append({
            "raw": " ".join(marriage_parts)
        })

    if f.get("notes"):
        fam_events.append({
            "raw": f"note {f.get('notes')}"
        })

    return fam_events

