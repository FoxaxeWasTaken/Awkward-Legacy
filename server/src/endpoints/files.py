from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from ..geneweb_converter import db_to_json, json_to_db
from ..converter.json_normalizer import convert_to_json_serializable, normalize_db_json
from ..converter.entity_extractor import extract_entities
from sqlmodel import Session
from uuid import UUID
import tempfile
import aiofiles
import os

from ..db import get_session
from ..crud.family import family_crud
from ..crud.person import person_crud
from ..crud.event import event_crud
from ..crud.child import child_crud

from ..gw_parser import GWParser
from ..serializer.family_serializer import serialize_family
from ..serializer.person_serializer import serialize_person
from ..serializer.event_serializer import serialize_event
from ..serializer.sources_serializer import serialize_sources


router = APIRouter(prefix="/api/v1/files", tags=["files"])


@router.post("/import", status_code=201)
async def import_geneweb_file(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    try:
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".gw")
        os.close(tmp_fd)  # Close the file descriptor as we'll use aiofiles

        async with aiofiles.open(tmp_path, "wb") as tmp:
            content = await file.read()
            await tmp.write(content)

        parser = GWParser(tmp_path)
        data = parser.parse()

        flat_data = extract_entities(data)
        summary = json_to_db(flat_data, session)

        os.unlink(tmp_path)

        return {"message": "GeneWeb file imported successfully", **summary}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@router.get("/export", response_class=FileResponse)
async def export_geneweb_file(session: Session = Depends(get_session)):
    json_data = db_to_json(session)
    normalized_data = normalize_db_json(json_data)

    # Use GWSerializer for proper .gw file generation
    from ..serializer.gw_serializer import GWSerializer

    serializer = GWSerializer(normalized_data)
    output_text = serializer.serialize()

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".gw")
    os.close(tmp_fd)  # Close the file descriptor as we'll use aiofiles

    async with aiofiles.open(tmp_path, "w", encoding="utf-8") as tmp:
        await tmp.write(output_text)

    return FileResponse(
        tmp_path,
        media_type="text/plain",
        filename="geneweb_export.gw",
    )


@router.post("/import/json", status_code=201)
async def import_json_data(
    json_data: dict,
    session: Session = Depends(get_session),
):
    """
    Import structured JSON data directly (bypassing .gw parsing).

    Useful for testing or when another service sends ready-to-store genealogy data.
    """
    try:
        flat_data = extract_entities(json_data)
        summary = json_to_db(flat_data, session)

        return {"message": "JSON data imported successfully", **summary}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"JSON import failed: {str(e)}")


def validate_family_exists(session: Session, family_id: UUID) -> None:
    """Validate that the family exists in the database."""
    family = family_crud.get(session, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")


def get_family_detail_safe(session: Session, family_id: UUID):
    """Get family detail with error handling."""
    family_detail = family_crud.get_family_detail(session, family_id)
    if not family_detail:
        raise HTTPException(status_code=404, detail="Family not found")
    return family_detail


def build_family_content_lines(family_detail, family_id: UUID) -> list[str]:
    """Build the content lines for the GeneWeb file."""
    lines = [f"# Family {family_id}"]

    if family_detail.husband:
        first_name = family_detail.husband.get("first_name", "")
        last_name = family_detail.husband.get("last_name", "")
        lines.append(f"# Husband: {first_name} {last_name}")

    if family_detail.wife:
        first_name = family_detail.wife.get("first_name", "")
        last_name = family_detail.wife.get("last_name", "")
        lines.append(f"# Wife: {first_name} {last_name}")

    if family_detail.marriage_date:
        lines.append(f"# Marriage: {family_detail.marriage_date}")

    if family_detail.marriage_place:
        lines.append(f"# Place: {family_detail.marriage_place}")

    return lines


def create_temp_file(content_lines: list[str]) -> str:
    """Create a temporary file with the given content."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".gw", delete=False) as temp_file:
        temp_file.write("\n".join(content_lines))
        temp_file.flush()  # Ensure content is written
        return temp_file.name


def generate_filename(family_detail, family_id: UUID) -> str:
    """Generate a filename for the exported family file."""
    husband_name = (
        family_detail.husband.get("first_name", "Unknown")
        if family_detail.husband
        else "Unknown"
    )
    wife_name = (
        family_detail.wife.get("first_name", "Unknown")
        if family_detail.wife
        else "Unknown"
    )
    return f"family_{husband_name}_{wife_name}_{family_id}.gw"


def _filter_data_for_family(normalized_data: dict, family_id: str) -> dict:
    """Filter normalized data to include only the specified family and its related persons."""
    family_id_str = str(family_id)

    # Find the target family
    target_family = None
    for family in normalized_data.get("families", []):
        if str(family.get("id")) == family_id_str:
            target_family = family
            break

    if not target_family:
        raise HTTPException(status_code=404, detail="Family not found")

    # Get all person names related to this family
    related_person_names = set()

    # Add husband and wife names
    if target_family.get("husband") and target_family["husband"].get("raw"):
        husband_name = target_family["husband"]["raw"].strip()
        if husband_name:
            related_person_names.add(husband_name)
    if target_family.get("wife") and target_family["wife"].get("raw"):
        wife_name = target_family["wife"]["raw"].strip()
        if wife_name:
            related_person_names.add(wife_name)

    # Add children names
    for child in target_family.get("children", []):
        if child.get("person") and child["person"].get("raw"):
            related_person_names.add(child["person"]["raw"])

    # Filter persons to only include related ones
    filtered_persons = []
    for person in normalized_data.get("persons", []):
        person_name = (
            f"{person.get('first_name', '')} {person.get('last_name', '')}".strip()
        )
        if person_name in related_person_names:
            filtered_persons.append(person)

    # Filter families to only include the target family
    filtered_families = [target_family]

    # Filter notes to only include related persons
    filtered_notes = []
    for note in normalized_data.get("notes", []):
        person_name = note.get("person", "")
        # Check if this note belongs to a related person
        for person in filtered_persons:
            person_full_name = (
                f"{person.get('first_name', '')} {person.get('last_name', '')}".strip()
            )
            if person_name == person_full_name:
                filtered_notes.append(note)
                break

    return {
        "persons": filtered_persons,
        "families": filtered_families,
        "events": [],  # Events are included with persons
        "notes": filtered_notes,
        "extended_pages": {},  # Not implemented yet
        "database_notes": None,
        "raw_header": normalized_data.get(
            "raw_header", {"gwplus": True, "encoding": "utf-8"}
        ),
    }


def _filter_data_for_family_raw(db_json: dict, family_id: str) -> dict:
    """Filter raw database JSON to include only the specified family and its related persons."""
    family_id_str = str(family_id)

    # Find the target family
    target_family = None
    for family in db_json.get("families", []):
        if str(family.get("id")) == family_id_str:
            target_family = family
            break

    if not target_family:
        raise HTTPException(status_code=404, detail="Family not found")

    # Get all person IDs related to this family
    related_person_ids = set()

    # Add husband and wife IDs
    if target_family.get("husband_id"):
        related_person_ids.add(str(target_family["husband_id"]))
    if target_family.get("wife_id"):
        related_person_ids.add(str(target_family["wife_id"]))

    # Add children IDs
    for child in db_json.get("children", []):
        if str(child.get("family_id")) == family_id_str:
            if child.get("child_id"):
                related_person_ids.add(str(child["child_id"]))

    # Filter persons to only include related ones
    filtered_persons = []
    for person in db_json.get("persons", []):
        if str(person.get("id")) in related_person_ids:
            filtered_persons.append(person)

    # Filter families to only include the target family
    filtered_families = [target_family]

    # Filter children to only include related ones
    filtered_children = []
    for child in db_json.get("children", []):
        if str(child.get("family_id")) == family_id_str:
            filtered_children.append(child)

    # Filter events to only include related ones
    filtered_events = []
    for event in db_json.get("events", []):
        if (
            event.get("person_id") and str(event["person_id"]) in related_person_ids
        ) or (event.get("family_id") and str(event["family_id"]) == family_id_str):
            filtered_events.append(event)

    # Build notes for related persons
    filtered_notes = []
    for person in filtered_persons:
        if person.get("notes"):
            person_name = (
                f"{person.get('first_name', '')} {person.get('last_name', '')}".strip()
            )
            if person_name:
                filtered_notes.append({"person": person_name, "text": person["notes"]})

    return {
        "persons": filtered_persons,
        "families": filtered_families,
        "events": filtered_events,
        "children": filtered_children,
        "notes": filtered_notes,
        "extended_pages": {},
        "database_notes": None,
        "raw_header": {"gwplus": True, "encoding": "utf-8"},
    }


def _filter_data_for_family_fixed(
    normalized_data: dict, raw_data: dict, family_id: str
) -> dict:
    """Filter data for family, fixing empty names issue."""
    family_id_str = str(family_id)
    target_family_raw = _find_target_family(raw_data, family_id_str)
    related_person_ids = _get_related_person_ids(raw_data, family_id_str, target_family_raw)
    filtered_persons = _build_filtered_persons(raw_data, related_person_ids)
    husband_name, wife_name = _extract_spouse_names(raw_data, target_family_raw)
    family_header = _build_family_header(husband_name, wife_name, target_family_raw)
    children_data = _build_children_data(raw_data, family_id_str)
    family_events = _build_family_events(raw_data, family_id_str)
    fixed_family = _build_fixed_family(
        family_id_str, family_header, husband_name, wife_name, 
        family_events, children_data, target_family_raw
    )
    filtered_notes = _build_filtered_notes(filtered_persons)

    return {
        "persons": filtered_persons,
        "families": [fixed_family],
        "events": [],  # Events are included with persons
        "notes": filtered_notes,
        "extended_pages": {},
        "database_notes": None,
        "raw_header": {"gwplus": True, "encoding": "utf-8"},
    }


def _find_target_family(raw_data: dict, family_id_str: str) -> dict:
    """Find the target family in raw data."""
    for family in raw_data.get("families", []):
        if str(family.get("id")) == family_id_str:
            return family
    raise HTTPException(status_code=404, detail="Family not found")


def _get_related_person_ids(raw_data: dict, family_id_str: str, target_family_raw: dict) -> set:
    """Get all person IDs related to this family."""
    related_person_ids = set()
    
    # Add husband and wife IDs
    if target_family_raw.get("husband_id"):
        related_person_ids.add(str(target_family_raw["husband_id"]))
    if target_family_raw.get("wife_id"):
        related_person_ids.add(str(target_family_raw["wife_id"]))
    
    # Add children IDs
    for child in raw_data.get("children", []):
        if str(child.get("family_id")) == family_id_str and child.get("child_id"):
            related_person_ids.add(str(child["child_id"]))
    
    return related_person_ids


def _build_filtered_persons(raw_data: dict, related_person_ids: set) -> list:
    """Build filtered persons list with their events."""
    filtered_persons = []
    for person in raw_data.get("persons", []):
        if str(person.get("id")) in related_person_ids:
            person_events = _get_person_events(raw_data, person.get("id"))
            person["events"] = person_events
            filtered_persons.append(person)
    return filtered_persons


def _get_person_events(raw_data: dict, person_id: str) -> list:
    """Get events for a specific person."""
    person_events = []
    for event in raw_data.get("events", []):
        if str(event.get("person_id")) == str(person_id):
            person_events.append({
                "id": str(event.get("id")),
                "type": event.get("type"),
                "date": event.get("date"),
                "place": event.get("place"),
                "description": event.get("description"),
                "person_id": str(event.get("person_id")) if event.get("person_id") else None,
                "family_id": str(event.get("family_id")) if event.get("family_id") else None,
            })
    return person_events


def _extract_spouse_names(raw_data: dict, target_family_raw: dict) -> tuple:
    """Extract husband and wife names from raw data."""
    husband_name = ""
    wife_name = ""
    
    for person in raw_data.get("persons", []):
        if str(person.get("id")) == str(target_family_raw.get("husband_id")):
            husband_name = f"{person.get('first_name', '')} {person.get('last_name', '')}".strip()
        elif str(person.get("id")) == str(target_family_raw.get("wife_id")):
            wife_name = f"{person.get('first_name', '')} {person.get('last_name', '')}".strip()
    
    return husband_name, wife_name


def _build_family_header(husband_name: str, wife_name: str, target_family_raw: dict) -> str:
    """Build family header string."""
    if husband_name and wife_name:
        family_header = f"{husband_name} + {wife_name}"
    elif husband_name:
        family_header = f"{husband_name} + Unknown"
    elif wife_name:
        family_header = f"Unknown + {wife_name}"
    else:
        family_header = "Unknown + Unknown"
    
    # Add marriage info
    if target_family_raw.get("marriage_date"):
        family_header += f" {target_family_raw['marriage_date']}"
    if target_family_raw.get("marriage_place"):
        family_header += f" #mp {target_family_raw['marriage_place']}"
    
    return family_header


def _build_children_data(raw_data: dict, family_id_str: str) -> list:
    """Build children data for the family."""
    children_data = []
    for child in raw_data.get("children", []):
        if str(child.get("family_id")) == family_id_str:
            child_person = _find_person_by_id(raw_data, child.get("child_id"))
            if child_person:
                child_name = f"{child_person.get('first_name', '')} {child_person.get('last_name', '')}".strip()
                if child_name:
                    gender = "h" if child_person.get("sex") == "M" else "f" if child_person.get("sex") == "F" else "h"
                    children_data.append({
                        "raw": f"- {gender} {child_name}",
                        "gender": "male" if gender == "h" else "female",
                        "person": {"raw": child_name},
                    })
    return children_data


def _find_person_by_id(raw_data: dict, person_id: str) -> dict:
    """Find a person by ID in raw data."""
    for person in raw_data.get("persons", []):
        if str(person.get("id")) == str(person_id):
            return person
    return None


def _build_family_events(raw_data: dict, family_id_str: str) -> list:
    """Build family events list."""
    family_events = []
    for event in raw_data.get("events", []):
        if str(event.get("family_id")) == family_id_str:
            family_events.append({
                "type": event.get("type", ""),
                "date": event.get("date", ""),
                "place": event.get("place", ""),
                "description": event.get("description", ""),
            })
    return family_events


def _build_fixed_family(family_id_str: str, family_header: str, husband_name: str, 
                       wife_name: str, family_events: list, children_data: list, 
                       target_family_raw: dict) -> dict:
    """Build the fixed family structure."""
    return {
        "id": family_id_str,
        "raw_header": family_header,
        "husband": {"raw": husband_name} if husband_name else None,
        "wife": {"raw": wife_name} if wife_name else None,
        "sources": {},
        "events": family_events,
        "children": children_data,
        "marriage_date": target_family_raw.get("marriage_date"),
        "marriage_place": target_family_raw.get("marriage_place"),
        "notes": target_family_raw.get("notes"),
    }


def _build_filtered_notes(filtered_persons: list) -> list:
    """Build filtered notes for related persons."""
    filtered_notes = []
    for person in filtered_persons:
        if person.get("notes"):
            person_name = f"{person.get('first_name', '')} {person.get('last_name', '')}".strip()
            if person_name:
                filtered_notes.append({"person": person_name, "text": person["notes"]})
    return filtered_notes


@router.get("/export/family/{family_id}", response_class=FileResponse)
async def export_family_file(
    family_id: UUID,
    session: Session = Depends(get_session),
):
    """
    Export a specific family and all related data as a GeneWeb file.

    Returns a .gw file containing the family, related persons, children, and events.
    """
    temp_file_path = None
    try:
        validate_family_exists(session, family_id)

        # Get all data and filter to just this family
        json_data = db_to_json(session)
        normalized_data = normalize_db_json(json_data)

        # Filter to only include the requested family and its related persons
        family_data = _filter_data_for_family_fixed(
            normalized_data, json_data, family_id
        )

        # Use GWSerializer for proper .gw file generation
        from ..serializer.gw_serializer import GWSerializer

        serializer = GWSerializer(family_data)
        output_text = serializer.serialize()

        temp_file_path = create_temp_file([output_text])
        filename = f"family_{family_id}.gw"

        return FileResponse(
            path=temp_file_path, filename=filename, media_type="text/plain"
        )
    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file on error
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass  # Ignore cleanup errors
        raise HTTPException(status_code=500, detail=f"Error exporting family: {str(e)}")


@router.get("/export/json", response_class=JSONResponse)
def export_json_data(session: Session = Depends(get_session)):
    """
    Export all genealogy data from the database as structured JSON.
    """
    persons = person_crud.get_all(session)
    families = family_crud.get_all(session)
    events = event_crud.get_all(session)
    children = child_crud.get_all(session)

    data = {
        "persons": [convert_to_json_serializable(p.model_dump()) for p in persons],
        "families": [convert_to_json_serializable(f.model_dump()) for f in families],
        "events": [convert_to_json_serializable(e.model_dump()) for e in events],
        "children": [convert_to_json_serializable(c.model_dump()) for c in children],
    }

    return JSONResponse(content=data)
