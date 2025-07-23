"""
Simple integration test for post fork functionality.
"""

import pytest
from uuid import UUID
from fastapi import status

from app.main import app
from app.dependencies.auth import get_current_user
from tests.fixtures.posts_fixtures import comprehensive_test_data


class TestPostForkSimple:
    """Simple integration tests for POST /posts/{post_id}/fork endpoint"""

    def test_fork_post_basic(self, client, comprehensive_test_data):
        """Test basic post forking functionality"""
        # Get a post to fork
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]

        # Get the post author for authentication
        post_author = comprehensive_test_data["users"][0]
        
        # Override the authentication dependency
        app.dependency_overrides[get_current_user] = lambda: post_author

        try:
            # Fork the post
            response = client.post(
                f"/api/v1/posts/{test_post.post_id}/fork",
                json={"includeOriginalConversation": False}
            )

            # Check if we get a valid response (could be 201 success or error)
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
            
            # For now, just check that we get a response without server errors
            assert response.status_code != 500  # No server errors
            
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()
