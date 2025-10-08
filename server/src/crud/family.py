"""CRUD operations for Family model."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from ..models.family import Family, FamilyCreate, FamilyUpdate


class FamilyCRUD:
    """CRUD operations for Family model."""

    def create(self, db: Session, family: FamilyCreate) -> Family:
        """Create a new family."""
        db_family = Family.model_validate(family)
        db.add(db_family)
        db.commit()
        db.refresh(db_family)
        return db_family

    def get(self, db: Session, family_id: UUID) -> Optional[Family]:
        """Get a family by ID."""
        return db.get(Family, family_id)

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Family]:
        """Get all families with pagination."""
        statement = select(Family).offset(skip).limit(limit)
        return list(db.exec(statement))

    def get_by_husband(self, db: Session, husband_id: UUID) -> List[Family]:
        """Get families by husband ID."""
        statement = select(Family).where(Family.husband_id == husband_id)
        return list(db.exec(statement))

    def get_by_wife(self, db: Session, wife_id: UUID) -> List[Family]:
        """Get families by wife ID."""
        statement = select(Family).where(Family.wife_id == wife_id)
        return list(db.exec(statement))

    def get_by_spouse(self, db: Session, spouse_id: UUID) -> List[Family]:
        """Get families by spouse ID (either husband or wife)."""
        statement = select(Family).where(
            (Family.husband_id == spouse_id) | (Family.wife_id == spouse_id)
        )
        return list(db.exec(statement))

    def update(
        self, db: Session, family_id: UUID, family_update: FamilyUpdate
    ) -> Optional[Family]:
        """Update a family."""
        db_family = db.get(Family, family_id)
        if not db_family:
            return None

        family_data = family_update.model_dump(exclude_unset=True)
        for field, value in family_data.items():
            setattr(db_family, field, value)

        db.add(db_family)
        db.commit()
        db.refresh(db_family)
        return db_family

    def delete(self, db: Session, family_id: UUID) -> bool:
        """Delete a family."""
        db_family = db.get(Family, family_id)
        if not db_family:
            return False

        db.delete(db_family)
        db.commit()
        return True


# Create a singleton instance
family_crud = FamilyCRUD()
