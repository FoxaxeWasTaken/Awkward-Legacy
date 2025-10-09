"""Test suite for Family CRUD operations."""

import pytest
from uuid import uuid4
from datetime import date

from src.crud.family import family_crud
from src.models.family import FamilyCreate, FamilyUpdate


class TestFamilyCRUD:
    """Test class for Family CRUD operations."""

    def test_create_family(
        self, test_db, sample_family_data, sample_person, sample_person_2
    ):
        """Test creating a new family."""
        family_data = FamilyCreate(
            husband_id=sample_person.id,
            wife_id=sample_person_2.id,
            marriage_date="2015-06-20",
            marriage_place="Las Vegas",
            notes="Test family",
        )

        created_family = family_crud.create(test_db, family_data)

        assert created_family is not None
        assert created_family.id is not None
        assert created_family.husband_id == sample_person.id
        assert created_family.wife_id == sample_person_2.id
        assert created_family.marriage_date == date(2015, 6, 20)
        assert created_family.marriage_place == "Las Vegas"
        assert created_family.notes == "Test family"

    def test_create_family_minimal_data(self, test_db):
        """Test creating a family with minimal data."""
        minimal_family = FamilyCreate()

        created_family = family_crud.create(test_db, minimal_family)

        assert created_family is not None
        assert created_family.id is not None
        assert created_family.husband_id is None
        assert created_family.wife_id is None
        assert created_family.marriage_date is None
        assert created_family.marriage_place is None
        assert created_family.notes is None

    def test_create_family_with_husband_only(self, test_db, sample_person):
        """Test creating a family with only husband."""
        family_data = FamilyCreate(
            husband_id=sample_person.id, marriage_date="2015-06-20"
        )

        created_family = family_crud.create(test_db, family_data)

        assert created_family is not None
        assert created_family.husband_id == sample_person.id
        assert created_family.wife_id is None
        assert created_family.marriage_date == date(2015, 6, 20)

    def test_create_family_with_wife_only(self, test_db, sample_person_2):
        """Test creating a family with only wife."""
        family_data = FamilyCreate(
            wife_id=sample_person_2.id, marriage_date="2015-06-20"
        )

        created_family = family_crud.create(test_db, family_data)

        assert created_family is not None
        assert created_family.husband_id is None
        assert created_family.wife_id == sample_person_2.id
        assert created_family.marriage_date == date(2015, 6, 20)

    def test_get_family_by_id(self, test_db, sample_family):
        """Test getting a family by ID."""
        retrieved_family = family_crud.get(test_db, sample_family.id)

        assert retrieved_family is not None
        assert retrieved_family.id == sample_family.id
        assert retrieved_family.husband_id == sample_family.husband_id
        assert retrieved_family.wife_id == sample_family.wife_id

    def test_get_family_by_id_not_found(self, test_db):
        """Test getting a family by non-existent ID."""
        non_existent_id = uuid4()

        retrieved_family = family_crud.get(test_db, non_existent_id)

        assert retrieved_family is None

    def test_get_all_families_empty(self, test_db):
        """Test getting all families when database is empty."""
        families = family_crud.get_all(test_db)

        assert families == []

    def test_get_all_families_with_data(self, test_db, sample_family):
        """Test getting all families with data."""
        families = family_crud.get_all(test_db)

        assert len(families) == 1
        assert families[0].id == sample_family.id

    def test_get_all_families_with_pagination(
        self, test_db, sample_person, sample_person_2
    ):
        """Test getting all families with pagination."""
        for i in range(5):
            family_data = FamilyCreate(
                husband_id=sample_person.id,
                wife_id=sample_person_2.id,
                marriage_date=f"201{i}-01-01",
            )
            family_crud.create(test_db, family_data)

        families = family_crud.get_all(test_db, skip=0, limit=3)

        assert len(families) == 3

        families = family_crud.get_all(test_db, skip=3, limit=2)

        assert len(families) == 2

    def test_get_by_husband(self, test_db, sample_family, sample_person):
        """Test getting families by husband ID."""
        families = family_crud.get_by_husband(test_db, sample_person.id)

        assert len(families) == 1
        assert families[0].id == sample_family.id
        assert families[0].husband_id == sample_person.id

    def test_get_by_husband_no_match(self, test_db, sample_family):
        """Test getting families by non-existent husband ID."""
        non_existent_id = uuid4()

        families = family_crud.get_by_husband(test_db, non_existent_id)

        assert families == []

    def test_get_by_husband_multiple_families(
        self, test_db, sample_person, sample_person_2
    ):
        """Test getting multiple families for the same husband."""
        for i in range(3):
            family_data = FamilyCreate(
                husband_id=sample_person.id,
                wife_id=sample_person_2.id,
                marriage_date=f"201{i}-01-01",
            )
            family_crud.create(test_db, family_data)

        families = family_crud.get_by_husband(test_db, sample_person.id)

        assert len(families) == 3
        for family in families:
            assert family.husband_id == sample_person.id

    def test_get_by_wife(self, test_db, sample_family, sample_person_2):
        """Test getting families by wife ID."""
        families = family_crud.get_by_wife(test_db, sample_person_2.id)

        assert len(families) == 1
        assert families[0].id == sample_family.id
        assert families[0].wife_id == sample_person_2.id

    def test_get_by_wife_no_match(self, test_db, sample_family):
        """Test getting families by non-existent wife ID."""
        non_existent_id = uuid4()

        families = family_crud.get_by_wife(test_db, non_existent_id)

        assert families == []

    def test_get_by_spouse_as_husband(self, test_db, sample_family, sample_person):
        """Test getting families by spouse ID when person is husband."""
        families = family_crud.get_by_spouse(test_db, sample_person.id)

        assert len(families) == 1
        assert families[0].id == sample_family.id
        assert families[0].husband_id == sample_person.id

    def test_get_by_spouse_as_wife(self, test_db, sample_family, sample_person_2):
        """Test getting families by spouse ID when person is wife."""
        families = family_crud.get_by_spouse(test_db, sample_person_2.id)

        assert len(families) == 1
        assert families[0].id == sample_family.id
        assert families[0].wife_id == sample_person_2.id

    def test_get_by_spouse_no_match(self, test_db, sample_family):
        """Test getting families by non-existent spouse ID."""
        non_existent_id = uuid4()

        families = family_crud.get_by_spouse(test_db, non_existent_id)

        assert families == []

    def test_get_by_spouse_multiple_roles(
        self, test_db, sample_person, sample_person_2
    ):
        """Test getting families where a person is both husband and wife in different families."""
        family1_data = FamilyCreate(
            husband_id=sample_person.id,
            wife_id=sample_person_2.id,
            marriage_date="2010-01-01",
        )
        family1 = family_crud.create(test_db, family1_data)

        family2_data = FamilyCreate(
            husband_id=sample_person_2.id,
            wife_id=sample_person.id,
            marriage_date="2020-01-01",
        )
        family2 = family_crud.create(test_db, family2_data)

        families = family_crud.get_by_spouse(test_db, sample_person.id)

        assert len(families) == 2
        family_ids = [f.id for f in families]
        assert family1.id in family_ids
        assert family2.id in family_ids

    def test_update_family_full_update(
        self, test_db, sample_family, sample_person, sample_person_2
    ):
        """Test updating a family with all fields."""
        update_data = FamilyUpdate(
            husband_id=sample_person_2.id,
            wife_id=sample_person.id,
            marriage_date=date(2020, 1, 1),
            marriage_place="Updated Place",
            notes="Updated notes",
        )

        updated_family = family_crud.update(test_db, sample_family.id, update_data)

        assert updated_family is not None
        assert updated_family.id == sample_family.id
        assert updated_family.husband_id == sample_person_2.id
        assert updated_family.wife_id == sample_person.id
        assert updated_family.marriage_date == date(2020, 1, 1)
        assert updated_family.marriage_place == "Updated Place"
        assert updated_family.notes == "Updated notes"

    def test_update_family_partial_update(self, test_db, sample_family):
        """Test updating a family with only some fields."""
        update_data = FamilyUpdate(marriage_place="New Place", notes="New notes")

        updated_family = family_crud.update(test_db, sample_family.id, update_data)

        assert updated_family is not None
        assert updated_family.id == sample_family.id
        assert updated_family.husband_id == sample_family.husband_id
        assert updated_family.wife_id == sample_family.wife_id
        assert updated_family.marriage_date == sample_family.marriage_date
        assert updated_family.marriage_place == "New Place"
        assert updated_family.notes == "New notes"

    def test_update_family_clear_fields(self, test_db, sample_family):
        """Test updating a family to clear some fields."""
        update_data = FamilyUpdate(
            husband_id=None, wife_id=None, marriage_place=None, notes=None
        )

        updated_family = family_crud.update(test_db, sample_family.id, update_data)

        assert updated_family is not None
        assert updated_family.id == sample_family.id
        assert updated_family.husband_id is None
        assert updated_family.wife_id is None
        assert updated_family.marriage_date == sample_family.marriage_date
        assert updated_family.marriage_place is None
        assert updated_family.notes is None

    def test_update_family_not_found(self, test_db):
        """Test updating a non-existent family."""
        non_existent_id = uuid4()
        update_data = FamilyUpdate(marriage_place="Updated")

        updated_family = family_crud.update(test_db, non_existent_id, update_data)

        assert updated_family is None

    def test_delete_family(self, test_db, sample_family):
        """Test deleting a family."""
        result = family_crud.delete(test_db, sample_family.id)

        assert result is True

        deleted_family = family_crud.get(test_db, sample_family.id)
        assert deleted_family is None

    def test_delete_family_not_found(self, test_db):
        """Test deleting a non-existent family."""
        non_existent_id = uuid4()

        result = family_crud.delete(test_db, non_existent_id)

        assert result is False

    def test_family_relationships(
        self, test_db, sample_family, sample_child, sample_event
    ):
        """Test that family relationships are properly established."""
        retrieved_family = family_crud.get(test_db, sample_family.id)

        assert retrieved_family is not None

    def test_family_date_validation(self, test_db, sample_person, sample_person_2):
        """Test family date field validation."""
        from pydantic_core import ValidationError

        with pytest.raises(ValidationError):
            family_data = FamilyCreate(
                husband_id=sample_person.id,
                wife_id=sample_person_2.id,
                marriage_date="invalid-date",
            )

    def test_family_field_lengths(self, test_db, sample_person, sample_person_2):
        """Test family field length constraints."""
        from pydantic_core import ValidationError

        long_place = "A" * 201

        with pytest.raises(ValidationError):
            family_data = FamilyCreate(
                husband_id=sample_person.id,
                wife_id=sample_person_2.id,
                marriage_place=long_place,
            )

    def test_family_foreign_key_constraints(self, test_db):
        """Test family foreign key constraints."""
        from sqlalchemy.exc import IntegrityError

        non_existent_id = uuid4()
        family_data = FamilyCreate(husband_id=non_existent_id, wife_id=non_existent_id)

        with pytest.raises(IntegrityError):
            family_crud.create(test_db, family_data)

    def test_family_self_marriage(self, test_db, sample_person):
        """Test creating a family where husband and wife are the same person."""
        family_data = FamilyCreate(
            husband_id=sample_person.id,
            wife_id=sample_person.id,
            marriage_date="2015-06-20",
        )

        created_family = family_crud.create(test_db, family_data)

        assert created_family is not None
        assert created_family.husband_id == sample_person.id
        assert created_family.wife_id == sample_person.id
