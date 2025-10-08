"""Family model for genealogy data."""

from datetime import date
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    from .person import Person
    from .event import Event


class FamilyBase(SQLModel):
    """Base Family model with common fields."""

    husband_id: Optional[UUID] = Field(default=None, foreign_key="persons.id")
    wife_id: Optional[UUID] = Field(default=None, foreign_key="persons.id")
    marriage_date: Optional[date] = Field(default=None)
    marriage_place: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None)


class Family(FamilyBase, table=True):
    """Family model for database storage."""

    __tablename__ = "families"

    id: UUID = Field(default_factory=uuid4, primary_key=True)


class FamilyCreate(FamilyBase):
    """Family model for creation requests."""

    pass


class FamilyRead(FamilyBase):
    """Family model for read responses."""

    id: UUID


class FamilyUpdate(SQLModel):
    """Family model for update requests."""

    husband_id: Optional[UUID] = Field(default=None, foreign_key="persons.id")
    wife_id: Optional[UUID] = Field(default=None, foreign_key="persons.id")
    marriage_date: Optional[date] = Field(default=None)
    marriage_place: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None)
