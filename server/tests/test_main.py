import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "Hello": "World",
        "message": "Geneweb API is running!",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "database": "connected",
    }
