from datetime import date as date_type
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .person import Person
    from .event import Event
    from .child import Child


class FamilyBase(SQLModel):
    """Base Family model with common fields."""

    husband_id: Optional[UUID] = Field(default=None, foreign_key="persons.id")
    wife_id: Optional[UUID] = Field(default=None, foreign_key="persons.id")
    marriage_date: Optional[date_type] = Field(default=None)
    marriage_place: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None)


class Family(FamilyBase, table=True):
    """Family model for database storage."""

    __tablename__ = "families"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    husband: Optional["Person"] = Relationship(back_populates="families_as_husband")
    wife: Optional["Person"] = Relationship(back_populates="families_as_wife")
    events: List["Event"] = Relationship(back_populates="family")
    children: List["Child"] = Relationship(back_populates="family")


class FamilyCreate(FamilyBase):
    """Family model for creation requests."""

    pass


class FamilyRead(FamilyBase):
    """Family model for read responses."""

    id: UUID


class FamilyUpdate(SQLModel):
    """Family model for update requests."""

    husband_id: Optional[UUID] = Field(default=None)
    wife_id: Optional[UUID] = Field(default=None)
    marriage_date: Optional[date_type] = Field(default=None)
    marriage_place: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
