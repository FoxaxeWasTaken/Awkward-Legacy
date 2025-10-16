"""Main FastAPI application module."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .db import create_db_and_tables, get_session
from .endpoints.person import router as person_router
from .endpoints.family import router as family_router
from .endpoints.child import router as child_router
from .endpoints.event import router as event_router
from .endpoints.files import router as files_router

ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://client-dev:5173"
).split(",")
ALLOWED_METHODS = os.getenv("CORS_METHODS", "*").split(",")
ALLOWED_HEADERS = os.getenv("CORS_HEADERS", "*").split(",")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Handle application lifespan events."""
    create_db_and_tables()
    yield


app = FastAPI(
    title="Genealogy API",
    description="A modern genealogy application API with PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)

app.include_router(person_router)
app.include_router(family_router)
app.include_router(child_router)
app.include_router(event_router)
app.include_router(files_router)


@app.get("/")
def read_root():
    """Return a simple greeting message."""
    return {
        "Hello": "World",
        "message": "Genealogy API is running!",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


@app.get("/health")
def health_check(session: Session = Depends(get_session)):
    """Health check endpoint to verify database connectivity."""
    try:
        session.exec(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except SQLAlchemyError as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
