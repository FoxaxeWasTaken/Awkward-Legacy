"""Main FastAPI application module."""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    """Return a simple greeting message."""
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    """Return item information with optional query parameter."""
    return {"item_id": item_id, "q": q}
