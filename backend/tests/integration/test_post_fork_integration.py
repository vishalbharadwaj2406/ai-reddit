"""
Integration Tests for POST /posts/{post_id}/fork API

Comprehensive test suite for the fork functionality - the core differentiator of our platform.
These tests cover the complete fork workflow including:
- Post forking with conversation creation
- Original post context inclusion
- Original conversation context inclusion (when public)
- Fork tracking and analytics
- Privacy controls and error handling
- Database relationships and data integrity

This is a critical feature that must be flawless - comprehensive testing required.
"""

import pytest
import uuid
from datetime import datetime, timezone
from fastapi import status

from app.main import app
from app.dependencies.auth import get_current_user
from tests.fixtures.posts_fixtures import comprehensive_test_data


class TestPostForkIntegration:
    """Integration tests for POST /posts/{post_id}/fork endpoint"""

    def test_fork_post_success_basic(self, client, comprehensive_test_data):
        """Test basic post forking without original conversation inclusion"""
        # Get a post to fork
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]

        # Get the post author for authentication
        post_author = comprehensive_test_data["users"][0]
        
        # Override the authentication dependency
        app.dependency_overrides[get_current_user] = lambda: post_author

        try:
            # Fork the post without including original conversation
            response = client.post(
                f"/api/v1/posts/{test_post.post_id}/fork",
                json={"includeOriginalConversation": False}
            )

            assert response.status_code == 201
            
            data = response.json()
            
            # Verify response structure
            assert data["success"] is True
            assert data["message"] == "Post forked successfully"
            assert data["errorCode"] is None
            assert "data" in data
            
            fork_data = data["data"]
            
            # Verify fork response data
            assert "conversationId" in fork_data
            assert "title" in fork_data
            assert "forkedFrom" in fork_data
            assert "includeOriginalConversation" in fork_data
            
            # Verify conversation details
            assert fork_data["forkedFrom"] == str(test_post.post_id)
            assert fork_data["title"] == f"Fork of: {test_post.title}"
            assert fork_data["includeOriginalConversation"] is False
            
            # Verify conversation was created with proper links
            conversation_id = fork_data["conversationId"]
            assert conversation_id is not None
            
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    def test_fork_post_with_original_conversation_inclusion(self, client, comprehensive_test_data):
        """Test forking with original conversation context included"""
        # Get a post with a public conversation
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]  # Assuming this has a public conversation
        
        # Get a different user to fork (not the original author)
        fork_user = comprehensive_test_data["users"][1]
        auth_headers = {"Authorization": f"Bearer fake_token_{fork_user.user_id}"}
        
        # Override the authentication dependency
        app.dependency_overrides[get_current_user] = lambda: fork_user
        
        try:
            # Fork the post with original conversation inclusion
            response = client.post(
                f"/api/v1/posts/{test_post.post_id}/fork",
                json={"includeOriginalConversation": True},
                headers=auth_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            
            # Verify response
            assert data["success"] is True
            fork_data = data["data"]
            assert fork_data["includeOriginalConversation"] is True
            
            # Verify conversation was created with original context
            conversation_id = fork_data["conversationId"]
            conversation_response = client.get(
                f"/api/v1/conversations/{conversation_id}",
                headers=auth_headers
            )
            assert conversation_response.status_code == 200
            
            # TODO: Verify that system prompt includes original conversation context
            # This will be validated when we implement the messaging with AI context
        finally:
            app.dependency_overrides.clear()

    def test_fork_post_default_include_original_if_public(self, client, comprehensive_test_data):
        """Test that original conversation is included by default if it's public"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        fork_user = comprehensive_test_data["users"][1]
        
        # Override the authentication dependency
        app.dependency_overrides[get_current_user] = lambda: fork_user
        
        try:
            # Fork without specifying includeOriginalConversation
            response = client.post(
                f"/api/v1/posts/{test_post.post_id}/fork",
                json={},  # Empty body - should default to true if conversation is public
            )
            
            assert response.status_code == 201
            data = response.json()
            
            fork_data = data["data"]
            
            # Should default to True if original conversation is public
            if test_post.is_conversation_visible:
                assert fork_data["includeOriginalConversation"] is True
            else:
                assert fork_data["includeOriginalConversation"] is False
        finally:
            app.dependency_overrides.clear()

    def test_fork_post_privacy_controls(self, client, comprehensive_test_data):
        """Test privacy controls - can't include private conversation context"""
        # TODO: Create a post with private conversation and test that
        # includeOriginalConversation gets forced to False
        pass

    def test_fork_tracking_and_analytics(self, client, comprehensive_test_data):
        """Test that fork actions are properly tracked for analytics"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        fork_user = comprehensive_test_data["users"][1]
        auth_headers = {"Authorization": f"Bearer fake_token_{fork_user.user_id}"}
        
        # Get initial fork count (should be 0)
        # TODO: Implement endpoint to get post analytics/fork count
        
        # Fork the post
        response = client.post(
            f"/api/v1/posts/{test_post.post_id}/fork",
            json={"includeOriginalConversation": False},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        
        # TODO: Verify fork count increased
        # TODO: Verify post_forks table has new record with correct data
        # - user_id = fork_user.user_id
        # - post_id = test_post.post_id
        # - conversation_id = new conversation id
        # - forked_at timestamp
        # - status = 'active'

    def test_fork_post_multiple_forks_by_same_user(self, client, comprehensive_test_data):
        """Test that same user can fork same post multiple times"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        fork_user = comprehensive_test_data["users"][1]
        auth_headers = {"Authorization": f"Bearer fake_token_{fork_user.user_id}"}
        
        # First fork
        response1 = client.post(
            f"/api/v1/posts/{test_post.post_id}/fork",
            json={"includeOriginalConversation": False},
            headers=auth_headers
        )
        assert response1.status_code == 201
        conversation_id_1 = response1.json()["data"]["conversationId"]
        
        # Second fork by same user
        response2 = client.post(
            f"/api/v1/posts/{test_post.post_id}/fork",
            json={"includeOriginalConversation": False},
            headers=auth_headers
        )
        assert response2.status_code == 201
        conversation_id_2 = response2.json()["data"]["conversationId"]
        
        # Should create different conversations
        assert conversation_id_1 != conversation_id_2

    def test_fork_own_post_allowed(self, client, comprehensive_test_data):
        """Test that users can fork their own posts"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        # Use the original post author
        post_author = comprehensive_test_data["users"][0]
        auth_headers = {"Authorization": f"Bearer fake_token_{post_author.user_id}"}
        
        response = client.post(
            f"/api/v1/posts/{test_post.post_id}/fork",
            json={"includeOriginalConversation": False},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_fork_post_not_found(self, client, comprehensive_test_data):
        """Test forking non-existent post returns 404"""
        fake_post_id = str(uuid.uuid4())
        
        fork_user = comprehensive_test_data["users"][0]
        auth_headers = {"Authorization": f"Bearer fake_token_{fork_user.user_id}"}
        
        response = client.post(
            f"/api/v1/posts/{fake_post_id}/fork",
            json={"includeOriginalConversation": False},
            headers=auth_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["errorCode"] == "POST_NOT_FOUND"
        assert "not found" in data["message"].lower()

    def test_fork_post_invalid_uuid(self, client, comprehensive_test_data):
        """Test forking with invalid UUID format returns 422"""
        fork_user = comprehensive_test_data["users"][0]
        auth_headers = {"Authorization": f"Bearer fake_token_{fork_user.user_id}"}
        
        response = client.post(
            "/api/v1/posts/invalid-uuid/fork",
            json={"includeOriginalConversation": False},
            headers=auth_headers
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["errorCode"] == "INVALID_POST_ID"
        assert "invalid" in data["message"].lower()

    def test_fork_post_unauthenticated(self, client, comprehensive_test_data):
        """Test forking without authentication returns 401"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        response = client.post(
            f"/api/v1/posts/{test_post.post_id}/fork",
            json={"includeOriginalConversation": False}
            # No auth headers
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["errorCode"] == "AUTH_REQUIRED"

    def test_fork_archived_post(self, client, comprehensive_test_data):
        """Test that archived/deleted posts cannot be forked"""
        # TODO: Create an archived post and test that fork returns appropriate error
        pass

    def test_fork_conversation_title_generation(self, client, comprehensive_test_data):
        """Test that forked conversation titles are generated correctly"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        fork_user = comprehensive_test_data["users"][1]
        auth_headers = {"Authorization": f"Bearer fake_token_{fork_user.user_id}"}
        
        response = client.post(
            f"/api/v1/posts/{test_post.post_id}/fork",
            json={"includeOriginalConversation": False},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        expected_title = f"Fork of: {test_post.title}"
        assert data["data"]["title"] == expected_title

    def test_fork_performance_multiple_concurrent_forks(self, client, comprehensive_test_data):
        """Test system performance under multiple concurrent fork requests"""
        # TODO: Implement concurrent fork testing to ensure database locks
        # and transaction handling work correctly
        pass


class TestPostForkErrorCases:
    """Test error cases and edge conditions for post forking"""

    def test_fork_with_invalid_request_body(self, client, comprehensive_test_data):
        """Test forking with invalid request body format"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        fork_user = comprehensive_test_data["users"][0]
        auth_headers = {"Authorization": f"Bearer fake_token_{fork_user.user_id}"}
        
        # Test with invalid includeOriginalConversation type
        response = client.post(
            f"/api/v1/posts/{test_post.post_id}/fork",
            json={"includeOriginalConversation": "invalid_boolean"},
            headers=auth_headers
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["errorCode"] == "INVALID_INPUT"

    def test_fork_database_error_handling(self, client, comprehensive_test_data):
        """Test proper error handling when database operations fail"""
        # TODO: Mock database failures and ensure proper error responses
        pass

    def test_fork_conversation_service_error_handling(self, client, comprehensive_test_data):
        """Test error handling when conversation creation fails"""
        # TODO: Mock conversation service failures
        pass


class TestPostForkAnalytics:
    """Test analytics and tracking functionality for post forks"""

    def test_fork_count_tracking(self, client, comprehensive_test_data):
        """Test that fork counts are tracked correctly"""
        # TODO: Implement fork count tracking tests
        pass

    def test_fork_history_tracking(self, client, comprehensive_test_data):
        """Test that complete fork history is maintained"""
        # TODO: Test that we can query:
        # - All forks of a specific post
        # - All posts a user has forked
        # - Fork relationship chains
        pass
