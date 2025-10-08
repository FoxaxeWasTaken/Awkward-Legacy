"""Main FastAPI application module."""

from fastapi import FastAPI, Depends
from sqlmodel import Session

from .db import create_db_and_tables, get_session

app = FastAPI(
    title="Genealogy API",
    description="A modern genealogy application API with PostgreSQL",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    """Initialize database tables on application startup."""
    create_db_and_tables()


@app.get("/")
def read_root():
    """Return a simple greeting message."""
    return {
        "Hello": "World",
        "message": "Genealogy API is running!",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    """Return item information with optional query parameter."""
    return {"item_id": item_id, "q": q}
