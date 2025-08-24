"""
Integration Tests for GET /posts/{post_id} API

Test-Driven Development for the individual post retrieval endpoint.
These tests will fail initially (TDD Red phase) until we implement the endpoint.

Tests cover:
- Basic post retrieval with full details
- Post with comments and nested replies
- Post with reactions and vote counts
- Post with tags and user information
- Error cases: not found, invalid UUID, etc.
"""

import pytest
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import status

from tests.fixtures.posts_fixtures import comprehensive_test_data


class TestGetPostByIdAPI:
    """Integration tests for GET /posts/{post_id} endpoint"""

    def test_get_post_by_id_success_basic(self, client, comprehensive_test_data):
        """Test retrieving a basic post by ID with all details"""
        # Get the first post from our test data
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        response = client.get(f"/api/v1/posts/{test_post.post_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data["success"] is True
        assert data["message"] == "Post retrieved successfully"
        assert data["errorCode"] is None
        assert "data" in data
        assert "post" in data["data"]
        
        post = data["data"]["post"]
        
        # Verify post basic fields
        assert post["post_id"] == str(test_post.post_id)
        assert post["title"] == test_post.title
        assert post["content"] == test_post.content
        assert post["status"] == test_post.status
        assert post["is_conversation_visible"] == test_post.is_conversation_visible
        
        # Verify timestamps
        assert "created_at" in post
        assert "updated_at" in post
        
        # Verify user information
        assert "user" in post
        user_info = post["user"]
        assert "user_id" in user_info
        assert "user_name" in user_info
        assert "profile_picture" in user_info
        
        # Verify tags
        assert "tags" in post
        assert isinstance(post["tags"], list)
        
        # Verify reactions
        assert "reactions" in post
        reactions = post["reactions"]
        assert "upvote" in reactions
        assert "downvote" in reactions
        assert "heart" in reactions
        assert "insightful" in reactions
        assert "accurate" in reactions
        
        # Verify vote count
        assert "vote_count" in post
        assert isinstance(post["vote_count"], int)
        
        # Verify comments
        assert "comments" in post
        assert isinstance(post["comments"], list)
        
        # Verify analytics fields (NEW)
        assert "viewCount" in post
        assert isinstance(post["viewCount"], int)
        assert post["viewCount"] >= 0
        
        assert "shareCount" in post  
        assert isinstance(post["shareCount"], int)
        assert post["shareCount"] >= 0
        
        assert "userViewCount" in post
        assert isinstance(post["userViewCount"], int)
        assert post["userViewCount"] >= 0

    def test_get_post_by_id_with_comments(self, client, comprehensive_test_data):
        """Test retrieving a post that has comments with proper nesting"""
        # Find a post that should have comments based on our test data
        test_posts = comprehensive_test_data["posts"] 
        test_post = test_posts[1]  # Use second post
        
        response = client.get(f"/api/v1/posts/{test_post.post_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        post = data["data"]["post"]
        comments = post["comments"]
        
        # Verify comments structure
        for comment in comments:
            assert "comment_id" in comment
            assert "content" in comment
            assert "created_at" in comment
            assert "user" in comment
            assert "reactions" in comment
            assert "vote_count" in comment
            assert "replies" in comment  # Nested replies
            
            # Verify comment user info
            comment_user = comment["user"]
            assert "user_id" in comment_user
            assert "user_name" in comment_user
            
            # Check nested replies structure
            for reply in comment["replies"]:
                assert "comment_id" in reply
                assert "content" in reply
                assert "parent_comment_id" in reply
                assert "user" in reply

    def test_get_post_by_id_with_reactions_count(self, client, comprehensive_test_data):
        """Test that post reactions are properly counted and displayed"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[2]  # Use third post which should have reactions
        
        response = client.get(f"/api/v1/posts/{test_post.post_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        post = data["data"]["post"]
        reactions = post["reactions"]
        
        # Verify reaction counts are integers and make sense
        assert isinstance(reactions["upvote"], int)
        assert isinstance(reactions["downvote"], int)
        assert isinstance(reactions["heart"], int)
        assert isinstance(reactions["insightful"], int)
        assert isinstance(reactions["accurate"], int)
        
        # Verify vote count calculation
        expected_vote_count = reactions["upvote"] - reactions["downvote"]
        assert post["vote_count"] == expected_vote_count
        
        # Ensure non-negative reaction counts
        for reaction_type, count in reactions.items():
            assert count >= 0

    def test_get_post_by_id_with_tags(self, client, comprehensive_test_data):
        """Test that post tags are properly included"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        response = client.get(f"/api/v1/posts/{test_post.post_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        post = data["data"]["post"]
        tags = post["tags"]
        
        # Verify tags structure
        for tag in tags:
            assert "tag_id" in tag
            assert "name" in tag
            assert isinstance(tag["name"], str)
            assert len(tag["name"]) > 0

    def test_get_post_by_id_conversation_link(self, client, comprehensive_test_data):
        """Test that conversation information is included when visible"""
        test_posts = comprehensive_test_data["posts"]
        # Find a post with conversation visible
        test_post = None
        for post in test_posts:
            if post.is_conversation_visible:
                test_post = post
                break
        
        assert test_post is not None, "Need a post with visible conversation for this test"
        
        response = client.get(f"/api/v1/posts/{test_post.post_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        post = data["data"]["post"]
        
        # Verify conversation information
        assert "conversation_id" in post
        if post["conversation_id"]:
            assert "conversation" in post
            conversation = post["conversation"]
            assert "conversation_id" in conversation
            assert "title" in conversation
            assert "created_at" in conversation

    def test_get_post_by_id_not_found(self, client, comprehensive_test_data):
        """Test retrieving a post that doesn't exist"""
        non_existent_id = str(uuid.uuid4())
        
        response = client.get(f"/api/v1/posts/{non_existent_id}")
        
        assert response.status_code == 404
        data = response.json()
        
        # FastAPI wraps HTTPException detail in "detail" field
        detail = data["detail"]
        assert detail["success"] is False
        assert "not found" in detail["message"].lower()
        assert detail["errorCode"] == "POST_NOT_FOUND"

    def test_get_post_by_id_invalid_uuid(self, client, comprehensive_test_data):
        """Test retrieving a post with invalid UUID format"""
        invalid_id = "not-a-uuid"
        
        response = client.get(f"/api/v1/posts/{invalid_id}")
        
        assert response.status_code == 422
        data = response.json()
        
        # FastAPI wraps HTTPException detail in "detail" field
        detail = data["detail"]
        assert detail["success"] is False
        assert "invalid" in detail["message"].lower()
        assert detail["errorCode"] == "INVALID_POST_ID"

    def test_get_post_by_id_deleted_post(self, client, comprehensive_test_data):
        """Test retrieving a post that has been deleted/archived"""
        # We'll need to create a deleted post for this test
        # For now, let's test the basic structure
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        # First verify the post exists
        response = client.get(f"/api/v1/posts/{test_post.post_id}")
        assert response.status_code == 200
        
        # TODO: Once we implement post deletion, we'll update this test
        # to actually delete the post and then test retrieval

    def test_get_post_by_id_performance(self, client, comprehensive_test_data):
        """Test that post retrieval is reasonably fast even with complex data"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        import time
        start_time = time.time()
        
        response = client.get(f"/api/v1/posts/{test_post.post_id}")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Should respond within 1 second for individual post
        assert response_time < 1.0
        assert response.status_code == 200

    def test_get_post_by_id_response_consistency(self, client, comprehensive_test_data):
        """Test that multiple requests for the same post return consistent data"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        # Make multiple requests
        response1 = client.get(f"/api/v1/posts/{test_post.post_id}")
        response2 = client.get(f"/api/v1/posts/{test_post.post_id}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Core post data should be identical
        post1 = data1["data"]["post"]
        post2 = data2["data"]["post"]
        
        assert post1["post_id"] == post2["post_id"]
        assert post1["title"] == post2["title"]
        assert post1["content"] == post2["content"]
        assert post1["created_at"] == post2["created_at"]


class TestGetPostByIdEdgeCases:
    """Edge cases and boundary conditions for GET /posts/{post_id}"""

    def test_get_post_empty_content(self, client, comprehensive_test_data):
        """Test retrieving a post with minimal content"""
        # This will test how the endpoint handles edge cases in data
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[-1]  # Use last post which might have minimal data
        
        response = client.get(f"/api/v1/posts/{test_post.post_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        post = data["data"]["post"]
        
        # Even minimal posts should have required fields
        assert "post_id" in post
        assert "title" in post
        assert "content" in post
        assert "user" in post
        assert "created_at" in post

    def test_get_post_long_content(self, client, comprehensive_test_data):
        """Test retrieving a post with very long content"""
        # Find a post with substantial content
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[3]  # Use fourth post
        
        response = client.get(f"/api/v1/posts/{test_post.post_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        post = data["data"]["post"]
        
        # Verify content is returned completely without truncation
        assert len(post["content"]) > 0
        assert post["content"] == test_post.content

    def test_get_post_special_characters(self, client, comprehensive_test_data):
        """Test retrieving posts with special characters in content"""
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        
        response = client.get(f"/api/v1/posts/{test_post.post_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should handle JSON serialization properly
        post = data["data"]["post"]
        assert isinstance(post["title"], str)
        assert isinstance(post["content"], str)

    def test_get_post_by_id_analytics_counts_integration(self, client, comprehensive_test_data, db_session):
        """Test that analytics counts are calculated correctly"""
        from app.models.post_view import PostView
        from app.models.post_share import PostShare
        
        # Get test data
        test_posts = comprehensive_test_data["posts"]
        test_post = test_posts[0]
        test_users = comprehensive_test_data["users"]
        test_user = test_users[0]
        
        # Add some views and shares directly to database
        # Add 3 views (2 authenticated, 1 anonymous)
        view1 = PostView(post_id=test_post.post_id, user_id=test_user.user_id)
        view2 = PostView(post_id=test_post.post_id, user_id=test_users[1].user_id)
        view3 = PostView(post_id=test_post.post_id, user_id=None)  # Anonymous
        db_session.add_all([view1, view2, view3])
        
        # Add 2 shares
        share1 = PostShare(post_id=test_post.post_id, shared_by_user_id=test_user.user_id, platform="twitter")
        share2 = PostShare(post_id=test_post.post_id, shared_by_user_id=test_users[1].user_id, platform="facebook")
        db_session.add_all([share1, share2])
        db_session.commit()
        
        # Test with authenticated user (should see their own view count)
        response = client.get(f"/api/v1/posts/{test_post.post_id}")
        
        assert response.status_code == 200
        data = response.json()
        post = data["data"]["post"]
        
        # Verify analytics counts
        assert post["viewCount"] == 3  # Total views (2 authenticated + 1 anonymous)
        assert post["shareCount"] == 2  # Total shares
        assert post["userViewCount"] == 0  # Current user's views (auth not properly mocked in this test)
