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
    from sqlmodel import select
    from sqlalchemy.orm import joinedload
    from .models.person import Person
    from .models.family import Family
    from .models.event import Event
    from .models.child import Child
    
    # Load persons with their events using selectinload for one-to-many relationships
    from sqlalchemy.orm import selectinload
    persons_statement = select(Person).options(selectinload(Person.events))
    persons = list(session.exec(persons_statement))
    
    # Load families with their relationships
    families_statement = select(Family).options(
        joinedload(Family.husband),
        joinedload(Family.wife),
        joinedload(Family.events),
        joinedload(Family.children).joinedload(Child.child)
    )
    families = list(session.exec(families_statement).unique())
    
    # Load all events separately for the events list
    events = event_crud.get_all(session)
    children = child_crud.get_all(session)

    # Convert persons with their events to dictionaries
    persons_data = []
    for person in persons:
        # Get base person data
        person_dict = {
            "id": str(person.id),
            "first_name": person.first_name,
            "last_name": person.last_name,
            "sex": person.sex,
            "birth_date": person.birth_date,
            "death_date": person.death_date,
            "birth_place": person.birth_place,
            "death_place": person.death_place,
            "occupation": person.occupation,
            "notes": person.notes,
        }
        
        # Manually attach events for this person
        person_events = []
        for event in events:
            if event.person_id == person.id:
                person_events.append({
                    "id": str(event.id),
                    "type": event.type,
                    "date": event.date,
                    "place": event.place,
                    "description": event.description,
                    "person_id": str(event.person_id) if event.person_id else None,
                    "family_id": str(event.family_id) if event.family_id else None,
                })
        
        person_dict["events"] = person_events
        persons_data.append(person_dict)
    
    # Convert families with their relationships to dictionaries
    families_data = []
    for family in families:
        family_dict = family.model_dump()
        # Convert events to dictionaries
        family_dict["events"] = [event.model_dump() for event in family.events]
        # Convert children to the expected format
        children_data = []
        for child in family.children:
            child_dict = child.model_dump()
            # Add the child person data
            if child.child:
                child_dict["person"] = {"raw": f"{child.child.first_name} {child.child.last_name}".strip()}
                # Add gender based on child's sex
                sex = child.child.sex
                child_dict["gender"] = "male" if sex == "M" else "female" if sex == "F" else "male"
            children_data.append(child_dict)
        family_dict["children"] = children_data
        families_data.append(family_dict)

    return {
        "persons": persons_data,
        "families": families_data,
        "events": [e.model_dump() for e in events],
        "children": [c.model_dump() for c in children],
    }
