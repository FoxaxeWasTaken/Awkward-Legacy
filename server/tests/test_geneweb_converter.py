"""
Tests for geneweb_converter module.
"""

import pytest
from unittest.mock import Mock, patch
from src.geneweb_converter import json_to_db, db_to_json


class TestJsonToDb:
    """Test the json_to_db function."""

    def test_json_to_db_empty_data(self):
        """Test inserting empty data."""
        mock_session = Mock()

        with patch("src.geneweb_converter.person_crud") as mock_person_crud, patch(
            "src.geneweb_converter.family_crud"
        ) as mock_family_crud, patch(
            "src.geneweb_converter.event_crud"
        ) as mock_event_crud, patch(
            "src.geneweb_converter.child_crud"
        ) as mock_child_crud:

            data = {"persons": [], "families": [], "events": [], "children": []}

            result = json_to_db(data, mock_session)

            expected = {
                "persons_created": 0,
                "families_created": 0,
                "events_created": 0,
                "children_created": 0,
            }
            assert result == expected

            mock_person_crud.create.assert_not_called()
            mock_family_crud.create.assert_not_called()
            mock_event_crud.create.assert_not_called()
            mock_child_crud.create.assert_not_called()

    def test_json_to_db_with_persons_only(self):
        """Test inserting data with persons only."""
        mock_session = Mock()

        with patch("src.geneweb_converter.person_crud") as mock_person_crud, patch(
            "src.geneweb_converter.family_crud"
        ) as mock_family_crud, patch(
            "src.geneweb_converter.event_crud"
        ) as mock_event_crud, patch(
            "src.geneweb_converter.child_crud"
        ) as mock_child_crud:

            mock_person = Mock()
            mock_person.id = "person1"
            mock_person_crud.create.return_value = mock_person

            data = {
                "persons": [
                    {
                        "id": "person1",
                        "first_name": "John",
                        "last_name": "Doe",
                        "sex": "M",
                    }
                ],
                "families": [],
                "events": [],
                "children": [],
            }

            result = json_to_db(data, mock_session)

            expected = {
                "persons_created": 1,
                "families_created": 0,
                "events_created": 0,
                "children_created": 0,
            }
            assert result == expected

            mock_person_crud.create.assert_called_once_with(
                mock_session, data["persons"][0]
            )
            mock_family_crud.create.assert_not_called()
            mock_event_crud.create.assert_not_called()
            mock_child_crud.create.assert_not_called()

    def test_json_to_db_with_families(self):
        """Test inserting data with families."""
        mock_session = Mock()

        with patch("src.geneweb_converter.person_crud") as mock_person_crud, patch(
            "src.geneweb_converter.family_crud"
        ) as mock_family_crud, patch(
            "src.geneweb_converter.event_crud"
        ) as mock_event_crud, patch(
            "src.geneweb_converter.child_crud"
        ) as mock_child_crud:

            mock_person1 = Mock()
            mock_person1.id = "person1"
            mock_person2 = Mock()
            mock_person2.id = "person2"
            mock_person_crud.create.side_effect = [mock_person1, mock_person2]

            mock_family = Mock()
            mock_family.id = "family1"
            mock_family_crud.create.return_value = mock_family

            data = {
                "persons": [
                    {
                        "id": "person1",
                        "first_name": "John",
                        "last_name": "Doe",
                        "sex": "M",
                    },
                    {
                        "id": "person2",
                        "first_name": "Jane",
                        "last_name": "Smith",
                        "sex": "F",
                    },
                ],
                "families": [
                    {"id": "family1", "husband_id": "person1", "wife_id": "person2"}
                ],
                "events": [],
                "children": [],
            }

            result = json_to_db(data, mock_session)

            expected = {
                "persons_created": 2,
                "families_created": 1,
                "events_created": 0,
                "children_created": 0,
            }
            assert result == expected

            assert mock_person_crud.create.call_count == 2

            family_call = mock_family_crud.create.call_args[0][1]
            assert family_call["husband_id"] == "person1"
            assert family_call["wife_id"] == "person2"

    def test_json_to_db_with_events(self):
        """Test inserting data with events."""
        mock_session = Mock()

        with patch("src.geneweb_converter.person_crud") as mock_person_crud, patch(
            "src.geneweb_converter.family_crud"
        ) as mock_family_crud, patch(
            "src.geneweb_converter.event_crud"
        ) as mock_event_crud, patch(
            "src.geneweb_converter.child_crud"
        ) as mock_child_crud:

            data = {
                "persons": [],
                "families": [],
                "events": [
                    {"type": "marriage", "date": "2020-01-01", "place": "Paris"}
                ],
                "children": [],
            }

            result = json_to_db(data, mock_session)

            expected = {
                "persons_created": 0,
                "families_created": 0,
                "events_created": 1,
                "children_created": 0,
            }
            assert result == expected

            mock_event_crud.create.assert_called_once_with(
                mock_session, data["events"][0]
            )

    def test_json_to_db_with_children(self):
        """Test inserting data with children."""
        mock_session = Mock()

        with patch("src.geneweb_converter.person_crud") as mock_person_crud, patch(
            "src.geneweb_converter.family_crud"
        ) as mock_family_crud, patch(
            "src.geneweb_converter.event_crud"
        ) as mock_event_crud, patch(
            "src.geneweb_converter.child_crud"
        ) as mock_child_crud:

            mock_person = Mock()
            mock_person.id = "person1"
            mock_person_crud.create.return_value = mock_person

            mock_family = Mock()
            mock_family.id = "family1"
            mock_family_crud.create.return_value = mock_family

            data = {
                "persons": [
                    {
                        "id": "person1",
                        "first_name": "John",
                        "last_name": "Doe",
                        "sex": "M",
                    }
                ],
                "families": [
                    {"id": "family1", "husband_id": "person1", "wife_id": None}
                ],
                "events": [],
                "children": [{"family_id": "family1", "child_id": "person1"}],
            }

            result = json_to_db(data, mock_session)

            expected = {
                "persons_created": 1,
                "families_created": 1,
                "events_created": 0,
                "children_created": 1,
            }
            assert result == expected

            child_call = mock_child_crud.create.call_args[0][1]
            assert child_call["family_id"] == "family1"
            assert child_call["child_id"] == "person1"

    def test_json_to_db_missing_family_for_child(self):
        """Test inserting child with missing family."""
        mock_session = Mock()

        with patch("src.geneweb_converter.person_crud") as mock_person_crud, patch(
            "src.geneweb_converter.family_crud"
        ) as mock_family_crud, patch(
            "src.geneweb_converter.event_crud"
        ) as mock_event_crud, patch(
            "src.geneweb_converter.child_crud"
        ) as mock_child_crud:

            data = {
                "persons": [],
                "families": [],
                "events": [],
                "children": [
                    {"family_id": "missing_family", "child_id": "missing_child"}
                ],
            }

            result = json_to_db(data, mock_session)

            expected = {
                "persons_created": 0,
                "families_created": 0,
                "events_created": 0,
                "children_created": 0,
            }
            assert result == expected

            mock_child_crud.create.assert_not_called()

    def test_json_to_db_complete_data(self):
        """Test inserting complete data with all entity types."""
        mock_session = Mock()

        with patch("src.geneweb_converter.person_crud") as mock_person_crud, patch(
            "src.geneweb_converter.family_crud"
        ) as mock_family_crud, patch(
            "src.geneweb_converter.event_crud"
        ) as mock_event_crud, patch(
            "src.geneweb_converter.child_crud"
        ) as mock_child_crud:

            mock_person1 = Mock()
            mock_person1.id = "person1"
            mock_person2 = Mock()
            mock_person2.id = "person2"
            mock_person_crud.create.side_effect = [mock_person1, mock_person2]

            mock_family = Mock()
            mock_family.id = "family1"
            mock_family_crud.create.return_value = mock_family

            data = {
                "persons": [
                    {
                        "id": "person1",
                        "first_name": "John",
                        "last_name": "Doe",
                        "sex": "M",
                    },
                    {
                        "id": "person2",
                        "first_name": "Jane",
                        "last_name": "Smith",
                        "sex": "F",
                    },
                ],
                "families": [
                    {"id": "family1", "husband_id": "person1", "wife_id": "person2"}
                ],
                "events": [
                    {"type": "marriage", "date": "2020-01-01", "place": "Paris"}
                ],
                "children": [{"family_id": "family1", "child_id": "person1"}],
            }

            result = json_to_db(data, mock_session)

            expected = {
                "persons_created": 2,
                "families_created": 1,
                "events_created": 1,
                "children_created": 1,
            }
            assert result == expected

            assert mock_person_crud.create.call_count == 2
            assert mock_family_crud.create.call_count == 1
            assert mock_event_crud.create.call_count == 1
            assert mock_child_crud.create.call_count == 1


class TestDbToJson:
    """Test the db_to_json function."""

    def test_db_to_json_empty_database(self):
        """Test converting empty database to JSON."""
        mock_session = Mock()

        # Mock the session.exec() method to return empty results
        mock_result = Mock()
        mock_result.unique.return_value = []
        mock_result.__iter__ = lambda self: iter([])
        mock_session.exec.return_value = mock_result

        with patch("src.geneweb_converter.event_crud") as mock_event_crud, patch(
            "src.geneweb_converter.child_crud"
        ) as mock_child_crud:

            mock_event_crud.get_all.return_value = []
            mock_child_crud.get_all.return_value = []

            result = db_to_json(mock_session)

            expected = {"persons": [], "families": [], "events": [], "children": []}
            assert result == expected

            mock_event_crud.get_all.assert_called_once_with(mock_session)
            mock_child_crud.get_all.assert_called_once_with(mock_session)

    def test_db_to_json_with_data(self):
        """Test converting database with data to JSON."""
        mock_session = Mock()

        # Mock the session.exec() method to return empty results for SQL queries
        mock_result = Mock()
        mock_result.unique.return_value = []
        mock_result.__iter__ = lambda self: iter([])
        mock_session.exec.return_value = mock_result

        with patch("src.geneweb_converter.event_crud") as mock_event_crud, patch(
            "src.geneweb_converter.child_crud"
        ) as mock_child_crud:

            mock_event = Mock()
            mock_event.model_dump.return_value = {"id": "event1", "type": "marriage"}

            mock_child = Mock()
            mock_child.model_dump.return_value = {
                "family_id": "family1",
                "child_id": "person1",
            }

            mock_event_crud.get_all.return_value = [mock_event]
            mock_child_crud.get_all.return_value = [mock_child]

            result = db_to_json(mock_session)

            expected = {
                "persons": [],
                "families": [],
                "events": [{"id": "event1", "type": "marriage"}],
                "children": [{"family_id": "family1", "child_id": "person1"}],
            }
            assert result == expected

            mock_event.model_dump.assert_called_once()
            mock_child.model_dump.assert_called_once()

    def test_db_to_json_multiple_entities(self):
        """Test converting database with multiple entities to JSON."""
        mock_session = Mock()

        # Mock the session.exec() method to return empty results for SQL queries
        mock_result = Mock()
        mock_result.unique.return_value = []
        mock_result.__iter__ = lambda self: iter([])
        mock_session.exec.return_value = mock_result

        with patch("src.geneweb_converter.event_crud") as mock_event_crud, patch(
            "src.geneweb_converter.child_crud"
        ) as mock_child_crud:

            mock_event1 = Mock()
            mock_event1.model_dump.return_value = {"id": "event1", "type": "marriage"}
            mock_event2 = Mock()
            mock_event2.model_dump.return_value = {"id": "event2", "type": "divorce"}

            mock_child = Mock()
            mock_child.model_dump.return_value = {
                "family_id": "family1",
                "child_id": "person1",
            }

            mock_event_crud.get_all.return_value = [mock_event1, mock_event2]
            mock_child_crud.get_all.return_value = [mock_child]

            result = db_to_json(mock_session)

            assert len(result["persons"]) == 0
            assert len(result["families"]) == 0
            assert len(result["events"]) == 2
            assert len(result["children"]) == 1

            mock_event1.model_dump.assert_called_once()
            mock_event2.model_dump.assert_called_once()
            mock_child.model_dump.assert_called_once()
