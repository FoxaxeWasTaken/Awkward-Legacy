from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from ..geneweb_converter import (
    convert_to_json_serializable,
    db_to_json,
    extract_entities,
    json_to_db,
    normalize_db_json,
)
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
