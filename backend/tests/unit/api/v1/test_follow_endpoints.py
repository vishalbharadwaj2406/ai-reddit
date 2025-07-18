"""
Test Follow API Endpoints

Comprehensive tests for Instagram-like follow system endpoints.
Tests cover follow/unfollow operations, request handling, and privacy controls.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import Mock, patch
from uuid import uuid4

from app.main import app
from app.models.user import User
from app.dependencies.auth import get_current_user, get_current_user_optional

# Import from our test infrastructure
from tests.fixtures.auth_fixtures import sample_user, valid_token, mock_db_session
from tests.fixtures.follow_fixtures import (
    sample_follow_pending, sample_follow_accepted,
    sample_private_user, sample_public_user,
    mock_follow_repository, mock_follow_service
)
from tests.utils.test_helpers import (
    APITestClient, assert_api_response_format,
    create_mock_db_session, mock_dependency_override
)


class TestFollowEndpoints:
    """Test suite for follow API endpoints"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    def api_client(self, client):
        """Enhanced API test client"""
        return APITestClient(client)
    
    # ========== FOLLOW USER TESTS ==========
    
    def test_follow_public_user_success(self, api_client, sample_user, sample_public_user, valid_token):
        """Test successfully following a public user (instant follow)"""
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.follow_user.return_value = {
                        "success": True,
                        "message": "Now following user",
                        "follow_status": "accepted",
                        "data": {
                            "follow_id": f"{sample_user.user_id}_{sample_public_user.user_id}",
                            "status": "accepted",
                            "created_at": "2024-01-01T00:00:00Z"
                        }
                    }
                    mock_service.return_value = mock_service_instance
                    
                    response = api_client.post_with_auth(
                        f"/api/v1/users/{sample_public_user.user_id}/follow",
                        {},
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_api_response_format(data, success=True)
        assert data["message"] == "Now following user"
        assert data["errorCode"] is None
        assert "follow_id" in data["data"]
    
    def test_follow_private_user_success(self, api_client, sample_user, sample_private_user, valid_token):
        """Test successfully sending follow request to private user"""
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.follow_user.return_value = {
                        "success": True,
                        "message": "Follow request sent",
                        "follow_status": "pending",
                        "data": {
                            "follow_id": f"{sample_user.user_id}_{sample_private_user.user_id}",
                            "status": "pending",
                            "created_at": "2024-01-01T00:00:00Z"
                        }
                    }
                    mock_service.return_value = mock_service_instance
                    
                    response = api_client.post_with_auth(
                        f"/api/v1/users/{sample_private_user.user_id}/follow",
                        {},
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_api_response_format(data, success=True)
        assert data["message"] == "Follow request sent"
        assert data["errorCode"] is None
        assert data["data"]["status"] == "pending"
    
    def test_follow_user_not_found(self, api_client, sample_user, valid_token):
        """Test following non-existent user"""
        non_existent_user_id = str(uuid4())
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.follow_user.return_value = {
                        "success": False,
                        "message": "User not found",
                        "error_code": "USER_NOT_FOUND"
                    }
                    mock_service.return_value = mock_service_instance
                    
                    response = api_client.post_with_auth(
                        f"/api/v1/users/{non_existent_user_id}/follow",
                        {},
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "detail" in data
        assert_api_response_format(data["detail"], success=False)
        assert data["detail"]["message"] == "User not found"
        assert data["detail"]["errorCode"] == "USER_NOT_FOUND"
    
    def test_follow_already_following(self, api_client, sample_user, sample_public_user, valid_token):
        """Test following user already being followed"""
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.follow_user.return_value = {
                        "success": False,
                        "message": "Already following this user",
                        "error_code": "ALREADY_FOLLOWING"
                    }
                    mock_service.return_value = mock_service_instance
                    
                    response = api_client.post_with_auth(
                        f"/api/v1/users/{sample_public_user.user_id}/follow",
                        {},
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "detail" in data
        assert_api_response_format(data["detail"], success=False)
        assert data["detail"]["message"] == "Already following this user"
        assert data["detail"]["errorCode"] == "ALREADY_FOLLOWING"
    
    def test_follow_self_forbidden(self, api_client, sample_user, valid_token):
        """Test following yourself (should be forbidden)"""
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.follow_user.return_value = {
                        "success": False,
                        "message": "Cannot follow yourself",
                        "error_code": "SELF_FOLLOW_FORBIDDEN"
                    }
                    mock_service.return_value = mock_service_instance
                    
                    response = api_client.post_with_auth(
                        f"/api/v1/users/{sample_user.user_id}/follow",
                        {},
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "detail" in data
        assert_api_response_format(data["detail"], success=False)
        assert data["detail"]["message"] == "Cannot follow yourself"
        assert data["detail"]["errorCode"] == "SELF_FOLLOW_FORBIDDEN"
    
    def test_follow_unauthorized(self, client):
        """Test following user without authentication"""
        user_id = str(uuid4())
        
        response = client.post(f"/api/v1/users/{user_id}/follow")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "AUTH_REQUIRED"
    
    # ========== UNFOLLOW USER TESTS ==========
    
    def test_unfollow_user_success(self, api_client, sample_user, sample_public_user, valid_token):
        """Test successfully unfollowing a user"""
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.unfollow_user.return_value = {
                        "success": True,
                        "message": "Unfollowed user successfully",
                        "follow_status": "none"
                    }
                    mock_service.return_value = mock_service_instance
                    
                    response = api_client.delete_with_auth(
                        f"/api/v1/users/{sample_public_user.user_id}/follow",
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_api_response_format(data, success=True)
        assert data["message"] == "Unfollowed user successfully"
        assert data["errorCode"] is None
    
    def test_unfollow_not_following(self, api_client, sample_user, sample_public_user, valid_token):
        """Test unfollowing user not being followed"""
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.unfollow_user.return_value = {
                        "success": False,
                        "message": "Not following this user",
                        "error_code": "NOT_FOLLOWING"
                    }
                    mock_service.return_value = mock_service_instance
                    
                    response = api_client.delete_with_auth(
                        f"/api/v1/users/{sample_public_user.user_id}/follow",
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "detail" in data
        assert_api_response_format(data["detail"], success=False)
        assert data["detail"]["message"] == "Not following this user"
        assert data["detail"]["errorCode"] == "NOT_FOLLOWING"
    
    # ========== FOLLOW REQUESTS TESTS ==========
    
    def test_get_follow_requests_success(self, api_client, sample_user, valid_token):
        """Test getting follow requests successfully"""
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.get_follow_requests.return_value = {
                        "success": True,
                        "message": "Follow requests retrieved successfully",
                        "data": {
                            "requests": [
                                {
                                    "follower_id": str(uuid4()),
                                    "follower_name": "test_user",
                                    "profile_picture": "https://example.com/pic.jpg",
                                    "requested_at": "2024-01-01T00:00:00Z"
                                }
                            ],
                            "count": 1
                        }
                    }
                    mock_service.return_value = mock_service_instance
                    
                    response = api_client.get_with_auth("/api/v1/users/me/follow-requests", valid_token)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_api_response_format(data, success=True)
        assert data["message"] == "Follow requests retrieved successfully"
        assert data["errorCode"] is None
        assert "requests" in data["data"]
        assert data["data"]["count"] == 1
    
    def test_get_follow_requests_empty(self, api_client, sample_user, valid_token):
        """Test getting follow requests when none exist"""
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.get_follow_requests.return_value = {
                        "success": True,
                        "message": "Follow requests retrieved successfully",
                        "data": {
                            "requests": [],
                            "count": 0
                        }
                    }
                    mock_service.return_value = mock_service_instance
                    
                    response = api_client.get_with_auth("/api/v1/users/me/follow-requests", valid_token)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_api_response_format(data, success=True)
        assert data["data"]["count"] == 0
        assert len(data["data"]["requests"]) == 0
    
    # ========== HANDLE FOLLOW REQUESTS TESTS ==========
    
    def test_accept_follow_request_success(self, api_client, sample_user, valid_token):
        """Test successfully accepting a follow request"""
        follower_id = str(uuid4())
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.accept_follow_request.return_value = {
                        "success": True,
                        "message": "Follow request accepted",
                        "data": {
                            "follow_id": f"{follower_id}_{sample_user.user_id}",
                            "status": "accepted",
                            "updated_at": "2024-01-01T00:00:00Z"
                        }
                    }
                    mock_service.return_value = mock_service_instance
                    
                    response = api_client.patch_with_auth(
                        f"/api/v1/users/me/follow-requests/{follower_id}",
                        {},
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_api_response_format(data, success=True)
        assert data["message"] == "Follow request accepted"
        assert data["errorCode"] is None
        assert "follow_id" in data["data"]
    
    def test_handle_follow_request_not_found(self, api_client, sample_user, valid_token):
        """Test handling non-existent follow request"""
        follower_id = str(uuid4())
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.accept_follow_request.return_value = {
                        "success": False,
                        "message": "Follow request not found or already processed",
                        "error_code": "REQUEST_NOT_FOUND"
                    }
                    mock_service.return_value = mock_service_instance
                    
                    response = api_client.patch_with_auth(
                        f"/api/v1/users/me/follow-requests/{follower_id}",
                        {},
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "detail" in data
        assert_api_response_format(data["detail"], success=False)
        assert data["detail"]["message"] == "Follow request not found or already processed"
        assert data["detail"]["errorCode"] == "REQUEST_NOT_FOUND"
    
    # ========== FOLLOWER/FOLLOWING LIST TESTS ==========

    def test_get_followers_list_success(self, api_client, sample_user, sample_public_user, valid_token):
        """Test successfully getting followers list for public user"""
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
                        f"/api/v1/users/{sample_public_user.user_id}/followers",
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_api_response_format(data, success=True)
        assert data["message"] == "Followers retrieved successfully"
        assert data["errorCode"] is None
        assert "followers" in data["data"]
        assert "pagination" in data["data"]
        assert data["data"]["pagination"]["total_count"] == 1

    def test_get_followers_list_private_account_forbidden(self, api_client, sample_user, sample_private_user, valid_token):
        """Test getting followers list for private account without permission"""
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

    def test_get_followers_list_user_not_found(self, api_client, sample_user, valid_token):
        """Test getting followers list for non-existent user"""
        non_existent_user_id = str(uuid4())
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user_optional, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.get_followers_list.return_value = {
                        "success": False,
                        "message": "User not found",
                        "error_code": "USER_NOT_FOUND"
                    }
                    mock_service.return_value = mock_service_instance
                    
                    response = api_client.get_with_auth(
                        f"/api/v1/users/{non_existent_user_id}/followers",
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "detail" in data
        assert_api_response_format(data["detail"], success=False)
        assert data["detail"]["message"] == "User not found"
        assert data["detail"]["errorCode"] == "USER_NOT_FOUND"

    def test_get_following_list_success(self, api_client, sample_user, sample_public_user, valid_token):
        """Test successfully getting following list for public user"""
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user_optional, sample_user):
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
                                    "followed_at": "2024-01-01T00:00:00Z",
                                    "follow_status": {
                                        "follow_status": "accepted",
                                        "is_following": True,
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
                        f"/api/v1/users/{sample_public_user.user_id}/following",
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_api_response_format(data, success=True)
        assert data["message"] == "Following retrieved successfully"
        assert data["errorCode"] is None
        assert "following" in data["data"]
        assert "pagination" in data["data"]
        assert data["data"]["pagination"]["total_count"] == 1

    def test_get_following_list_private_account_forbidden(self, api_client, sample_user, sample_private_user, valid_token):
        """Test getting following list for private account without permission"""
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user_optional, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.get_following_list.return_value = {
                        "success": False,
                        "message": "Private account - must be following to see following",
                        "error_code": "PRIVATE_ACCOUNT_FOLLOW_REQUIRED"
                    }
                    mock_service.return_value = mock_service_instance
                    
                    response = api_client.get_with_auth(
                        f"/api/v1/users/{sample_private_user.user_id}/following",
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert "detail" in data
        assert_api_response_format(data["detail"], success=False)
        assert data["detail"]["message"] == "Private account - must be following to see following"
        assert data["detail"]["errorCode"] == "PRIVATE_ACCOUNT_FOLLOW_REQUIRED"

    def test_get_followers_list_pagination(self, api_client, sample_user, sample_public_user, valid_token):
        """Test followers list pagination"""
        mock_db = create_mock_db_session(user_return=sample_user, count_return=0)
        
        with mock_dependency_override(app, get_current_user_optional, sample_user):
            with patch("app.core.database.get_db", return_value=mock_db):
                with patch("app.services.follow_service.FollowService") as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance.get_followers_list.return_value = {
                        "success": True,
                        "message": "Followers retrieved successfully",
                        "data": {
                            "followers": [],
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
                    
                    response = api_client.get_with_auth(
                        f"/api/v1/users/{sample_public_user.user_id}/followers?limit=10&offset=10",
                        valid_token
                    )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_api_response_format(data, success=True)
        pagination = data["data"]["pagination"]
        assert pagination["total_count"] == 25
        assert pagination["limit"] == 10
        assert pagination["offset"] == 10
        assert pagination["has_next"] is True
        assert pagination["has_previous"] is True

    def test_get_followers_list_unauthenticated(self, client, sample_public_user):
        """Test getting followers list without authentication (should work for public accounts)"""
        mock_db = create_mock_db_session(user_return=None, count_return=0)
        
        with patch("app.core.database.get_db", return_value=mock_db):
            with patch("app.services.follow_service.FollowService") as mock_service:
                mock_service_instance = Mock()
                mock_service_instance.get_followers_list.return_value = {
                    "success": True,
                    "message": "Followers retrieved successfully",
                    "data": {
                        "followers": [],
                        "pagination": {
                            "total_count": 0,
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
