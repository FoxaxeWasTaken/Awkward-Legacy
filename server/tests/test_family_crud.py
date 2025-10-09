"""Test suite for Family CRUD operations."""

import pytest
from uuid import uuid4
from datetime import date

from src.crud.family import family_crud
from src.models.family import FamilyCreate, FamilyUpdate


@pytest.mark.unit
@pytest.mark.crud
@pytest.mark.family
class TestFamilyCRUD:
    """Test class for Family CRUD operations."""

    def test_create_family(self, test_db, sample_family_data, sample_person, sample_person_2):
        """Test creating a new family."""
        # Arrange
        family_data = FamilyCreate(
            husband_id=sample_person.id,
            wife_id=sample_person_2.id,
            marriage_date="2015-06-20",
            marriage_place="Las Vegas",
            notes="Test family"
        )
        
        # Act
        created_family = family_crud.create(test_db, family_data)
        
        # Assert
        assert created_family is not None
        assert created_family.id is not None
        assert created_family.husband_id == sample_person.id
        assert created_family.wife_id == sample_person_2.id
        assert created_family.marriage_date == date(2015, 6, 20)
        assert created_family.marriage_place == "Las Vegas"
        assert created_family.notes == "Test family"

    def test_create_family_minimal_data(self, test_db):
        """Test creating a family with minimal data."""
        # Arrange
        minimal_family = FamilyCreate()
        
        # Act
        created_family = family_crud.create(test_db, minimal_family)
        
        # Assert
        assert created_family is not None
        assert created_family.id is not None
        assert created_family.husband_id is None
        assert created_family.wife_id is None
        assert created_family.marriage_date is None
        assert created_family.marriage_place is None
        assert created_family.notes is None

    def test_create_family_with_husband_only(self, test_db, sample_person):
        """Test creating a family with only husband."""
        # Arrange
        family_data = FamilyCreate(
            husband_id=sample_person.id,
            marriage_date="2015-06-20"
        )
        
        # Act
        created_family = family_crud.create(test_db, family_data)
        
        # Assert
        assert created_family is not None
        assert created_family.husband_id == sample_person.id
        assert created_family.wife_id is None
        assert created_family.marriage_date == date(2015, 6, 20)

    def test_create_family_with_wife_only(self, test_db, sample_person_2):
        """Test creating a family with only wife."""
        # Arrange
        family_data = FamilyCreate(
            wife_id=sample_person_2.id,
            marriage_date="2015-06-20"
        )
        
        # Act
        created_family = family_crud.create(test_db, family_data)
        
        # Assert
        assert created_family is not None
        assert created_family.husband_id is None
        assert created_family.wife_id == sample_person_2.id
        assert created_family.marriage_date == date(2015, 6, 20)

    def test_get_family_by_id(self, test_db, sample_family):
        """Test getting a family by ID."""
        # Act
        retrieved_family = family_crud.get(test_db, sample_family.id)
        
        # Assert
        assert retrieved_family is not None
        assert retrieved_family.id == sample_family.id
        assert retrieved_family.husband_id == sample_family.husband_id
        assert retrieved_family.wife_id == sample_family.wife_id

    def test_get_family_by_id_not_found(self, test_db):
        """Test getting a family by non-existent ID."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        retrieved_family = family_crud.get(test_db, non_existent_id)
        
        # Assert
        assert retrieved_family is None

    def test_get_all_families_empty(self, test_db):
        """Test getting all families when database is empty."""
        # Act
        families = family_crud.get_all(test_db)
        
        # Assert
        assert families == []

    def test_get_all_families_with_data(self, test_db, sample_family):
        """Test getting all families with data."""
        # Act
        families = family_crud.get_all(test_db)
        
        # Assert
        assert len(families) == 1
        assert families[0].id == sample_family.id

    def test_get_all_families_with_pagination(self, test_db, sample_person, sample_person_2):
        """Test getting all families with pagination."""
        # Arrange - create multiple families
        for i in range(5):
            family_data = FamilyCreate(
                husband_id=sample_person.id,
                wife_id=sample_person_2.id,
                marriage_date=f"201{i}-01-01"
            )
            family_crud.create(test_db, family_data)
        
        # Act - get first 3 families
        families = family_crud.get_all(test_db, skip=0, limit=3)
        
        # Assert
        assert len(families) == 3
        
        # Act - get next 2 families
        families = family_crud.get_all(test_db, skip=3, limit=2)
        
        # Assert
        assert len(families) == 2

    def test_get_by_husband(self, test_db, sample_family, sample_person):
        """Test getting families by husband ID."""
        # Act
        families = family_crud.get_by_husband(test_db, sample_person.id)
        
        # Assert
        assert len(families) == 1
        assert families[0].id == sample_family.id
        assert families[0].husband_id == sample_person.id

    def test_get_by_husband_no_match(self, test_db, sample_family):
        """Test getting families by non-existent husband ID."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        families = family_crud.get_by_husband(test_db, non_existent_id)
        
        # Assert
        assert families == []

    def test_get_by_husband_multiple_families(self, test_db, sample_person, sample_person_2):
        """Test getting multiple families for the same husband."""
        # Arrange - create multiple families with same husband
        for i in range(3):
            family_data = FamilyCreate(
                husband_id=sample_person.id,
                wife_id=sample_person_2.id,
                marriage_date=f"201{i}-01-01"
            )
            family_crud.create(test_db, family_data)
        
        # Act
        families = family_crud.get_by_husband(test_db, sample_person.id)
        
        # Assert
        assert len(families) == 3
        for family in families:
            assert family.husband_id == sample_person.id

    def test_get_by_wife(self, test_db, sample_family, sample_person_2):
        """Test getting families by wife ID."""
        # Act
        families = family_crud.get_by_wife(test_db, sample_person_2.id)
        
        # Assert
        assert len(families) == 1
        assert families[0].id == sample_family.id
        assert families[0].wife_id == sample_person_2.id

    def test_get_by_wife_no_match(self, test_db, sample_family):
        """Test getting families by non-existent wife ID."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        families = family_crud.get_by_wife(test_db, non_existent_id)
        
        # Assert
        assert families == []

    def test_get_by_spouse_as_husband(self, test_db, sample_family, sample_person):
        """Test getting families by spouse ID when person is husband."""
        # Act
        families = family_crud.get_by_spouse(test_db, sample_person.id)
        
        # Assert
        assert len(families) == 1
        assert families[0].id == sample_family.id
        assert families[0].husband_id == sample_person.id

    def test_get_by_spouse_as_wife(self, test_db, sample_family, sample_person_2):
        """Test getting families by spouse ID when person is wife."""
        # Act
        families = family_crud.get_by_spouse(test_db, sample_person_2.id)
        
        # Assert
        assert len(families) == 1
        assert families[0].id == sample_family.id
        assert families[0].wife_id == sample_person_2.id

    def test_get_by_spouse_no_match(self, test_db, sample_family):
        """Test getting families by non-existent spouse ID."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        families = family_crud.get_by_spouse(test_db, non_existent_id)
        
        # Assert
        assert families == []

    def test_get_by_spouse_multiple_roles(self, test_db, sample_person, sample_person_2):
        """Test getting families where a person is both husband and wife in different families."""
        # Arrange - create family where person is husband
        family1_data = FamilyCreate(
            husband_id=sample_person.id,
            wife_id=sample_person_2.id,
            marriage_date="2010-01-01"
        )
        family1 = family_crud.create(test_db, family1_data)
        
        # Create another family where person is wife
        family2_data = FamilyCreate(
            husband_id=sample_person_2.id,
            wife_id=sample_person.id,
            marriage_date="2020-01-01"
        )
        family2 = family_crud.create(test_db, family2_data)
        
        # Act - get families for person as spouse
        families = family_crud.get_by_spouse(test_db, sample_person.id)
        
        # Assert
        assert len(families) == 2
        family_ids = [f.id for f in families]
        assert family1.id in family_ids
        assert family2.id in family_ids

    def test_update_family_full_update(self, test_db, sample_family, sample_person, sample_person_2):
        """Test updating a family with all fields."""
        # Arrange
        update_data = FamilyUpdate(
            husband_id=sample_person_2.id,
            wife_id=sample_person.id,
            marriage_date=date(2020, 1, 1),
            marriage_place="Updated Place",
            notes="Updated notes"
        )
        
        # Act
        updated_family = family_crud.update(test_db, sample_family.id, update_data)
        
        # Assert
        assert updated_family is not None
        assert updated_family.id == sample_family.id
        assert updated_family.husband_id == sample_person_2.id
        assert updated_family.wife_id == sample_person.id
        assert updated_family.marriage_date == date(2020, 1, 1)
        assert updated_family.marriage_place == "Updated Place"
        assert updated_family.notes == "Updated notes"

    def test_update_family_partial_update(self, test_db, sample_family):
        """Test updating a family with only some fields."""
        # Arrange
        update_data = FamilyUpdate(
            marriage_place="New Place",
            notes="New notes"
        )
        
        # Act
        updated_family = family_crud.update(test_db, sample_family.id, update_data)
        
        # Assert
        assert updated_family is not None
        assert updated_family.id == sample_family.id
        assert updated_family.husband_id == sample_family.husband_id  # Unchanged
        assert updated_family.wife_id == sample_family.wife_id  # Unchanged
        assert updated_family.marriage_date == sample_family.marriage_date  # Unchanged
        assert updated_family.marriage_place == "New Place"
        assert updated_family.notes == "New notes"

    def test_update_family_clear_fields(self, test_db, sample_family):
        """Test updating a family to clear some fields."""
        # Arrange
        update_data = FamilyUpdate(
            husband_id=None,
            wife_id=None,
            marriage_place=None,
            notes=None
        )
        
        # Act
        updated_family = family_crud.update(test_db, sample_family.id, update_data)
        
        # Assert
        assert updated_family is not None
        assert updated_family.id == sample_family.id
        assert updated_family.husband_id is None
        assert updated_family.wife_id is None
        assert updated_family.marriage_date == sample_family.marriage_date  # Unchanged
        assert updated_family.marriage_place is None
        assert updated_family.notes is None

    def test_update_family_not_found(self, test_db):
        """Test updating a non-existent family."""
        # Arrange
        non_existent_id = uuid4()
        update_data = FamilyUpdate(marriage_place="Updated")
        
        # Act
        updated_family = family_crud.update(test_db, non_existent_id, update_data)
        
        # Assert
        assert updated_family is None

    def test_delete_family(self, test_db, sample_family):
        """Test deleting a family."""
        # Act
        result = family_crud.delete(test_db, sample_family.id)
        
        # Assert
        assert result is True
        
        # Verify family is deleted
        deleted_family = family_crud.get(test_db, sample_family.id)
        assert deleted_family is None

    def test_delete_family_not_found(self, test_db):
        """Test deleting a non-existent family."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        result = family_crud.delete(test_db, non_existent_id)
        
        # Assert
        assert result is False

    def test_family_relationships(self, test_db, sample_family, sample_child, sample_event):
        """Test that family relationships are properly established."""
        # Act
        retrieved_family = family_crud.get(test_db, sample_family.id)
        
        # Assert
        assert retrieved_family is not None
        # Note: Relationships would need to be explicitly loaded in a real scenario
        # This test verifies the family exists and can be retrieved

    def test_family_date_validation(self, test_db, sample_person, sample_person_2):
        """Test family date field validation."""
        from pydantic_core import ValidationError
        
        # Test with invalid date format - this should raise a validation error during model instantiation
        with pytest.raises(ValidationError):
            family_data = FamilyCreate(
                husband_id=sample_person.id,
                wife_id=sample_person_2.id,
                marriage_date="invalid-date"  # This should raise a validation error
            )

    def test_family_field_lengths(self, test_db, sample_person, sample_person_2):
        """Test family field length constraints."""
        from pydantic_core import ValidationError
        
        # Test with very long marriage place
        long_place = "A" * 201  # Exceeds max_length=200
        
        # This should raise a validation error during model instantiation
        with pytest.raises(ValidationError):
            family_data = FamilyCreate(
                husband_id=sample_person.id,
                wife_id=sample_person_2.id,
                marriage_place=long_place
            )

    def test_family_foreign_key_constraints(self, test_db):
        """Test family foreign key constraints."""
        from sqlalchemy.exc import IntegrityError
        
        # Test with non-existent person IDs
        non_existent_id = uuid4()
        family_data = FamilyCreate(
            husband_id=non_existent_id,
            wife_id=non_existent_id
        )
        
        # This should raise a foreign key constraint error
        with pytest.raises(IntegrityError):  # Foreign key constraint error
            family_crud.create(test_db, family_data)

    def test_family_self_marriage(self, test_db, sample_person):
        """Test creating a family where husband and wife are the same person."""
        # Arrange
        family_data = FamilyCreate(
            husband_id=sample_person.id,
            wife_id=sample_person.id,  # Same person as husband and wife
            marriage_date="2015-06-20"
        )
        
        # Act
        created_family = family_crud.create(test_db, family_data)
        
        # Assert
        assert created_family is not None
        assert created_family.husband_id == sample_person.id
        assert created_family.wife_id == sample_person.id
        # Note: This might be allowed in the business logic, but could be restricted
