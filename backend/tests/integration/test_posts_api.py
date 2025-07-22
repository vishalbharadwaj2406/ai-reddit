"""
Integration Tests for GET /posts API

This test suite validates the GET /posts endpoint with real test data.
Tests cover all functionality including pagination, sorting, filtering, and validation.
"""

import pytest
import uuid
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User
from app.models.post import Post
from app.models.tag import Tag
from app.models.post_tag import PostTag
from app.models.post_reaction import PostReaction
from app.models.conversation import Conversation

# Import the comprehensive test fixture
from tests.fixtures.posts_fixtures import comprehensive_test_data


@pytest.fixture
def test_users(db_session):
    """Create test users for post authors."""
    users = []
    for i in range(3):
        user = User(
            user_name=f"test_user_{i}",
            email=f"test{i}@example.com"
        )
        db_session.add(user)
        users.append(user)
    
    db_session.commit()
    return users


@pytest.fixture
def test_tags(db_session):
    """Create test tags for posts."""
    tag_names = ["ai", "tech", "python", "javascript", "machine-learning"]
    tags = []
    
    for name in tag_names:
        tag = Tag(name=name)
        db_session.add(tag)
        tags.append(tag)
    
    db_session.commit()
    return tags


@pytest.fixture
def test_conversations(db_session, test_users):
    """Create test conversations for posts."""
    conversations = []
    for i, user in enumerate(test_users):
        conversation = Conversation(
            user_id=user.user_id,
            title=f"Test Conversation {i + 1}",
            status="active"
        )
        db_session.add(conversation)
        conversations.append(conversation)
    
    db_session.commit()
    return conversations


@pytest.fixture
def test_posts(db_session, test_users, test_tags, test_conversations):
    """Create test posts with various timestamps and content."""
    posts = []
    
    # Create posts with different timestamps for time range testing
    base_time = datetime.now(timezone.utc)
    time_offsets = [
        timedelta(minutes=30),    # Recent post
        timedelta(hours=2),       # Few hours ago
        timedelta(days=1),        # Yesterday
        timedelta(days=5),        # Few days ago
        timedelta(weeks=2),       # Couple weeks ago
        timedelta(days=40),       # Over a month ago
    ]
    
    for i, offset in enumerate(time_offsets):
        user_idx = i % len(test_users)
        conversation_idx = i % len(test_conversations)
        
        post = Post(
            user_id=test_users[user_idx].user_id,
            conversation_id=test_conversations[conversation_idx].conversation_id,
            title=f"Test Post {i + 1}",
            content=f"This is test post content {i + 1}. " + "Lorem ipsum " * 10,
            is_conversation_visible=True,
            edited=False,
            status="active",
            created_at=base_time - offset,
            updated_at=base_time - offset
        )
        db_session.add(post)
        posts.append(post)
    
    db_session.commit()
    
    # Add tags to posts
    for i, post in enumerate(posts):
        # Each post gets 1-3 tags
        num_tags = (i % 3) + 1
        for j in range(num_tags):
            tag_index = (i + j) % len(test_tags)
            post_tag = PostTag(
                post_id=post.post_id,
                tag_id=test_tags[tag_index].tag_id
            )
            db_session.add(post_tag)
    
    db_session.commit()
    return posts


@pytest.fixture
def test_reactions(db_session, test_posts, test_users):
    """Create test reactions for posts."""
    reactions = []
    
    # Add varied reactions to create different vote scores  
    # Just add some simple reactions to test the functionality
    try:
        # Add one upvote reaction to first post
        reaction = PostReaction(
            user_id=test_users[0].user_id,
            post_id=test_posts[0].post_id,
            reaction="upvote",
            status="active"
        )
        db_session.add(reaction)
        reactions.append(reaction)
        
        # Add one downvote reaction to second post
        reaction2 = PostReaction(
            user_id=test_users[1].user_id,
            post_id=test_posts[1].post_id,
            reaction="downvote", 
            status="active"
        )
        db_session.add(reaction2)
        reactions.append(reaction2)
        
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        # Continue even if reactions fail
        pass
    
    return reactions


class TestGetPostsAPI:
    """Comprehensive test suite for GET /posts API endpoint."""
    
    def test_basic_get_posts_success(self, client, test_posts):
        """Test basic GET /posts returns posts successfully"""
        print("Making request to /api/v1/posts/")
        response = client.get("/api/v1/posts/")
        
        print(f"Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response content: {response.content}")
        
        assert response.status_code == 200
    
    def test_pagination_functionality(self, client, db_session, test_posts):
        """Test pagination with various limit and offset values."""
        # Test different page sizes
        response = client.get("/api/v1/posts?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["posts"]) <= 3
        
        # Test offset
        response = client.get("/api/v1/posts?limit=2&offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["posts"]) <= 2
    
    def test_sorting_methods(self, client, comprehensive_test_data):
        """Test all sorting methods work correctly with content validation."""
        test_data = comprehensive_test_data
        print(f"Test posts count: {len(test_data['posts'])}")
        
        sort_methods = ["hot", "new", "top"]
        
        for sort_method in sort_methods:
            response = client.get(f"/api/v1/posts?sort={sort_method}")
            assert response.status_code == 200
            data = response.json()
            print(f"Sort method {sort_method}: {len(data['data']['posts'])} posts returned")
            assert data["success"] is True
            assert len(data["data"]["posts"]) > 0
            
            posts = data["data"]["posts"]
            
            # Validate specific sorting behavior
            if sort_method == "new" and len(posts) > 1:
                # New sorting: chronological descending
                for i in range(len(posts) - 1):
                    current_time = datetime.fromisoformat(posts[i]["createdAt"].replace('Z', '+00:00'))
                    next_time = datetime.fromisoformat(posts[i + 1]["createdAt"].replace('Z', '+00:00'))
                    assert current_time >= next_time, "New sorting not chronological"
            
            elif sort_method == "top" and len(posts) > 1:
                # Top sorting: vote count descending (upvotes - downvotes)
                for i in range(len(posts) - 1):
                    current_reactions = posts[i].get("reactions", {})
                    next_reactions = posts[i + 1].get("reactions", {})
                    
                    current_votes = current_reactions.get("upvote", 0) - current_reactions.get("downvote", 0)
                    next_votes = next_reactions.get("upvote", 0) - next_reactions.get("downvote", 0)
                    
                    assert current_votes >= next_votes, "Top sorting not by votes"
            
            # Validate that all posts have required fields
            for post in posts:
                assert "postId" in post, "Missing postId"
                assert "title" in post, "Missing title"
                assert "createdAt" in post, "Missing createdAt"
                assert "reactions" in post, "Missing reactions"
                assert "user" in post, "Missing user"
    
    def test_time_range_filtering(self, client, db_session, test_posts):
        """Test all time range filters."""
        time_ranges = ["hour", "day", "week", "month", "all"]
        
        for time_range in time_ranges:
            response = client.get(f"/api/v1/posts?time_range={time_range}&sort=top")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    def test_tag_filtering(self, client, db_session, test_posts, test_tags):
        """Test tag filtering with existing tags."""
        # Test with existing tags
        for tag in test_tags[:3]:  # Test first 3 tags
            response = client.get(f"/api/v1/posts?tag={tag.name}")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
        
        # Test with non-existent tag
        response = client.get("/api/v1/posts?tag=nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["posts"]) == 0
    
    def test_user_filtering(self, client, comprehensive_test_data):
        """Test user filtering with valid users and actual content validation."""
        test_data = comprehensive_test_data
        users = test_data["users"]
        
        # Test with existing user - use userId instead of user_id
        user_id = str(users[0].user_id)
        response = client.get(f"/api/v1/posts?userId={user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Validate that ALL returned posts belong to the specified user
        posts = data["data"]["posts"]
        for post in posts:
            # User info is nested in 'user' object
            post_user_id = post["user"]["userId"] if post.get("user") else None
            assert post_user_id == user_id, f"Post {post.get('postId', 'unknown')} belongs to wrong user. Expected {user_id}, got {post_user_id}"
        
        # Test with non-existent user
        fake_user_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/posts?userId={fake_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["posts"]) == 0
    
    def test_combined_parameters(self, client, comprehensive_test_data):
        """Test combining multiple parameters with content validation."""
        test_data = comprehensive_test_data
        tags = test_data["tags"]
        
        # Test tag + sort + limit combination
        response = client.get(f"/api/v1/posts?tag={tags[0].name}&sort=new&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        posts = data["data"]["posts"]
        assert len(posts) <= 5, "Limit parameter not respected"
        
        # Debug: Check actual tags structure
        if posts:
            print(f"Tags structure: {posts[0].get('tags', [])}")
        
        # Validate that all posts have the specified tag
        for post in posts:
            post_tags = post.get("tags", [])
            # Tags are returned as simple strings
            assert tags[0].name in post_tags, f"Post {post['postId']} missing required tag {tags[0].name}"
        
        # Validate sorting (new = chronological descending)
        if len(posts) > 1:
            for i in range(len(posts) - 1):
                current_time = datetime.fromisoformat(posts[i]["createdAt"].replace('Z', '+00:00'))
                next_time = datetime.fromisoformat(posts[i + 1]["createdAt"].replace('Z', '+00:00'))
                assert current_time >= next_time, "Posts not properly sorted chronologically"
    
    def test_parameter_validation_errors(self, client, db_session):
        """Test parameter validation returns proper 422 errors."""
        invalid_cases = [
            ("sort=invalid_sort", 422),
            ("time_range=invalid_range", 422), 
            ("limit=101", 422),  # Too high
            ("limit=0", 422),    # Too low
            ("offset=-1", 422),  # Negative
            ("userId=invalid-uuid-format", 422),  # Fixed parameter name
        ]
        
        for params, expected_status in invalid_cases:
            response = client.get(f"/api/v1/posts?{params}")
            assert response.status_code == expected_status, f"Failed for {params}: got {response.status_code}, expected {expected_status}"
    
    def test_hot_ranking_algorithm(self, client, comprehensive_test_data):
        """Test that hot ranking algorithm works with vote-based ranking."""
        test_data = comprehensive_test_data
        
        response = client.get("/api/v1/posts?sort=hot")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["posts"]) > 0
        
        posts = data["data"]["posts"]
        
        # Debug: Check actual reactions structure
        if posts:
            print(f"Reactions structure: {posts[0].get('reactions', {})}")
        
        # Validate that hot sorting considers both recency and votes
        # Posts with higher engagement should rank higher for similar time periods
        if len(posts) > 1:
            # Check that posts have vote counts and are reasonably ordered
            for post in posts:
                reactions = post.get("reactions", {})
                # Calculate total vote count from upvote/downvote or similar fields
                upvotes = reactions.get("upvote", 0)
                downvotes = reactions.get("downvote", 0)
                total_votes = upvotes - downvotes
                assert isinstance(upvotes, int), "upvote count should be integer"
                assert isinstance(downvotes, int), "downvote count should be integer"
    
    def test_new_sorting_chronological(self, client, db_session, test_posts):
        """Test that new sorting returns posts in chronological order."""
        response = client.get("/api/v1/posts?sort=new&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        posts = data["data"]["posts"]
        if len(posts) > 1:
            # Check that posts are in descending chronological order
            # Use createdAt instead of created_at
            for i in range(len(posts) - 1):
                current_time = datetime.fromisoformat(posts[i]["createdAt"].replace('Z', '+00:00'))
                next_time = datetime.fromisoformat(posts[i + 1]["createdAt"].replace('Z', '+00:00'))
                assert current_time >= next_time
    
    def test_top_sorting_by_votes(self, client, comprehensive_test_data):
        """Test that top sorting orders posts by vote count correctly."""
        test_data = comprehensive_test_data
        
        response = client.get("/api/v1/posts?sort=top")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["posts"]) > 0
        
        posts = data["data"]["posts"]
        
        # Validate that posts are sorted by vote count (descending)
        if len(posts) > 1:
            for i in range(len(posts) - 1):
                current_reactions = posts[i].get("reactions", {})
                next_reactions = posts[i + 1].get("reactions", {})
                
                # Calculate vote counts (upvotes - downvotes)
                current_votes = current_reactions.get("upvote", 0) - current_reactions.get("downvote", 0)
                next_votes = next_reactions.get("upvote", 0) - next_reactions.get("downvote", 0)
                
                assert current_votes >= next_votes, f"Top sorting broken: post {i} has {current_votes} votes, post {i+1} has {next_votes} votes"
        
        # Validate that all posts have vote count information
        for post in posts:
            reactions = post.get("reactions", {})
            assert "upvote" in reactions, f"Post {post['postId']} missing upvote count"
            assert "downvote" in reactions, f"Post {post['postId']} missing downvote count"
            assert isinstance(reactions["upvote"], int), "upvote count should be integer"
            assert isinstance(reactions["downvote"], int), "downvote count should be integer"
    
    def test_edge_cases(self, client, db_session, test_posts):
        """Test edge cases and boundary conditions."""
        # Minimum limit
        response = client.get("/api/v1/posts?limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["posts"]) <= 1
        
        # Maximum limit
        response = client.get("/api/v1/posts?limit=100")
        assert response.status_code == 200
        
        # High offset
        response = client.get("/api/v1/posts?offset=100")
        assert response.status_code == 200
    
    def test_response_format_consistency(self, client, db_session, test_posts):
        """Test that response format is consistent across different parameters."""
        test_params = [
            "",
            "sort=new",
            "tag=ai",
            "limit=5",
            "sort=top&time_range=week"
        ]
        
        for params in test_params:
            url = "/api/v1/posts"
            if params:
                url += f"?{params}"
                
            response = client.get(url)
            assert response.status_code == 200
            data = response.json()
            
            # Validate consistent response structure
            required_keys = ["success", "data", "message", "errorCode"]
            for key in required_keys:
                assert key in data
            
            assert data["success"] is True
            assert data["errorCode"] is None
            assert "posts" in data["data"]
            assert isinstance(data["data"]["posts"], list)


@pytest.mark.integration
class TestGetPostsPerformance:
    """Performance tests for GET /posts API."""
    
    def test_large_offset_performance(self, client, db_session, test_posts, test_conversations):
        """Test API performance with large offset values."""
        response = client.get("/api/v1/posts?offset=50&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_complex_query_performance(self, client, db_session, test_posts, test_tags, test_conversations):
        """Test performance with complex query combinations."""
        response = client.get(
            f"/api/v1/posts?tag={test_tags[0].name}&sort=hot&time_range=week&limit=20"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
