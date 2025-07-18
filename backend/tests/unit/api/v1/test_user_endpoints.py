"""
Test User API Endpoints

Tests for user management endpoints including profile retrieval,
updates, and social features like following.

This file tests the API layer specifically - ensuring endpoints
return correct responses and handle errors properly.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from app.main import app
from app.models.user import User
from app.dependencies.auth import get_current_user

# Import from our new test infrastructure
from tests.fixtures.auth_fixtures import sample_user, valid_token, mock_db_session
from tests.utils.test_helpers import APITestClient, assert_api_response_format, mock_dependency_override


def assert_user_data_format(user_data):
    """Assert user data has expected format"""
    required_fields = ["user_id", "user_name", "email", "profile_picture", "is_private", "created_at"]
    for field in required_fields:
        assert field in user_data, f"Missing field: {field}"


def create_mock_db_session(user_return=None, count_return=0):
    """Create mock database session using the imported helper"""
    from tests.utils.test_helpers import create_mock_db_session as helper_create_mock_db_session
    return helper_create_mock_db_session(user_return, count_return)

from app.main import app
from app.dependencies.auth import get_current_user
from tests.fixtures.auth_fixtures import (
    sample_user, sample_private_user, valid_token, mock_db_session
)
from tests.utils.test_helpers import (
    APITestClient, assert_api_response_format, assert_user_data_format,
    create_mock_db_session, mock_dependency_override
)


class TestUserEndpoints:
    """Test suite for user API endpoints"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    def api_client(self, client):
        """Enhanced API test client"""
        return APITestClient(client)
    
    def test_get_current_user_profile_success(self, api_client, sample_user, valid_token):
        """Test successful retrieval of current user profile"""
        # Mock database session
        mock_db = create_mock_db_session(user_return=sample_user, count_return=5)
        
        # Override dependencies
        with mock_dependency_override(app, get_current_user, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                response = api_client.get_with_auth("/api/v1/users/me", valid_token)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_api_response_format(data, success=True)
        assert data["message"] == "Profile retrieved successfully"
        
        user_data = data["data"]["user"]
        assert_user_data_format(user_data)
        assert user_data["user_id"] == str(sample_user.user_id)
        assert user_data["user_name"] == sample_user.user_name
        assert user_data["email"] == sample_user.email
        assert user_data["is_private"] is False
    
    def test_get_current_user_profile_unauthorized(self, client):
        """Test user profile retrieval without authentication"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "AUTH_REQUIRED"
        assert data["detail"]["message"] == "Authentication required"
    
    def test_get_current_user_profile_invalid_token(self, client):
        """Test user profile retrieval with invalid token"""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "INVALID_TOKEN"
        assert data["detail"]["message"] == "Invalid or expired token"
    
    def test_update_current_user_profile_success(self, api_client, sample_user, valid_token):
        """Test successful user profile update"""
        # Mock database session
        mock_db = create_mock_db_session(user_return=sample_user, count_return=5)
        
        # Update data
        update_data = {
            "user_name": "updated_user",
            "is_private": True
        }
        
        # Override dependencies and mock all database operations
        with mock_dependency_override(app, get_current_user, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                # Mock the database operations that would fail with Mock objects
                with patch.object(mock_db, 'commit', return_value=None):
                    with patch.object(mock_db, 'refresh', return_value=None):
                        response = api_client.patch_with_auth("/api/v1/users/me", update_data, valid_token)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_api_response_format(data, success=True)
        assert data["message"] == "Profile updated successfully"
        
        user_data = data["data"]["user"]
        assert_user_data_format(user_data)
        # Check that the user attributes were updated
        assert user_data["user_name"] == "updated_user"
        assert user_data["is_private"] is True

    def test_update_current_user_profile_unauthorized(self, client):
        """Test profile update without authentication"""
        update_data = {"user_name": "new_name"}
        
        response = client.patch("/api/v1/users/me", json=update_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "AUTH_REQUIRED"

    def test_update_current_user_profile_invalid_data(self, api_client, sample_user, valid_token):
        """Test profile update with invalid data"""
        # Mock database session
        mock_db = create_mock_db_session(user_return=sample_user, count_return=5)
        
        # Invalid update data (empty username)
        update_data = {"user_name": ""}
        
        # Override dependencies
        with mock_dependency_override(app, get_current_user, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                response = api_client.patch_with_auth("/api/v1/users/me", update_data, valid_token)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_current_user_profile_no_changes(self, api_client, sample_user, valid_token):
        """Test profile update with no changes"""
        # Mock database session
        mock_db = create_mock_db_session(user_return=sample_user, count_return=5)
        
        # Empty update data
        update_data = {}
        
        # Override dependencies
        with mock_dependency_override(app, get_current_user, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                response = api_client.patch_with_auth("/api/v1/users/me", update_data, valid_token)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_api_response_format(data, success=True)
        assert data["message"] == "Profile updated successfully"
