"""Test cases for Event API endpoints."""

from datetime import date
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_person(client):
    """Create a sample person for event tests."""
    return client.post(
        "/api/v1/persons",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "sex": "M",
            "birth_date": "1980-01-01",
        },
    ).json()


@pytest.fixture
def sample_family(client):
    """Create a sample family for event tests."""
    husband = client.post(
        "/api/v1/persons",
        json={"first_name": "John", "last_name": "Doe", "sex": "M"},
    ).json()

    wife = client.post(
        "/api/v1/persons",
        json={"first_name": "Jane", "last_name": "Smith", "sex": "F"},
    ).json()

    return client.post(
        "/api/v1/families",
        json={"husband_id": husband["id"], "wife_id": wife["id"]},
    ).json()


@pytest.fixture
def sample_event_data(sample_person):
    """Sample event data for tests."""
    return {
        "person_id": sample_person["id"],
        "type": "Birth",
        "date": "1980-01-01",
        "place": "New York",
        "description": "Born in New York Hospital",
    }


@pytest.fixture
def sample_family_event_data(sample_family):
    """Sample family event data for tests."""
    return {
        "family_id": sample_family["id"],
        "type": "Marriage",
        "date": "2005-06-20",
        "place": "Las Vegas",
        "description": "Wedding ceremony",
    }


class TestEventCreate:
    """Test creating events via API endpoint."""

    def test_create_person_event_success(self, client, sample_event_data):
        """Test successful person event creation."""
        response = client.post("/api/v1/events", json=sample_event_data)
        assert response.status_code == 201
        data = response.json()
        assert data["person_id"] == sample_event_data["person_id"]
        assert data["type"] == sample_event_data["type"]
        assert "id" in data

    def test_create_family_event_success(self, client, sample_family_event_data):
        """Test successful family event creation."""
        response = client.post("/api/v1/events", json=sample_family_event_data)
        assert response.status_code == 201
        data = response.json()
        assert data["family_id"] == sample_family_event_data["family_id"]
        assert data["type"] == sample_family_event_data["type"]

    def test_create_event_without_person_or_family(self, client):
        """Test creating event without person or family (should fail)."""
        minimal_data = {"type": "Custom Event"}
        response = client.post("/api/v1/events", json=minimal_data)
        # An event must be associated with either a person or a family
        assert response.status_code in [400, 422]
        assert (
            "person" in response.json()["detail"].lower()
            or "family" in response.json()["detail"].lower()
            or "required" in response.json()["detail"].lower()
        )

    def test_create_event_with_all_fields(self, client, sample_event_data):
        """Test creating event with all possible fields."""
        response = client.post("/api/v1/events", json=sample_event_data)
        assert response.status_code == 201
        data = response.json()
        assert data["date"] == sample_event_data["date"]
        assert data["place"] == sample_event_data["place"]
        assert data["description"] == sample_event_data["description"]

    def test_create_event_missing_type(self, client, sample_person):
        """Test creating event without type field."""
        incomplete_data = {"person_id": sample_person["id"]}
        response = client.post("/api/v1/events", json=incomplete_data)
        assert response.status_code == 422

    def test_create_event_invalid_person_id(self, client):
        """Test creating event with non-existent person."""
        invalid_data = {
            "person_id": str(uuid4()),
            "type": "Birth",
        }
        response = client.post("/api/v1/events", json=invalid_data)
        assert response.status_code in [400, 404, 422]

    def test_create_event_invalid_family_id(self, client):
        """Test creating event with non-existent family."""
        invalid_data = {
            "family_id": str(uuid4()),
            "type": "Marriage",
        }
        response = client.post("/api/v1/events", json=invalid_data)
        assert response.status_code in [400, 404, 422]

    def test_create_event_invalid_date_format(self, client, sample_person):
        """Test creating event with invalid date format."""
        invalid_data = {
            "person_id": sample_person["id"],
            "type": "Birth",
            "date": "invalid-date",
        }
        response = client.post("/api/v1/events", json=invalid_data)
        assert response.status_code == 422


class TestEventRead:
    """Test reading events via API endpoint."""

    def test_get_event_by_id_success(self, client, sample_event_data):
        """Test successfully getting an event by ID."""
        create_response = client.post("/api/v1/events", json=sample_event_data)
        event_id = create_response.json()["id"]

        response = client.get(f"/api/v1/events/{event_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == event_id
        assert data["type"] == sample_event_data["type"]

    def test_get_event_by_id_not_found(self, client):
        """Test getting a non-existent event."""
        non_existent_id = str(uuid4())
        response = client.get(f"/api/v1/events/{non_existent_id}")
        assert response.status_code == 404

    def test_get_event_invalid_uuid(self, client):
        """Test getting an event with invalid UUID format."""
        response = client.get("/api/v1/events/invalid-uuid")
        assert response.status_code == 422

    def test_get_all_events_empty(self, client):
        """Test getting all events when database is empty."""
        response = client.get("/api/v1/events")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_all_events_with_data(self, client, sample_event_data):
        """Test getting all events with multiple records."""
        client.post("/api/v1/events", json=sample_event_data)

        event_data_2 = sample_event_data.copy()
        event_data_2["type"] = "Death"
        client.post("/api/v1/events", json=event_data_2)

        response = client.get("/api/v1/events")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_get_all_events_with_pagination(self, client, sample_event_data):
        """Test getting all events with pagination."""
        for i in range(5):
            event_data = sample_event_data.copy()
            event_data["type"] = f"Event{i}"
            client.post("/api/v1/events", json=event_data)

        response = client.get("/api/v1/events?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2


class TestEventQuery:
    """Test querying events via API endpoint."""

    def test_get_events_by_person(self, client, sample_event_data, sample_person):
        """Test getting events for a specific person."""
        client.post("/api/v1/events", json=sample_event_data)

        event_data_2 = sample_event_data.copy()
        event_data_2["type"] = "Graduation"
        client.post("/api/v1/events", json=event_data_2)

        person_id = sample_person["id"]
        response = client.get(f"/api/v1/events/by-person/{person_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert all(e["person_id"] == person_id for e in data)

    def test_get_events_by_family(
        self, client, sample_family_event_data, sample_family
    ):
        """Test getting events for a specific family."""
        client.post("/api/v1/events", json=sample_family_event_data)

        event_data_2 = sample_family_event_data.copy()
        event_data_2["type"] = "Divorce"
        client.post("/api/v1/events", json=event_data_2)

        family_id = sample_family["id"]
        response = client.get(f"/api/v1/events/by-family/{family_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert all(e["family_id"] == family_id for e in data)

    def test_get_events_by_type(self, client, sample_event_data):
        """Test getting events by type."""
        client.post("/api/v1/events", json=sample_event_data)

        event_data_2 = sample_event_data.copy()
        client.post("/api/v1/events", json=event_data_2)

        response = client.get(
            f"/api/v1/events/by-type?type={sample_event_data['type']}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert all(e["type"] == sample_event_data["type"] for e in data)

    def test_search_events_by_type(self, client, sample_event_data):
        """Test searching events by partial type match."""
        client.post("/api/v1/events", json=sample_event_data)

        response = client.get("/api/v1/events/search?type=Bir")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_get_events_person_not_found(self, client):
        """Test getting events for non-existent person."""
        non_existent_id = str(uuid4())
        response = client.get(f"/api/v1/events/by-person/{non_existent_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_events_family_not_found(self, client):
        """Test getting events for non-existent family."""
        non_existent_id = str(uuid4())
        response = client.get(f"/api/v1/events/by-family/{non_existent_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestEventUpdate:
    """Test updating events via API endpoint."""

    def test_update_event_success(self, client, sample_event_data):
        """Test successfully updating an event."""
        create_response = client.post("/api/v1/events", json=sample_event_data)
        event_id = create_response.json()["id"]

        update_data = {
            "type": "Updated Event",
            "description": "Updated description",
        }
        response = client.patch(f"/api/v1/events/{event_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "Updated Event"
        assert data["description"] == "Updated description"

    def test_update_event_partial(self, client, sample_event_data):
        """Test partial update of event."""
        create_response = client.post("/api/v1/events", json=sample_event_data)
        event_id = create_response.json()["id"]

        update_data = {"place": "Updated Place"}
        response = client.patch(f"/api/v1/events/{event_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["place"] == "Updated Place"
        assert data["type"] == sample_event_data["type"]

    def test_update_event_not_found(self, client):
        """Test updating a non-existent event."""
        non_existent_id = str(uuid4())
        update_data = {"type": "Updated"}
        response = client.patch(f"/api/v1/events/{non_existent_id}", json=update_data)
        assert response.status_code == 404

    def test_update_event_invalid_person_id(self, client, sample_event_data):
        """Test updating event with invalid person ID."""
        create_response = client.post("/api/v1/events", json=sample_event_data)
        event_id = create_response.json()["id"]

        update_data = {"person_id": str(uuid4())}
        response = client.patch(f"/api/v1/events/{event_id}", json=update_data)
        assert response.status_code in [400, 404, 422]

    def test_update_event_empty_data(self, client, sample_event_data):
        """Test updating event with empty data."""
        create_response = client.post("/api/v1/events", json=sample_event_data)
        event_id = create_response.json()["id"]

        response = client.patch(f"/api/v1/events/{event_id}", json={})
        assert response.status_code == 200


class TestEventDelete:
    """Test deleting events via API endpoint."""

    def test_delete_event_success(self, client, sample_event_data):
        """Test successfully deleting an event."""
        create_response = client.post("/api/v1/events", json=sample_event_data)
        event_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/events/{event_id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/api/v1/events/{event_id}")
        assert get_response.status_code == 404

    def test_delete_event_not_found(self, client):
        """Test deleting a non-existent event."""
        non_existent_id = str(uuid4())
        response = client.delete(f"/api/v1/events/{non_existent_id}")
        assert response.status_code == 404

    def test_delete_event_invalid_uuid(self, client):
        """Test deleting event with invalid UUID."""
        response = client.delete("/api/v1/events/invalid-uuid")
        assert response.status_code == 422


class TestEventEdgeCases:
    """Test edge cases for event endpoints."""

    def test_create_event_both_person_and_family(
        self, client, sample_person, sample_family
    ):
        """Test creating event with both person and family IDs (should fail)."""
        data = {
            "person_id": sample_person["id"],
            "family_id": sample_family["id"],
            "type": "Mixed Event",
        }
        response = client.post("/api/v1/events", json=data)
        assert response.status_code in [400, 422]
        assert (
            "either" in response.json()["detail"].lower()
            or "both" in response.json()["detail"].lower()
            or "exclusive" in response.json()["detail"].lower()
        )

    def test_create_event_very_long_type(self, client, sample_person):
        """Test creating event with very long type."""
        long_type_data = {
            "person_id": sample_person["id"],
            "type": "A" * 100,
        }
        response = client.post("/api/v1/events", json=long_type_data)
        assert response.status_code == 422

    def test_create_event_very_long_place(self, client, sample_person):
        """Test creating event with very long place name."""
        long_place_data = {
            "person_id": sample_person["id"],
            "type": "Birth",
            "place": "A" * 300,
        }
        response = client.post("/api/v1/events", json=long_place_data)
        assert response.status_code == 422

    def test_create_event_with_special_characters(self, client, sample_person):
        """Test creating event with special characters."""
        special_data = {
            "person_id": sample_person["id"],
            "type": "Événement Spécial",
            "place": "São Paulo, Brasil",
            "description": "Special chars: éàüñ @#$%",
        }
        response = client.post("/api/v1/events", json=special_data)
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == special_data["type"]

    def test_create_event_with_future_date(self, client, sample_person):
        """Test creating event with future date (should fail for most event types)."""
        future_data = {
            "person_id": sample_person["id"],
            "type": "Birth",
            "date": "2099-12-31",
        }
        response = client.post("/api/v1/events", json=future_data)
        assert response.status_code in [400, 422]
        assert (
            "future" in response.json()["detail"].lower()
            or "invalid" in response.json()["detail"].lower()
        )

    def test_get_multiple_event_types_for_person(self, client, sample_person):
        """Test getting multiple types of events for a person."""
        person_id = sample_person["id"]
        event_types = ["Birth", "Graduation", "Marriage", "Death"]

        for event_type in event_types:
            client.post(
                "/api/v1/events",
                json={"person_id": person_id, "type": event_type},
            )

        response = client.get(f"/api/v1/events/by-person/{person_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= len(event_types)

    def test_search_events_case_sensitive(self, client, sample_event_data):
        """Test that event type search is case-sensitive."""
        client.post("/api/v1/events", json=sample_event_data)

        response = client.get("/api/v1/events/search?type=birth")
        assert response.status_code == 200

    def test_create_event_before_person_birth(self, client):
        """Test creating event before person birth (should fail)."""
        person = client.post(
            "/api/v1/persons",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "sex": "M",
                "birth_date": "1990-01-01",
            },
        ).json()

        event_data = {
            "person_id": person["id"],
            "type": "Graduation",
            "date": "1980-01-01",
        }
        response = client.post("/api/v1/events", json=event_data)
        assert response.status_code in [400, 422]
        assert (
            "birth" in response.json()["detail"].lower()
            or "before" in response.json()["detail"].lower()
        )

    def test_create_event_after_person_death(self, client):
        """Test creating event after person death (should fail)."""
        person = client.post(
            "/api/v1/persons",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "sex": "M",
                "birth_date": "1920-01-01",
                "death_date": "2000-12-31",
            },
        ).json()

        event_data = {
            "person_id": person["id"],
            "type": "Graduation",
            "date": "2010-06-15",
        }
        response = client.post("/api/v1/events", json=event_data)
        assert response.status_code in [400, 422]
        assert (
            "death" in response.json()["detail"].lower()
            or "after" in response.json()["detail"].lower()
            or "deceased" in response.json()["detail"].lower()
        )

    def test_update_event_to_have_both_person_and_family(
        self, client, sample_event_data, sample_family
    ):
        """Test updating event to have both person_id and family_id (should fail)."""
        create_response = client.post("/api/v1/events", json=sample_event_data)
        event_id = create_response.json()["id"]

        update_data = {"family_id": sample_family["id"]}
        response = client.patch(f"/api/v1/events/{event_id}", json=update_data)
        assert response.status_code in [400, 422]
        assert (
            "either" in response.json()["detail"].lower()
            or "both" in response.json()["detail"].lower()
            or "exclusive" in response.json()["detail"].lower()
        )

    def test_update_event_to_remove_both_person_and_family(
        self, client, sample_event_data
    ):
        """Test updating event to have neither person nor family (should fail)."""
        create_response = client.post("/api/v1/events", json=sample_event_data)
        event_id = create_response.json()["id"]

        update_data = {"person_id": None}
        response = client.patch(f"/api/v1/events/{event_id}", json=update_data)
        assert response.status_code in [400, 422]
        assert (
            "person" in response.json()["detail"].lower()
            or "family" in response.json()["detail"].lower()
            or "required" in response.json()["detail"].lower()
        )
