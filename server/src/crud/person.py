"""CRUD operations for Person model."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select, col

from ..models.person import Person, PersonCreate, PersonUpdate


class PersonCRUD:
    """CRUD operations for Person model."""

    def create(self, db: Session, person: PersonCreate) -> Person:
        """Create a new person."""
        db_person = Person.model_validate(person)
        db.add(db_person)
        db.commit()
        db.refresh(db_person)
        return db_person

    def get(self, db: Session, person_id: UUID) -> Optional[Person]:
        """Get a person by ID."""
        return db.get(Person, person_id)

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Person]:
        """Get all persons with pagination."""
        statement = select(Person).offset(skip).limit(limit)
        return list(db.exec(statement))

    def get_by_name(self, db: Session, first_name: str, last_name: str) -> List[Person]:
        """Get persons by first and last name."""
        statement = select(Person).where(
            Person.first_name == first_name, Person.last_name == last_name
        )
        return list(db.exec(statement))

    def search_by_name(self, db: Session, name: str) -> List[Person]:
        """Search persons by name (first or last name contains the search term, case-sensitive)."""
        # The col() function from SQLModel does return an object with a contains() method, pylint just can't detect it through static analysis.
        statement = select(Person).where(
            (
                col(Person.first_name).contains(name, autoescape=True)
            )  # pylint: disable=no-member
            | (
                col(Person.last_name).contains(name, autoescape=True)
            )  # pylint: disable=no-member
        )
        return list(db.exec(statement))

    def update(
        self, db: Session, person_id: UUID, person_update: PersonUpdate
    ) -> Optional[Person]:
        """Update a person."""
        db_person = db.get(Person, person_id)
        if not db_person:
            return None

        person_data = person_update.model_dump(exclude_unset=True)
        for field, value in person_data.items():
            setattr(db_person, field, value)

        db.add(db_person)
        db.commit()
        db.refresh(db_person)
        return db_person

    def delete(self, db: Session, person_id: UUID) -> bool:
        """Delete a person."""
        db_person = db.get(Person, person_id)
        if not db_person:
            return False

        db.delete(db_person)
        db.commit()
        return True


# Create a singleton instance
person_crud = PersonCRUD()
