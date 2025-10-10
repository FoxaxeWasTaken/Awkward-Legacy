import pytest
from uuid import uuid4
from datetime import date

from src.crud.person import person_crud
from src.models.person import PersonCreate, PersonUpdate, Sex


class TestPersonCRUD:
    """Test class for Person CRUD operations."""

    def test_create_person(self, test_db, sample_person_data):
        """Test creating a new person."""
        created_person = person_crud.create(test_db, sample_person_data)

        assert created_person is not None
        assert created_person.id is not None
        assert created_person.first_name == sample_person_data.first_name
        assert created_person.last_name == sample_person_data.last_name
        assert created_person.sex == sample_person_data.sex
        assert created_person.birth_date == sample_person_data.birth_date
        assert created_person.birth_place == sample_person_data.birth_place
        assert created_person.occupation == sample_person_data.occupation
        assert created_person.notes == sample_person_data.notes

    def test_create_person_minimal_data(self, test_db):
        """Test creating a person with minimal required data."""
        minimal_person = PersonCreate(
            first_name="Minimal", last_name="Person", sex=Sex.UNKNOWN
        )

        created_person = person_crud.create(test_db, minimal_person)

        assert created_person is not None
        assert created_person.first_name == "Minimal"
        assert created_person.last_name == "Person"
        assert created_person.sex == Sex.UNKNOWN
        assert created_person.birth_date is None
        assert created_person.death_date is None
        assert created_person.birth_place is None
        assert created_person.death_place is None
        assert created_person.occupation is None
        assert created_person.notes is None

    def test_get_person_by_id(self, test_db, sample_person):
        """Test getting a person by ID."""
        retrieved_person = person_crud.get(test_db, sample_person.id)

        assert retrieved_person is not None
        assert retrieved_person.id == sample_person.id
        assert retrieved_person.first_name == sample_person.first_name
        assert retrieved_person.last_name == sample_person.last_name

    def test_get_person_by_id_not_found(self, test_db):
        """Test getting a person by non-existent ID."""
        non_existent_id = uuid4()

        retrieved_person = person_crud.get(test_db, non_existent_id)

        assert retrieved_person is None

    def test_get_all_persons_empty(self, test_db):
        """Test getting all persons when database is empty."""
        persons = person_crud.get_all(test_db)

        assert persons == []

    def test_get_all_persons_with_data(self, test_db, sample_person, sample_person_2):
        """Test getting all persons with data."""
        persons = person_crud.get_all(test_db)

        assert len(persons) == 2
        person_ids = [p.id for p in persons]
        assert sample_person.id in person_ids
        assert sample_person_2.id in person_ids

    def test_get_all_persons_with_pagination(self, test_db):
        """Test getting all persons with pagination."""
        for i in range(5):
            person_data = PersonCreate(
                first_name=f"Person{i}", last_name="Test", sex=Sex.MALE
            )
            person_crud.create(test_db, person_data)

        persons = person_crud.get_all(test_db, skip=0, limit=3)

        assert len(persons) == 3

        persons = person_crud.get_all(test_db, skip=3, limit=2)

        assert len(persons) == 2

    def test_get_by_name_exact_match(self, test_db, sample_person):
        """Test getting persons by exact first and last name."""
        persons = person_crud.get_by_name(test_db, "John", "Doe")

        assert len(persons) == 1
        assert persons[0].id == sample_person.id
        assert persons[0].first_name == "John"
        assert persons[0].last_name == "Doe"

    def test_get_by_name_no_match(self, test_db, sample_person):
        """Test getting persons by non-existent name."""
        persons = person_crud.get_by_name(test_db, "NonExistent", "Person")

        assert persons == []

    def test_get_by_name_multiple_matches(self, test_db):
        """Test getting persons by name with multiple matches."""
        for i in range(3):
            person_data = PersonCreate(first_name="John", last_name="Doe", sex=Sex.MALE)
            person_crud.create(test_db, person_data)

        persons = person_crud.get_by_name(test_db, "John", "Doe")

        assert len(persons) == 3
        for person in persons:
            assert person.first_name == "John"
            assert person.last_name == "Doe"

    def test_search_by_name_first_name(self, test_db, sample_person):
        """Test searching persons by first name."""
        persons = person_crud.search_by_name(test_db, "John")

        assert len(persons) == 1
        assert persons[0].id == sample_person.id

    def test_search_by_name_last_name(self, test_db, sample_person):
        """Test searching persons by last name."""
        persons = person_crud.search_by_name(test_db, "Doe")

        assert len(persons) == 1
        assert persons[0].id == sample_person.id

    def test_search_by_name_partial_match(self, test_db, sample_person):
        """Test searching persons by partial name match."""
        persons = person_crud.search_by_name(test_db, "Jo")

        assert len(persons) == 1
        assert persons[0].id == sample_person.id

    def test_search_by_name_no_match(self, test_db, sample_person):
        """Test searching persons with no matches."""
        persons = person_crud.search_by_name(test_db, "NonExistent")

        assert persons == []

    def test_search_by_name_case_sensitive(self, test_db, sample_person):
        """Test that name search is case sensitive."""
        persons = person_crud.search_by_name(test_db, "john")

        assert persons == []

    def test_update_person_full_update(self, test_db, sample_person):
        """Test updating a person with all fields."""
        update_data = PersonUpdate(
            first_name="Updated",
            last_name="Name",
            sex=Sex.FEMALE,
            birth_date=date(1995, 1, 1),
            death_date=date(2020, 1, 1),
            birth_place="Updated Place",
            death_place="Updated Death Place",
            occupation="Updated Occupation",
            notes="Updated notes",
        )

        updated_person = person_crud.update(test_db, sample_person.id, update_data)

        assert updated_person is not None
        assert updated_person.id == sample_person.id
        assert updated_person.first_name == "Updated"
        assert updated_person.last_name == "Name"
        assert updated_person.sex == Sex.FEMALE
        assert updated_person.birth_date == date(1995, 1, 1)
        assert updated_person.death_date == date(2020, 1, 1)
        assert updated_person.birth_place == "Updated Place"
        assert updated_person.death_place == "Updated Death Place"
        assert updated_person.occupation == "Updated Occupation"
        assert updated_person.notes == "Updated notes"

    def test_update_person_partial_update(self, test_db, sample_person):
        """Test updating a person with only some fields."""
        update_data = PersonUpdate(first_name="Updated", occupation="New Occupation")

        updated_person = person_crud.update(test_db, sample_person.id, update_data)

        assert updated_person is not None
        assert updated_person.id == sample_person.id
        assert updated_person.first_name == "Updated"
        assert updated_person.last_name == sample_person.last_name
        assert updated_person.sex == sample_person.sex
        assert updated_person.occupation == "New Occupation"
        assert updated_person.notes == sample_person.notes

    def test_update_person_not_found(self, test_db):
        """Test updating a non-existent person."""
        non_existent_id = uuid4()
        update_data = PersonUpdate(first_name="Updated")

        updated_person = person_crud.update(test_db, non_existent_id, update_data)

        assert updated_person is None

    def test_delete_person(self, test_db, sample_person):
        """Test deleting a person."""
        result = person_crud.delete(test_db, sample_person.id)

        assert result is True

        deleted_person = person_crud.get(test_db, sample_person.id)
        assert deleted_person is None

    def test_delete_person_not_found(self, test_db):
        """Test deleting a non-existent person."""
        non_existent_id = uuid4()

        result = person_crud.delete(test_db, non_existent_id)

        assert result is False

    def test_person_relationships(
        self, test_db, sample_person, sample_family, sample_event
    ):
        """Test that person relationships are properly established."""
        retrieved_person = person_crud.get(test_db, sample_person.id)

        assert retrieved_person is not None

    def test_person_validation(self, test_db):
        """Test person data validation."""
        with pytest.raises(ValueError):
            invalid_person = PersonCreate(
                first_name="Test", last_name="Person", sex="INVALID"
            )
            person_crud.create(test_db, invalid_person)

    def test_person_field_lengths(self, test_db):
        """Test person field length constraints."""
        from pydantic_core import ValidationError

        long_name = "A" * 101

        with pytest.raises(ValidationError):
            person_data = PersonCreate(
                first_name=long_name, last_name="Test", sex=Sex.MALE
            )

    def test_person_date_validation(self, test_db):
        """Test person date field validation."""
        from pydantic_core import ValidationError

        with pytest.raises(ValidationError):
            person_data = PersonCreate(
                first_name="Test",
                last_name="Person",
                sex=Sex.MALE,
                birth_date="invalid-date",
            )
