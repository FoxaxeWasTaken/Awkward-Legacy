"""Family model definitions for the genealogy application."""

from datetime import date as date_type
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from ..constants import PERSONS_TABLE_ID

if TYPE_CHECKING:
    from .person import Person
    from .event import Event
    from .child import Child


class FamilyBase(SQLModel):
    """Base Family model with common fields."""

    husband_id: Optional[UUID] = Field(default=None, foreign_key=PERSONS_TABLE_ID)
    wife_id: Optional[UUID] = Field(default=None, foreign_key=PERSONS_TABLE_ID)
    marriage_date: Optional[date_type] = Field(default=None)
    marriage_place: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None)


class Family(FamilyBase, table=True):
    """Family model for database storage."""

    __tablename__ = "families"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    husband: Optional["Person"] = Relationship(
        back_populates="families_as_husband",
        sa_relationship_kwargs={"foreign_keys": "[Family.husband_id]"},
    )
    wife: Optional["Person"] = Relationship(
        back_populates="families_as_wife",
        sa_relationship_kwargs={"foreign_keys": "[Family.wife_id]"},
    )
    events: List["Event"] = Relationship(
        back_populates="family",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    children: List["Child"] = Relationship(
        back_populates="family",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class FamilyCreate(FamilyBase):
    """Family model for creation requests."""


class FamilyRead(FamilyBase):
    """Family model for read responses."""

    id: UUID


class FamilyUpdate(SQLModel):
    """Family model for update requests."""

    husband_id: Optional[UUID] = Field(default=None, foreign_key=PERSONS_TABLE_ID)
    wife_id: Optional[UUID] = Field(default=None, foreign_key=PERSONS_TABLE_ID)
    marriage_date: Optional[date_type] = Field(default=None)
    marriage_place: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None)


class FamilySearchResult(SQLModel):
    """Family model for search results."""

    id: UUID
    husband_name: Optional[str] = None
    wife_name: Optional[str] = None
    husband_sex: Optional[str] = None  # M, F, or U
    wife_sex: Optional[str] = None  # M, F, or U
    marriage_date: Optional[date_type] = None
    marriage_place: Optional[str] = None
    children_count: int = 0
    summary: str  # Human-readable summary like "John Doe & Jane Smith (1920)"


class FamilyDetailResult(FamilyRead):
    """Family model for detailed responses with related data."""

    husband: Optional[dict] = None
    wife: Optional[dict] = None
    children: List[dict] = []
    events: List[dict] = []
