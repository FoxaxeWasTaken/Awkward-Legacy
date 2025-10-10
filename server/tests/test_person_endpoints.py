from datetime import date
from uuid import uuid4
import pytest
from sqlmodel import Session

from src.models.person import Person, PersonCreate, Sex
from src.crud.person import person_crud


@pytest.fixture
def sample_person_data():
    """Sample person data for tests."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "sex": "M",
        "birth_date": "1990-01-15",
        "birth_place": "New York",
        "occupation": "Engineer",
    }


@pytest.fixture
def sample_person_data_2():
    """Second sample person data for tests."""
    return {
        "first_name": "Jane",
        "last_name": "Smith",
        "sex": "F",
        "birth_date": "1992-05-20",
        "death_date": "2020-12-31",
        "birth_place": "London",
        "death_place": "Paris",
        "occupation": "Doctor",
        "notes": "Notable achievements",
    }


class TestPersonCreate:
    """Test creating persons via API endpoint."""

    def test_create_person_success(self, client, sample_person_data):
        """Test successful person creation."""
        response = client.post("/api/v1/persons", json=sample_person_data)
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == sample_person_data["first_name"]
        assert data["last_name"] == sample_person_data["last_name"]
        assert data["sex"] == sample_person_data["sex"]
        assert "id" in data

    def test_create_person_minimal_data(self, client):
        """Test creating person with minimal required data."""
        minimal_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "sex": "F",
        }
        response = client.post("/api/v1/persons", json=minimal_data)
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == minimal_data["first_name"]
        assert data["last_name"] == minimal_data["last_name"]

    def test_create_person_with_all_fields(self, client, sample_person_data_2):
        """Test creating person with all possible fields."""
        response = client.post("/api/v1/persons", json=sample_person_data_2)
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == sample_person_data_2["first_name"]
        assert data["notes"] == sample_person_data_2["notes"]

    def test_create_person_invalid_sex(self, client):
        """Test creating person with invalid sex value."""
        invalid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "sex": "X",
        }
        response = client.post("/api/v1/persons", json=invalid_data)
        assert response.status_code == 422

    def test_create_person_missing_required_field(self, client):
        """Test creating person without required fields."""
        incomplete_data = {
            "first_name": "John",
        }
        response = client.post("/api/v1/persons", json=incomplete_data)
        assert response.status_code == 422

    def test_create_person_invalid_date_format(self, client):
        """Test creating person with invalid date format."""
        invalid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "sex": "M",
            "birth_date": "invalid-date",
        }
        response = client.post("/api/v1/persons", json=invalid_data)
        assert response.status_code == 422


class TestPersonRead:
    """Test reading persons via API endpoint."""

    def test_get_person_by_id_success(self, client, sample_person_data):
        """Test successfully getting a person by ID."""
        create_response = client.post("/api/v1/persons", json=sample_person_data)
        person_id = create_response.json()["id"]

        response = client.get(f"/api/v1/persons/{person_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == person_id
        assert data["first_name"] == sample_person_data["first_name"]

    def test_get_person_by_id_not_found(self, client):
        """Test getting a non-existent person."""
        non_existent_id = str(uuid4())
        response = client.get(f"/api/v1/persons/{non_existent_id}")
        assert response.status_code == 404

    def test_get_person_invalid_uuid(self, client):
        """Test getting a person with invalid UUID format."""
        response = client.get("/api/v1/persons/invalid-uuid")
        assert response.status_code == 422

    def test_get_all_persons_empty(self, client):
        """Test getting all persons when database is empty."""
        response = client.get("/api/v1/persons")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_all_persons_with_data(
        self, client, sample_person_data, sample_person_data_2
    ):
        """Test getting all persons with multiple records."""
        client.post("/api/v1/persons", json=sample_person_data)
        client.post("/api/v1/persons", json=sample_person_data_2)

        response = client.get("/api/v1/persons")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_get_all_persons_with_pagination(self, client, sample_person_data):
        """Test getting all persons with pagination parameters."""
        for i in range(5):
            data = sample_person_data.copy()
            data["first_name"] = f"Person{i}"
            client.post("/api/v1/persons", json=data)

        response = client.get("/api/v1/persons?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2


class TestPersonSearch:
    """Test searching persons via API endpoint."""

    def test_search_by_name(self, client, sample_person_data):
        """Test searching persons by name."""
        client.post("/api/v1/persons", json=sample_person_data)

        response = client.get(
            f"/api/v1/persons/search?name={sample_person_data['first_name']}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any(p["first_name"] == sample_person_data["first_name"] for p in data)

    def test_search_by_partial_name(self, client, sample_person_data):
        """Test searching persons by partial name match."""
        client.post("/api/v1/persons", json=sample_person_data)

        response = client.get("/api/v1/persons/search?name=Joh")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_search_no_results(self, client):
        """Test searching with no matching results."""
        response = client.get("/api/v1/persons/search?name=NonExistent")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_by_exact_name(self, client, sample_person_data):
        """Test getting persons by exact first and last name."""
        client.post("/api/v1/persons", json=sample_person_data)

        response = client.get(
            f"/api/v1/persons/by-name?first_name={sample_person_data['first_name']}"
            f"&last_name={sample_person_data['last_name']}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["first_name"] == sample_person_data["first_name"]
        assert data[0]["last_name"] == sample_person_data["last_name"]


class TestPersonUpdate:
    """Test updating persons via API endpoint."""

    def test_update_person_success(self, client, sample_person_data):
        """Test successfully updating a person."""
        create_response = client.post("/api/v1/persons", json=sample_person_data)
        person_id = create_response.json()["id"]

        update_data = {"first_name": "UpdatedName", "occupation": "Updated Occupation"}
        response = client.patch(f"/api/v1/persons/{person_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "UpdatedName"
        assert data["occupation"] == "Updated Occupation"
        assert data["last_name"] == sample_person_data["last_name"]

    def test_update_person_partial(self, client, sample_person_data):
        """Test partial update of person."""
        create_response = client.post("/api/v1/persons", json=sample_person_data)
        person_id = create_response.json()["id"]

        update_data = {"notes": "Added notes"}
        response = client.patch(f"/api/v1/persons/{person_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Added notes"

    def test_update_person_not_found(self, client):
        """Test updating a non-existent person."""
        non_existent_id = str(uuid4())
        update_data = {"first_name": "Updated"}
        response = client.patch(f"/api/v1/persons/{non_existent_id}", json=update_data)
        assert response.status_code == 404

    def test_update_person_invalid_data(self, client, sample_person_data):
        """Test updating person with invalid data."""
        create_response = client.post("/api/v1/persons", json=sample_person_data)
        person_id = create_response.json()["id"]

        update_data = {"sex": "INVALID"}
        response = client.patch(f"/api/v1/persons/{person_id}", json=update_data)
        assert response.status_code == 422

    def test_update_person_empty_data(self, client, sample_person_data):
        """Test updating person with empty data."""
        create_response = client.post("/api/v1/persons", json=sample_person_data)
        person_id = create_response.json()["id"]

        response = client.patch(f"/api/v1/persons/{person_id}", json={})
        assert response.status_code == 200


class TestPersonDelete:
    """Test deleting persons via API endpoint."""

    def test_delete_person_success(self, client, sample_person_data):
        """Test successfully deleting a person."""
        create_response = client.post("/api/v1/persons", json=sample_person_data)
        person_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/persons/{person_id}")
        assert response.status_code == 204

        get_response = client.get(f"/api/v1/persons/{person_id}")
        assert get_response.status_code == 404

    def test_delete_person_not_found(self, client):
        """Test deleting a non-existent person."""
        non_existent_id = str(uuid4())
        response = client.delete(f"/api/v1/persons/{non_existent_id}")
        assert response.status_code == 404

    def test_delete_person_invalid_uuid(self, client):
        """Test deleting person with invalid UUID."""
        response = client.delete("/api/v1/persons/invalid-uuid")
        assert response.status_code == 422


class TestPersonEdgeCases:
    """Test edge cases for person endpoints."""

    def test_create_person_with_future_birth_date(self, client):
        """Test creating person with future birth date (should fail)."""
        future_data = {
            "first_name": "Future",
            "last_name": "Person",
            "sex": "M",
            "birth_date": "2099-01-01",
        }
        response = client.post("/api/v1/persons", json=future_data)
        assert response.status_code in [400, 422]
        assert (
            "future" in response.json()["detail"].lower()
            or "invalid" in response.json()["detail"].lower()
        )

    def test_create_person_death_before_birth(self, client):
        """Test creating person with death date before birth date (should fail)."""
        invalid_data = {
            "first_name": "Invalid",
            "last_name": "Person",
            "sex": "M",
            "birth_date": "2000-01-01",
            "death_date": "1999-01-01",
        }
        response = client.post("/api/v1/persons", json=invalid_data)
        assert response.status_code in [400, 422]
        assert (
            "death" in response.json()["detail"].lower()
            or "birth" in response.json()["detail"].lower()
        )

    def test_create_person_very_long_name(self, client):
        """Test creating person with very long name."""
        long_name_data = {
            "first_name": "A" * 200,
            "last_name": "Doe",
            "sex": "M",
        }
        response = client.post("/api/v1/persons", json=long_name_data)
        assert response.status_code == 422

    def test_special_characters_in_name(self, client):
        """Test creating person with special characters in name."""
        special_data = {
            "first_name": "Jean-François",
            "last_name": "O'Connor",
            "sex": "M",
        }
        response = client.post("/api/v1/persons", json=special_data)
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == special_data["first_name"]
        assert data["last_name"] == special_data["last_name"]

    def test_unicode_characters_in_name(self, client):
        """Test creating person with Unicode characters."""
        unicode_data = {
            "first_name": "李",
            "last_name": "明",
            "sex": "M",
        }
        response = client.post("/api/v1/persons", json=unicode_data)
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == unicode_data["first_name"]

    def test_create_person_with_valid_death_date(self, client):
        """Test creating person with valid death date (after birth)."""
        valid_data = {
            "first_name": "Deceased",
            "last_name": "Person",
            "sex": "F",
            "birth_date": "1920-01-01",
            "death_date": "2010-12-31",
        }
        response = client.post("/api/v1/persons", json=valid_data)
        assert response.status_code == 201
        data = response.json()
        assert data["birth_date"] == valid_data["birth_date"]
        assert data["death_date"] == valid_data["death_date"]

    def test_create_person_with_unknown_sex(self, client):
        """Test creating person with unknown sex (U)."""
        unknown_sex_data = {
            "first_name": "Unknown",
            "last_name": "Person",
            "sex": "U",
        }
        response = client.post("/api/v1/persons", json=unknown_sex_data)
        assert response.status_code == 201
        data = response.json()
        assert data["sex"] == "U"

    def test_update_person_death_before_birth(self, client, sample_person_data):
        """Test updating person to have death before birth (should fail)."""
        create_response = client.post("/api/v1/persons", json=sample_person_data)
        person_id = create_response.json()["id"]

        update_data = {"death_date": "1980-01-01"}
        response = client.patch(f"/api/v1/persons/{person_id}", json=update_data)
        assert response.status_code in [400, 422]
        assert (
            "death" in response.json()["detail"].lower()
            or "birth" in response.json()["detail"].lower()
        )

    def test_update_person_birth_to_future(self, client, sample_person_data):
        """Test updating person birth date to future (should fail)."""
        create_response = client.post("/api/v1/persons", json=sample_person_data)
        person_id = create_response.json()["id"]

        update_data = {"birth_date": "2099-01-01"}
        response = client.patch(f"/api/v1/persons/{person_id}", json=update_data)
        assert response.status_code in [400, 422]
        assert (
            "future" in response.json()["detail"].lower()
            or "invalid" in response.json()["detail"].lower()
        )

    def test_create_person_with_empty_names(self, client):
        """Test creating person with empty string names (should fail)."""
        empty_name_data = {
            "first_name": "",
            "last_name": "Doe",
            "sex": "M",
        }
        response = client.post("/api/v1/persons", json=empty_name_data)
        assert response.status_code == 422
