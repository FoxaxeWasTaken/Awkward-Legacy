"""
Tests for files endpoints.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from fastapi.testclient import TestClient
from fastapi import UploadFile
import tempfile
import os
from io import BytesIO

from src.main import app
from src.endpoints.files import router


class TestImportGenewebFile:
    """Test the import_geneweb_file endpoint."""

    def test_import_geneweb_file_success(self):
        """Test successful import of GeneWeb file."""
        client = TestClient(app)
        
        # Create a mock GeneWeb file content
        gw_content = """encoding: utf-8
gwplus

fam 0
husb 0 John Doe
wife 0 Jane Smith
"""
        
        with patch('src.endpoints.files.GWParser') as mock_parser_class, \
             patch('src.endpoints.files.json_to_db') as mock_json_to_db, \
             patch('src.endpoints.files.extract_entities') as mock_extract_entities:
            
            # Mock parser
            mock_parser = Mock()
            mock_parser.parse.return_value = {
                "families": [
                    {
                        "id": "fam1",
                        "husband": {"first_name": "John", "last_name": "Doe"},
                        "wife": {"first_name": "Jane", "last_name": "Smith"}
                    }
                ]
            }
            mock_parser_class.return_value = mock_parser
            
            # Mock entity extraction
            mock_extract_entities.return_value = {
                "persons": [{"id": "person1", "first_name": "John", "last_name": "Doe"}],
                "families": [{"id": "family1", "husband_id": "person1"}],
                "events": [],
                "children": []
            }
            
            # Mock database insertion
            mock_json_to_db.return_value = {
                "persons": 1,
                "families": 1,
                "events": 0,
                "children": 0
            }
            
            # Create file-like object
            file_content = BytesIO(gw_content.encode('utf-8'))
            
            response = client.post(
                "/api/v1/files/import",
                files={"file": ("test.gw", file_content, "text/plain")}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["message"] == "File imported successfully"
            assert data["persons"] == 1
            assert data["families"] == 1
            assert data["events"] == 0
            assert data["children"] == 0

    def test_import_geneweb_file_parsing_error(self):
        """Test import with parsing error."""
        client = TestClient(app)
        
        with patch('src.endpoints.files.GWParser') as mock_parser_class:
            # Mock parser to raise exception
            mock_parser = Mock()
            mock_parser.parse.side_effect = Exception("Parsing error")
            mock_parser_class.return_value = mock_parser
            
            file_content = BytesIO(b"invalid content")
            
            response = client.post(
                "/api/v1/files/import",
                files={"file": ("test.gw", file_content, "text/plain")}
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert "Parsing error" in data["error"]

    def test_import_geneweb_file_database_error(self):
        """Test import with database error."""
        client = TestClient(app)
        
        gw_content = """encoding: utf-8
fam 0
husb 0 John Doe
"""
        
        with patch('src.endpoints.files.GWParser') as mock_parser_class, \
             patch('src.endpoints.files.extract_entities') as mock_extract_entities, \
             patch('src.endpoints.files.json_to_db') as mock_json_to_db:
            
            # Mock parser
            mock_parser = Mock()
            mock_parser.parse.return_value = {"families": []}
            mock_parser_class.return_value = mock_parser
            
            # Mock entity extraction
            mock_extract_entities.return_value = {
                "persons": [],
                "families": [],
                "events": [],
                "children": []
            }
            
            # Mock database error
            mock_json_to_db.side_effect = Exception("Database error")
            
            file_content = BytesIO(gw_content.encode('utf-8'))
            
            response = client.post(
                "/api/v1/files/import",
                files={"file": ("test.gw", file_content, "text/plain")}
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
            assert "Database error" in data["error"]

    def test_import_geneweb_file_no_file(self):
        """Test import without file."""
        client = TestClient(app)
        
        response = client.post("/api/v1/files/import")
        
        assert response.status_code == 422  # Validation error

    def test_import_geneweb_file_empty_file(self):
        """Test import with empty file."""
        client = TestClient(app)
        
        with patch('src.endpoints.files.GWParser') as mock_parser_class, \
             patch('src.endpoints.files.extract_entities') as mock_extract_entities, \
             patch('src.endpoints.files.json_to_db') as mock_json_to_db:
            
            # Mock parser
            mock_parser = Mock()
            mock_parser.parse.return_value = {}
            mock_parser_class.return_value = mock_parser
            
            # Mock entity extraction
            mock_extract_entities.return_value = {
                "persons": [],
                "families": [],
                "events": [],
                "children": []
            }
            
            # Mock database insertion
            mock_json_to_db.return_value = {
                "persons": 0,
                "families": 0,
                "events": 0,
                "children": 0
            }
            
            file_content = BytesIO(b"")
            
            response = client.post(
                "/api/v1/files/import",
                files={"file": ("empty.gw", file_content, "text/plain")}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["persons"] == 0
            assert data["families"] == 0


class TestExportGenewebFile:
    """Test the export_geneweb_file endpoint."""

    def test_export_geneweb_file_success(self):
        """Test successful export of GeneWeb file."""
        client = TestClient(app)
        
        with patch('src.endpoints.files.db_to_json') as mock_db_to_json, \
             patch('src.endpoints.files.normalize_db_json') as mock_normalize, \
             patch('src.endpoints.files.serialize_family') as mock_serialize_family, \
             patch('src.endpoints.files.serialize_person') as mock_serialize_person, \
             patch('src.endpoints.files.serialize_event') as mock_serialize_event, \
             patch('src.endpoints.files.serialize_sources') as mock_serialize_sources, \
             patch('tempfile.NamedTemporaryFile') as mock_temp_file:
            
            # Mock database data
            mock_db_to_json.return_value = {
                "persons": [{"id": "person1", "first_name": "John", "last_name": "Doe"}],
                "families": [{"id": "family1", "husband_id": "person1"}],
                "events": [{"id": "event1", "type": "marriage"}],
                "children": []
            }
            
            # Mock normalization
            mock_normalize.return_value = {
                "persons": [{"id": "person1", "first_name": "John", "last_name": "Doe"}],
                "families": [{"id": "family1", "husband_id": "person1"}],
                "events": [{"id": "event1", "type": "marriage"}]
            }
            
            # Mock serializers
            mock_serialize_family.return_value = "fam 0\nhusb 0 John Doe\n"
            mock_serialize_person.return_value = "pevt 0 John Doe\n"
            mock_serialize_event.return_value = "event 0 marriage\n"
            mock_serialize_sources.return_value = "sources\n"
            
            # Mock temporary file
            mock_file = Mock()
            mock_file.name = "/tmp/test.gw"
            mock_temp_file.return_value.__enter__.return_value = mock_file
            
            response = client.get("/api/v1/files/export")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/plain; charset=utf-8"
            assert response.headers["content-disposition"] == "attachment; filename=genealogy.gw"

    def test_export_geneweb_file_database_error(self):
        """Test export with database error."""
        client = TestClient(app)
        
        with patch('src.endpoints.files.db_to_json') as mock_db_to_json:
            # Mock database error
            mock_db_to_json.side_effect = Exception("Database error")
            
            response = client.get("/api/v1/files/export")
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
            assert "Database error" in data["error"]

    def test_export_geneweb_file_serialization_error(self):
        """Test export with serialization error."""
        client = TestClient(app)
        
        with patch('src.endpoints.files.db_to_json') as mock_db_to_json, \
             patch('src.endpoints.files.normalize_db_json') as mock_normalize, \
             patch('src.endpoints.files.serialize_family') as mock_serialize_family:
            
            # Mock database data
            mock_db_to_json.return_value = {
                "persons": [],
                "families": [],
                "events": [],
                "children": []
            }
            
            # Mock normalization
            mock_normalize.return_value = {
                "persons": [],
                "families": [],
                "events": []
            }
            
            # Mock serialization error
            mock_serialize_family.side_effect = Exception("Serialization error")
            
            response = client.get("/api/v1/files/export")
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
            assert "Serialization error" in data["error"]


class TestGetGenewebData:
    """Test the get_geneweb_data endpoint."""

    def test_get_geneweb_data_success(self):
        """Test successful retrieval of GeneWeb data."""
        client = TestClient(app)
        
        with patch('src.endpoints.files.db_to_json') as mock_db_to_json, \
             patch('src.endpoints.files.normalize_db_json') as mock_normalize:
            
            # Mock database data
            mock_db_to_json.return_value = {
                "persons": [{"id": "person1", "first_name": "John", "last_name": "Doe"}],
                "families": [{"id": "family1", "husband_id": "person1"}],
                "events": [{"id": "event1", "type": "marriage"}],
                "children": []
            }
            
            # Mock normalization
            mock_normalize.return_value = {
                "persons": [{"id": "person1", "first_name": "John", "last_name": "Doe"}],
                "families": [{"id": "family1", "husband_id": "person1"}],
                "events": [{"id": "event1", "type": "marriage"}]
            }
            
            response = client.get("/api/v1/files/data")
            
            assert response.status_code == 200
            data = response.json()
            assert "persons" in data
            assert "families" in data
            assert "events" in data
            assert len(data["persons"]) == 1
            assert len(data["families"]) == 1
            assert len(data["events"]) == 1

    def test_get_geneweb_data_database_error(self):
        """Test retrieval with database error."""
        client = TestClient(app)
        
        with patch('src.endpoints.files.db_to_json') as mock_db_to_json:
            # Mock database error
            mock_db_to_json.side_effect = Exception("Database error")
            
            response = client.get("/api/v1/files/data")
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
            assert "Database error" in data["error"]

    def test_get_geneweb_data_empty_database(self):
        """Test retrieval from empty database."""
        client = TestClient(app)
        
        with patch('src.endpoints.files.db_to_json') as mock_db_to_json, \
             patch('src.endpoints.files.normalize_db_json') as mock_normalize:
            
            # Mock empty database
            mock_db_to_json.return_value = {
                "persons": [],
                "families": [],
                "events": [],
                "children": []
            }
            
            # Mock normalization
            mock_normalize.return_value = {
                "persons": [],
                "families": [],
                "events": []
            }
            
            response = client.get("/api/v1/files/data")
            
            assert response.status_code == 200
            data = response.json()
            assert data["persons"] == []
            assert data["families"] == []
            assert data["events"] == []
