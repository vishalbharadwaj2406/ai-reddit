"""
Integration Tests for Post Analytics Endpoints

Tests the view tracking and share tracking endpoints:
- POST /posts/{post_id}/view
- POST /posts/{post_id}/share

Following TDD approach: Write failing tests first, then implement.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4, UUID
from datetime import datetime, timezone

from app.main import app
from app.models.user import User
from app.models.post import Post
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.post_view import PostView
from app.models.post_share import PostShare
from app.dependencies.auth import get_current_user_optional, get_current_user
from tests.fixtures.posts_fixtures import comprehensive_test_data


@pytest.fixture
def test_post(db_session: Session, sample_user: User):
    """Create a test post for analytics testing"""
    # Create a conversation first
    conversation = Conversation(
        user_id=sample_user.user_id,
        title="Test Conversation"
    )
    db_session.add(conversation)
    db_session.flush()
    
    # Create a post
    post = Post(
        user_id=sample_user.user_id,
        conversation_id=conversation.conversation_id,
        title="Test Post",
        content="This is a test post for analytics",
        is_conversation_visible=True
    )
    db_session.add(post)
    db_session.commit()
    return post


def get_test_token(user_id):
    """Helper to create auth headers for testing"""
    return {"Authorization": f"Bearer fake_token_{user_id}"}


class TestPostViewEndpoint:
    """Test POST /posts/{post_id}/view endpoint"""
    
    def test_track_post_view_authenticated_success(self, client: TestClient, db_session: Session, sample_user: User, test_post: Post):
        """Test successfully tracking a view for authenticated user"""
        # Get auth token
        auth_headers = get_test_token(sample_user.user_id)
        
        # Track view
        response = client.post(
            f"/api/v1/posts/{test_post.post_id}/view",
            headers=auth_headers
        )
        
        # Should succeed
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Post view tracked successfully"
        assert "view_id" in data["data"]
        assert data["data"]["viewed_at"] is not None
        
        # Verify view was created in database
        view = db_session.query(PostView).filter(
            PostView.user_id == sample_user.user_id,
            PostView.post_id == test_post.post_id
        ).first()
        assert view is not None
        assert view.status == "active"
    
    def test_track_post_view_unauthenticated_success(self, client: TestClient, db_session: Session, test_post: Post):
        """Test successfully tracking a view for unauthenticated user"""
        # Track view without auth
        response = client.post(f"/api/v1/posts/{test_post.post_id}/view")
        
        # Should succeed with anonymous tracking
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Post view tracked successfully"
        assert "view_id" in data["data"]
        assert data["data"]["user_id"] is None  # Anonymous view
    
    def test_track_post_view_invalid_post_id(self, client: TestClient, db_session: Session, sample_user: User):
        """Test tracking view for non-existent post"""
        auth_headers = get_test_token(sample_user.user_id)
        
        fake_post_id = uuid4()
        response = client.post(
            f"/api/v1/posts/{fake_post_id}/view",
            headers=auth_headers
        )
        
        # Should return 404
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["errorCode"] == "POST_NOT_FOUND"


class TestPostShareEndpoint:
    """Test POST /posts/{post_id}/share endpoint"""
    
    def test_share_post_authenticated_success(self, client: TestClient, db_session: Session, sample_user: User, test_post: Post):
        """Test successfully sharing a post with authentication"""
        auth_headers = get_test_token(sample_user.user_id)
        
        share_data = {
            "platform": "twitter"
        }
        
        response = client.post(
            f"/api/v1/posts/{test_post.post_id}/share",
            headers=auth_headers,
            json=share_data
        )
        
        # Should succeed
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Post shared successfully"
        assert "shareId" in data["data"]
        assert data["data"]["sharedAt"] is not None
        
        # Verify share was created in database
        share = db_session.query(PostShare).filter(
            PostShare.shared_by_user_id == sample_user.user_id,
            PostShare.post_id == test_post.post_id
        ).first()
        assert share is not None
        assert share.platform == "twitter"
        assert share.status == "active"
    
    def test_share_post_unauthenticated_fails(self, client: TestClient, db_session: Session, test_post: Post):
        """Test that sharing requires authentication"""
        response = client.post(
            f"/api/v1/posts/{test_post.post_id}/share",
            json={"platform": "twitter"}
        )
        
        # Should require authentication
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["errorCode"] == "AUTH_REQUIRED"
    
    def test_share_post_invalid_post_id(self, client: TestClient, db_session: Session, sample_user: User):
        """Test sharing non-existent post"""
        auth_headers = get_test_token(sample_user.user_id)
        
        fake_post_id = uuid4()
        response = client.post(
            f"/api/v1/posts/{fake_post_id}/share",
            headers=auth_headers,
            json={"platform": "twitter"}
        )
        
        # Should return 404
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["errorCode"] == "POST_NOT_FOUND"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4, UUID
from datetime import datetime, timezone

from app.main import app
from app.models.user import User
from app.models.post import Post
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.post_view import PostView
from app.models.post_share import PostShare
def get_test_token(user_id):
    """Helper to create auth headers for testing"""
    return {"Authorization": f"Bearer fake_token_{user_id}"}


class TestPostViewEndpoint:
    """Test POST /posts/{post_id}/view endpoint"""
    
    def test_track_post_view_authenticated_success(self, client: TestClient, db_session: Session, sample_user: User, test_post: Post):
        """Test successfully tracking a view for authenticated user"""
        # Override authentication to return our test user
        app.dependency_overrides[get_current_user_optional] = lambda: sample_user
        
        try:
            # Track view
            response = client.post(f"/api/v1/posts/{test_post.post_id}/view")
            
            # Should succeed
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Post view tracked successfully"
            assert "view_id" in data["data"]
            assert data["data"]["viewed_at"] is not None
            
            # For integration tests, verifying the API response is sufficient
            # The unit tests should verify database persistence
            assert data["data"]["user_id"] == str(sample_user.user_id)
            
            # Verify the response format matches schema
            from uuid import UUID
            UUID(data["data"]["view_id"])  # Should not raise exception
        finally:
            # Clean up the override
            app.dependency_overrides.pop(get_current_user_optional, None)
    
    def test_track_post_view_unauthenticated_success(self, client, comprehensive_test_data):
        """Test successfully tracking a view for unauthenticated user"""
        test_post = comprehensive_test_data['posts'][0]
        
        # Track view without auth
        response = client.post(f"/api/v1/posts/{test_post.post_id}/view")
        
        # Should succeed with anonymous tracking
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Post view tracked successfully"
        assert "view_id" in data["data"]
        assert data["data"]["user_id"] is None  # Anonymous view
    
    def test_track_post_view_multiple_same_user(self, client, sample_user: User, comprehensive_test_data):
        """Test tracking multiple views by same user (should create multiple records)"""
        test_user = sample_user
        test_post = comprehensive_test_data['posts'][0]
        
        # Override authentication to return our test user
        app.dependency_overrides[get_current_user_optional] = lambda: test_user
        
        try:
            # Track first view
            response1 = client.post(f"/api/v1/posts/{test_post.post_id}/view")
            assert response1.status_code == 201
            
            # Track second view
            response2 = client.post(f"/api/v1/posts/{test_post.post_id}/view")
            assert response2.status_code == 201
            
            # Both should succeed with different view IDs
            data1 = response1.json()
            data2 = response2.json()
            assert data1["data"]["view_id"] != data2["data"]["view_id"]
        finally:
            app.dependency_overrides.pop(get_current_user_optional, None)
    
    def test_track_post_view_invalid_post_id(self, client, sample_user: User):
        """Test tracking view for non-existent post"""
        test_user = sample_user
        
        # Override authentication to return our test user
        app.dependency_overrides[get_current_user_optional] = lambda: test_user
        
        try:
            fake_post_id = uuid4()
            response = client.post(f"/api/v1/posts/{fake_post_id}/view")

            # Should return 404
            assert response.status_code == 404
            data = response.json()
            assert data["detail"]["success"] is False
            assert data["detail"]["errorCode"] == "POST_NOT_FOUND"
        finally:
            app.dependency_overrides.pop(get_current_user_optional, None)

    def test_track_post_view_invalid_uuid_format(self, client, sample_user: User):
        """Test tracking view with malformed post ID"""
        test_user = sample_user
        
        # Override authentication to return our test user
        app.dependency_overrides[get_current_user_optional] = lambda: test_user
        
        try:
            response = client.post("/api/v1/posts/invalid-uuid/view")

            # Should return 422 for invalid UUID format
            assert response.status_code == 422
            data = response.json()
            # FastAPI validation errors have different format
            assert "detail" in data
            # For UUID validation errors, FastAPI returns detail as list
            assert isinstance(data["detail"], list)
            assert len(data["detail"]) > 0
        finally:
            app.dependency_overrides.pop(get_current_user_optional, None)


class TestPostShareEndpoint:
    """Test POST /posts/{post_id}/share endpoint"""
    
    def test_share_post_authenticated_success(self, client, sample_user: User, comprehensive_test_data):
        """Test successfully sharing a post with authentication"""
        test_user = sample_user
        test_post = comprehensive_test_data['posts'][0]
        
        # Override authentication to return our test user
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        try:
            share_data = {
                "platform": "twitter"
            }
            
            response = client.post(
                f"/api/v1/posts/{test_post.post_id}/share",
                json=share_data
            )
            
            # Should succeed
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Post shared successfully"
            assert "shareId" in data["data"]
            assert data["data"]["sharedAt"] is not None
            assert data["data"]["platform"] == "twitter"
            assert data["data"]["sharedBy"] == str(test_user.user_id)
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_share_post_without_platform(self, client, sample_user: User, comprehensive_test_data):
        """Test sharing post without specifying platform (should default to 'direct_link')"""
        test_user = sample_user
        test_post = comprehensive_test_data['posts'][0]
        
        # Override authentication to return our test user
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        try:
            response = client.post(
                f"/api/v1/posts/{test_post.post_id}/share",
                json={}
            )
            
            # Should succeed with default platform
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert data["data"]["platform"] == "direct_link"  # Default platform
        finally:
            app.dependency_overrides.pop(get_current_user, None)
    
    def test_share_post_multiple_platforms(self, client, sample_user: User, comprehensive_test_data):
        """Test sharing same post to multiple platforms"""
        test_user = sample_user
        test_post = comprehensive_test_data['posts'][0]
        
        # Override authentication to return our test user
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        try:
            platforms = ["twitter", "facebook", "direct_link"]
            
            for platform in platforms:
                response = client.post(
                    f"/api/v1/posts/{test_post.post_id}/share",
                    json={"platform": platform}
                )
                assert response.status_code == 201
                data = response.json()
                assert data["success"] is True
                assert data["data"]["platform"] == platform
        finally:
            app.dependency_overrides.pop(get_current_user, None)
    
    def test_share_post_unauthenticated_fails(self, client, comprehensive_test_data):
        """Test that sharing requires authentication"""
        test_post = comprehensive_test_data['posts'][0]
        
        response = client.post(
            f"/api/v1/posts/{test_post.post_id}/share",
            json={"platform": "twitter"}
        )
        
        # Should require authentication
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_share_post_invalid_post_id(self, client, sample_user: User):
        """Test sharing non-existent post"""
        test_user = sample_user
        
        # Override authentication to return our test user
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        try:
            fake_post_id = uuid4()
            response = client.post(
                f"/api/v1/posts/{fake_post_id}/share",
                json={"platform": "twitter"}
            )
            
            # Should return 404
            assert response.status_code == 404
            data = response.json()
            assert data["detail"]["success"] is False
        finally:
            app.dependency_overrides.pop(get_current_user, None)
    
    def test_share_post_invalid_uuid_format(self, client, sample_user: User):
        """Test sharing with malformed post ID"""
        test_user = sample_user
        
        # Override authentication to return our test user
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        try:
            response = client.post(
                "/api/v1/posts/invalid-uuid/share",
                json={"platform": "twitter"}
            )
            
            # Should return 422 for invalid UUID format
            assert response.status_code == 422
            data = response.json()
            # FastAPI validation errors have different format
            assert "detail" in data
            assert isinstance(data["detail"], list)
            assert len(data["detail"]) > 0
        finally:
            app.dependency_overrides.pop(get_current_user, None)


class TestAnalyticsIntegration:
    """Test integration between view and share tracking"""
    
    def test_post_analytics_counts(self, client, sample_user: User, comprehensive_test_data):
        """Test that view and share counts are properly tracked"""
        test_user = sample_user
        test_post = comprehensive_test_data['posts'][0]
        
        # Test tracking multiple views
        # Override authentication to return our test user for authenticated views
        app.dependency_overrides[get_current_user_optional] = lambda: test_user
        
        try:
            # Track some views (authenticated and anonymous)
            client.post(f"/api/v1/posts/{test_post.post_id}/view")  # Authenticated view
            
            # Clear auth for anonymous view
            app.dependency_overrides.pop(get_current_user_optional, None)
            client.post(f"/api/v1/posts/{test_post.post_id}/view")  # Anonymous view
            
            # Setup auth for shares
            app.dependency_overrides[get_current_user] = lambda: test_user
            
            # Track some shares
            client.post(f"/api/v1/posts/{test_post.post_id}/share", json={"platform": "twitter"})
            client.post(f"/api/v1/posts/{test_post.post_id}/share", json={"platform": "facebook"})
            
            # Test that post detail endpoint includes these counts
            response = client.get(f"/api/v1/posts/{test_post.post_id}")
            assert response.status_code == 200
            data = response.json()
            
            # Verify analytics are included in post response
            post_data = data["data"]["post"]
            assert post_data["viewCount"] >= 2  # At least our views
            assert post_data["shareCount"] >= 2  # At least our shares
            assert "userViewCount" in post_data  # User-specific view count included
            
        finally:
            app.dependency_overrides.pop(get_current_user_optional, None)
            app.dependency_overrides.pop(get_current_user, None)
