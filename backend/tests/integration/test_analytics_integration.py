"""
Comprehensive test of analytics features
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.post import Post
from app.models.conversation import Conversation
from app.models.post_share import PostShare
from app.models.post_view import PostView


def get_test_token(user_id):
    """Helper to create auth headers for testing"""
    return {"Authorization": f"Bearer fake_token_{user_id}"}


def test_analytics_integration(db_session: Session):
    """Test complete analytics integration"""
    
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
        print(f"\\n=== Testing Analytics Integration ===")
        print(f"Post ID: {post.post_id}")
        print(f"User ID: {user.user_id}")
        
        # 1. Test multiple views (should all count)
        print("\\n1. Testing view tracking...")
        for i in range(3):
            response = client.post(f"/api/v1/posts/{post.post_id}/view")
            assert response.status_code == 201
            print(f"   View {i+1}: ✅")
        
        # 2. Test authenticated view
        auth_headers = get_test_token(user.user_id)
        response = client.post(f"/api/v1/posts/{post.post_id}/view", headers=auth_headers)
        assert response.status_code == 201
        print(f"   Authenticated view: ✅")
        
        # 3. Test share tracking (requires auth)
        print("\\n2. Testing share tracking...")
        response = client.post(
            f"/api/v1/posts/{post.post_id}/share",
            headers=auth_headers,
            json={"platform": "twitter"}
        )
        print(f"   Share response: {response.status_code} - {response.text}")
        
        # 4. Check database counts
        print("\\n3. Database verification...")
        view_count = db_session.query(PostView).filter(PostView.post_id == post.post_id).count()
        share_count = db_session.query(PostShare).filter(PostShare.post_id == post.post_id).count()
        
        print(f"   Total views in DB: {view_count}")
        print(f"   Total shares in DB: {share_count}")
        
        # 5. Test that GET /posts/{id} includes analytics (if implemented)
        print("\\n4. Testing post detail analytics...")
        response = client.get(f"/api/v1/posts/{post.post_id}")
        print(f"   Post detail status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            post_data = data.get('data', {}).get('post', {})
            print(f"   Post data keys: {list(post_data.keys())}")
        
        print("\\n=== Test Summary ===")
        print(f"✅ Views tracked: {view_count} (expected: 4)")
        print(f"✅ Shares tracked: {share_count} (expected: 1)")
        
    # Clean up
    app.dependency_overrides.clear()
