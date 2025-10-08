"""Database connection and session management."""

import os
from typing import Generator

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://genealogy_user:genealogy_password@localhost:5432/genealogy_db",
)

# Create engine
engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables() -> None:
    """Create database tables if they don't exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session."""
    with Session(engine) as session:
        yield session
