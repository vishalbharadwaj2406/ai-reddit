"""
Unit Tests for Post Reactions API Endpoints

Tests the POST /posts/{post_id}/reaction endpoint for adding/updating reactions to posts.
Follows TDD methodology with comprehensive coverage of success scenarios, validation,
authorization, and error handling.
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.post import Post
from app.models.post_reaction import PostReaction


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
def mock_post():
    """Mock post object with proper UUID"""
    post = Mock(spec=Post)
    post.post_id = uuid4()
    post.title = "Test Post"
    post.content = "This is a test post"
    return post


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()


class TestPostReactionsEndpoints:
    """Test class for POST /posts/{post_id}/reaction endpoint"""

    def test_add_new_reaction_success(self, client, mock_user, mock_post, mock_db):
        """Test adding a new reaction to a post"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock reaction counts response
        mock_counts = {
            "upvote": 1, "downvote": 0, "heart": 0,
            "insightful": 0, "accurate": 0
        }
        
        with patch('app.services.post_reaction_service.PostReactionService.add_or_update_reaction') as mock_add, \
             patch('app.services.post_reaction_service.PostReactionService.get_post_reactions') as mock_get_counts, \
             patch('app.services.post_reaction_service.PostReactionService.get_user_reaction') as mock_get_user:
            
            mock_reaction = Mock(spec=PostReaction)
            mock_add.return_value = (mock_reaction, "created")
            mock_get_counts.return_value = mock_counts
            mock_get_user.return_value = "upvote"
            
            response = client.post(
                f"/api/v1/posts/{mock_post.post_id}/reaction",
                json={"reactionType": "upvote"}
            )
            
        print(f"Response status: {response.status_code}")
        if response.status_code != 201:
            print(f"Response body: {response.json()}")
            
        assert response.status_code == 201
        
        # Clean up
        app.dependency_overrides.clear()

    def test_invalid_reaction_type(self, client, mock_user, mock_post, mock_db):
        """Test that invalid reaction types are rejected"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        response = client.post(
            f"/api/v1/posts/{mock_post.post_id}/reaction",
            json={"reactionType": "invalid_reaction"}
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code != 422:
            print(f"Response body: {response.json()}")
            
        assert response.status_code == 422
        
        # Clean up
        app.dependency_overrides.clear()

    def test_unauthenticated_request(self, client, mock_post, mock_db):
        """Test that unauthenticated requests are rejected"""
        
        app.dependency_overrides[get_db] = lambda: mock_db
        # No auth override - should get 401
        
        response = client.post(
            f"/api/v1/posts/{mock_post.post_id}/reaction",
            json={"reactionType": "upvote"}
        )
        
        assert response.status_code == 401
        
        # Clean up
        app.dependency_overrides.clear()
