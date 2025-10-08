"""Main FastAPI application module."""

from fastapi import FastAPI, Depends
from sqlmodel import Session

from .db import create_db_and_tables, get_session
from .api.persons import router as persons_router

app = FastAPI(
    title="Genealogy API",
    description="A modern genealogy application API with PostgreSQL backend",
    version="1.0.0",
)

# Include API routers
app.include_router(persons_router)


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


@app.get("/health")
def health_check(db: Session = Depends(get_session)):
    """Health check endpoint that verifies database connectivity."""
    try:
        # Simple query to test database connection
        db.exec("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    """Return item information with optional query parameter."""
    return {"item_id": item_id, "q": q}
