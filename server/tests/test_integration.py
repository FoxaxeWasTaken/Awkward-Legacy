import pytest
from datetime import date

from src.crud.person import person_crud
from src.crud.family import family_crud
from src.crud.child import child_crud
from src.crud.event import event_crud
from src.models.person import PersonCreate, Sex
from src.models.family import FamilyCreate
from src.models.child import ChildCreate
from src.models.event import EventCreate


class TestGenealogyIntegration:
    """Integration tests for genealogy workflows."""

    def test_complete_family_tree_workflow(self, test_db):
        """Test creating a complete family tree with multiple generations."""
        grandfather_data = PersonCreate(
            first_name="John",
            last_name="Smith",
            sex=Sex.MALE,
            birth_date="1950-01-01",
            birth_place="New York",
        )
        grandfather = person_crud.create(test_db, grandfather_data)

        grandmother_data = PersonCreate(
            first_name="Mary",
            last_name="Johnson",
            sex=Sex.FEMALE,
            birth_date="1952-03-15",
            birth_place="Boston",
        )
        grandmother = person_crud.create(test_db, grandmother_data)

        father_data = PersonCreate(
            first_name="Robert",
            last_name="Smith",
            sex=Sex.MALE,
            birth_date="1980-05-20",
            birth_place="Chicago",
        )
        father = person_crud.create(test_db, father_data)

        mother_data = PersonCreate(
            first_name="Sarah",
            last_name="Brown",
            sex=Sex.FEMALE,
            birth_date="1982-08-10",
            birth_place="Los Angeles",
        )
        mother = person_crud.create(test_db, mother_data)

        child1_data = PersonCreate(
            first_name="Tom",
            last_name="Smith",
            sex=Sex.MALE,
            birth_date="2010-12-25",
            birth_place="Seattle",
        )
        child1 = person_crud.create(test_db, child1_data)

        child2_data = PersonCreate(
            first_name="Emma",
            last_name="Smith",
            sex=Sex.FEMALE,
            birth_date="2012-07-14",
            birth_place="Seattle",
        )
        child2 = person_crud.create(test_db, child2_data)

        grandparents_marriage = FamilyCreate(
            husband_id=grandfather.id,
            wife_id=grandmother.id,
            marriage_date="1975-06-15",
            marriage_place="New York",
        )
        grandparents_family = family_crud.create(test_db, grandparents_marriage)

        parents_marriage = FamilyCreate(
            husband_id=father.id,
            wife_id=mother.id,
            marriage_date="2005-09-10",
            marriage_place="Las Vegas",
        )
        parents_family = family_crud.create(test_db, parents_marriage)

        father_as_child = ChildCreate(
            family_id=grandparents_family.id, child_id=father.id
        )
        child_crud.create(test_db, father_as_child)

        child1_relationship = ChildCreate(
            family_id=parents_family.id, child_id=child1.id
        )
        child_crud.create(test_db, child1_relationship)

        child2_relationship = ChildCreate(
            family_id=parents_family.id, child_id=child2.id
        )
        child_crud.create(test_db, child2_relationship)

        grandfather_birth = EventCreate(
            person_id=grandfather.id, type="Birth", date="1950-01-01", place="New York"
        )
        event_crud.create(test_db, grandfather_birth)

        parents_wedding = EventCreate(
            family_id=parents_family.id,
            type="Wedding",
            date="2005-09-10",
            place="Las Vegas",
        )
        event_crud.create(test_db, parents_wedding)

        grandparents_children = child_crud.get_by_family(
            test_db, grandparents_family.id
        )
        assert len(grandparents_children) == 1
        assert grandparents_children[0].child_id == father.id

        parents_children = child_crud.get_by_family(test_db, parents_family.id)
        assert len(parents_children) == 2
        child_ids = [c.child_id for c in parents_children]
        assert child1.id in child_ids
        assert child2.id in child_ids

        father_as_husband = family_crud.get_by_husband(test_db, father.id)
        assert len(father_as_husband) == 1
        assert father_as_husband[0].id == parents_family.id

        father_as_child_families = child_crud.get_by_child(test_db, father.id)
        assert len(father_as_child_families) == 1
        assert father_as_child_families[0].family_id == grandparents_family.id

    def test_person_with_multiple_marriages(self, test_db):
        """Test a person with multiple marriages."""
        person_data = PersonCreate(
            first_name="John", last_name="Doe", sex=Sex.MALE, birth_date="1970-01-01"
        )
        person = person_crud.create(test_db, person_data)

        wife1_data = PersonCreate(
            first_name="Jane",
            last_name="Smith",
            sex=Sex.FEMALE,
            birth_date="1972-01-01",
        )
        wife1 = person_crud.create(test_db, wife1_data)

        wife2_data = PersonCreate(
            first_name="Alice",
            last_name="Johnson",
            sex=Sex.FEMALE,
            birth_date="1975-01-01",
        )
        wife2 = person_crud.create(test_db, wife2_data)

        marriage1 = FamilyCreate(
            husband_id=person.id,
            wife_id=wife1.id,
            marriage_date="1995-06-15",
            marriage_place="New York",
        )
        family1 = family_crud.create(test_db, marriage1)

        marriage2 = FamilyCreate(
            husband_id=person.id,
            wife_id=wife2.id,
            marriage_date="2010-08-20",
            marriage_place="Las Vegas",
        )
        family2 = family_crud.create(test_db, marriage2)

        person_marriages = family_crud.get_by_husband(test_db, person.id)
        assert len(person_marriages) == 2

        marriage_ids = [m.id for m in person_marriages]
        assert family1.id in marriage_ids
        assert family2.id in marriage_ids

    def test_person_with_multiple_children_from_different_families(self, test_db):
        """Test a person who is a child in multiple families."""
        person_data = PersonCreate(
            first_name="Child",
            last_name="Person",
            sex=Sex.MALE,
            birth_date="1990-01-01",
        )
        person = person_crud.create(test_db, person_data)

        family1_data = FamilyCreate(marriage_date="1985-01-01")
        family1 = family_crud.create(test_db, family1_data)

        family2_data = FamilyCreate(marriage_date="1995-01-01")
        family2 = family_crud.create(test_db, family2_data)

        child1_relationship = ChildCreate(family_id=family1.id, child_id=person.id)
        child_crud.create(test_db, child1_relationship)

        child2_relationship = ChildCreate(family_id=family2.id, child_id=person.id)
        child_crud.create(test_db, child2_relationship)

        person_families = child_crud.get_by_child(test_db, person.id)
        assert len(person_families) == 2

        family_ids = [f.family_id for f in person_families]
        assert family1.id in family_ids
        assert family2.id in family_ids

    def test_complex_event_timeline(self, test_db):
        """Test creating a complex timeline of events for a person."""
        person_data = PersonCreate(
            first_name="Timeline",
            last_name="Person",
            sex=Sex.MALE,
            birth_date="1980-01-01",
        )
        person = person_crud.create(test_db, person_data)

        family_data = FamilyCreate(marriage_date="2005-06-15")
        family = family_crud.create(test_db, family_data)

        events_data = [
            ("Birth", "1980-01-01", "Hospital", "Born in hospital"),
            ("Baptism", "1980-02-15", "Church", "Baptized in church"),
            ("Graduation", "1998-06-15", "School", "High school graduation"),
            ("Wedding", "2005-06-15", "Garden", "Wedding ceremony"),
            ("Birth of Child", "2007-03-20", "Hospital", "First child born"),
            ("Anniversary", "2015-06-15", "Restaurant", "10th anniversary"),
        ]

        created_events = []
        for event_type, event_date, place, description in events_data:
            event_data = EventCreate(
                person_id=person.id,
                family_id=(
                    family.id
                    if "Wedding" in event_type or "Anniversary" in event_type
                    else None
                ),
                type=event_type,
                date=event_date,
                place=place,
                description=description,
            )
            event = event_crud.create(test_db, event_data)
            created_events.append(event)

        person_events = event_crud.get_by_person(test_db, person.id)
        assert len(person_events) == 6

        family_events = event_crud.get_by_family(test_db, family.id)
        assert len(family_events) == 2

        birth_events = event_crud.get_by_type(test_db, "Birth")
        assert len(birth_events) == 1
        assert birth_events[0].person_id == person.id

    def test_search_functionality_across_entities(self, test_db):
        """Test search functionality across different entities."""
        person1_data = PersonCreate(first_name="John", last_name="Smith", sex=Sex.MALE)
        person1 = person_crud.create(test_db, person1_data)

        person2_data = PersonCreate(
            first_name="Johnny", last_name="Smithson", sex=Sex.MALE
        )
        person2 = person_crud.create(test_db, person2_data)

        person3_data = PersonCreate(
            first_name="Jane", last_name="Smith", sex=Sex.FEMALE
        )
        person3 = person_crud.create(test_db, person3_data)

        event1_data = EventCreate(
            person_id=person1.id, type="Birth Certificate", date="1990-01-01"
        )
        event_crud.create(test_db, event1_data)

        event2_data = EventCreate(
            person_id=person2.id, type="Birth Registration", date="1991-01-01"
        )
        event_crud.create(test_db, event2_data)

        event3_data = EventCreate(
            person_id=person3.id, type="Death Certificate", date="2020-01-01"
        )
        event_crud.create(test_db, event3_data)

        john_persons = person_crud.search_by_name(test_db, "John")
        assert len(john_persons) == 2

        smith_persons = person_crud.search_by_name(test_db, "Smith")
        assert len(smith_persons) == 3

        birth_events = event_crud.search_by_type(test_db, "Birth")
        assert len(birth_events) == 2

        certificate_events = event_crud.search_by_type(test_db, "Certificate")
        assert len(certificate_events) == 2

    def test_data_consistency_after_updates(self, test_db):
        """Test data consistency after various update operations."""
        person_data = PersonCreate(
            first_name="Original",
            last_name="Name",
            sex=Sex.MALE,
            birth_date="1980-01-01",
        )
        person = person_crud.create(test_db, person_data)

        family_data = FamilyCreate(marriage_date="2005-01-01")
        family = family_crud.create(test_db, family_data)

        child_data = ChildCreate(family_id=family.id, child_id=person.id)
        child_crud.create(test_db, child_data)

        event_data = EventCreate(
            person_id=person.id, family_id=family.id, type="Birth", date="1980-01-01"
        )
        event = event_crud.create(test_db, event_data)

        from src.models.person import PersonUpdate

        person_update = PersonUpdate(
            first_name="Updated", last_name="Name", birth_date=date(1985, 1, 1)
        )
        updated_person = person_crud.update(test_db, person.id, person_update)

        from src.models.family import FamilyUpdate

        family_update = FamilyUpdate(
            marriage_date=date(2010, 1, 1), marriage_place="Updated Place"
        )
        updated_family = family_crud.update(test_db, family.id, family_update)

        from src.models.event import EventUpdate

        event_update = EventUpdate(type="Updated Event", place="Updated Place")
        updated_event = event_crud.update(test_db, event.id, event_update)

        assert updated_person.first_name == "Updated"
        assert updated_person.birth_date == date(1985, 1, 1)

        assert updated_family.marriage_date == date(2010, 1, 1)
        assert updated_family.marriage_place == "Updated Place"

        assert updated_event.type == "Updated Event"
        assert updated_event.place == "Updated Place"

        person_families = child_crud.get_by_child(test_db, person.id)
        assert len(person_families) == 1
        assert person_families[0].family_id == family.id

        person_events = event_crud.get_by_person(test_db, person.id)
        assert len(person_events) == 1
        assert person_events[0].id == event.id

    def test_cascade_deletion_behavior(self, test_db):
        """Test cascade deletion behavior across related entities."""
        person_data = PersonCreate(
            first_name="ToDelete", last_name="Person", sex=Sex.MALE
        )
        person = person_crud.create(test_db, person_data)

        family_data = FamilyCreate(marriage_date="2005-01-01")
        family = family_crud.create(test_db, family_data)

        child_data = ChildCreate(family_id=family.id, child_id=person.id)
        child_crud.create(test_db, child_data)

        person_event_data = EventCreate(person_id=person.id, type="Person Event")
        person_event = event_crud.create(test_db, person_event_data)

        family_event_data = EventCreate(family_id=family.id, type="Family Event")
        family_event = event_crud.create(test_db, family_event_data)

        person_crud.delete(test_db, person.id)

        deleted_person = person_crud.get(test_db, person.id)
        assert deleted_person is None

        child_relationships = child_crud.get_by_child(test_db, person.id)
        assert len(child_relationships) == 0

        person_events = event_crud.get_by_person(test_db, person.id)
        assert len(person_events) == 0

        remaining_family = family_crud.get(test_db, family.id)
        assert remaining_family is not None

        family_events = event_crud.get_by_family(test_db, family.id)
        assert len(family_events) == 1
        assert family_events[0].id == family_event.id

        family_crud.delete(test_db, family.id)

        deleted_family = family_crud.get(test_db, family.id)
        assert deleted_family is None

        family_events = event_crud.get_by_family(test_db, family.id)
        assert len(family_events) == 0

    def test_performance_with_large_dataset(self, test_db):
        """Test performance with a larger dataset."""
        persons = []
        for i in range(100):
            person_data = PersonCreate(
                first_name=f"Person{i}",
                last_name="Test",
                sex=Sex.MALE if i % 2 == 0 else Sex.FEMALE,
            )
            person = person_crud.create(test_db, person_data)
            persons.append(person)

        families = []
        for i in range(0, 100, 2):
            family_data = FamilyCreate(
                husband_id=persons[i].id,
                wife_id=persons[i + 1].id,
                marriage_date=f"200{i % 10}-01-01",
            )
            family = family_crud.create(test_db, family_data)
            families.append(family)

        for i in range(0, 50, 2):
            child_data = ChildCreate(
                family_id=families[i // 2].id, child_id=persons[i + 50].id
            )
            child_crud.create(test_db, child_data)

        for i in range(100):
            event_data = EventCreate(
                person_id=persons[i].id,
                type=f"Event{i % 10}",
                date=f"199{i % 10}-01-01",
            )
            event_crud.create(test_db, event_data)

        all_persons = person_crud.get_all(test_db)
        assert len(all_persons) == 100

        all_families = family_crud.get_all(test_db)
        assert len(all_families) == 50

        all_events = event_crud.get_all(test_db)
        assert len(all_events) == 100

        first_page = person_crud.get_all(test_db, skip=0, limit=10)
        assert len(first_page) == 10

        second_page = person_crud.get_all(test_db, skip=10, limit=10)
        assert len(second_page) == 10

        test_persons = person_crud.search_by_name(test_db, "Person1")
        assert len(test_persons) == 11

        event0_events = event_crud.get_by_type(test_db, "Event0")
        assert len(event0_events) == 10
