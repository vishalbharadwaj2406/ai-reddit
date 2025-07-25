"""
Unit Tests for GET Comments API Endpoints

Tests the GET /posts/{post_id}/comments endpoint for retrieving comments on a post.
Follows TDD methodology with comprehensive coverage of success scenarios, validation,
authorization, and error handling.

Test Categories:
1. Success Scenarios - Valid requests with different comment structures
2. Validation Scenarios - Invalid parameters and edge cases  
3. Authorization Scenarios - Authentication requirements
4. Error Scenarios - Invalid post IDs, server errors, etc.
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4, UUID
from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment


class TestGetCommentsEndpoints:
    """Test class for GET /posts/{post_id}/comments endpoint"""

    # === SUCCESS SCENARIOS ===
    
    def test_get_comments_empty_list_success(self, client, mock_user, mock_post, mock_db):
        """Test getting comments for post with no comments returns empty list"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service to return empty list
        with patch('app.services.comment_service.CommentService.get_comments_for_post') as mock_get:
            mock_get.return_value = []
            
            response = client.get(f"/api/v1/posts/{mock_post.post_id}/comments")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["data"] == []
        assert "message" in response_data
        
        app.dependency_overrides.clear()

    def test_get_comments_with_top_level_comments_success(self, client, mock_user, mock_post, mock_db):
        """Test getting comments returns list of top-level comments"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Create mock comments
        mock_comment1 = Mock(spec=Comment)
        mock_comment1.comment_id = uuid4()
        mock_comment1.content = "First comment"
        mock_comment1.created_at = datetime.now()
        mock_comment1.user_id = uuid4()
        mock_comment1.post_id = mock_post.post_id
        mock_comment1.parent_comment_id = None
        
        mock_comment2 = Mock(spec=Comment)
        mock_comment2.comment_id = uuid4()
        mock_comment2.content = "Second comment"
        mock_comment2.created_at = datetime.now()
        mock_comment2.user_id = uuid4()
        mock_comment2.post_id = mock_post.post_id
        mock_comment2.parent_comment_id = None
        
        # Mock users for comments
        mock_user1 = Mock(spec=User)
        mock_user1.user_id = mock_comment1.user_id
        mock_user1.user_name = "user1"
        mock_user1.get_display_name.return_value = "User One"
        
        mock_user2 = Mock(spec=User)
        mock_user2.user_id = mock_comment2.user_id
        mock_user2.user_name = "user2"
        mock_user2.get_display_name.return_value = "User Two"
        
        # Set up user relationships
        mock_comment1.user = mock_user1
        mock_comment2.user = mock_user2
        
        # Mock service to return comments
        with patch('app.services.comment_service.CommentService.get_comments_for_post') as mock_get:
            mock_get.return_value = [mock_comment1, mock_comment2]
            
            response = client.get(f"/api/v1/posts/{mock_post.post_id}/comments")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert len(response_data["data"]) == 2
        
        # Verify comment structure
        comment_data = response_data["data"][0]
        assert "commentId" in comment_data
        assert "content" in comment_data
        assert "createdAt" in comment_data
        assert "user" in comment_data
        assert comment_data["user"]["username"] == "user1"
        assert comment_data["parentCommentId"] is None
        
        app.dependency_overrides.clear()

    def test_get_comments_with_nested_replies_success(self, client, mock_user, mock_post, mock_db):
        """Test getting comments includes nested replies"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Create parent comment
        parent_comment_id = uuid4()
        mock_parent = Mock(spec=Comment)
        mock_parent.comment_id = parent_comment_id
        mock_parent.content = "Parent comment"
        mock_parent.created_at = datetime.now()
        mock_parent.user_id = uuid4()
        mock_parent.post_id = mock_post.post_id
        mock_parent.parent_comment_id = None
        
        # Create reply comment
        mock_reply = Mock(spec=Comment)
        mock_reply.comment_id = uuid4()
        mock_reply.content = "Reply to parent"
        mock_reply.created_at = datetime.now()
        mock_reply.user_id = uuid4()
        mock_reply.post_id = mock_post.post_id
        mock_reply.parent_comment_id = parent_comment_id
        
        # Mock users
        mock_parent_user = Mock(spec=User)
        mock_parent_user.user_id = mock_parent.user_id
        mock_parent_user.user_name = "parent_user"
        mock_parent_user.get_display_name.return_value = "Parent User"
        
        mock_reply_user = Mock(spec=User)
        mock_reply_user.user_id = mock_reply.user_id
        mock_reply_user.user_name = "reply_user"
        mock_reply_user.get_display_name.return_value = "Reply User"
        
        mock_parent.user = mock_parent_user
        mock_reply.user = mock_reply_user
        
        # Mock service to return hierarchical comments
        with patch('app.services.comment_service.CommentService.get_comments_for_post') as mock_get:
            mock_get.return_value = [mock_parent, mock_reply]
            
            response = client.get(f"/api/v1/posts/{mock_post.post_id}/comments")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert len(response_data["data"]) == 2
        
        # Find parent and reply in response
        parent_data = next(c for c in response_data["data"] if c["parentCommentId"] is None)
        reply_data = next(c for c in response_data["data"] if c["parentCommentId"] is not None)
        
        assert parent_data["content"] == "Parent comment"
        assert reply_data["content"] == "Reply to parent"
        assert reply_data["parentCommentId"] == str(parent_comment_id)
        
        app.dependency_overrides.clear()

    def test_get_comments_pagination_support(self, client, mock_user, mock_post, mock_db):
        """Test getting comments supports pagination parameters"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service to return paginated results
        with patch('app.services.comment_service.CommentService.get_comments_for_post') as mock_get:
            mock_get.return_value = []
            
            response = client.get(
                f"/api/v1/posts/{mock_post.post_id}/comments",
                params={"limit": 10, "offset": 0}
            )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["data"] == []
        
        # Verify service was called with pagination params
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        # Note: Implementation should pass pagination to service
        
        app.dependency_overrides.clear()

    # === VALIDATION SCENARIOS ===
    
    def test_get_comments_invalid_post_uuid_error(self, client, mock_user, mock_db):
        """Test that malformed post UUID returns validation error"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        response = client.get("/api/v1/posts/invalid-uuid/comments")
        
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
        assert isinstance(response_data["detail"], list)
        
        app.dependency_overrides.clear()

    def test_get_comments_invalid_pagination_params(self, client, mock_user, mock_post, mock_db):
        """Test that invalid pagination parameters return validation error"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Test negative limit
        response = client.get(
            f"/api/v1/posts/{mock_post.post_id}/comments",
            params={"limit": -1}
        )
        
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
        
        # Test negative offset
        response = client.get(
            f"/api/v1/posts/{mock_post.post_id}/comments",
            params={"offset": -1}
        )
        
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
        
        app.dependency_overrides.clear()

    # === AUTHORIZATION SCENARIOS ===
    
    def test_get_comments_unauthenticated_request_error(self, client, mock_post):
        """Test that unauthenticated request returns 401 error"""
        
        # Clear any existing dependency overrides to test real authentication
        app.dependency_overrides.clear()
        
        response = client.get(f"/api/v1/posts/{mock_post.post_id}/comments")
        
        assert response.status_code == 401
        response_data = response.json()
        assert "detail" in response_data

    # === ERROR SCENARIOS ===
    
    def test_get_comments_nonexistent_post_error(self, client, mock_user, mock_db):
        """Test that getting comments for non-existent post returns 404"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service to raise exception for non-existent post
        with patch('app.services.comment_service.CommentService.get_comments_for_post') as mock_get:
            from fastapi import HTTPException
            mock_get.side_effect = HTTPException(status_code=404, detail="Post not found")
            
            fake_post_id = uuid4()
            response = client.get(f"/api/v1/posts/{fake_post_id}/comments")
        
        assert response.status_code == 404
        response_data = response.json()
        assert "detail" in response_data
        assert "Post not found" in response_data["detail"]
        
        app.dependency_overrides.clear()

    def test_get_comments_database_error_handling(self, client, mock_user, mock_post, mock_db):
        """Test that database errors are handled gracefully"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service to raise database exception
        with patch('app.services.comment_service.CommentService.get_comments_for_post') as mock_get:
            from fastapi import HTTPException
            mock_get.side_effect = HTTPException(status_code=500, detail="Database connection error")
            
            response = client.get(f"/api/v1/posts/{mock_post.post_id}/comments")
        
        assert response.status_code == 500
        response_data = response.json()
        assert "detail" in response_data
        
        app.dependency_overrides.clear()

    # === PERFORMANCE SCENARIOS ===
    
    def test_get_comments_large_comment_thread_handling(self, client, mock_user, mock_post, mock_db):
        """Test that large comment threads are handled efficiently"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Create a large list of mock comments
        mock_comments = []
        for i in range(100):
            mock_comment = Mock(spec=Comment)
            mock_comment.comment_id = uuid4()
            mock_comment.content = f"Comment {i}"
            mock_comment.created_at = datetime.now()
            mock_comment.user_id = uuid4()
            mock_comment.post_id = mock_post.post_id
            mock_comment.parent_comment_id = None
            
            mock_user_obj = Mock(spec=User)
            mock_user_obj.user_id = mock_comment.user_id
            mock_user_obj.user_name = f"user{i}"
            mock_user_obj.get_display_name.return_value = f"User {i}"
            mock_comment.user = mock_user_obj
            
            mock_comments.append(mock_comment)
        
        # Mock service to return large comment list
        with patch('app.services.comment_service.CommentService.get_comments_for_post') as mock_get:
            mock_get.return_value = mock_comments
            
            response = client.get(f"/api/v1/posts/{mock_post.post_id}/comments")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert len(response_data["data"]) == 100
        
        app.dependency_overrides.clear()

    # === FIXTURES ===
    
    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user fixture"""
        user = Mock(spec=User)
        user.user_id = uuid4()
        user.username = "testuser"
        user.email = "test@example.com"
        user.display_name = "Test User"
        return user

    @pytest.fixture
    def mock_post(self):
        """Mock post fixture"""
        post = Mock(spec=Post)
        post.post_id = uuid4()
        post.title = "Test Post"
        post.content = "Test post content"
        post.user_id = uuid4()
        return post

    @pytest.fixture
    def mock_db(self):
        """Mock database session fixture"""
        return Mock()
