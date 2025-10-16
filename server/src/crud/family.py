"""CRUD operations for Family model."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select, or_, and_

from ..models.family import Family, FamilyCreate, FamilyUpdate, FamilySearchResult, FamilyDetailResult


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

    def search_families(
        self, 
        db: Session, 
        query: Optional[str] = None, 
        family_id: Optional[UUID] = None,
        limit: int = 20
    ) -> List[FamilySearchResult]:
        """Search families by name or get by ID."""
        from ..models.person import Person
        
        if family_id:
            # Get specific family by ID
            family = db.get(Family, family_id)
            if not family:
                return []
            
            # Get spouse names
            husband_name = None
            wife_name = None
            if family.husband:
                husband_name = f"{family.husband.first_name} {family.husband.last_name}".strip()
            if family.wife:
                wife_name = f"{family.wife.first_name} {family.wife.last_name}".strip()
            
            # Create summary
            summary_parts = []
            if husband_name:
                summary_parts.append(husband_name)
            if wife_name:
                summary_parts.append(wife_name)
            
            summary = " & ".join(summary_parts) if summary_parts else "Unknown Family"
            if family.marriage_date:
                summary += f" ({family.marriage_date.year})"
            
            return [FamilySearchResult(
                id=family.id,
                husband_name=husband_name,
                wife_name=wife_name,
                marriage_date=family.marriage_date,
                marriage_place=family.marriage_place,
                children_count=len(family.children),
                summary=summary
            )]
        
        if query:
            # Search by spouse names - split query into words for multi-word searches
            query_words = query.lower().split()
            
            # Build conditions for each word
            conditions = []
            for word in query_words:
                conditions.append(
                    or_(
                        Person.first_name.ilike(f"%{word}%"),
                        Person.last_name.ilike(f"%{word}%")
                    )
                )
            
            statement = (
                select(Family)
                .join(Person, or_(Family.husband_id == Person.id, Family.wife_id == Person.id), isouter=True)
                .where(and_(*conditions) if len(conditions) > 1 else conditions[0])
                .distinct()
                .limit(limit)
            )
        else:
            # Get all families with pagination
            statement = select(Family).limit(limit)
        
        families = list(db.exec(statement))
        results = []
        
        for family in families:
            # Get spouse names
            husband_name = None
            wife_name = None
            if family.husband:
                husband_name = f"{family.husband.first_name} {family.husband.last_name}".strip()
            if family.wife:
                wife_name = f"{family.wife.first_name} {family.wife.last_name}".strip()
            
            # Create summary
            summary_parts = []
            if husband_name:
                summary_parts.append(husband_name)
            if wife_name:
                summary_parts.append(wife_name)
            
            summary = " & ".join(summary_parts) if summary_parts else "Unknown Family"
            if family.marriage_date:
                summary += f" ({family.marriage_date.year})"
            
            results.append(FamilySearchResult(
                id=family.id,
                husband_name=husband_name,
                wife_name=wife_name,
                marriage_date=family.marriage_date,
                marriage_place=family.marriage_place,
                children_count=len(family.children),
                summary=summary
            ))
        
        return results

    def get_family_detail(self, db: Session, family_id: UUID) -> Optional[FamilyDetailResult]:
        """Get a family with all related data including cross-family connections."""
        family = db.get(Family, family_id)
        if not family:
            return None
        
        # Convert related objects to dictionaries
        husband = family.husband.model_dump() if family.husband else None
        wife = family.wife.model_dump() if family.wife else None
        
        # Include full person data for children and detect cross-family relationships
        children = []
        for child in family.children:
            child_dict = child.model_dump()
            if child.child:
                child_person = child.child.model_dump()
                
                # Check if this child has their own family (cross-family connection)
                child_families = self.get_by_spouse(db, child.child.id)
                if child_families:
                    # Add information about the child's own family
                    child_person['has_own_family'] = True
                    child_person['own_families'] = []
                    for child_family in child_families:
                        family_info = {
                            'id': str(child_family.id),
                            'marriage_date': child_family.marriage_date.isoformat() if child_family.marriage_date else None,
                            'marriage_place': child_family.marriage_place,
                            'spouse': None
                        }
                        
                        # Get spouse information
                        if child_family.husband_id == child.child.id and child_family.wife:
                            family_info['spouse'] = {
                                'id': child_family.wife.id,
                                'name': f"{child_family.wife.first_name} {child_family.wife.last_name}",
                                'sex': child_family.wife.sex
                            }
                        elif child_family.wife_id == child.child.id and child_family.husband:
                            family_info['spouse'] = {
                                'id': child_family.husband.id,
                                'name': f"{child_family.husband.first_name} {child_family.husband.last_name}",
                                'sex': child_family.husband.sex
                            }
                        
                        child_person['own_families'].append(family_info)
                else:
                    child_person['has_own_family'] = False
                
                child_dict['person'] = child_person
            children.append(child_dict)
        
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
            events=events
        )


# Create a singleton instance
family_crud = FamilyCRUD()
