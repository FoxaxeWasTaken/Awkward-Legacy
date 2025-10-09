import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "Hello": "World",
        "message": "Genealogy API is running!",
        "docs": "/docs",
        "health": "/health",
    }


def test_read_item_no_query():
    response = client.get("/items/42")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "q": None}


def test_read_item_with_query():
    response = client.get("/items/99?q=test")
    assert response.status_code == 200
    assert response.json() == {"item_id": 99, "q": "test"}
