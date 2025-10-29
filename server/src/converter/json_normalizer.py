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
    notes = _build_notes_list(db_json, person_lookup)
    extended_pages = _build_extended_pages_list(db_json)

    return {
        "persons": persons,
        "families": families,
        "events": [],
        "notes": notes,
        "extended_pages": extended_pages,
        "database_notes": None,  # Could be enhanced later
        "raw_header": {"gwplus": True, "encoding": "utf-8"},
    }


def _build_person_lookup(db_json: dict) -> Dict[str, str]:
    """Build person lookup dictionary."""
    person_lookup = {}
    for p in db_json.get("persons", []):
        person_id = str(p.get("id"))
        name = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
        person_lookup[person_id] = name
    return person_lookup


def _build_events_by_person(db_json: dict) -> Dict[str, list]:
    """Build events grouped by person ID."""
    events_by_person = {}
    for event in db_json.get("events", []):
        person_id = event.get("person_id")
        if person_id:
            person_id = str(person_id)
            if person_id not in events_by_person:
                events_by_person[person_id] = []

            # Convert event to GeneWeb format
            event_data = {
                "type": event.get("type", ""),
                "date": event.get("date", ""),
                "place": event.get("place", ""),
                "description": event.get("description", ""),
            }

            # Create raw event string for GeneWeb format
            raw_parts = []
            if event_data["type"]:
                raw_parts.append(f"#{event_data['type'].lower()}")
            if event_data["date"]:
                # Convert date to string if it's a date object
                date_str = (
                    str(event_data["date"])
                    if hasattr(event_data["date"], "strftime")
                    else event_data["date"]
                )
                raw_parts.append(date_str)
            if event_data["place"]:
                raw_parts.append(f"#p {event_data['place']}")
            if event_data["description"]:
                raw_parts.append(f"note {event_data['description']}")

            event_data["raw"] = " ".join(raw_parts)
            events_by_person[person_id].append(event_data)

    return events_by_person


def _build_persons_list(db_json: dict) -> list:
    """Build persons list from database JSON."""
    persons = []
    for p in db_json.get("persons", []):
        person_data = _build_single_person(p)
        persons.append(person_data)
    return persons


def _build_single_person(p: dict) -> dict:
    """Build a single person data structure."""
    raw = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
    tags = _build_person_tags(p)
    dates = _build_person_dates(p)
    person_events = _build_person_events(p)

    return {
        "name": raw,
        "raw": raw,
        "tags": tags,
        "dates": dates,
        "events": person_events,
        "sex": p.get("sex", "U"),
        # carry base fields so event synthesis/serializers can use them
        "birth_date": p.get("birth_date"),
        "death_date": p.get("death_date"),
        "birth_place": p.get("birth_place", ""),
        "death_place": p.get("death_place", ""),
    }


def _build_person_tags(p: dict) -> dict:
    """Build tags for a person."""
    tags = {}
    if occ := p.get("occupation"):
        tags["occu"] = [occ]
    if notes := p.get("notes"):
        tags["note"] = [notes]
    if birth_place := p.get("birth_place"):
        tags["bp"] = [birth_place]
    if death_place := p.get("death_place"):
        tags["dp"] = [death_place]
    return tags


def _build_person_dates(p: dict) -> list:
    """Build dates list for a person."""
    dates = []
    if p.get("birth_date"):
        dates.append(str(p.get("birth_date")))
    if p.get("death_date"):
        dates.append(str(p.get("death_date")))
    return dates


def _build_person_events(p: dict) -> list:
    """Build events list for a person."""
    explicit = _normalize_explicit_events(p)
    if explicit:
        return explicit
    return _synthesize_core_events(p)


def _normalize_explicit_events(p: dict) -> list:
    events = []
    for event in p.get("events") or []:
        event_data = _build_single_event(event)
        if event_data:
            events.append(event_data)
    return events


def _synthesize_core_events(p: dict) -> list:
    synthesized = []
    _maybe_add_synth_event(
        synthesized,
        "birt",
        p.get("birth_date", ""),
        p.get("birth_place", ""),
    )
    _maybe_add_synth_event(
        synthesized,
        "deat",
        p.get("death_date", ""),
        p.get("death_place", ""),
    )
    return synthesized


def _maybe_add_synth_event(acc: list, ev_type: str, date, place: str) -> None:
    if not date and not place:
        return
    acc.append(
        {
            "type": ev_type,
            "date": date or "",
            "place": place or "",
            "description": "",
            "raw": _serialize_event_raw(ev_type, date or "", place or "", ""),
        }
    )


def _serialize_event_raw(event_type: str, date, place: str, description: str) -> str:
    parts = [f"#{event_type}"]
    if date:
        parts.append(str(date))
    if place:
        parts.append(f"#p {place}")
    if description:
        parts.append(f"note {description}")
    return " ".join(parts)


def _build_single_event(event: dict) -> dict:
    """Build a single event data structure."""
    event_data = {
        "type": event.get("type", ""),
        "date": event.get("date", ""),
        "place": event.get("place", ""),
        "description": event.get("description", ""),
    }

    raw_parts = _build_event_raw_parts(event_data)
    event_data["raw"] = " ".join(raw_parts)
    return event_data


def _build_event_raw_parts(event_data: dict) -> list:
    """Build raw parts for an event."""
    raw_parts = []
    if event_data["type"]:
        raw_parts.append(f"#{event_data['type'].lower()}")
    if event_data["date"]:
        date_str = _convert_date_to_string(event_data["date"])
        raw_parts.append(date_str)
    if event_data["place"]:
        raw_parts.append(f"#p {event_data['place']}")
    if event_data["description"]:
        raw_parts.append(f"note {event_data['description']}")
    return raw_parts


def _convert_date_to_string(date) -> str:
    """Convert date to string if it's a date object."""
    return str(date) if hasattr(date, "strftime") else date


def _build_children_by_family(
    db_json: dict, person_lookup: Dict[str, str]
) -> Dict[str, list]:
    """Build children by family dictionary."""
    children_by_family = {}
    for c in db_json.get("children", []):
        family_id = str(c.get("family_id"))
        child_id = str(c.get("child_id"))

        _ensure_family_exists(children_by_family, family_id)
        context = {
            "db_json": db_json,
            "children_by_family": children_by_family,
            "family_id": family_id,
            "child_id": child_id,
            "person_lookup": person_lookup,
        }
        _add_child_if_valid(context)

    return children_by_family


def _ensure_family_exists(children_by_family: Dict[str, list], family_id: str) -> None:
    """Ensure family exists in children_by_family dictionary."""
    if family_id not in children_by_family:
        children_by_family[family_id] = []


def _add_child_if_valid(context: dict) -> None:
    """Add child to family if valid."""
    db_json = context["db_json"]
    children_by_family = context["children_by_family"]
    family_id = context["family_id"]
    child_id = context["child_id"]
    person_lookup = context["person_lookup"]

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

    return {"gender": gender, "person": {"raw": child_name}}


def _build_families_list(
    db_json: dict, person_lookup: Dict[str, str], children_by_family: Dict[str, list]
) -> list:
    """Build families list from database JSON."""
    families = []
    for f in db_json.get("families", []):
        family_data = _create_family_data(f, person_lookup, children_by_family)
        families.append(family_data)
    return families


def _create_family_data(
    family: dict, person_lookup: Dict[str, str], children_by_family: Dict[str, list]
) -> dict:
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

    result = {
        "id": family_id,
        "raw_header": header,
        "husband": {"raw": husband_name} if husband_name else None,
        "wife": {"raw": wife_name} if wife_name else None,
        "sources": sources,
        "events": fam_events,
        "children": family_children,
    }

    # Preserve other family fields
    for key, value in family.items():
        if key not in ["id", "husband_id", "wife_id"]:
            result[key] = value

    return result


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

        fam_events.append({"raw": " ".join(marriage_parts)})

    if f.get("notes"):
        fam_events.append({"raw": f"note {f.get('notes')}"})

    return fam_events


def _build_notes_list(db_json: dict, person_lookup: Dict[str, str]) -> list:
    """Build notes list from persons with notes."""
    notes = []
    for p in db_json.get("persons", []):
        person_id = str(p.get("id"))
        note_text = (p.get("notes") or "").strip()
        if not note_text or person_id not in person_lookup:
            continue
        notes.append(
            {
                "person": person_lookup[person_id],
                "text": note_text,
                "raw_lines": note_text.split("\n"),
            }
        )

    return notes


def _build_extended_pages_list(db_json: dict) -> dict:
    """Build extended pages dict (placeholder for future enhancement)."""
    # For now, return empty dict as extended pages are not stored in DB
    # This could be enhanced to store extended pages in the database
    return {}
