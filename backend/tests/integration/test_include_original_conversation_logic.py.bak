"""
Test for includeOriginalConversation Logic

Specific tests to verify the includeOriginalConversation logic we implemented works correctly
according to the user's MVP requirements.
"""

import pytest
from app.main import app
from app.dependencies.auth import get_current_user
from tests.fixtures.posts_fixtures import comprehensive_test_data


class TestIncludeOriginalConversationLogic:
    """Test the specific includeOriginalConversation logic implementation"""
    
    def test_explicit_false_respected(self, client, comprehensive_test_data):
        """Test that explicit includeOriginalConversation=false is respected regardless of defaults"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        test_user = comprehensive_test_data["users"][0]
        
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        try:
            # Explicit false should always be respected
            response = client.post(
                f"/api/v1/posts/{test_post.post_id}/fork",
                json={"includeOriginalConversation": False}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            fork_data = data["data"]
            # Should always be False when explicitly set to False
            assert fork_data["includeOriginalConversation"] is False
            
        finally:
            app.dependency_overrides.clear()
    
    def test_explicit_true_handled_correctly(self, client, comprehensive_test_data):
        """Test that explicit includeOriginalConversation=true is handled according to privacy settings"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        test_user = comprehensive_test_data["users"][0]
        
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        try:
            # Explicit true - outcome depends on conversation existence and privacy
            response = client.post(
                f"/api/v1/posts/{test_post.post_id}/fork",
                json={"includeOriginalConversation": True}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            fork_data = data["data"]
            # Value depends on whether conversation exists and is public
            # But the request should succeed either way
            assert "includeOriginalConversation" in fork_data
            assert isinstance(fork_data["includeOriginalConversation"], bool)
            
        finally:
            app.dependency_overrides.clear()
    
    def test_default_behavior_when_not_specified(self, client, comprehensive_test_data):
        """Test default behavior when includeOriginalConversation is not specified"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        test_user = comprehensive_test_data["users"][0]
        
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        try:
            # No includeOriginalConversation specified
            response = client.post(
                f"/api/v1/posts/{test_post.post_id}/fork",
                json={}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            fork_data = data["data"]
            # Should default based on conversation availability and privacy
            assert "includeOriginalConversation" in fork_data
            assert isinstance(fork_data["includeOriginalConversation"], bool)
            
        finally:
            app.dependency_overrides.clear()
    
    def test_response_structure_consistency(self, client, comprehensive_test_data):
        """Test that response structure is consistent regardless of includeOriginalConversation value"""
        test_posts = comprehensive_test_data["posts"]
        test_post_1 = test_posts[0]
        test_post_2 = test_posts[1] if len(test_posts) > 1 else test_posts[0]  # Use different posts to avoid duplicate fork
        test_user = comprehensive_test_data["users"][0]
        
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        try:
            # Test with False on first post
            response_false = client.post(
                f"/api/v1/posts/{test_post_1.post_id}/fork",
                json={"includeOriginalConversation": False}
            )
            
            # Test with True on second post (or same post after delay if only one)
            if test_post_1 == test_post_2:
                import time
                time.sleep(0.01)  # Small delay to avoid duplicate fork constraint
            
            response_true = client.post(
                f"/api/v1/posts/{test_post_2.post_id}/fork",
                json={"includeOriginalConversation": True}
            )
            
            # Both should succeed
            assert response_false.status_code == 200
            assert response_true.status_code == 200
            
            data_false = response_false.json()
            data_true = response_true.json()
            
            # Both should have same structure
            expected_keys = {"conversationId", "title", "forkedFrom", "includeOriginalConversation"}
            
            assert set(data_false["data"].keys()) == expected_keys
            assert set(data_true["data"].keys()) == expected_keys
            
            # Values should be consistent with request
            assert data_false["data"]["includeOriginalConversation"] is False
            # data_true value depends on privacy settings but should be boolean
            assert isinstance(data_true["data"]["includeOriginalConversation"], bool)
            
        finally:
            app.dependency_overrides.clear()
            
    def test_fork_title_generation(self, client, comprehensive_test_data):
        """Test that fork titles are generated correctly"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        test_user = comprehensive_test_data["users"][0]
        
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        try:
            response = client.post(
                f"/api/v1/posts/{test_post.post_id}/fork",
                json={"includeOriginalConversation": False}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            fork_data = data["data"]
            # Title should contain "Fork of:" prefix
            assert "Fork of:" in fork_data["title"]
            assert test_post.title in fork_data["title"]
            
        finally:
            app.dependency_overrides.clear()
