from datetime import date
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .family import Family
    from .event import Event
    from .child import Child


class Sex(str, Enum):
    """Biological sex enumeration."""

    MALE = "M"
    FEMALE = "F"
    UNKNOWN = "U"


class PersonBase(SQLModel):
    """Base Person model with common fields."""

    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    sex: Sex
    birth_date: Optional[date] = Field(default=None)
    death_date: Optional[date] = Field(default=None)
    birth_place: Optional[str] = Field(default=None, max_length=200)
    death_place: Optional[str] = Field(default=None, max_length=200)
    occupation: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None)


class Person(PersonBase, table=True):
    """Person model for database storage."""

    __tablename__ = "persons"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    events: List["Event"] = Relationship(back_populates="person")
    families_as_husband: List["Family"] = Relationship(back_populates="husband")
    families_as_wife: List["Family"] = Relationship(back_populates="wife")
    child_relationships: List["Child"] = Relationship(back_populates="child")


class PersonCreate(PersonBase):
    """Person model for creation requests."""

    pass


class PersonRead(PersonBase):
    """Person model for read responses."""

    id: UUID


class PersonUpdate(SQLModel):
    """Person model for update requests."""

    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    sex: Optional[Sex] = Field(default=None)
    birth_date: Optional[date] = Field(default=None)
    death_date: Optional[date] = Field(default=None)
    birth_place: Optional[str] = Field(default=None, max_length=200)
    death_place: Optional[str] = Field(default=None, max_length=200)
    occupation: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None)
