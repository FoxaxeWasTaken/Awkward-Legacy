"""CRUD operations for Family model."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select, or_, and_
from sqlalchemy.orm import joinedload
from ..models.child import Child

from ..models.family import (
    Family,
    FamilyCreate,
    FamilyUpdate,
    FamilySearchResult,
    FamilyDetailResult,
)


class FamilyCRUD:
    """CRUD operations for Family model."""

    def exists_same_couple(self, db: Session, husband_id: UUID, wife_id: UUID) -> bool:
        """Return True if a family already exists with the same two spouses, order-indifferent.

        Only applies when both spouses are provided. If either is None, returns False.
        """
        if not husband_id or not wife_id:
            return False

        statement = select(Family).where(
            ((Family.husband_id == husband_id) & (Family.wife_id == wife_id))
            | ((Family.husband_id == wife_id) & (Family.wife_id == husband_id))
        )
        return db.exec(statement).first() is not None

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
        statement = (
            select(Family)
            .where((Family.husband_id == spouse_id) | (Family.wife_id == spouse_id))
            .options(
                joinedload(Family.husband),
                joinedload(Family.wife),
                joinedload(Family.events),
            )
        )
        return list(db.exec(statement).unique())

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

    def _get_spouse_names(self, family: Family) -> tuple[Optional[str], Optional[str]]:
        """Get husband and wife names from family."""
        husband_name = None
        wife_name = None
        if family.husband:
            husband_name = (
                f"{family.husband.first_name} {family.husband.last_name}".strip()
            )
        if family.wife:
            wife_name = f"{family.wife.first_name} {family.wife.last_name}".strip()
        return husband_name, wife_name

    def _get_spouse_sex(self, family: Family) -> tuple[Optional[str], Optional[str]]:
        """Get husband and wife sex from family."""
        husband_sex = None
        wife_sex = None
        if family.husband:
            husband_sex = family.husband.sex
        if family.wife:
            wife_sex = family.wife.sex
        return husband_sex, wife_sex

    def _create_family_summary(
        self, husband_name: Optional[str], wife_name: Optional[str], marriage_date
    ) -> str:
        """Create family summary string."""
        summary_parts = []
        if husband_name:
            summary_parts.append(husband_name)
        if wife_name:
            summary_parts.append(wife_name)

        summary = " & ".join(summary_parts) if summary_parts else "Unknown Family"
        if marriage_date:
            summary += f" ({marriage_date.year})"
        return summary

    def _get_family_by_id(
        self, db: Session, family_id: UUID
    ) -> List[FamilySearchResult]:
        """Get specific family by ID."""
        family = db.get(Family, family_id)
        if not family:
            return []

        husband_name, wife_name = self._get_spouse_names(family)
        summary = self._create_family_summary(
            husband_name, wife_name, family.marriage_date
        )

        return [
            FamilySearchResult(
                id=family.id,
                husband_name=husband_name,
                wife_name=wife_name,
                marriage_date=family.marriage_date,
                marriage_place=family.marriage_place,
                children_count=len(family.children),
                summary=summary,
            )
        ]

    def search_families(
        self,
        db: Session,
        query: Optional[str] = None,
        family_id: Optional[UUID] = None,
        limit: int = 20,
    ) -> List[FamilySearchResult]:
        """Search families by name or get by ID."""
        # Import here to avoid circular imports
        from ..models.person import Person  # pylint: disable=import-outside-toplevel

        if family_id:
            return self._get_family_by_id(db, family_id)

        families = self._search_families_by_query(db, query, limit, Person)
        return self._build_search_results(families)

    def _search_families_by_query(
        self, db: Session, query: Optional[str], limit: int, person_model
    ) -> List[Family]:
        """Search families by query or get all families."""
        if query:
            # Search by spouse names - split query into words for multi-word searches
            query_words = query.lower().split()

            # Build conditions for each word
            conditions = []
            for word in query_words:
                conditions.append(
                    or_(
                        person_model.first_name.ilike(
                            f"%{word}%"
                        ),  # pylint: disable=no-member
                        person_model.last_name.ilike(
                            f"%{word}%"
                        ),  # pylint: disable=no-member
                    )
                )

            # Build the query
            statement = (
                select(Family)
                .join(
                    person_model,
                    or_(
                        Family.husband_id == person_model.id,
                        Family.wife_id == person_model.id,
                    ),
                    isouter=True,
                )
                .distinct()
                .limit(limit)
            )

            # Add where clause if we have conditions
            if conditions:
                if len(conditions) == 1:
                    statement = statement.where(conditions[0])
                else:
                    statement = statement.where(and_(*conditions))
        else:
            # Get all families with pagination
            statement = select(Family).limit(limit)

        return list(db.exec(statement))

    def _build_search_results(self, families: List[Family]) -> List[FamilySearchResult]:
        """Build search results from family list."""
        results = []
        for family in families:
            husband_name, wife_name = self._get_spouse_names(family)
            husband_sex, wife_sex = self._get_spouse_sex(family)
            summary = self._create_family_summary(
                husband_name, wife_name, family.marriage_date
            )

            results.append(
                FamilySearchResult(
                    id=family.id,
                    husband_name=husband_name,
                    wife_name=wife_name,
                    husband_sex=husband_sex,
                    wife_sex=wife_sex,
                    marriage_date=family.marriage_date,
                    marriage_place=family.marriage_place,
                    children_count=len(family.children),
                    summary=summary,
                )
            )
        return results

    def get_family_detail(
        self, db: Session, family_id: UUID
    ) -> Optional[FamilyDetailResult]:
        """Get a family with all related data including cross-family connections."""

        statement = (
            select(Family)
            .where(Family.id == family_id)
            .options(
                joinedload(Family.husband),
                joinedload(Family.wife),
                joinedload(Family.children).joinedload(Child.child),
                joinedload(Family.events),
            )
        )
        family = db.exec(statement).first()
        if not family:
            return None

        # Convert related objects to dictionaries
        husband = family.husband.model_dump() if family.husband else None
        wife = family.wife.model_dump() if family.wife else None

        # Include full person data for children and detect cross-family relationships
        children = self._process_children_with_families(db, family.children)

        events = [event.model_dump() for event in family.events]

        return FamilyDetailResult(
            id=family.id,
            husband_id=family.husband_id,
            wife_id=family.wife_id,
            marriage_date=family.marriage_date,
            marriage_place=family.marriage_place,
            notes=family.notes,
            husband=husband,
            wife=wife,
            children=children,
            events=events,
        )

    def _process_children_with_families(self, db: Session, children) -> list:
        """Process children and detect cross-family relationships."""
        processed_children = []
        for child in children:
            child_dict = child.model_dump()
            if child.child:
                child_person = child.child.model_dump()
                self._add_child_family_info(db, child.child, child_person)
                child_dict["person"] = child_person
            processed_children.append(child_dict)
        return processed_children

    def _add_child_family_info(self, db: Session, child_person, child_person_dict):
        """Add family information for a child person."""
        child_families = self.get_by_spouse(db, child_person.id)
        if child_families:
            child_person_dict["has_own_family"] = True
            child_person_dict["own_families"] = []
            for child_family in child_families:
                family_info = self._create_family_info(child_family, child_person)
                child_person_dict["own_families"].append(family_info)
        else:
            child_person_dict["has_own_family"] = False

    def _create_family_info(self, child_family, child_person):
        """Create family information dictionary."""
        family_info = {
            "id": str(child_family.id),
            "marriage_date": (
                child_family.marriage_date.isoformat()
                if child_family.marriage_date
                else None
            ),
            "marriage_place": child_family.marriage_place,
            "spouse": None,
            "events": [event.model_dump() for event in child_family.events],
        }
        self._add_spouse_info(child_family, child_person, family_info)
        return family_info

    def _add_spouse_info(self, child_family, child_person, family_info):
        """Add spouse information to family info."""
        if child_family.husband_id == child_person.id and child_family.wife:
            family_info["spouse"] = {
                "id": child_family.wife.id,
                "name": (
                    f"{child_family.wife.first_name} {child_family.wife.last_name}"
                ),
                "sex": child_family.wife.sex,
            }
        elif child_family.wife_id == child_person.id and child_family.husband:
            family_info["spouse"] = {
                "id": child_family.husband.id,
                "name": (
                    f"{child_family.husband.first_name} {child_family.husband.last_name}"
                ),
                "sex": child_family.husband.sex,
            }


# Create a singleton instance
family_crud = FamilyCRUD()
