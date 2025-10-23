"""GeneWeb converter module.

Handles conversion between JSON data and database entities.
"""

from typing import Dict, Any
from sqlmodel import Session
from src.crud.person import person_crud
from src.crud.family import family_crud
from src.crud.event import event_crud
from src.crud.child import child_crud


def json_to_db(data: Dict[str, Any], session: Session):
    """Insert parsed GeneWeb JSON data into the database using CRUDs."""
    persons = data.get("persons", [])
    families = data.get("families", [])
    events = data.get("events", [])
    children = data.get("children", [])

    person_map = _create_persons(session, persons)
    family_map = _create_families(session, families, person_map)
    _create_events(session, events)
    created_children = _create_children(session, children, family_map, person_map)

    return {
        "persons_created": len(persons),
        "families_created": len(families),
        "events_created": len(events),
        "children_created": created_children,
    }


def _create_persons(session: Session, persons: list) -> Dict[str, int]:
    """Create persons and return mapping of original ID to database ID."""
    person_map = {}
    for person_data in persons:
        created = person_crud.create(session, person_data)
        person_map[person_data.get("id")] = created.id
    return person_map


def _create_families(
    session: Session, families: list, person_map: Dict[str, int]
) -> Dict[str, int]:
    """Create families and return mapping of original ID to database ID."""
    family_map = {}
    for family_data in families:
        husband_id = person_map.get(family_data.get("husband_id"))
        wife_id = person_map.get(family_data.get("wife_id"))
        family_data["husband_id"] = husband_id
        family_data["wife_id"] = wife_id
        created = family_crud.create(session, family_data)
        family_map[family_data.get("id")] = created.id
    return family_map


def _create_events(session: Session, events: list) -> None:
    """Create events in the database."""
    for event_data in events:
        event_crud.create(session, event_data)


def _create_children(
    session: Session,
    children: list,
    family_map: Dict[str, int],
    person_map: Dict[str, int],
) -> int:
    """Create children and return count of successfully created children."""
    created_children = 0
    for child_data in children:
        family_id = family_map.get(child_data.get("family_id"))
        child_id = person_map.get(child_data.get("child_id"))
        if family_id and child_id:
            child_data["family_id"] = family_id
            child_data["child_id"] = child_id
            child_crud.create(session, child_data)
            created_children += 1
    return created_children


def db_to_json(session: Session) -> Dict[str, Any]:
    """Convert all DB entities into structured GeneWeb-like JSON."""
    persons = person_crud.get_all(session)
    families = family_crud.get_all(session)
    events = event_crud.get_all(session)
    children = child_crud.get_all(session)

    return {
        "persons": [p.model_dump() for p in persons],
        "families": [f.model_dump() for f in families],
        "events": [e.model_dump() for e in events],
        "children": [c.model_dump() for c in children],
    }
