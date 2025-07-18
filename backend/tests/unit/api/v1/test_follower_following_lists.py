"""
Test Follower/Following List Endpoints

Comprehensive tests for follower and following list endpoints with privacy controls.
Tests cover pagination, privacy restrictions, and authentication scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import Mock, patch
from uuid import uuid4

from app.main import app
from app.models.user import User
from app.dependencies.auth import get_current_user_optional

# Import from our test infrastructure
from tests.fixtures.auth_fixtures import sample_user, valid_token, mock_db_session
from tests.fixtures.follow_fixtures import (
    sample_private_user, sample_public_user,
    mock_follow_service
)
from tests.utils.test_helpers import (
    APITestClient, assert_api_response_format,
    create_mock_db_session, mock_dependency_override
)


class TestFollowerFollowingListEndpoints:
    """Test suite for follower/following list endpoints"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    def api_client(self, client):
        """Enhanced API test client"""
        return APITestClient(client)
    
    # ========== FOLLOWERS LIST TESTS ==========
    
    def test_get_public_user_followers_success(self, client, sample_public_user):
        """Test getting followers of a public user (no auth required)"""
        mock_db = create_mock_db_session(user_return=sample_public_user, count_return=0)
        
        with patch("app.core.database.get_db", return_value=mock_db):
            with patch("app.services.follow_service.FollowService") as mock_service:
                mock_service_instance = Mock()
                mock_service_instance.get_followers_list.return_value = {
                    "success": True,
                    "message": "Followers retrieved successfully",
                    "data": {
                        "followers": [
                            {
                                "user_id": str(uuid4()),
                                "user_name": "follower1",
                                "profile_picture": "https://example.com/pic1.jpg",
                                "is_private": False,
                                "followed_at": "2024-01-01T00:00:00Z"
                            },
                            {
                                "user_id": str(uuid4()),
                                "user_name": "follower2",
                                "profile_picture": "https://example.com/pic2.jpg",
                                "is_private": True,
                                "followed_at": "2024-01-02T00:00:00Z"
                            }
                        ],
                        "pagination": {
                            "total_count": 2,
                            "limit": 20,
                            "offset": 0,
                            "has_next": False,
                            "has_previous": False
                        }
                    }
                }
                mock_service.return_value = mock_service_instance
                
                response = client.get(f"/api/v1/users/{sample_public_user.user_id}/followers")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_api_response_format(data, success=True)
        assert data["message"] == "Followers retrieved successfully"
        assert data["errorCode"] is None
        
        followers = data["data"]["followers"]
        assert len(followers) == 2
        assert followers[0]["user_name"] == "follower1"
        assert followers[1]["user_name"] == "follower2"
        
        pagination = data["data"]["pagination"]
        assert pagination["total_count"] == 2
        assert pagination["limit"] == 20
        assert pagination["offset"] == 0
        assert pagination["has_next"] is False
        assert pagination["has_previous"] is False
    
    def test_get_private_user_followers_authenticated_following(self, api_client, sample_user, sample_private_user, valid_token):
        """Test getting followers of private user when authenticated and following them"""
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user_optional, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.get_followers_list.return_value = {
                        "success": True,
                        "message": "Followers retrieved successfully",
                        "data": {
                            "followers": [
                                {
                                    "user_id": str(uuid4()),
                                    "user_name": "follower1",
                                    "profile_picture": "https://example.com/pic1.jpg",
                                    "is_private": False,
                                    "followed_at": "2024-01-01T00:00:00Z",
                                    "follow_status": {
                                        "follow_status": "none",
                                        "is_following": False,
                                        "request_pending": False,
                                        "follows_you": False
                                    }
                                }
                            ],
                            "pagination": {
                                "total_count": 1,
                                "limit": 20,
                                "offset": 0,
                                "has_next": False,
                                "has_previous": False
                            }
                        }
                    }
                    mock_service.return_value = mock_service_instance
                    
                    response = api_client.get_with_auth(
                        f"/api/v1/users/{sample_private_user.user_id}/followers",
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_api_response_format(data, success=True)
        assert data["message"] == "Followers retrieved successfully"
        assert "follow_status" in data["data"]["followers"][0]
    
    def test_get_private_user_followers_unauthenticated(self, client, sample_private_user):
        """Test getting followers of private user without authentication"""
        mock_db = create_mock_db_session(user_return=sample_private_user, count_return=0)
        
        with patch("app.core.database.get_db", return_value=mock_db):
            with patch("app.services.follow_service.FollowService") as mock_service:
                mock_service_instance = Mock()
                mock_service_instance.get_followers_list.return_value = {
                    "success": False,
                    "message": "Private account - authentication required",
                    "error_code": "PRIVATE_ACCOUNT_AUTH_REQUIRED"
                }
                mock_service.return_value = mock_service_instance
                
                response = client.get(f"/api/v1/users/{sample_private_user.user_id}/followers")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert "detail" in data
        assert_api_response_format(data["detail"], success=False)
        assert data["detail"]["message"] == "Private account - authentication required"
        assert data["detail"]["errorCode"] == "PRIVATE_ACCOUNT_AUTH_REQUIRED"
    
    def test_get_private_user_followers_not_following(self, api_client, sample_user, sample_private_user, valid_token):
        """Test getting followers of private user when not following them"""
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user_optional, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.get_followers_list.return_value = {
                        "success": False,
                        "message": "Private account - must be following to see followers",
                        "error_code": "PRIVATE_ACCOUNT_FOLLOW_REQUIRED"
                    }
                    mock_service.return_value = mock_service_instance
                    
                    response = api_client.get_with_auth(
                        f"/api/v1/users/{sample_private_user.user_id}/followers",
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert "detail" in data
        assert_api_response_format(data["detail"], success=False)
        assert data["detail"]["message"] == "Private account - must be following to see followers"
        assert data["detail"]["errorCode"] == "PRIVATE_ACCOUNT_FOLLOW_REQUIRED"
    
    def test_get_followers_with_pagination(self, client, sample_public_user):
        """Test getting followers with pagination parameters"""
        mock_db = create_mock_db_session(user_return=sample_public_user, count_return=0)
        
        with patch("app.core.database.get_db", return_value=mock_db):
            with patch("app.services.follow_service.FollowService") as mock_service:
                mock_service_instance = Mock()
                mock_service_instance.get_followers_list.return_value = {
                    "success": True,
                    "message": "Followers retrieved successfully",
                    "data": {
                        "followers": [
                            {
                                "user_id": str(uuid4()),
                                "user_name": "follower1",
                                "profile_picture": "https://example.com/pic1.jpg",
                                "is_private": False,
                                "followed_at": "2024-01-01T00:00:00Z"
                            }
                        ],
                        "pagination": {
                            "total_count": 25,
                            "limit": 10,
                            "offset": 10,
                            "has_next": True,
                            "has_previous": True
                        }
                    }
                }
                mock_service.return_value = mock_service_instance
                
                response = client.get(
                    f"/api/v1/users/{sample_public_user.user_id}/followers?limit=10&offset=10"
                )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        pagination = data["data"]["pagination"]
        assert pagination["limit"] == 10
        assert pagination["offset"] == 10
        assert pagination["has_next"] is True
        assert pagination["has_previous"] is True
    
    def test_get_followers_user_not_found(self, client):
        """Test getting followers for non-existent user"""
        non_existent_user_id = str(uuid4())
        mock_db = create_mock_db_session(user_return=None, count_return=0)
        
        with patch("app.core.database.get_db", return_value=mock_db):
            with patch("app.services.follow_service.FollowService") as mock_service:
                mock_service_instance = Mock()
                mock_service_instance.get_followers_list.return_value = {
                    "success": False,
                    "message": "User not found",
                    "error_code": "USER_NOT_FOUND"
                }
                mock_service.return_value = mock_service_instance
                
                response = client.get(f"/api/v1/users/{non_existent_user_id}/followers")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "detail" in data
        assert_api_response_format(data["detail"], success=False)
        assert data["detail"]["message"] == "User not found"
        assert data["detail"]["errorCode"] == "USER_NOT_FOUND"
    
    # ========== FOLLOWING LIST TESTS ==========
    
    def test_get_public_user_following_success(self, client, sample_public_user):
        """Test getting following of a public user (no auth required)"""
        mock_db = create_mock_db_session(user_return=sample_public_user, count_return=0)
        
        with patch("app.core.database.get_db", return_value=mock_db):
            with patch("app.services.follow_service.FollowService") as mock_service:
                mock_service_instance = Mock()
                mock_service_instance.get_following_list.return_value = {
                    "success": True,
                    "message": "Following retrieved successfully",
                    "data": {
                        "following": [
                            {
                                "user_id": str(uuid4()),
                                "user_name": "following1",
                                "profile_picture": "https://example.com/pic1.jpg",
                                "is_private": False,
                                "followed_at": "2024-01-01T00:00:00Z"
                            }
                        ],
                        "pagination": {
                            "total_count": 1,
                            "limit": 20,
                            "offset": 0,
                            "has_next": False,
                            "has_previous": False
                        }
                    }
                }
                mock_service.return_value = mock_service_instance
                
                response = client.get(f"/api/v1/users/{sample_public_user.user_id}/following")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_api_response_format(data, success=True)
        assert data["message"] == "Following retrieved successfully"
        assert data["errorCode"] is None
        
        following = data["data"]["following"]
        assert len(following) == 1
        assert following[0]["user_name"] == "following1"
    
    def test_get_private_user_following_unauthenticated(self, client, sample_private_user):
        """Test getting following of private user without authentication"""
        mock_db = create_mock_db_session(user_return=sample_private_user, count_return=0)
        
        with patch("app.core.database.get_db", return_value=mock_db):
            with patch("app.services.follow_service.FollowService") as mock_service:
                mock_service_instance = Mock()
                mock_service_instance.get_following_list.return_value = {
                    "success": False,
                    "message": "Private account - authentication required",
                    "error_code": "PRIVATE_ACCOUNT_AUTH_REQUIRED"
                }
                mock_service.return_value = mock_service_instance
                
                response = client.get(f"/api/v1/users/{sample_private_user.user_id}/following")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert "detail" in data
        assert_api_response_format(data["detail"], success=False)
        assert data["detail"]["message"] == "Private account - authentication required"
        assert data["detail"]["errorCode"] == "PRIVATE_ACCOUNT_AUTH_REQUIRED"
    
    def test_get_following_user_not_found(self, client):
        """Test getting following for non-existent user"""
        non_existent_user_id = str(uuid4())
        mock_db = create_mock_db_session(user_return=None, count_return=0)
        
        with patch("app.core.database.get_db", return_value=mock_db):
            with patch("app.services.follow_service.FollowService") as mock_service:
                mock_service_instance = Mock()
                mock_service_instance.get_following_list.return_value = {
                    "success": False,
                    "message": "User not found",
                    "error_code": "USER_NOT_FOUND"
                }
                mock_service.return_value = mock_service_instance
                
                response = client.get(f"/api/v1/users/{non_existent_user_id}/following")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "detail" in data
        assert_api_response_format(data["detail"], success=False)
        assert data["detail"]["message"] == "User not found"
        assert data["detail"]["errorCode"] == "USER_NOT_FOUND"
    
    def test_get_following_with_pagination(self, client, sample_public_user):
        """Test getting following with pagination parameters"""
        mock_db = create_mock_db_session(user_return=sample_public_user, count_return=0)
        
        with patch("app.core.database.get_db", return_value=mock_db):
            with patch("app.services.follow_service.FollowService") as mock_service:
                mock_service_instance = Mock()
                mock_service_instance.get_following_list.return_value = {
                    "success": True,
                    "message": "Following retrieved successfully",
                    "data": {
                        "following": [],
                        "pagination": {
                            "total_count": 0,
                            "limit": 5,
                            "offset": 0,
                            "has_next": False,
                            "has_previous": False
                        }
                    }
                }
                mock_service.return_value = mock_service_instance
                
                response = client.get(
                    f"/api/v1/users/{sample_public_user.user_id}/following?limit=5&offset=0"
                )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        pagination = data["data"]["pagination"]
        assert pagination["limit"] == 5
        assert pagination["offset"] == 0
    
    def test_get_followers_invalid_user_id(self, client):
        """Test getting followers with invalid user ID format"""
        invalid_user_id = "invalid-uuid"
        
        response = client.get(f"/api/v1/users/{invalid_user_id}/followers")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "detail" in data
        assert_api_response_format(data["detail"], success=False)
        assert data["detail"]["message"] == "Invalid user ID format"
        assert data["detail"]["errorCode"] == "INVALID_USER_ID"
    
    def test_get_following_invalid_user_id(self, client):
        """Test getting following with invalid user ID format"""
        invalid_user_id = "invalid-uuid"
        
        response = client.get(f"/api/v1/users/{invalid_user_id}/following")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "detail" in data
        assert_api_response_format(data["detail"], success=False)
        assert data["detail"]["message"] == "Invalid user ID format"
        assert data["detail"]["errorCode"] == "INVALID_USER_ID"
