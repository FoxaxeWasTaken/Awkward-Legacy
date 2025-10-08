from datetime import date
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .person import Person
    from .family import Family


class EventBase(SQLModel):
    """Base Event model with common fields."""

    person_id: Optional[UUID] = Field(default=None, foreign_key="persons.id")
    family_id: Optional[UUID] = Field(default=None, foreign_key="families.id")
    type: str = Field(max_length=50)
    date: Optional[date] = Field(default=None)
    place: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None)


class Event(EventBase, table=True):
    """Event model for database storage."""

    __tablename__ = "events"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    person: Optional["Person"] = Relationship(back_populates="events")
    family: Optional["Family"] = Relationship(back_populates="events")


class EventCreate(EventBase):
    """Event model for creation requests."""

    pass


class EventRead(EventBase):
    """Event model for read responses."""

    id: UUID


class EventUpdate(SQLModel):
    """Event model for update requests."""

    person_id: Optional[UUID] = Field(default=None, foreign_key="persons.id")
    family_id: Optional[UUID] = Field(default=None, foreign_key="families.id")
    type: Optional[str] = Field(default=None, max_length=50)
    date: Optional[date] = Field(default=None)
    place: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None)
