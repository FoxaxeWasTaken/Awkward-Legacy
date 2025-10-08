"""Child association model for many-to-many Family ↔ Person relationship."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    from .family import Family
    from .person import Person


class ChildBase(SQLModel):
    """Base Child model with common fields."""

    family_id: UUID = Field(foreign_key="families.id")
    child_id: UUID = Field(foreign_key="persons.id")


class Child(ChildBase, table=True):
    """Child model for database storage."""

    __tablename__ = "children"

    # Composite primary key
    family_id: UUID = Field(primary_key=True, foreign_key="families.id")
    child_id: UUID = Field(primary_key=True, foreign_key="persons.id")


class ChildCreate(ChildBase):
    """Child model for creation requests."""

    pass


class ChildRead(ChildBase):
    """Child model for read responses."""

    pass
