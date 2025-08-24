"""
Integration Tests for GET /posts/{post_id}/conversation API

This test suite validates the endpoint that returns the source conversation for a post.
Tests cover visibility permissions, privacy controls, and proper error handling.
"""

import pytest
import uuid
from datetime import datetime, timezone
from fastapi import status

from tests.fixtures.posts_fixtures import comprehensive_test_data
from app.models.user import User
from app.models.post import Post
from app.models.conversation import Conversation
from app.models.message import Message


@pytest.fixture
def post_with_private_conversation(db_session):
    """Create test data with a post that has a private conversation."""
    # Create user
    user = User(
        user_name="private_conv_user",
        email="private@example.com",
        status="active"
    )
    db_session.add(user)
    db_session.flush()
    
    # Create conversation with messages
    conversation = Conversation(
        user_id=user.user_id,
        title="Private Conversation",
        status="active"
    )
    db_session.add(conversation)
    db_session.flush()
    
    # Add messages to conversation
    messages = [
        Message(
            conversation_id=conversation.conversation_id,
            user_id=user.user_id,
            role="user",
            content="This is a private conversation",
            is_blog=False,
            status="active"
        ),
        Message(
            conversation_id=conversation.conversation_id,
            user_id=None,  # AI message
            role="assistant",
            content="Yes, this conversation is private",
            is_blog=False,
            status="active"
        )
    ]
    
    for message in messages:
        db_session.add(message)
    
    db_session.flush()
    
    # Create post with private conversation
    post = Post(
        user_id=user.user_id,
        title="Post with Private Conversation",
        content="This post has a private conversation",
        conversation_id=conversation.conversation_id,
        is_conversation_visible=False,  # Private conversation
        status="active"
    )
    db_session.add(post)
    db_session.commit()
    
    return {
        "user": user,
        "conversation": conversation,
        "messages": messages,
        "post": post
    }


@pytest.fixture
def post_without_conversation(db_session):
    """Create test data with a post that has no linked conversation."""
    # Actually, based on the Post model, conversation_id is NOT NULL
    # So this test case doesn't make sense. Let's skip this fixture.
    pass


class TestGetPostConversationAPI:
    """Test cases for GET /posts/{post_id}/conversation endpoint."""
    
    def test_get_conversation_for_public_post_success(self, client, comprehensive_test_data):
        """Test successfully retrieving conversation for post with visible conversation."""
        # Get a post from comprehensive test data (all have public conversations)
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        response = client.get(f"/api/v1/posts/{test_post.post_id}/conversation")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert data["success"] is True
        assert "data" in data
        assert "conversation" in data["data"]
        assert data["message"] == "Conversation retrieved successfully"
        assert data["errorCode"] is None
        
        # Validate conversation data
        conversation = data["data"]["conversation"]
        assert "conversationId" in conversation
        assert "title" in conversation
        assert "createdAt" in conversation
        assert "forkedFrom" in conversation
        assert "messages" in conversation
        
        # Validate messages structure
        messages = conversation["messages"]
        assert len(messages) >= 0  # May be empty if no messages in test data
        
        for message in messages:
            assert "messageId" in message
            assert "role" in message
            assert "content" in message
            assert "isBlog" in message
            assert "createdAt" in message
            assert message["role"] in ["user", "assistant", "system"]
    
    def test_get_conversation_private_returns_404(self, client, post_with_private_conversation):
        """Test that private conversations return 404."""
        test_post = post_with_private_conversation["post"]
        
        response = client.get(f"/api/v1/posts/{test_post.post_id}/conversation")
        
        assert response.status_code == 404
        data = response.json()
        
        # FastAPI wraps HTTPException detail in "detail" field
        detail = data["detail"]
        assert detail["success"] is False
        assert detail["data"] is None
        assert "not viewable" in detail["message"].lower() or "not found" in detail["message"].lower()
        assert detail["errorCode"] == "CONVERSATION_NOT_VIEWABLE"
    
    def test_get_conversation_nonexistent_post_returns_404(self, client):
        """Test that non-existent post returns 404."""
        nonexistent_id = str(uuid.uuid4())
        
        response = client.get(f"/api/v1/posts/{nonexistent_id}/conversation")
        
        assert response.status_code == 404
        data = response.json()
        
        # FastAPI wraps HTTPException detail in "detail" field
        detail = data["detail"]
        assert detail["success"] is False
        assert detail["data"] is None
        assert "not found" in detail["message"].lower()
        assert detail["errorCode"] == "POST_NOT_FOUND"
    
    def test_get_conversation_invalid_uuid_returns_422(self, client):
        """Test that invalid UUID format returns 422."""
        response = client.get("/api/v1/posts/invalid-uuid/conversation")
        
        assert response.status_code == 422
        data = response.json()
        
        # FastAPI wraps HTTPException detail in "detail" field
        detail = data["detail"]
        assert detail["success"] is False
        assert detail["data"] is None
        assert "invalid" in detail["message"].lower()
        assert detail["errorCode"] == "INVALID_POST_ID"
    
    def test_get_conversation_no_auth_required(self, client, comprehensive_test_data):
        """Test that endpoint works without authentication."""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        # Make request without any authentication headers
        response = client.get(f"/api/v1/posts/{test_post.post_id}/conversation")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
