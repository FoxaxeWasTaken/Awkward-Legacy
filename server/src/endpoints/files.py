from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from geneweb_converter import db_to_json, extract_entities, json_to_db
from sqlmodel import Session
from uuid import UUID
import tempfile

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
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gw") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        parser = GWParser(tmp_path)
        data = parser.parse()

        print("Data parsed from .gw file:", data)
        flat_data = extract_entities(data)
        summary = json_to_db(flat_data, session)
        return {"message": "GeneWeb file imported successfully", **summary}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@router.get("/export", response_class=FileResponse)
def export_geneweb_file(session: Session = Depends(get_session)):
    json_data = db_to_json(session)

    lines = []
    for person in json_data["persons"]:
        lines.append(serialize_person(person))
    for family in json_data["families"]:
        lines.append(serialize_family(family))
    for event in json_data["events"]:
        lines.append(serialize_event(event))

    output_text = "\n\n".join(lines)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".gw", mode="w", encoding="utf-8") as tmp:
        tmp.write(output_text)
        tmp_path = tmp.name

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
        persons = json_data.get("persons", [])
        families = json_data.get("families", [])
        events = json_data.get("events", [])
        children = json_data.get("children", [])

        for person in persons:
            person_crud.create(session, person)

        for family in families:
            family_crud.create(session, family)

        for event in events:
            event_crud.create(session, event)

        for child in children:
            child_crud.create(session, child)

        return {"message": "JSON data imported successfully"}

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
        "persons": [p.model_dump() for p in persons],
        "families": [f.model_dump() for f in families],
        "events": [e.model_dump() for e in events],
        "children": [c.model_dump() for c in children],
    }

    return JSONResponse(content=data)
