from typing import Dict, Any, List, Optional
from datetime import date, datetime
from uuid import UUID, uuid4
from sqlmodel import Session
from src.models import Person, Family, Event, Child
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

    person_map = {}
    family_map = {}

    for person_data in persons:
        created = person_crud.create(session, person_data)
        person_map[person_data.get("id")] = created.id

    for family_data in families:
        husband_id = person_map.get(family_data.get("husband_id"))
        wife_id = person_map.get(family_data.get("wife_id"))
        family_data["husband_id"] = husband_id
        family_data["wife_id"] = wife_id
        created = family_crud.create(session, family_data)
        family_map[family_data.get("id")] = created.id

    for event_data in events:
        event_crud.create(session, event_data)

    for child_data in children:
        family_id = family_map.get(child_data.get("family_id"))
        child_id = person_map.get(child_data.get("child_id"))
        if family_id and child_id:
            child_data["family_id"] = family_id
            child_data["child_id"] = child_id
            child_crud.create(session, child_data)

    return {
        "persons": len(persons),
        "families": len(families),
        "events": len(events),
        "children": len(children),
    }


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

def extract_entities(parsed: Dict[str, Any]):
    persons, families, events, children = [], [], [], []

    for fam in parsed.get("families", []):
        husband = fam.get("husband")
        wife = fam.get("wife")

        fam_id = fam.get("id") or str(uuid4())

        husband_id = None
        wife_id = None

        if husband:
            husband_data = ensure_person_fields(husband)
            persons.append(husband_data)
            husband_id = husband_data.get("id")

        if wife:
            wife_data = ensure_person_fields(wife)
            persons.append(wife_data)
            wife_id = wife_data.get("id")

        marriage_date = extract_marriage_date_from_family_data(fam)
        marriage_place = extract_marriage_place_from_family_data(fam)
        family_notes = extract_family_notes_from_family_data(fam)

        family_data = {k:v for k,v in fam.items() if k not in ["husband","wife","children","events"]}
        family_data.update({
            "id": fam_id,
            "husband_id": husband_id,
            "wife_id": wife_id,
            "marriage_date": marriage_date,
            "marriage_place": marriage_place,
            "notes": family_notes
        })
        families.append(family_data)

        for child in fam.get("children", []):
            c = child.get("person")
            if c:
                if "gender" in child:
                    c["gender"] = child["gender"]
                elif "gender" in c:
                    c["gender"] = c["gender"]

                child_data = ensure_person_fields(c)
                persons.append(child_data)
                children.append({"family_id": fam_id, "child_id": child_data.get("id")})

        for evt in fam.get("events", []):
            event_data = ensure_event_fields(evt)
            events.append({"family_id": fam_id, **event_data})

    return {
        "persons": persons,
        "families": families,
        "events": events,
        "children": children
    }

def ensure_person_fields(person_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure that a person object has the required fields for database insertion.

    Args:
        person_data: The person data dictionary

    Returns:
        Person data with required fields (id, first_name, last_name, sex, birth_date, death_date, etc.)
    """
    first_name = person_data.get("first_name", "")
    last_name = person_data.get("last_name", "")
    gender = person_data.get("gender")
    if gender == "male":
        sex = "M"
    elif gender == "female":
        sex = "F"
    else:
        sex = "U"

    if not first_name and not last_name and person_data.get("name"):
        from src.parsing.utils import split_name_into_parts
        first_name, last_name = split_name_into_parts(person_data["name"])

    birth_date = extract_birth_date_from_person_data(person_data)
    death_date = extract_death_date_from_person_data(person_data)
    birth_place = extract_birth_place_from_person_data(person_data)
    death_place = extract_death_place_from_person_data(person_data)
    occupation = extract_occupation_from_person_data(person_data)
    notes = extract_notes_from_person_data(person_data)

    result = person_data.copy()
    result["id"] = person_data.get("id") or str(uuid4())
    result["first_name"] = first_name
    result["last_name"] = last_name
    result["sex"] = sex
    result["birth_date"] = birth_date
    result["death_date"] = death_date
    result["birth_place"] = birth_place
    result["death_place"] = death_place
    result["occupation"] = occupation
    result["notes"] = notes

    return result

def ensure_event_fields(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure that an event object has the required fields for database insertion.

    Args:
        event_data: The event data dictionary

    Returns:
        Event data with required fields (date, place, description converted properly)
    """
    result = event_data.copy()

    if "date" in event_data and isinstance(event_data["date"], dict):
        date_dict = event_data["date"]
        parsed_date = parse_date_dict_to_date(date_dict)
        result["date"] = parsed_date
    elif "date" in event_data and isinstance(event_data["date"], str):
        parsed_date = parse_date_string_to_date(event_data["date"])
        result["date"] = parsed_date

    if "place_raw" in event_data:
        result["place"] = event_data["place_raw"]
    elif "place" in event_data:
        result["place"] = event_data["place"]

    if "notes" in event_data and event_data["notes"]:
        if isinstance(event_data["notes"], list):
            result["description"] = " | ".join(event_data["notes"])
        else:
            result["description"] = str(event_data["notes"])

    if "id" not in result:
        result["id"] = str(uuid4())

    return result

def parse_date_dict_to_date(date_dict: Dict[str, Any]) -> Optional[date]:
    """
    Convert a date dictionary from GeneWeb parsing to a proper date object.

    Args:
        date_dict: Dictionary with date information (e.g., {'raw': '3/3/1835', 'value': '3/3/1835'})

    Returns:
        Parsed date object or None if parsing fails
    """
    if not date_dict:
        return None

    date_str = date_dict.get("value") or date_dict.get("raw", "")

    if not date_str:
        return None

    return parse_date_string_to_date(date_str)

def parse_date_string_to_date(date_str: str) -> Optional[date]:
    """
    Parse a date string to a date object.

    Args:
        date_str: Date string in various formats (e.g., "3/3/1835", "1835-03-03", "1835")

    Returns:
        Parsed date object or None if parsing fails
    """
    if not date_str:
        return None

    date_formats = [
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%Y",
        "%m/%Y",
        "%Y-%m",
    ]

    for fmt in date_formats:
        try:
            parsed_datetime = datetime.strptime(date_str, fmt)
            return parsed_datetime.date()
        except ValueError:
            continue

    try:
        import re
        year_match = re.search(r'\b(1[0-9]{3}|2[0-9]{3})\b', date_str)
        if year_match:
            year = int(year_match.group(1))
            return date(year, 1, 1)
    except (ValueError, AttributeError):
        pass

    return None

# ===== PERSON DATA EXTRACTION FUNCTIONS =====

def extract_birth_date_from_person_data(person_data: Dict[str, Any]) -> Optional[date]:
    """Extract birth date from person data."""
    events = person_data.get("events", [])
    for event in events:
        if event.get("type") == "birth" and "date" in event:
            return parse_date_dict_to_date(event["date"]) if isinstance(event["date"], dict) else parse_date_string_to_date(event["date"])

    dates = person_data.get("dates", [])
    if dates:
        first_date = dates[0]
        if isinstance(first_date, dict):
            return parse_date_dict_to_date(first_date)
        elif isinstance(first_date, str):
            return parse_date_string_to_date(first_date)

    tags = person_data.get("tags", {})
    if "birth" in tags:
        birth_values = tags["birth"]
        if birth_values:
            return parse_date_string_to_date(birth_values[0])

    raw_string = person_data.get("raw", "")
    if raw_string:
        import re
        years = re.findall(r'\b(1[0-9]{3}|2[0-9]{3})\b', raw_string)
        if years:
            try:
                year = int(years[0])
                return date(year, 1, 1)
            except ValueError:
                pass

    return None

def extract_death_date_from_person_data(person_data: Dict[str, Any]) -> Optional[date]:
    """Extract death date from person data."""
    events = person_data.get("events", [])
    for event in events:
        if event.get("type") == "death" and "date" in event:
            return parse_date_dict_to_date(event["date"]) if isinstance(event["date"], dict) else parse_date_string_to_date(event["date"])

    dates = person_data.get("dates", [])
    if len(dates) >= 2:
        second_date = dates[1]
        if isinstance(second_date, dict):
            return parse_date_dict_to_date(second_date)
        elif isinstance(second_date, str):
            return parse_date_string_to_date(second_date)

    tags = person_data.get("tags", {})
    if "death" in tags:
        death_values = tags["death"]
        if death_values:
            return parse_date_string_to_date(death_values[0])

    raw_string = person_data.get("raw", "")
    if raw_string:
        import re
        years = re.findall(r'\b(1[0-9]{3}|2[0-9]{3})\b', raw_string)
        if len(years) >= 2:
            try:
                year = int(years[1])
                return date(year, 1, 1)
            except ValueError:
                pass

    return None

def extract_birth_place_from_person_data(person_data: Dict[str, Any]) -> Optional[str]:
    """Extract birth place from person data."""
    events = person_data.get("events", [])
    for event in events:
        if event.get("type") == "birth" and "place_raw" in event:
            return event["place_raw"]

    tags = person_data.get("tags", {})
    if "birth_place" in tags:
        birth_places = tags["birth_place"]
        if birth_places:
            return birth_places[0]

    return None

def extract_death_place_from_person_data(person_data: Dict[str, Any]) -> Optional[str]:
    """Extract death place from person data."""
    events = person_data.get("events", [])
    for event in events:
        if event.get("type") == "death" and "place_raw" in event:
            return event["place_raw"]

    tags = person_data.get("tags", {})
    if "death_place" in tags:
        death_places = tags["death_place"]
        if death_places:
            return death_places[0]

    return None

def extract_occupation_from_person_data(person_data: Dict[str, Any]) -> Optional[str]:
    """Extract occupation from person data."""
    tags = person_data.get("tags", {})
    if "occu" in tags:
        occupations = tags["occu"]
        if occupations:
            return occupations[0]

    if "occupation" in tags:
        occupations = tags["occupation"]
        if occupations:
            return occupations[0]

    events = person_data.get("events", [])
    for event in events:
        if event.get("type") == "occupation" and "description" in event:
            return event["description"]

    return None

def extract_notes_from_person_data(person_data: Dict[str, Any]) -> Optional[str]:
    """Extract notes from person data."""
    notes = person_data.get("notes", [])
    if notes:
        return " | ".join(notes)

    tags = person_data.get("tags", {})
    if "src" in tags:
        src_notes = tags["src"]
        if src_notes:
            return " | ".join(src_notes)

    events = person_data.get("events", [])
    event_notes = []
    for event in events:
        if "notes" in event and event["notes"]:
            event_notes.extend(event["notes"])

    if event_notes:
        return " | ".join(event_notes)

    return None

# ===== FAMILY DATA EXTRACTION FUNCTIONS =====

def extract_marriage_date_from_family_data(family_data: Dict[str, Any]) -> Optional[date]:
    """Extract marriage date from family data."""
    events = family_data.get("events", [])
    for event in events:
        if event.get("type") == "marriage" and "date" in event:
            return parse_date_dict_to_date(event["date"]) if isinstance(event["date"], dict) else parse_date_string_to_date(event["date"])

    return None

def extract_marriage_place_from_family_data(family_data: Dict[str, Any]) -> Optional[str]:
    """Extract marriage place from family data."""
    events = family_data.get("events", [])
    for event in events:
        if event.get("type") == "marriage" and "place_raw" in event:
            return event["place_raw"]

    return None

def extract_family_notes_from_family_data(family_data: Dict[str, Any]) -> Optional[str]:
    """Extract family notes from family data."""

    events = family_data.get("events", [])
    event_notes = []
    for event in events:
        if "notes" in event and event["notes"]:
            if isinstance(event["notes"], list):
                event_notes.extend(event["notes"])
            else:
                event_notes.append(str(event["notes"]))

    if event_notes:
        return " | ".join(event_notes)

    return None

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

    person_lookup = {}
    for p in db_json.get("persons", []):
        person_id = str(p.get("id"))
        name = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
        person_lookup[person_id] = name

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

    children_by_family = {}
    for c in db_json.get("children", []):
        family_id = str(c.get("family_id"))
        child_id = str(c.get("child_id"))
        if family_id not in children_by_family:
            children_by_family[family_id] = []

        child_person = None
        for p in db_json.get("persons", []):
            if str(p.get("id")) == child_id:
                child_person = p
                break

        if child_person and child_id in person_lookup:
            sex = child_person.get("sex", "M")
            gender = "male" if sex == "M" else "female" if sex == "F" else "male"

            children_by_family[family_id].append({
                "gender": gender,
                "person": {
                    "raw": person_lookup[child_id]
                }
            })

    families = []
    for f in db_json.get("families", []):
        husband_id = str(f.get("husband_id", "")) if f.get("husband_id") else ""
        wife_id = str(f.get("wife_id", "")) if f.get("wife_id") else ""

        husband_name = person_lookup.get(husband_id, "")
        wife_name = person_lookup.get(wife_id, "")

        if husband_name and wife_name:
            header = f"{husband_name} + {wife_name}"
        elif husband_name:
            header = husband_name
        elif wife_name:
            header = wife_name
        else:
            header = "Unknown + Unknown"

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

        sources = {}

        family_id = str(f.get("id"))
        family_children = children_by_family.get(family_id, [])

        families.append({
            "raw_header": header,
            "sources": sources,
            "events": fam_events,
            "children": family_children,
        })

    return {"persons": persons, "families": families, "events": []}
