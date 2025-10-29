from datetime import date
from uuid import uuid4
import pytest

from src.models.person import Sex


@pytest.fixture
def sample_persons(client):
    """Create sample persons for family tests."""
    husband = client.post(
        "/api/v1/persons",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "sex": "M",
            "birth_date": "1980-01-01",
        },
    ).json()

    wife = client.post(
        "/api/v1/persons",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "sex": "F",
            "birth_date": "1982-05-15",
        },
    ).json()

    return {"husband": husband, "wife": wife}


@pytest.fixture
def sample_family_data(sample_persons):
    """Sample family data for tests."""
    return {
        "husband_id": sample_persons["husband"]["id"],
        "wife_id": sample_persons["wife"]["id"],
        "marriage_date": "2005-06-20",
        "marriage_place": "New York City",
        "notes": "First marriage",
    }


class TestFamilyCreate:
    """Test creating families via API endpoint."""

    def test_create_family_success(self, client, sample_family_data):
        """Test successful family creation."""
        response = client.post("/api/v1/families", json=sample_family_data)
        assert response.status_code == 201
        data = response.json()
        assert data["husband_id"] == sample_family_data["husband_id"]
        assert data["wife_id"] == sample_family_data["wife_id"]
        assert "id" in data

    def test_create_family_without_spouses(self, client):
        """Test creating family without any spouses (should fail)."""
        minimal_data = {}
        response = client.post("/api/v1/families", json=minimal_data)
        assert response.status_code == 422
        assert (
            "at least one spouse" in response.json()["detail"].lower()
            or "husband" in response.json()["detail"].lower()
            or "wife" in response.json()["detail"].lower()
        )

    def test_create_family_husband_only(self, client, sample_persons):
        """Test creating family with only husband."""
        data = {"husband_id": sample_persons["husband"]["id"]}
        response = client.post("/api/v1/families", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["husband_id"] == sample_persons["husband"]["id"]
        assert result["wife_id"] is None

    def test_create_family_wife_only(self, client, sample_persons):
        """Test creating family with only wife."""
        data = {"wife_id": sample_persons["wife"]["id"]}
        response = client.post("/api/v1/families", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["wife_id"] == sample_persons["wife"]["id"]
        assert result["husband_id"] is None

    def test_create_family_with_all_fields(self, client, sample_family_data):
        """Test creating family with all fields."""
        response = client.post("/api/v1/families", json=sample_family_data)
        assert response.status_code == 201
        data = response.json()
        assert data["marriage_date"] == sample_family_data["marriage_date"]
        assert data["marriage_place"] == sample_family_data["marriage_place"]
        assert data["notes"] == sample_family_data["notes"]

    def test_create_family_invalid_husband_id(self, client):
        """Test creating family with non-existent husband."""
        invalid_data = {
            "husband_id": str(uuid4()),
            "marriage_date": "2005-06-20",
        }
        response = client.post("/api/v1/families", json=invalid_data)
        assert response.status_code in [400, 404, 422]

    def test_create_family_invalid_date_format(self, client, sample_persons):
        """Test creating family with invalid date format."""
        invalid_data = {
            "husband_id": sample_persons["husband"]["id"],
            "marriage_date": "invalid-date",
        }
        response = client.post("/api/v1/families", json=invalid_data)
        assert response.status_code == 422


class TestFamilyRead:
    """Test reading families via API endpoint."""

    def test_get_family_by_id_success(self, client, sample_family_data):
        """Test successfully getting a family by ID."""
        create_response = client.post("/api/v1/families", json=sample_family_data)
        family_id = create_response.json()["id"]

        response = client.get(f"/api/v1/families/{family_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == family_id
        assert data["husband_id"] == sample_family_data["husband_id"]

    def test_get_family_by_id_not_found(self, client):
        """Test getting a non-existent family."""
        non_existent_id = str(uuid4())
        response = client.get(f"/api/v1/families/{non_existent_id}")
        assert response.status_code == 404

    def test_get_family_invalid_uuid(self, client):
        """Test getting a family with invalid UUID format."""
        response = client.get("/api/v1/families/invalid-uuid")
        assert response.status_code == 422

    def test_get_all_families_empty(self, client):
        """Test getting all families when database is empty."""
        response = client.get("/api/v1/families")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_all_families_with_data(
        self, client, sample_family_data, sample_persons
    ):
        """Test getting all families with multiple records."""
        client.post("/api/v1/families", json=sample_family_data)
        client.post(
            "/api/v1/families", json={"husband_id": sample_persons["husband"]["id"]}
        )

        response = client.get("/api/v1/families")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_get_all_families_with_pagination(self, client, sample_persons):
        """Test getting all families with pagination."""
        for i in range(5):
            client.post(
                "/api/v1/families", json={"husband_id": sample_persons["husband"]["id"]}
            )

        response = client.get("/api/v1/families?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2


class TestFamilyQuery:
    """Test querying families via API endpoint."""

    def test_get_families_by_husband(self, client, sample_family_data, sample_persons):
        """Test getting families by husband ID."""
        client.post("/api/v1/families", json=sample_family_data)
        husband_id = sample_persons["husband"]["id"]

        response = client.get(f"/api/v1/families/by-husband/{husband_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all(f["husband_id"] == husband_id for f in data)

    def test_get_families_by_wife(self, client, sample_family_data, sample_persons):
        """Test getting families by wife ID."""
        client.post("/api/v1/families", json=sample_family_data)
        wife_id = sample_persons["wife"]["id"]

        response = client.get(f"/api/v1/families/by-wife/{wife_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all(f["wife_id"] == wife_id for f in data)

    def test_get_families_by_spouse(self, client, sample_family_data, sample_persons):
        """Test getting families by spouse ID (either husband or wife)."""
        client.post("/api/v1/families", json=sample_family_data)
        husband_id = sample_persons["husband"]["id"]

        response = client.get(f"/api/v1/families/by-spouse/{husband_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_get_families_by_spouse_not_found(self, client):
        """Test getting families for a person not in any family."""
        non_existent_id = str(uuid4())
        response = client.get(f"/api/v1/families/by-spouse/{non_existent_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestFamilyUpdate:
    """Test updating families via API endpoint."""

    def test_update_family_success(self, client, sample_family_data):
        """Test successfully updating a family."""
        create_response = client.post("/api/v1/families", json=sample_family_data)
        family_id = create_response.json()["id"]

        update_data = {
            "marriage_place": "Updated Location",
            "notes": "Updated notes",
        }
        response = client.patch(f"/api/v1/families/{family_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["marriage_place"] == "Updated Location"
        assert data["notes"] == "Updated notes"

    def test_update_family_partial(self, client, sample_family_data):
        """Test partial update of family."""
        create_response = client.post("/api/v1/families", json=sample_family_data)
        family_id = create_response.json()["id"]

        update_data = {"notes": "Only updating notes"}
        response = client.patch(f"/api/v1/families/{family_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Only updating notes"
        assert data["husband_id"] == sample_family_data["husband_id"]

    def test_update_family_not_found(self, client):
        """Test updating a non-existent family."""
        non_existent_id = str(uuid4())
        update_data = {"notes": "Updated"}
        response = client.patch(f"/api/v1/families/{non_existent_id}", json=update_data)
        assert response.status_code == 404

    def test_update_family_invalid_person_id(self, client, sample_family_data):
        """Test updating family with invalid person ID."""
        create_response = client.post("/api/v1/families", json=sample_family_data)
        family_id = create_response.json()["id"]

        update_data = {"husband_id": str(uuid4())}
        response = client.patch(f"/api/v1/families/{family_id}", json=update_data)
        assert response.status_code in [400, 404, 422]

    def test_update_family_empty_data(self, client, sample_family_data):
        """Test updating family with empty data."""
        create_response = client.post("/api/v1/families", json=sample_family_data)
        family_id = create_response.json()["id"]

        response = client.patch(f"/api/v1/families/{family_id}", json={})
        assert response.status_code == 200


class TestFamilyDelete:
    """Test deleting families via API endpoint."""

    def test_delete_family_success(self, client, sample_family_data):
        """Test successfully deleting a family."""
        create_response = client.post("/api/v1/families", json=sample_family_data)
        family_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/families/{family_id}")
        assert response.status_code == 204

        get_response = client.get(f"/api/v1/families/{family_id}")
        assert get_response.status_code == 404

    def test_delete_family_not_found(self, client):
        """Test deleting a non-existent family."""
        non_existent_id = str(uuid4())
        response = client.delete(f"/api/v1/families/{non_existent_id}")
        assert response.status_code == 404

    def test_delete_family_invalid_uuid(self, client):
        """Test deleting family with invalid UUID."""
        response = client.delete("/api/v1/families/invalid-uuid")
        assert response.status_code == 422


class TestFamilyEdgeCases:
    """Test edge cases for family endpoints."""

    def test_create_family_same_person_as_both_spouses(self, client, sample_persons):
        """Test creating family with same person as husband and wife (should fail)."""
        invalid_data = {
            "husband_id": sample_persons["husband"]["id"],
            "wife_id": sample_persons["husband"]["id"],
        }
        response = client.post("/api/v1/families", json=invalid_data)
        assert response.status_code in [400, 422]
        assert (
            "same person" in response.json()["detail"].lower()
            or "invalid" in response.json()["detail"].lower()
        )

    def test_create_multiple_families_same_spouses(self, client, sample_family_data):
        """Test creating multiple families with same spouse combination (remarriage scenario)."""
        response1 = client.post("/api/v1/families", json=sample_family_data)
        assert response1.status_code == 201

        # Second creation with the exact same spouses should be rejected
        response2 = client.post("/api/v1/families", json=sample_family_data)
        assert response2.status_code == 409

    def test_create_family_same_spouses_swapped_order_conflict(
        self, client, sample_family_data
    ):
        """Test creating a family with spouses swapped order should also conflict (order-indifferent)."""
        # Create initial family
        response1 = client.post("/api/v1/families", json=sample_family_data)
        assert response1.status_code == 201

        # Try to create with swapped roles
        swapped = {
            "husband_id": sample_family_data["wife_id"],
            "wife_id": sample_family_data["husband_id"],
            "marriage_date": sample_family_data.get("marriage_date"),
            "marriage_place": sample_family_data.get("marriage_place"),
            "notes": sample_family_data.get("notes"),
        }
        response2 = client.post("/api/v1/families", json=swapped)
        assert response2.status_code == 409

    def test_create_family_with_very_long_place_name(self, client, sample_persons):
        """Test creating family with very long place name."""
        long_place_data = {
            "husband_id": sample_persons["husband"]["id"],
            "marriage_place": "A" * 300,
        }
        response = client.post("/api/v1/families", json=long_place_data)
        assert response.status_code == 422

    def test_create_family_with_special_characters(self, client, sample_persons):
        """Test creating family with special characters in fields."""
        special_data = {
            "husband_id": sample_persons["husband"]["id"],
            "marriage_place": "Saint-Jean-de-Luz, Pyrénées-Atlantiques",
            "notes": "Special characters: @#$%^&*()",
        }
        response = client.post("/api/v1/families", json=special_data)
        assert response.status_code == 201
        data = response.json()
        assert data["marriage_place"] == special_data["marriage_place"]

    def test_get_families_person_in_multiple_families(self, client, sample_persons):
        """Test getting families when person is in multiple families (multiple marriages)."""
        husband_id = sample_persons["husband"]["id"]
        wife1_id = sample_persons["wife"]["id"]

        wife2 = client.post(
            "/api/v1/persons",
            json={"first_name": "Susan", "last_name": "Johnson", "sex": "F"},
        ).json()

        client.post(
            "/api/v1/families", json={"husband_id": husband_id, "wife_id": wife1_id}
        )
        client.post(
            "/api/v1/families", json={"husband_id": husband_id, "wife_id": wife2["id"]}
        )

        response = client.get(f"/api/v1/families/by-husband/{husband_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_create_family_marriage_before_birth(self, client):
        """Test creating family with marriage date before spouse birth (should fail)."""
        person = client.post(
            "/api/v1/persons",
            json={
                "first_name": "Young",
                "last_name": "Person",
                "sex": "M",
                "birth_date": "1990-01-01",
            },
        ).json()

        invalid_data = {
            "husband_id": person["id"],
            "marriage_date": "1980-01-01",
        }
        response = client.post("/api/v1/families", json=invalid_data)
        assert response.status_code in [400, 422]
        assert (
            "birth" in response.json()["detail"].lower()
            or "before" in response.json()["detail"].lower()
        )

    def test_update_family_to_remove_all_spouses(self, client, sample_family_data):
        """Test updating family to have no spouses (should fail)."""
        create_response = client.post("/api/v1/families", json=sample_family_data)
        family_id = create_response.json()["id"]

        update_data = {"husband_id": None, "wife_id": None}
        response = client.patch(f"/api/v1/families/{family_id}", json=update_data)
        assert response.status_code in [400, 422]
        assert (
            "spouse" in response.json()["detail"].lower()
            or "husband" in response.json()["detail"].lower()
            or "wife" in response.json()["detail"].lower()
        )

    def test_create_family_marriage_after_death(self, client):
        """Test creating family with marriage after spouse death (should fail)."""
        deceased = client.post(
            "/api/v1/persons",
            json={
                "first_name": "Deceased",
                "last_name": "Person",
                "sex": "F",
                "birth_date": "1950-01-01",
                "death_date": "2000-12-31",
            },
        ).json()

        invalid_data = {
            "wife_id": deceased["id"],
            "marriage_date": "2010-06-20",
        }
        response = client.post("/api/v1/families", json=invalid_data)
        assert response.status_code in [400, 422]
        assert (
            "death" in response.json()["detail"].lower()
            or "after" in response.json()["detail"].lower()
            or "deceased" in response.json()["detail"].lower()
        )


class TestFamilySearch:
    """Test family search functionality via API endpoint."""

    def test_search_families_by_name_success(self, client, sample_family_data):
        """Test searching families by spouse name."""
        client.post("/api/v1/families", json=sample_family_data)

        # Search by first name
        response = client.get("/api/v1/families/search?q=John")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any("John" in result["summary"] for result in data)

        # Search by last name
        response = client.get("/api/v1/families/search?q=Smith")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any("Smith" in result["summary"] for result in data)

    def test_search_families_by_family_id(self, client, sample_family_data):
        """Test searching families by specific family ID."""
        create_response = client.post("/api/v1/families", json=sample_family_data)
        family_id = create_response.json()["id"]

        response = client.get(f"/api/v1/families/search?family_id={family_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == family_id
        assert "John" in data[0]["summary"]
        assert "Smith" in data[0]["summary"]

    def test_search_families_no_results(self, client):
        """Test searching families with no matching results."""
        response = client.get("/api/v1/families/search?q=NonexistentName")
        assert response.status_code == 404
        assert "No families found" in response.json()["detail"]

    def test_search_families_invalid_family_id(self, client):
        """Test searching with non-existent family ID."""
        non_existent_id = str(uuid4())
        response = client.get(f"/api/v1/families/search?family_id={non_existent_id}")
        assert response.status_code == 404
        assert "No families found" in response.json()["detail"]

    def test_search_families_missing_parameters(self, client):
        """Test searching families without required parameters."""
        response = client.get("/api/v1/families/search")
        assert response.status_code == 400
        assert (
            "Either 'q' (search query) or 'family_id' parameter is required"
            in response.json()["detail"]
        )

    def test_search_families_with_limit(self, client, sample_persons):
        """Test searching families with limit parameter."""
        # Create multiple families
        for i in range(5):
            client.post(
                "/api/v1/families", json={"husband_id": sample_persons["husband"]["id"]}
            )

        response = client.get("/api/v1/families/search?q=John&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_search_families_case_insensitive(self, client, sample_family_data):
        """Test that family search is case insensitive."""
        client.post("/api/v1/families", json=sample_family_data)

        # Test lowercase search
        response = client.get("/api/v1/families/search?q=john")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

        # Test uppercase search
        response = client.get("/api/v1/families/search?q=JOHN")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_search_families_partial_match(self, client, sample_family_data):
        """Test searching families with partial name matches."""
        client.post("/api/v1/families", json=sample_family_data)

        # Test partial first name
        response = client.get("/api/v1/families/search?q=Jo")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

        # Test partial last name
        response = client.get("/api/v1/families/search?q=Smi")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_search_families_all_families(self, client, sample_persons):
        """Test getting all families without search query."""
        # Create multiple families
        for i in range(3):
            client.post(
                "/api/v1/families", json={"husband_id": sample_persons["husband"]["id"]}
            )

        response = client.get("/api/v1/families")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3


class TestFamilyDetail:
    """Test family detail endpoint."""

    def test_get_family_detail_success(self, client, sample_family_data):
        """Test getting detailed family information."""
        create_response = client.post("/api/v1/families", json=sample_family_data)
        family_id = create_response.json()["id"]

        response = client.get(f"/api/v1/families/{family_id}/detail")
        assert response.status_code == 200
        data = response.json()

        # Check basic family info
        assert data["id"] == family_id
        assert data["husband_id"] == sample_family_data["husband_id"]
        assert data["wife_id"] == sample_family_data["wife_id"]

        # Check related data structure
        assert "husband" in data
        assert "wife" in data
        assert "children" in data
        assert "events" in data

        # Check spouse details
        assert data["husband"]["first_name"] == "John"
        assert data["wife"]["first_name"] == "Jane"

    def test_get_family_detail_not_found(self, client):
        """Test getting detail for non-existent family."""
        non_existent_id = str(uuid4())
        response = client.get(f"/api/v1/families/{non_existent_id}/detail")
        assert response.status_code == 404
        assert "Family not found" in response.json()["detail"]

    def test_get_family_detail_invalid_uuid(self, client):
        """Test getting family detail with invalid UUID."""
        response = client.get("/api/v1/families/invalid-uuid/detail")
        assert response.status_code == 422

    def test_get_family_detail_with_children(self, client, sample_family_data):
        """Test getting family detail with children."""
        create_response = client.post("/api/v1/families", json=sample_family_data)
        family_id = create_response.json()["id"]

        # Add a child to the family
        child = client.post(
            "/api/v1/persons",
            json={
                "first_name": "Child",
                "last_name": "Doe",
                "sex": "M",
                "birth_date": "2010-01-01",
            },
        ).json()

        client.post(
            "/api/v1/children",
            json={
                "family_id": family_id,
                "child_id": child["id"],
            },
        )

        response = client.get(f"/api/v1/families/{family_id}/detail")
        assert response.status_code == 200
        data = response.json()
        assert len(data["children"]) == 1
        assert data["children"][0]["child_id"] == child["id"]
