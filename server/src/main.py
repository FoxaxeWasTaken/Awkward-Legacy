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
    lifespan=lifespan,
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

@app.get("/health")
def health_check(session: Session = Depends(get_session)):
    """Health check endpoint to verify database connectivity."""
    try:
        session.exec(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
