"""Main FastAPI application module."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import Session

from .db import create_db_and_tables, get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application lifespan events."""
    create_db_and_tables()
    yield


app = FastAPI(
    title="Genealogy API",
    description="A modern genealogy application API with PostgreSQL",
    version="1.0.0",
)


@app.get("/")
def read_root():
    """Return a simple greeting message."""
    return {
        "Hello": "World",
        "message": "Genealogy API is running!",
        "docs": "/docs",
        "health": "/health",
    }
