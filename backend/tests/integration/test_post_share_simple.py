"""
Test the share endpoint
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.post import Post
from app.models.conversation import Conversation
from app.models.post_share import PostShare


def get_test_token(user_id):
    """Helper to create auth headers for testing"""
    return {"Authorization": f"Bearer fake_token_{user_id}"}


def test_track_post_share_with_real_post(db_session: Session):
    """Test share tracking with manually created post"""
    
    # Create test user
    user = User(user_name="test_user", email="test@example.com")
    db_session.add(user)
    db_session.flush()
    
    # Create test conversation
    conversation = Conversation(
        user_id=user.user_id,
        title="Test Conversation"
    )
    db_session.add(conversation)
    db_session.flush()
    
    # Create test post
    post = Post(
        user_id=user.user_id,
        conversation_id=conversation.conversation_id,
        title="Test Post",
        content="Test content"
    )
    db_session.add(post)
    db_session.commit()
    
    # Create test client
    from app.core.database import get_db
    
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        # Test the share endpoint
        auth_headers = get_test_token(user.user_id)
        
        print(f"Testing share with post ID: {post.post_id}")
        print(f"User ID: {user.user_id}")
        
        response = client.post(
            f"/api/v1/posts/{post.post_id}/share",
            headers=auth_headers,
            json={"platform": "twitter"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Check if share was created
        share_count = db_session.query(PostShare).filter(
            PostShare.post_id == post.post_id
        ).count()
        print(f"Shares in database: {share_count}")
        
    # Clean up
    app.dependency_overrides.clear()
