"""Test cases for Child API endpoints."""

from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_persons(client):
    """Create sample persons for child tests."""
    father = client.post(
        "/api/v1/persons",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "sex": "M",
            "birth_date": "1960-01-01",
        },
    ).json()

    mother = client.post(
        "/api/v1/persons",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "sex": "F",
            "birth_date": "1962-05-15",
        },
    ).json()

    child1 = client.post(
        "/api/v1/persons",
        json={
            "first_name": "Alice",
            "last_name": "Doe",
            "sex": "F",
            "birth_date": "1985-03-10",
        },
    ).json()

    child2 = client.post(
        "/api/v1/persons",
        json={
            "first_name": "Bob",
            "last_name": "Doe",
            "sex": "M",
            "birth_date": "1987-07-22",
        },
    ).json()

    return {
        "father": father,
        "mother": mother,
        "child1": child1,
        "child2": child2,
    }


@pytest.fixture
def sample_family(client, sample_persons):
    """Create a sample family for child tests."""
    return client.post(
        "/api/v1/families",
        json={
            "husband_id": sample_persons["father"]["id"],
            "wife_id": sample_persons["mother"]["id"],
        },
    ).json()


@pytest.fixture
def sample_child_data(sample_family, sample_persons):
    """Sample child relationship data for tests."""
    return {
        "family_id": sample_family["id"],
        "child_id": sample_persons["child1"]["id"],
    }


class TestChildCreate:
    """Test creating child relationships via API endpoint."""

    def test_create_child_success(self, client, sample_child_data):
        """Test successful child relationship creation."""
        response = client.post("/api/v1/children", json=sample_child_data)
        assert response.status_code == 201
        data = response.json()
        assert data["family_id"] == sample_child_data["family_id"]
        assert data["child_id"] == sample_child_data["child_id"]

    def test_create_multiple_children_same_family(
        self, client, sample_family, sample_persons
    ):
        """Test adding multiple children to the same family."""
        child1_data = {
            "family_id": sample_family["id"],
            "child_id": sample_persons["child1"]["id"],
        }
        child2_data = {
            "family_id": sample_family["id"],
            "child_id": sample_persons["child2"]["id"],
        }

        response1 = client.post("/api/v1/children", json=child1_data)
        assert response1.status_code == 201

        response2 = client.post("/api/v1/children", json=child2_data)
        assert response2.status_code == 201

    def test_create_child_duplicate(self, client, sample_child_data):
        """Test creating duplicate child relationship."""
        response1 = client.post("/api/v1/children", json=sample_child_data)
        assert response1.status_code == 201

        response2 = client.post("/api/v1/children", json=sample_child_data)
        assert response2.status_code in [400, 409, 422]

    def test_create_child_invalid_family_id(self, client, sample_persons):
        """Test creating child with non-existent family."""
        invalid_data = {
            "family_id": str(uuid4()),
            "child_id": sample_persons["child1"]["id"],
        }
        response = client.post("/api/v1/children", json=invalid_data)
        assert response.status_code in [400, 404, 422]

    def test_create_child_invalid_child_id(self, client, sample_family):
        """Test creating child with non-existent person."""
        invalid_data = {
            "family_id": sample_family["id"],
            "child_id": str(uuid4()),
        }
        response = client.post("/api/v1/children", json=invalid_data)
        assert response.status_code in [400, 404, 422]

    def test_create_child_missing_family_id(self, client, sample_persons):
        """Test creating child without family_id."""
        incomplete_data = {"child_id": sample_persons["child1"]["id"]}
        response = client.post("/api/v1/children", json=incomplete_data)
        assert response.status_code == 422

    def test_create_child_missing_child_id(self, client, sample_family):
        """Test creating child without child_id."""
        incomplete_data = {"family_id": sample_family["id"]}
        response = client.post("/api/v1/children", json=incomplete_data)
        assert response.status_code == 422


class TestChildRead:
    """Test reading child relationships via API endpoint."""

    def test_get_child_success(
        self, client, sample_child_data, sample_family, sample_persons
    ):
        """Test successfully getting a child relationship."""
        client.post("/api/v1/children", json=sample_child_data)

        family_id = sample_family["id"]
        child_id = sample_persons["child1"]["id"]
        response = client.get(f"/api/v1/children/{family_id}/{child_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["family_id"] == family_id
        assert data["child_id"] == child_id

    def test_get_child_not_found(self, client, sample_family):
        """Test getting a non-existent child relationship."""
        non_existent_child_id = str(uuid4())
        family_id = sample_family["id"]
        response = client.get(f"/api/v1/children/{family_id}/{non_existent_child_id}")
        assert response.status_code == 404

    def test_get_child_invalid_uuid(self, client):
        """Test getting a child with invalid UUID format."""
        response = client.get("/api/v1/children/invalid-uuid/invalid-uuid")
        assert response.status_code == 422

    def test_get_all_children_empty(self, client):
        """Test getting all child relationships when database is empty."""
        response = client.get("/api/v1/children")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_all_children_with_data(self, client, sample_family, sample_persons):
        """Test getting all child relationships with multiple records."""
        child1_data = {
            "family_id": sample_family["id"],
            "child_id": sample_persons["child1"]["id"],
        }
        child2_data = {
            "family_id": sample_family["id"],
            "child_id": sample_persons["child2"]["id"],
        }

        client.post("/api/v1/children", json=child1_data)
        client.post("/api/v1/children", json=child2_data)

        response = client.get("/api/v1/children")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_get_all_children_with_pagination(
        self, client, sample_family, sample_persons
    ):
        """Test getting all child relationships with pagination."""
        for person in [sample_persons["child1"], sample_persons["child2"]]:
            client.post(
                "/api/v1/children",
                json={"family_id": sample_family["id"], "child_id": person["id"]},
            )

        response = client.get("/api/v1/children?skip=0&limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1


class TestChildQuery:
    """Test querying child relationships via API endpoint."""

    def test_get_children_by_family(self, client, sample_family, sample_persons):
        """Test getting all children of a family."""
        child1_data = {
            "family_id": sample_family["id"],
            "child_id": sample_persons["child1"]["id"],
        }
        child2_data = {
            "family_id": sample_family["id"],
            "child_id": sample_persons["child2"]["id"],
        }

        client.post("/api/v1/children", json=child1_data)
        client.post("/api/v1/children", json=child2_data)

        family_id = sample_family["id"]
        response = client.get(f"/api/v1/children/by-family/{family_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert all(c["family_id"] == family_id for c in data)

    def test_get_children_by_child(self, client, sample_family, sample_persons):
        """Test getting all families where a person is a child."""
        adoptive_parent = client.post(
            "/api/v1/persons",
            json={"first_name": "Adoptive", "last_name": "Parent", "sex": "M"},
        ).json()
        family2 = client.post(
            "/api/v1/families",
            json={"husband_id": adoptive_parent["id"]},
        ).json()

        child_id = sample_persons["child1"]["id"]
        client.post(
            "/api/v1/children",
            json={"family_id": sample_family["id"], "child_id": child_id},
        )
        client.post(
            "/api/v1/children",
            json={"family_id": family2["id"], "child_id": child_id},
        )

        response = client.get(f"/api/v1/children/by-child/{child_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert all(c["child_id"] == child_id for c in data)

    def test_get_children_by_family_empty(self, client, sample_family):
        """Test getting children for a family with no children."""
        family_id = sample_family["id"]
        response = client.get(f"/api/v1/children/by-family/{family_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_children_by_child_not_in_family(self, client, sample_persons):
        """Test getting families for a person not in any family."""
        child_id = sample_persons["child1"]["id"]
        response = client.get(f"/api/v1/children/by-child/{child_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_children_by_family_not_found(self, client):
        """Test getting children for non-existent family."""
        non_existent_id = str(uuid4())
        response = client.get(f"/api/v1/children/by-family/{non_existent_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestChildDelete:
    """Test deleting child relationships via API endpoint."""

    def test_delete_child_success(
        self, client, sample_child_data, sample_family, sample_persons
    ):
        """Test successfully deleting a child relationship."""
        client.post("/api/v1/children", json=sample_child_data)

        family_id = sample_family["id"]
        child_id = sample_persons["child1"]["id"]
        response = client.delete(f"/api/v1/children/{family_id}/{child_id}")
        assert response.status_code == 204

        get_response = client.get(f"/api/v1/children/{family_id}/{child_id}")
        assert get_response.status_code == 404

    def test_delete_child_not_found(self, client, sample_family):
        """Test deleting a non-existent child relationship."""
        non_existent_child_id = str(uuid4())
        family_id = sample_family["id"]
        response = client.delete(
            f"/api/v1/children/{family_id}/{non_existent_child_id}"
        )
        assert response.status_code == 404

    def test_delete_child_invalid_uuid(self, client):
        """Test deleting child with invalid UUID."""
        response = client.delete("/api/v1/children/invalid-uuid/invalid-uuid")
        assert response.status_code == 422

    def test_delete_all_children_by_family(self, client, sample_family, sample_persons):
        """Test deleting all children of a family."""
        child1_data = {
            "family_id": sample_family["id"],
            "child_id": sample_persons["child1"]["id"],
        }
        child2_data = {
            "family_id": sample_family["id"],
            "child_id": sample_persons["child2"]["id"],
        }
        client.post("/api/v1/children", json=child1_data)
        client.post("/api/v1/children", json=child2_data)

        family_id = sample_family["id"]
        response = client.delete(f"/api/v1/children/by-family/{family_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] >= 2

        get_response = client.get(f"/api/v1/children/by-family/{family_id}")
        assert get_response.status_code == 200
        assert len(get_response.json()) == 0

    def test_delete_all_children_by_child(self, client, sample_family, sample_persons):
        """Test deleting all family relationships for a child."""
        adoptive_parent = client.post(
            "/api/v1/persons",
            json={"first_name": "Adoptive", "last_name": "Parent", "sex": "F"},
        ).json()
        family2 = client.post(
            "/api/v1/families",
            json={"wife_id": adoptive_parent["id"]},
        ).json()

        child_id = sample_persons["child1"]["id"]
        client.post(
            "/api/v1/children",
            json={"family_id": sample_family["id"], "child_id": child_id},
        )
        client.post(
            "/api/v1/children",
            json={"family_id": family2["id"], "child_id": child_id},
        )

        response = client.delete(f"/api/v1/children/by-child/{child_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] >= 2

        get_response = client.get(f"/api/v1/children/by-child/{child_id}")
        assert get_response.status_code == 200
        assert len(get_response.json()) == 0


class TestChildEdgeCases:
    """Test edge cases for child endpoints."""

    def test_create_child_parent_as_child(self, client, sample_family, sample_persons):
        """Test creating relationship where parent is also listed as child (should fail)."""
        invalid_data = {
            "family_id": sample_family["id"],
            "child_id": sample_persons["father"]["id"],
        }
        response = client.post("/api/v1/children", json=invalid_data)
        assert response.status_code in [400, 422]
        assert (
            "parent" in response.json()["detail"].lower()
            or "invalid" in response.json()["detail"].lower()
            or "circular" in response.json()["detail"].lower()
        )

    def test_child_in_multiple_families(self, client, sample_persons):
        """Test adding same child to multiple families (adoption/remarriage scenarios)."""
        adoptive_father = client.post(
            "/api/v1/persons",
            json={"first_name": "Adoptive", "last_name": "Father", "sex": "M"},
        ).json()

        family1 = client.post(
            "/api/v1/families",
            json={"husband_id": sample_persons["father"]["id"]},
        ).json()
        family2 = client.post(
            "/api/v1/families",
            json={"husband_id": adoptive_father["id"]},
        ).json()

        child_id = sample_persons["child1"]["id"]

        response1 = client.post(
            "/api/v1/children",
            json={"family_id": family1["id"], "child_id": child_id},
        )
        assert response1.status_code == 201

        response2 = client.post(
            "/api/v1/children",
            json={"family_id": family2["id"], "child_id": child_id},
        )
        assert response2.status_code == 201

        get_response = client.get(f"/api/v1/children/by-child/{child_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert len(data) >= 2

    def test_delete_family_cascades_children(
        self, client, sample_family, sample_child_data
    ):
        """Test that deleting a family also deletes child relationships."""
        client.post("/api/v1/children", json=sample_child_data)

        family_id = sample_family["id"]
        response = client.delete(f"/api/v1/families/{family_id}")
        assert response.status_code == 204

        get_response = client.get(f"/api/v1/children/by-family/{family_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert len(data) == 0

    def test_delete_person_cascades_child_relationships(
        self, client, sample_family, sample_child_data, sample_persons
    ):
        """Test that deleting a person also deletes their child relationships."""
        client.post("/api/v1/children", json=sample_child_data)

        child_id = sample_persons["child1"]["id"]
        response = client.delete(f"/api/v1/persons/{child_id}")
        assert response.status_code == 204

        family_id = sample_family["id"]
        get_response = client.get(f"/api/v1/children/{family_id}/{child_id}")
        assert get_response.status_code == 404

    def test_multiple_generations(self, client):
        """Test handling multiple generations of relationships."""
        grandpa = client.post(
            "/api/v1/persons",
            json={"first_name": "Grandpa", "last_name": "Doe", "sex": "M"},
        ).json()
        grandma = client.post(
            "/api/v1/persons",
            json={"first_name": "Grandma", "last_name": "Doe", "sex": "F"},
        ).json()

        parent = client.post(
            "/api/v1/persons",
            json={"first_name": "Parent", "last_name": "Doe", "sex": "M"},
        ).json()

        child = client.post(
            "/api/v1/persons",
            json={"first_name": "Child", "last_name": "Doe", "sex": "F"},
        ).json()

        grandparent_family = client.post(
            "/api/v1/families",
            json={"husband_id": grandpa["id"], "wife_id": grandma["id"]},
        ).json()

        client.post(
            "/api/v1/children",
            json={"family_id": grandparent_family["id"], "child_id": parent["id"]},
        )

        parent_family = client.post(
            "/api/v1/families",
            json={"husband_id": parent["id"]},
        ).json()

        response = client.post(
            "/api/v1/children",
            json={"family_id": parent_family["id"], "child_id": child["id"]},
        )
        assert response.status_code == 201

        parent_children = client.get(f"/api/v1/children/by-child/{parent['id']}").json()
        assert len(parent_children) >= 1

        grandchildren = client.get(
            f"/api/v1/children/by-family/{parent_family['id']}"
        ).json()
        assert len(grandchildren) >= 1
