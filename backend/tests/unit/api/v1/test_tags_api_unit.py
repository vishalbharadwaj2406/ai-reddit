"""
Unit Tests for Tags API Endpoints

Tests the GET /tags endpoint for retrieving all available tags with post counts.
Follows TDD methodology with comprehensive coverage of success scenarios,
validation, and error handling.

Based on API specification:
- GET /tags: Get all tags with post counts (no auth required)
- POST /tags: Create new tags (auth required, admin-only or auto-created)
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.tag import Tag


@pytest.fixture
def client():
    """Test client for making API requests"""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Mock user object with proper UUID"""
    user = Mock(spec=User)
    user.user_id = uuid4()
    user.email = "test@example.com"
    user.username = "testuser"
    return user


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()


@pytest.fixture
def sample_tags():
    """Sample tags with post counts for testing"""
    tag1 = Mock(spec=Tag)
    tag1.tag_id = uuid4()
    tag1.name = "python"
    
    tag2 = Mock(spec=Tag)
    tag2.tag_id = uuid4()
    tag2.name = "ai"
    
    tag3 = Mock(spec=Tag)
    tag3.tag_id = uuid4()
    tag3.name = "web-development"
    
    return [tag1, tag2, tag3]


class TestTagsEndpoints:
    """Test class for Tags API endpoints"""

    def test_get_all_tags_success(self, client, mock_db, sample_tags):
        """Test successfully retrieving all tags with post counts"""
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service response with tags and post counts
        mock_tags_data = [
            {"tagId": str(sample_tags[0].tag_id), "name": "python", "postCount": 15},
            {"tagId": str(sample_tags[1].tag_id), "name": "ai", "postCount": 8},
            {"tagId": str(sample_tags[2].tag_id), "name": "web-development", "postCount": 3}
        ]
        
        with patch('app.services.tag_service.TagService.get_all_tags_with_counts') as mock_get_tags:
            mock_get_tags.return_value = mock_tags_data
            
            response = client.get("/api/v1/tags")
            
        print(f"Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response body: {response.json()}")
            
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["success"] is True
        assert "tags" in response_data["data"]
        assert len(response_data["data"]["tags"]) == 3
        
        # Verify tag structure
        first_tag = response_data["data"]["tags"][0]
        assert "tagId" in first_tag
        assert "name" in first_tag
        assert "postCount" in first_tag
        assert first_tag["name"] == "python"
        assert first_tag["postCount"] == 15
        
        # Clean up
        app.dependency_overrides.clear()

    def test_get_all_tags_empty_response(self, client, mock_db):
        """Test retrieving tags when no tags exist"""
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        with patch('app.services.tag_service.TagService.get_all_tags_with_counts') as mock_get_tags:
            mock_get_tags.return_value = []
            
            response = client.get("/api/v1/tags")
            
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["data"]["tags"] == []
        assert response_data["message"] == "Tags retrieved successfully"
        
        # Clean up
        app.dependency_overrides.clear()

    def test_get_all_tags_service_error(self, client, mock_db):
        """Test handling service errors during tag retrieval"""
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        with patch('app.services.tag_service.TagService.get_all_tags_with_counts') as mock_get_tags:
            mock_get_tags.side_effect = Exception("Database connection error")
            
            response = client.get("/api/v1/tags")
            
        print(f"Response status: {response.status_code}")
        if response.status_code != 500:
            print(f"Response body: {response.json()}")
            
        assert response.status_code == 500
        
        # Clean up
        app.dependency_overrides.clear()

    def test_create_tag_success(self, client, mock_user, mock_db):
        """Test successfully creating a new tag"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        new_tag_id = uuid4()
        mock_tag_data = {
            "tagId": str(new_tag_id),
            "name": "machine-learning",
            "postCount": 0
        }
        
        with patch('app.services.tag_service.TagService.create_tag') as mock_create_tag:
            mock_create_tag.return_value = mock_tag_data
            
            response = client.post(
                "/api/v1/tags",
                json={"name": "Machine Learning"}
            )
            
        print(f"Response status: {response.status_code}")
        if response.status_code != 201:
            print(f"Response body: {response.json()}")
            
        assert response.status_code == 201
        
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["data"]["tag"]["name"] == "machine-learning"
        assert response_data["data"]["tag"]["postCount"] == 0
        assert response_data["message"] == "Tag created successfully"
        
        # Clean up
        app.dependency_overrides.clear()

    def test_create_tag_duplicate_name(self, client, mock_user, mock_db):
        """Test creating a tag with a name that already exists"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        with patch('app.services.tag_service.TagService.create_tag') as mock_create_tag:
            from app.core.exceptions import TagAlreadyExistsError
            mock_create_tag.side_effect = TagAlreadyExistsError("Tag 'python' already exists")
            
            response = client.post(
                "/api/v1/tags",
                json={"name": "Python"}
            )
            
        print(f"Response status: {response.status_code}")
        if response.status_code != 409:
            print(f"Response body: {response.json()}")
            
        assert response.status_code == 409
        
        response_data = response.json()
        # FastAPI puts custom detail in 'detail' field when raising HTTPException
        assert response_data["detail"]["success"] is False
        assert "already exists" in response_data["detail"]["message"]
        
        # Clean up
        app.dependency_overrides.clear()

    def test_create_tag_invalid_name(self, client, mock_user, mock_db):
        """Test creating a tag with invalid name (empty or None)"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Test empty name
        response = client.post(
            "/api/v1/tags",
            json={"name": ""}
        )
        
        assert response.status_code == 422
        
        # Test missing name
        response = client.post(
            "/api/v1/tags",
            json={}
        )
        
        assert response.status_code == 422
        
        # Clean up
        app.dependency_overrides.clear()

    def test_create_tag_unauthenticated(self, client, mock_db):
        """Test that unauthenticated requests to create tags are rejected"""
        
        app.dependency_overrides[get_db] = lambda: mock_db
        # No auth override - should get 401
        
        response = client.post(
            "/api/v1/tags",
            json={"name": "test-tag"}
        )
        
        assert response.status_code == 401
        
        # Clean up
        app.dependency_overrides.clear()
