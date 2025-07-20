"""
Unit Tests for GET /posts API Endpoint

Tests the API endpoint handler in isolation using mocks.
These tests focus on testing the router logic, parameter validation, and response formatting
without involving the database or service layer implementation.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.post import PostResponse
from app.models.user import User


client = TestClient(app)


@pytest.fixture
def mock_post_service():
    """Mock PostService for isolated testing."""
    return Mock()


@pytest.fixture
def mock_user():
    """Mock user for authentication tests."""
    user = Mock(spec=User)
    user.user_id = uuid4()
    user.user_name = "testuser"
    user.email = "test@example.com"
    return user


@pytest.fixture
def sample_post_response():
    """Sample PostResponse for testing."""
    return PostResponse(
        postId=uuid4(),
        title="Test Post",
        content="Test content",
        createdAt=datetime.now(timezone.utc),
        user={
            "userId": uuid4(),
            "userName": "testuser",
            "profilePicture": None
        },
        tags=["test", "python"],
        reactions={"upvote": 5, "downvote": 1},
        userReaction=None,
        commentCount=3,
        viewCount=42,
        userViewCount=0,
        conversationId=None
    )


class TestGetPostsAPIUnit:
    """Unit tests for GET /posts API endpoint."""

    @patch('app.api.v1.posts.PostService')
    def test_get_posts_feed_default_parameters(self, mock_service_class, sample_post_response):
        """Test GET /posts with default parameters."""
        # Setup mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_posts_feed = AsyncMock(return_value=[sample_post_response])
        
        # Make request
        response = client.get("/api/v1/posts")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["posts"]) == 1
        
        # Verify service was called with correct defaults
        mock_service.get_posts_feed.assert_called_once()
        call_kwargs = mock_service.get_posts_feed.call_args.kwargs
        assert call_kwargs["limit"] == 20
        assert call_kwargs["offset"] == 0
        assert call_kwargs["sort"] == "hot"
        assert call_kwargs["time_range"] == "all"
        assert call_kwargs["tag"] is None
        assert call_kwargs["user_id"] is None

    @patch('app.api.v1.posts.PostService')
    def test_get_posts_feed_custom_parameters(self, mock_service_class, sample_post_response):
        """Test GET /posts with custom parameters."""
        # Setup mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_posts_feed = AsyncMock(return_value=[sample_post_response])
        
        user_id = uuid4()
        
        # Make request with custom parameters
        response = client.get(
            f"/api/v1/posts?limit=5&offset=10&sort=new&time_range=week&tag=python&userId={user_id}"
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify service was called with custom parameters
        call_kwargs = mock_service.get_posts_feed.call_args.kwargs
        assert call_kwargs["limit"] == 5
        assert call_kwargs["offset"] == 10
        assert call_kwargs["sort"] == "new"
        assert call_kwargs["time_range"] == "week"
        assert call_kwargs["tag"] == "python"
        assert call_kwargs["user_id"] == user_id

    def test_get_posts_feed_invalid_sort_parameter(self):
        """Test GET /posts with invalid sort parameter returns 422."""
        response = client.get("/api/v1/posts?sort=invalid_sort")
        assert response.status_code == 422

    def test_get_posts_feed_invalid_time_range_parameter(self):
        """Test GET /posts with invalid time_range parameter returns 422."""
        response = client.get("/api/v1/posts?time_range=invalid_range")
        assert response.status_code == 422

    def test_get_posts_feed_invalid_limit_too_high(self):
        """Test GET /posts with limit too high returns 422."""
        response = client.get("/api/v1/posts?limit=101")
        assert response.status_code == 422

    def test_get_posts_feed_invalid_limit_too_low(self):
        """Test GET /posts with limit too low returns 422."""
        response = client.get("/api/v1/posts?limit=0")
        assert response.status_code == 422

    def test_get_posts_feed_invalid_offset_negative(self):
        """Test GET /posts with negative offset returns 422."""
        response = client.get("/api/v1/posts?offset=-1")
        assert response.status_code == 422

    def test_get_posts_feed_invalid_user_id_format(self):
        """Test GET /posts with invalid UUID format returns 422."""
        response = client.get("/api/v1/posts?userId=invalid-uuid-format")
        assert response.status_code == 422

    @patch('app.api.v1.posts.PostService')
    def test_get_posts_feed_service_error_handling(self, mock_service_class):
        """Test GET /posts handles service errors properly."""
        # Setup mock to raise exception
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_posts_feed = AsyncMock(side_effect=Exception("Database error"))
        
        # Make request
        response = client.get("/api/v1/posts")
        
        # Should return 500 error
        assert response.status_code == 500

    @patch('app.api.v1.posts.PostService')
    def test_get_posts_feed_empty_result(self, mock_service_class):
        """Test GET /posts with empty result from service."""
        # Setup mock to return empty list
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_posts_feed = AsyncMock(return_value=[])
        
        # Make request
        response = client.get("/api/v1/posts")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["posts"]) == 0
        assert data["data"]["posts"] == []

    @patch('app.api.v1.posts.PostService')
    def test_get_posts_feed_response_format(self, mock_service_class, sample_post_response):
        """Test GET /posts response format is correct."""
        # Setup mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_posts_feed = AsyncMock(return_value=[sample_post_response])
        
        # Make request
        response = client.get("/api/v1/posts")
        
        # Verify response structure
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level structure
        assert "success" in data
        assert "data" in data
        assert data["success"] is True
        
        # Check data structure
        assert "posts" in data["data"]
        assert isinstance(data["data"]["posts"], list)
        
        # Check post structure
        if len(data["data"]["posts"]) > 0:
            post = data["data"]["posts"][0]
            required_fields = [
                "postId", "title", "content", "createdAt", "user", 
                "tags", "reactions", "commentCount", "viewCount"
            ]
            for field in required_fields:
                assert field in post, f"Missing required field: {field}"

    @patch('app.api.v1.posts.PostService')
    def test_get_posts_feed_parameter_boundary_values(self, mock_service_class):
        """Test GET /posts with boundary parameter values."""
        # Setup mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_posts_feed = AsyncMock(return_value=[])
        
        # Test minimum valid values
        response = client.get("/api/v1/posts?limit=1&offset=0")
        assert response.status_code == 200
        
        # Test maximum valid values
        response = client.get("/api/v1/posts?limit=100&offset=999999")
        assert response.status_code == 200
        
        # Verify service calls
        assert mock_service.get_posts_feed.call_count == 2

    @patch('app.api.v1.posts.PostService')
    def test_get_posts_feed_all_sort_options(self, mock_service_class):
        """Test GET /posts with all valid sort options."""
        # Setup mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_posts_feed = AsyncMock(return_value=[])
        
        valid_sorts = ["hot", "new", "top"]
        
        for sort_option in valid_sorts:
            response = client.get(f"/api/v1/posts?sort={sort_option}")
            assert response.status_code == 200, f"Failed for sort: {sort_option}"
        
        # Verify service was called for each sort option
        assert mock_service.get_posts_feed.call_count == len(valid_sorts)

    @patch('app.api.v1.posts.PostService')
    def test_get_posts_feed_all_time_ranges(self, mock_service_class):
        """Test GET /posts with all valid time range options."""
        # Setup mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_posts_feed = AsyncMock(return_value=[])
        
        valid_time_ranges = ["hour", "day", "week", "month", "all"]
        
        for time_range in valid_time_ranges:
            response = client.get(f"/api/v1/posts?time_range={time_range}")
            assert response.status_code == 200, f"Failed for time_range: {time_range}"
        
        # Verify service was called for each time range
        assert mock_service.get_posts_feed.call_count == len(valid_time_ranges)
