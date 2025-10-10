"""Child relationship model definitions for the genealogy application."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, Relationship, SQLModel, Column

from ..constants import FAMILIES_TABLE_ID, PERSONS_TABLE_ID

if TYPE_CHECKING:
    from .family import Family
    from .person import Person


class ChildBase(SQLModel):
    """Base Child model with common fields."""

    family_id: UUID = Field(foreign_key=FAMILIES_TABLE_ID)
    child_id: UUID = Field(foreign_key=PERSONS_TABLE_ID)


class Child(ChildBase, table=True):
    """Child model for database storage."""

    __tablename__ = "children"

    family_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey(FAMILIES_TABLE_ID, ondelete="CASCADE"),
            primary_key=True,
        )
    )
    child_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey(PERSONS_TABLE_ID, ondelete="CASCADE"),
            primary_key=True,
        )
    )

    family: "Family" = Relationship(back_populates="children")
    child: "Person" = Relationship(back_populates="child_relationships")


class ChildCreate(ChildBase):
    """Child model for creation requests."""


class ChildRead(ChildBase):
    """Child model for read responses."""
