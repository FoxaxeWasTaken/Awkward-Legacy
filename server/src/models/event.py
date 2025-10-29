"""Event model definitions for the genealogy application."""

from datetime import date as date_type
from enum import Enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, Relationship, SQLModel, Column

from ..constants import FAMILIES_TABLE_ID, PERSONS_TABLE_ID

if TYPE_CHECKING:
    from .person import Person
    from .family import Family


class EventType(str, Enum):
    """Enumération des types d'événements."""

    # Événements de personne
    BIRTH = "BIRTH"
    BAPTISM = "BAPTISM"
    DEATH = "DEATH"
    BURIAL = "BURIAL"

    # Événements de famille
    MARRIAGE = "MARRIAGE"
    COUPLE = "COUPLE"
    ENGAGEMENT = "ENGAGEMENT"
    DIVORCE = "DIVORCE"
    SEPARATION = "SEPARATION"
    COHABITATION = "COHABITATION"
    MARRIAGE_ANNULMENT = "MARRIAGE_ANNULMENT"

    # Autres événements
    OTHER = "OTHER"


class EventBase(SQLModel):
    """Base Event model with common fields."""

    person_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey(PERSONS_TABLE_ID, ondelete="CASCADE"),
            nullable=True,
        ),
    )
    family_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey(FAMILIES_TABLE_ID, ondelete="CASCADE"),
            nullable=True,
        ),
    )
    # Allow free-text types (including empty string) to support tests
    type: str = Field(max_length=50)
    date: Optional[date_type] = Field(default=None)
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


class EventRead(EventBase):
    """Event model for read responses."""

    id: UUID


class EventUpdate(SQLModel):
    """Event model for update requests."""

    person_id: Optional[UUID] = Field(default=None, foreign_key=PERSONS_TABLE_ID)
    family_id: Optional[UUID] = Field(default=None, foreign_key=FAMILIES_TABLE_ID)
    type: Optional[str] = Field(default=None, max_length=50)
    date: Optional[date_type] = Field(default=None)
    place: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None)
