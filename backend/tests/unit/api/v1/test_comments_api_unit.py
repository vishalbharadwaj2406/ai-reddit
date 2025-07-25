"""
Test Comment Creation API Endpoints

TDD tests for POST /posts/{post_id}/comments endpoint with comprehensive coverage:
- Success scenarios (top-level and reply comments)
- Content validation and constraints
- Authentication and authorization
- Parent comment validation
- Threading business logic
- Error scenarios with proper response wrapper format

Following TDD methodology:
1. Write failing tests first (RED)
2. Implement minimal API to pass tests (GREEN)
3. Refactor and improve (REFACTOR)
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.dependencies.auth import get_current_user
from app.core.database import get_db


class TestPostCommentsEndpoints:
    """Test cases for POST /posts/{post_id}/comments endpoint"""

    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user fixture"""
        user = Mock(spec=User)
        user.user_id = uuid4()
        user.user_name = "testuser"
        user.email = "test@example.com"
        return user

    @pytest.fixture
    def mock_post(self):
        """Mock post fixture"""
        post = Mock(spec=Post)
        post.post_id = uuid4()
        post.title = "Test Post"
        post.content = "Test post content"
        post.status = "active"
        return post

    @pytest.fixture
    def mock_parent_comment(self, mock_post, mock_user):
        """Mock parent comment fixture for reply testing"""
        comment = Mock(spec=Comment)
        comment.comment_id = uuid4()
        comment.post_id = mock_post.post_id
        comment.user_id = mock_user.user_id
        comment.content = "Parent comment content"
        comment.parent_comment_id = None
        comment.status = "active"
        comment.created_at = datetime.now(timezone.utc)
        return comment

    @pytest.fixture
    def mock_db(self):
        """Mock database session fixture"""
        return Mock()

    @pytest.fixture
    def valid_comment_request(self):
        """Valid comment creation request fixture"""
        return {
            "content": "This is a thoughtful comment on the post."
        }

    @pytest.fixture
    def valid_reply_request(self, mock_parent_comment):
        """Valid reply comment creation request fixture"""
        return {
            "content": "This is a reply to the parent comment.",
            "parentCommentId": str(mock_parent_comment.comment_id)
        }

    # === SUCCESS SCENARIOS ===
    
    def test_create_top_level_comment_success(self, client, mock_user, mock_post, mock_db, valid_comment_request):
        """Test successful creation of a top-level comment"""
        
        # Mock the created comment
        created_comment = Mock(spec=Comment)
        created_comment.comment_id = uuid4()
        created_comment.post_id = mock_post.post_id
        created_comment.user_id = mock_user.user_id
        created_comment.content = valid_comment_request["content"]
        created_comment.parent_comment_id = None
        created_comment.status = "active"
        created_comment.created_at = datetime.now(timezone.utc)
        created_comment.updated_at = datetime.now(timezone.utc)
        
        # Mock dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service/repository calls
        with patch('app.services.comment_service.CommentService.create_comment') as mock_create:
            mock_create.return_value = created_comment
            
            # Make request
            response = client.post(
                f"/api/v1/posts/{mock_post.post_id}/comments",
                json=valid_comment_request
            )
        
        # Assertions
        assert response.status_code == 201
        response_data = response.json()
        
        # Verify standard response wrapper
        assert response_data["success"] is True
        assert response_data["message"] == "Comment created successfully"
        assert "data" in response_data
        
        # Verify comment data structure
        comment_data = response_data["data"]
        assert "commentId" in comment_data
        assert comment_data["content"] == valid_comment_request["content"]
        assert comment_data["parentCommentId"] is None
        assert "createdAt" in comment_data
        
        # Verify service was called with correct parameters
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]  # Get keyword arguments
        assert call_args["post_id"] == mock_post.post_id
        assert call_args["user_id"] == mock_user.user_id
        assert call_args["content"] == valid_comment_request["content"]
        assert call_args["parent_comment_id"] is None
        
        # Clean up
        app.dependency_overrides.clear()

    def test_create_reply_comment_success(self, client, mock_user, mock_post, mock_parent_comment, mock_db, valid_reply_request):
        """Test successful creation of a reply comment"""
        
        # Mock the created reply comment
        created_reply = Mock(spec=Comment)
        created_reply.comment_id = uuid4()
        created_reply.post_id = mock_post.post_id
        created_reply.user_id = mock_user.user_id
        created_reply.content = valid_reply_request["content"]
        created_reply.parent_comment_id = mock_parent_comment.comment_id
        created_reply.status = "active"
        created_reply.created_at = datetime.now(timezone.utc)
        created_reply.updated_at = datetime.now(timezone.utc)
        
        # Mock dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service/repository calls
        with patch('app.services.comment_service.CommentService.create_comment') as mock_create:
            mock_create.return_value = created_reply
            
            # Make request
            response = client.post(
                f"/api/v1/posts/{mock_post.post_id}/comments",
                json=valid_reply_request
            )
        
        # Assertions
        assert response.status_code == 201
        response_data = response.json()
        
        # Verify standard response wrapper
        assert response_data["success"] is True
        assert response_data["message"] == "Comment created successfully"
        
        # Verify reply-specific data
        comment_data = response_data["data"]
        assert comment_data["parentCommentId"] == str(mock_parent_comment.comment_id)
        assert comment_data["content"] == valid_reply_request["content"]
        
        # Verify service was called with parent comment ID
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["parent_comment_id"] == mock_parent_comment.comment_id
        
        # Clean up
        app.dependency_overrides.clear()

    def test_response_format_validation(self, client, mock_user, mock_post, mock_db, valid_comment_request):
        """Test that response follows exact API specification format"""
        
        # Mock created comment
        comment_id = uuid4()
        created_at = datetime.now(timezone.utc)
        
        created_comment = Mock(spec=Comment)
        created_comment.comment_id = comment_id
        created_comment.content = valid_comment_request["content"]
        created_comment.parent_comment_id = None
        created_comment.created_at = created_at
        
        # Mock dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        with patch('app.services.comment_service.CommentService.create_comment') as mock_create:
            mock_create.return_value = created_comment
            
            response = client.post(
                f"/api/v1/posts/{mock_post.post_id}/comments",
                json=valid_comment_request
            )
        
        response_data = response.json()
        
        # Verify exact response structure matches API spec
        expected_keys = {"success", "data", "message"}
        assert set(response_data.keys()) == expected_keys
        
        # Verify data object structure
        data_keys = {"commentId", "content", "parentCommentId", "createdAt"}
        assert set(response_data["data"].keys()) == data_keys
        
        # Verify data types
        assert isinstance(response_data["success"], bool)
        assert isinstance(response_data["message"], str)
        assert isinstance(response_data["data"]["commentId"], str)
        assert isinstance(response_data["data"]["content"], str)
        assert response_data["data"]["parentCommentId"] is None
        assert isinstance(response_data["data"]["createdAt"], str)
        
        app.dependency_overrides.clear()

    # === VALIDATION SCENARIOS ===
    
    def test_empty_content_validation_error(self, client, mock_user, mock_post, mock_db):
        """Test that empty content returns validation error"""

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        # Test empty string
        response = client.post(
            f"/api/v1/posts/{mock_post.post_id}/comments",
            json={"content": ""}
        )

        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
        assert isinstance(response_data["detail"], list)
        assert len(response_data["detail"]) > 0
        assert "content" in str(response_data["detail"]).lower()
        
        # Test whitespace only
        response = client.post(
            f"/api/v1/posts/{mock_post.post_id}/comments",
            json={"content": "   \n\t   "}
        )
        
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
        assert isinstance(response_data["detail"], list)
        
        app.dependency_overrides.clear()

    def test_missing_content_validation_error(self, client, mock_user, mock_post, mock_db):
        """Test that missing content field returns validation error"""

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.post(
            f"/api/v1/posts/{mock_post.post_id}/comments",
            json={}  # Missing content field
        )

        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
        assert isinstance(response_data["detail"], list)
        assert len(response_data["detail"]) > 0
        # Check that content field is mentioned in the error
        error_details = str(response_data["detail"]).lower()
        assert "content" in error_details and "required" in error_details

    def test_invalid_parent_comment_id_error(self, client, mock_user, mock_post, mock_db):
        """Test that invalid parent comment ID returns 404 error"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service to raise exception for invalid parent
        with patch('app.services.comment_service.CommentService.create_comment') as mock_create:
            from fastapi import HTTPException
            mock_create.side_effect = HTTPException(status_code=404, detail="Parent comment not found")
            
            fake_parent_id = uuid4()
            response = client.post(
                f"/api/v1/posts/{mock_post.post_id}/comments",
                json={
                    "content": "Reply to non-existent comment",
                    "parentCommentId": str(fake_parent_id)
                }
            )
        
        assert response.status_code == 404
        response_data = response.json()
        assert "detail" in response_data
        assert "Parent comment not found" in response_data["detail"]
        
        app.dependency_overrides.clear()

    def test_parent_comment_different_post_error(self, client, mock_user, mock_post, mock_db):
        """Test that parent comment from different post returns validation error"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service to raise exception for cross-post parent
        with patch('app.services.comment_service.CommentService.create_comment') as mock_create:
            from fastapi import HTTPException
            mock_create.side_effect = HTTPException(
                status_code=400, 
                detail="Parent comment must belong to the same post"
            )
            
            different_post_comment_id = uuid4()
            response = client.post(
                f"/api/v1/posts/{mock_post.post_id}/comments",
                json={
                    "content": "Reply to comment from different post",
                    "parentCommentId": str(different_post_comment_id)
                }
            )
        
        assert response.status_code == 400
        response_data = response.json()
        assert "detail" in response_data
        assert "Parent comment must belong to the same post" in response_data["detail"]
        
        app.dependency_overrides.clear()

    # === AUTHORIZATION SCENARIOS ===
    
    def test_unauthenticated_request_error(self, client, mock_post):
        """Test that unauthenticated request returns 401 error"""
        
        # Clear any existing dependency overrides to test real authentication
        app.dependency_overrides.clear()
        
        response = client.post(
            f"/api/v1/posts/{mock_post.post_id}/comments",
            json={"content": "Unauthenticated comment attempt"}
        )
        
        assert response.status_code == 401
        response_data = response.json()
        assert "detail" in response_data
        assert response_data["detail"]["error"] == "AUTH_REQUIRED"

    def test_invalid_post_id_error(self, client, mock_user, mock_db):
        """Test that invalid post ID returns 404 error"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service to raise exception for invalid post
        with patch('app.services.comment_service.CommentService.create_comment') as mock_create:
            from fastapi import HTTPException
            mock_create.side_effect = HTTPException(status_code=404, detail="Post not found")
            
            fake_post_id = uuid4()
            response = client.post(
                f"/api/v1/posts/{fake_post_id}/comments",
                json={"content": "Comment on non-existent post"}
            )
        
        assert response.status_code == 404
        response_data = response.json()
        assert "detail" in response_data
        assert "Post not found" in response_data["detail"]
        
        app.dependency_overrides.clear()

    def test_malformed_uuid_in_url_error(self, client, mock_user, mock_db):
        """Test that malformed UUID in URL returns 422 error"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        response = client.post(
            "/api/v1/posts/invalid-uuid/comments",
            json={"content": "Comment with invalid post ID"}
        )
        
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
        assert isinstance(response_data["detail"], list)
        
        app.dependency_overrides.clear()

    def test_malformed_parent_comment_uuid_error(self, client, mock_user, mock_post, mock_db):
        """Test that malformed parent comment UUID returns 422 error"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        response = client.post(
            f"/api/v1/posts/{mock_post.post_id}/comments",
            json={
                "content": "Reply with invalid parent ID",
                "parentCommentId": "invalid-uuid"
            }
        )
        
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
        assert isinstance(response_data["detail"], list)
        
        app.dependency_overrides.clear()

    # === EDGE CASES ===
    
    def test_very_long_content_handling(self, client, mock_user, mock_post, mock_db):
        """Test handling of very long comment content"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Create a very long comment (test content length limits)
        long_content = "A" * 10000  # 10K characters
        
        # Mock created comment
        created_comment = Mock(spec=Comment)
        created_comment.comment_id = uuid4()
        created_comment.content = long_content
        created_comment.parent_comment_id = None
        created_comment.created_at = datetime.now(timezone.utc)
        
        with patch('app.services.comment_service.CommentService.create_comment') as mock_create:
            mock_create.return_value = created_comment
            
            response = client.post(
                f"/api/v1/posts/{mock_post.post_id}/comments",
                json={"content": long_content}
            )
        
        # Should succeed (or fail gracefully if there's a length limit)
        assert response.status_code in [201, 422]
        
        if response.status_code == 201:
            response_data = response.json()
            assert response_data["success"] is True
            assert response_data["data"]["content"] == long_content
        
        app.dependency_overrides.clear()
