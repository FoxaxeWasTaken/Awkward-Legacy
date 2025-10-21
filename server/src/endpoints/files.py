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

    lines = []

    for person in normalized_data["persons"]:
        lines.append(serialize_person(person))

    for family in normalized_data["families"]:
        lines.append(serialize_family(family))

    for event in normalized_data["events"]:
        lines.append(serialize_event(event))

    output_text = "\n\n".join(line for line in lines if line.strip())

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
        family_detail = get_family_detail_safe(session, family_id)

        content_lines = build_family_content_lines(family_detail, family_id)
        temp_file_path = create_temp_file(content_lines)
        filename = generate_filename(family_detail, family_id)

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
