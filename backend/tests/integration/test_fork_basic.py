"""
Clean, simple fork tests following TDD principles.

Tests the core fork functionality to ensure our implementation works correctly.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.auth import get_current_user
from tests.fixtures.posts_fixtures import comprehensive_test_data


class TestForkFunctionality:
    """Basic fork functionality tests"""
    
    def test_fork_post_basic_success(self, client, comprehensive_test_data):
        """Test basic fork functionality works"""
        # Get test data
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        test_user = comprehensive_test_data["users"][0]
        
        # Override auth
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        try:
            # Make fork request
            response = client.post(
                f"/api/v1/posts/{test_post.post_id}/fork",
                json={"includeOriginalConversation": False}
            )
            
            # Verify response
            assert response.status_code == 200  # Fork endpoint returns 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            
            fork_data = data["data"]
            assert "conversationId" in fork_data
            assert "title" in fork_data
            assert fork_data["includeOriginalConversation"] is False
            
        finally:
            app.dependency_overrides.clear()
    
    def test_fork_post_with_original_conversation(self, client, comprehensive_test_data):
        """Test fork with original conversation inclusion"""
        # Get test data  
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        test_user = comprehensive_test_data["users"][0]
        
        # Override auth
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        try:
            # Make fork request with original conversation
            response = client.post(
                f"/api/v1/posts/{test_post.post_id}/fork",
                json={"includeOriginalConversation": True}
            )
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            fork_data = data["data"]
            assert "conversationId" in fork_data
            assert "title" in fork_data
            # Note: The actual value depends on conversation visibility
            assert "includeOriginalConversation" in fork_data
            
        finally:
            app.dependency_overrides.clear()
    
    def test_fork_post_default_behavior(self, client, comprehensive_test_data):
        """Test fork default behavior when no includeOriginalConversation specified"""
        # Get test data
        test_posts = comprehensive_test_data["posts"] 
        test_post = test_posts[0]
        test_user = comprehensive_test_data["users"][0]
        
        # Override auth
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        try:
            # Make fork request without specifying includeOriginalConversation
            response = client.post(
                f"/api/v1/posts/{test_post.post_id}/fork",
                json={}
            )
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            fork_data = data["data"]
            assert "conversationId" in fork_data
            assert "title" in fork_data
            # Should have some default value
            assert "includeOriginalConversation" in fork_data
            
        finally:
            app.dependency_overrides.clear()
    
    def test_fork_post_not_found(self, client, comprehensive_test_data):
        """Test fork request for non-existent post"""
        test_user = comprehensive_test_data["users"][0]
        
        # Override auth
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        try:
            # Try to fork non-existent post
            response = client.post(
                "/api/v1/posts/00000000-0000-0000-0000-000000000000/fork",
                json={"includeOriginalConversation": False}
            )
            
            # Should return 404
            assert response.status_code == 404
            
        finally:
            app.dependency_overrides.clear()
    
    def test_fork_post_unauthenticated(self, client, comprehensive_test_data):
        """Test fork request without authentication"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        # No auth override - should fail
        response = client.post(
            f"/api/v1/posts/{test_post.post_id}/fork",
            json={"includeOriginalConversation": False}
        )
        
        # Should return 401 or 403
        assert response.status_code in [401, 403]
