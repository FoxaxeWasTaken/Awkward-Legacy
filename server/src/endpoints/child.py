from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from ..crud.child import child_crud
from ..db import get_session
from ..models.child import Child, ChildCreate, ChildRead

router = APIRouter(prefix="/api/v1/children", tags=["children"])


@router.post("/", response_model=ChildRead, status_code=201)
def create_child(
    child: ChildCreate,
    session: Session = Depends(get_session),
):
    """Create a new child relationship."""
    existing_child = child_crud.get(session, child.family_id, child.child_id)
    if existing_child:
        raise HTTPException(status_code=409, detail="Child relationship already exists")

    from ..crud.family import family_crud

    family = family_crud.get(session, child.family_id)
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")

    from ..crud.person import person_crud

    person = person_crud.get(session, child.child_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    if family.husband_id == child.child_id or family.wife_id == child.child_id:
        raise HTTPException(
            status_code=400, detail="A parent cannot be their own child"
        )

    return child_crud.create(session, child)


@router.get("/", response_model=List[ChildRead])
def get_all_children(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session),
):
    """Get all child relationships with pagination."""
    return child_crud.get_all(session, skip=skip, limit=limit)


@router.get("/by-family/{family_id}", response_model=List[ChildRead])
def get_children_by_family(
    family_id: UUID,
    session: Session = Depends(get_session),
):
    """Get all children of a specific family."""
    return child_crud.get_by_family(session, family_id)


@router.get("/by-child/{child_id}", response_model=List[ChildRead])
def get_children_by_child(
    child_id: UUID,
    session: Session = Depends(get_session),
):
    """Get all families where a person is a child."""
    return child_crud.get_by_child(session, child_id)


@router.delete("/by-family/{family_id}")
def delete_children_by_family(
    family_id: UUID,
    session: Session = Depends(get_session),
):
    """Delete all child relationships for a family."""
    deleted_count = child_crud.delete_by_family(session, family_id)
    return {"deleted_count": deleted_count}


@router.delete("/by-child/{child_id}")
def delete_children_by_child(
    child_id: UUID,
    session: Session = Depends(get_session),
):
    """Delete all family relationships for a child."""
    deleted_count = child_crud.delete_by_child(session, child_id)
    return {"deleted_count": deleted_count}


@router.get("/{family_id}/{child_id}", response_model=ChildRead)
def get_child(
    family_id: UUID,
    child_id: UUID,
    session: Session = Depends(get_session),
):
    """Get a specific child relationship."""
    child = child_crud.get(session, family_id, child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child relationship not found")
    return child


@router.delete("/{family_id}/{child_id}", status_code=204)
def delete_child(
    family_id: UUID,
    child_id: UUID,
    session: Session = Depends(get_session),
):
    """Delete a specific child relationship."""
    success = child_crud.delete(session, family_id, child_id)
    if not success:
        raise HTTPException(status_code=404, detail="Child relationship not found")
