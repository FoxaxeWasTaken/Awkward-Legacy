"""Test suite for Child CRUD operations."""

import pytest
from uuid import uuid4

from src.crud.child import child_crud
from src.models.child import ChildCreate


class TestChildCRUD:
    """Test class for Child CRUD operations."""

    def test_create_child_relationship(self, test_db, sample_family, sample_person):
        """Test creating a new child relationship."""
        child_data = ChildCreate(family_id=sample_family.id, child_id=sample_person.id)

        created_child = child_crud.create(test_db, child_data)

        assert created_child is not None
        assert created_child.family_id == sample_family.id
        assert created_child.child_id == sample_person.id

    def test_create_child_relationship_duplicate(
        self, test_db, sample_family, sample_person
    ):
        """Test creating a duplicate child relationship."""
        child_data = ChildCreate(family_id=sample_family.id, child_id=sample_person.id)

        child_crud.create(test_db, child_data)

        with pytest.raises(Exception):
            child_crud.create(test_db, child_data)

    def test_get_child_relationship(self, test_db, sample_child):
        """Test getting a child relationship by family and child IDs."""
        retrieved_child = child_crud.get(
            test_db, sample_child.family_id, sample_child.child_id
        )

        assert retrieved_child is not None
        assert retrieved_child.family_id == sample_child.family_id
        assert retrieved_child.child_id == sample_child.child_id

    def test_get_child_relationship_not_found(
        self, test_db, sample_family, sample_person
    ):
        """Test getting a non-existent child relationship."""
        non_existent_child_id = uuid4()

        retrieved_child = child_crud.get(
            test_db, sample_family.id, non_existent_child_id
        )

        assert retrieved_child is None

    def test_get_by_family(self, test_db, sample_child):
        """Test getting all children of a family."""
        children = child_crud.get_by_family(test_db, sample_child.family_id)

        assert len(children) == 1
        assert children[0].family_id == sample_child.family_id
        assert children[0].child_id == sample_child.child_id

    def test_get_by_family_multiple_children(
        self, test_db, sample_family, sample_person, sample_person_2
    ):
        """Test getting multiple children of a family."""
        child1_data = ChildCreate(family_id=sample_family.id, child_id=sample_person.id)
        child1 = child_crud.create(test_db, child1_data)

        child2_data = ChildCreate(
            family_id=sample_family.id, child_id=sample_person_2.id
        )
        child2 = child_crud.create(test_db, child2_data)

        children = child_crud.get_by_family(test_db, sample_family.id)

        assert len(children) == 2
        child_ids = [c.child_id for c in children]
        assert sample_person.id in child_ids
        assert sample_person_2.id in child_ids

    def test_get_by_family_no_children(self, test_db, sample_family):
        """Test getting children of a family with no children."""
        children = child_crud.get_by_family(test_db, sample_family.id)

        assert children == []

    def test_get_by_family_non_existent(self, test_db):
        """Test getting children of a non-existent family."""
        non_existent_family_id = uuid4()

        children = child_crud.get_by_family(test_db, non_existent_family_id)

        assert children == []

    def test_get_by_child(self, test_db, sample_child):
        """Test getting all families where a person is a child."""
        families = child_crud.get_by_child(test_db, sample_child.child_id)

        assert len(families) == 1
        assert families[0].family_id == sample_child.family_id
        assert families[0].child_id == sample_child.child_id

    def test_get_by_child_multiple_families(
        self, test_db, sample_person, sample_family, sample_person_2
    ):
        """Test getting multiple families where a person is a child."""
        child1_data = ChildCreate(family_id=sample_family.id, child_id=sample_person.id)
        child_crud.create(test_db, child1_data)

        family2_data = {
            "husband_id": sample_person_2.id,
            "wife_id": sample_person.id,
            "marriage_date": "2020-01-01",
        }
        from src.crud.family import family_crud
        from src.models.family import FamilyCreate

        family2 = family_crud.create(test_db, FamilyCreate(**family2_data))

        child2_data = ChildCreate(family_id=family2.id, child_id=sample_person.id)
        child_crud.create(test_db, child2_data)

        families = child_crud.get_by_child(test_db, sample_person.id)

        assert len(families) == 2
        family_ids = [f.family_id for f in families]
        assert sample_family.id in family_ids
        assert family2.id in family_ids

    def test_get_by_child_no_families(self, test_db, sample_person):
        """Test getting families for a person who is not a child in any family."""
        families = child_crud.get_by_child(test_db, sample_person.id)

        assert families == []

    def test_get_by_child_non_existent(self, test_db):
        """Test getting families for a non-existent child."""
        non_existent_child_id = uuid4()

        families = child_crud.get_by_child(test_db, non_existent_child_id)

        assert families == []

    def test_get_all_child_relationships_empty(self, test_db):
        """Test getting all child relationships when database is empty."""
        children = child_crud.get_all(test_db)

        assert children == []

    def test_get_all_child_relationships_with_data(self, test_db, sample_child):
        """Test getting all child relationships with data."""
        children = child_crud.get_all(test_db)

        assert len(children) == 1
        assert children[0].family_id == sample_child.family_id
        assert children[0].child_id == sample_child.child_id

    def test_get_all_child_relationships_with_pagination(
        self, test_db, sample_family, sample_person, sample_person_2
    ):
        """Test getting all child relationships with pagination."""
        for i in range(5):
            from src.crud.person import person_crud
            from src.models.person import PersonCreate, Sex

            person_data = PersonCreate(
                first_name=f"Child{i}", last_name="Test", sex=Sex.MALE
            )
            person = person_crud.create(test_db, person_data)

            child_data = ChildCreate(family_id=sample_family.id, child_id=person.id)
            child_crud.create(test_db, child_data)

        children = child_crud.get_all(test_db, skip=0, limit=3)

        assert len(children) == 3

        children = child_crud.get_all(test_db, skip=3, limit=2)

        assert len(children) == 2

    def test_delete_child_relationship(self, test_db, sample_child):
        """Test deleting a child relationship."""
        result = child_crud.delete(
            test_db, sample_child.family_id, sample_child.child_id
        )

        assert result is True

        deleted_child = child_crud.get(
            test_db, sample_child.family_id, sample_child.child_id
        )
        assert deleted_child is None

    def test_delete_child_relationship_not_found(
        self, test_db, sample_family, sample_person
    ):
        """Test deleting a non-existent child relationship."""
        non_existent_child_id = uuid4()

        result = child_crud.delete(test_db, sample_family.id, non_existent_child_id)

        assert result is False

    def test_delete_by_family(
        self, test_db, sample_family, sample_person, sample_person_2
    ):
        """Test deleting all child relationships for a family."""
        child1_data = ChildCreate(family_id=sample_family.id, child_id=sample_person.id)
        child_crud.create(test_db, child1_data)

        child2_data = ChildCreate(
            family_id=sample_family.id, child_id=sample_person_2.id
        )
        child_crud.create(test_db, child2_data)

        deleted_count = child_crud.delete_by_family(test_db, sample_family.id)

        assert deleted_count == 2

        remaining_children = child_crud.get_by_family(test_db, sample_family.id)
        assert remaining_children == []

    def test_delete_by_family_no_children(self, test_db, sample_family):
        """Test deleting child relationships for a family with no children."""
        deleted_count = child_crud.delete_by_family(test_db, sample_family.id)

        assert deleted_count == 0

    def test_delete_by_family_non_existent(self, test_db):
        """Test deleting child relationships for a non-existent family."""
        non_existent_family_id = uuid4()

        deleted_count = child_crud.delete_by_family(test_db, non_existent_family_id)

        assert deleted_count == 0

    def test_delete_by_child(
        self, test_db, sample_person, sample_family, sample_person_2
    ):
        """Test deleting all family relationships for a child."""
        child1_data = ChildCreate(family_id=sample_family.id, child_id=sample_person.id)
        child_crud.create(test_db, child1_data)

        from src.crud.family import family_crud
        from src.models.family import FamilyCreate

        family2_data = FamilyCreate(
            husband_id=sample_person_2.id,
            wife_id=sample_person.id,
            marriage_date="2020-01-01",
        )
        family2 = family_crud.create(test_db, family2_data)

        child2_data = ChildCreate(family_id=family2.id, child_id=sample_person.id)
        child_crud.create(test_db, child2_data)

        deleted_count = child_crud.delete_by_child(test_db, sample_person.id)

        assert deleted_count == 2

        remaining_families = child_crud.get_by_child(test_db, sample_person.id)
        assert remaining_families == []

    def test_delete_by_child_no_families(self, test_db, sample_person):
        """Test deleting family relationships for a child with no families."""
        deleted_count = child_crud.delete_by_child(test_db, sample_person.id)

        assert deleted_count == 0

    def test_delete_by_child_non_existent(self, test_db):
        """Test deleting family relationships for a non-existent child."""
        non_existent_child_id = uuid4()

        deleted_count = child_crud.delete_by_child(test_db, non_existent_child_id)

        assert deleted_count == 0

    def test_child_relationships(self, test_db, sample_child):
        """Test that child relationships are properly established."""
        retrieved_child = child_crud.get(
            test_db, sample_child.family_id, sample_child.child_id
        )

        assert retrieved_child is not None

    def test_child_foreign_key_constraints(self, test_db):
        """Test child foreign key constraints."""
        from sqlalchemy.exc import IntegrityError

        non_existent_family_id = uuid4()
        non_existent_child_id = uuid4()

        child_data = ChildCreate(
            family_id=non_existent_family_id, child_id=non_existent_child_id
        )

        with pytest.raises(IntegrityError):
            child_crud.create(test_db, child_data)

    def test_child_self_relationship(self, test_db, sample_person):
        """Test creating a child relationship where a person is a child of themselves."""

        from src.crud.family import family_crud
        from src.models.family import FamilyCreate

        family_data = FamilyCreate(
            husband_id=sample_person.id,
            wife_id=sample_person.id,
            marriage_date="2015-01-01",
        )
        family = family_crud.create(test_db, family_data)

        child_data = ChildCreate(family_id=family.id, child_id=sample_person.id)

        created_child = child_crud.create(test_db, child_data)
        assert created_child is not None

    def test_child_cascade_behavior(self, test_db, sample_family, sample_person):
        """Test cascade behavior when related entities are deleted."""
        child_data = ChildCreate(family_id=sample_family.id, child_id=sample_person.id)
        child = child_crud.create(test_db, child_data)

        from src.crud.family import family_crud

        family_crud.delete(test_db, sample_family.id)

        remaining_child = child_crud.get(test_db, sample_family.id, sample_person.id)
        assert remaining_child is None
