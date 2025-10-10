"""CRUD operations for Child model."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from ..models.child import Child, ChildCreate


class ChildCRUD:
    """CRUD operations for Child model."""

    def create(self, db: Session, child: ChildCreate) -> Child:
        """Create a new child relationship."""
        db_child = Child.model_validate(child)
        db.add(db_child)
        db.commit()
        db.refresh(db_child)
        return db_child

    def get(self, db: Session, family_id: UUID, child_id: UUID) -> Optional[Child]:
        """Get a child relationship by family and child IDs."""
        statement = select(Child).where(
            Child.family_id == family_id, Child.child_id == child_id
        )
        return db.exec(statement).first()

    def get_by_family(self, db: Session, family_id: UUID) -> List[Child]:
        """Get all children of a family."""
        statement = select(Child).where(Child.family_id == family_id)
        return list(db.exec(statement))

    def get_by_child(self, db: Session, child_id: UUID) -> List[Child]:
        """Get all families where a person is a child."""
        statement = select(Child).where(Child.child_id == child_id)
        return list(db.exec(statement))

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Child]:
        """Get all child relationships with pagination."""
        statement = select(Child).offset(skip).limit(limit)
        return list(db.exec(statement))

    def delete(self, db: Session, family_id: UUID, child_id: UUID) -> bool:
        """Delete a child relationship."""
        statement = select(Child).where(
            Child.family_id == family_id, Child.child_id == child_id
        )
        db_child = db.exec(statement).first()
        if not db_child:
            return False

        db.delete(db_child)
        db.commit()
        return True

    def delete_by_family(self, db: Session, family_id: UUID) -> int:
        """Delete all child relationships for a family."""
        statement = select(Child).where(Child.family_id == family_id)
        children = list(db.exec(statement))
        for child in children:
            db.delete(child)
        db.commit()
        return len(children)

    def delete_by_child(self, db: Session, child_id: UUID) -> int:
        """Delete all family relationships for a child."""
        statement = select(Child).where(Child.child_id == child_id)
        children = list(db.exec(statement))
        for child in children:
            db.delete(child)
        db.commit()
        return len(children)


# Create a singleton instance
child_crud = ChildCRUD()
