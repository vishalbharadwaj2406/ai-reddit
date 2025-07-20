"""
Test cases for GET /posts API endpoint

Tests the public posts feed with various filtering, sorting, and pagination options.
Covers hot ranking algorithm, tag filtering, user filtering, and proper response formatting.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.post import Post
from app.models.tag import Tag
from app.models.post_tag import PostTag
from app.models.post_reaction import PostReaction
from app.models.comment import Comment
from app.models.post_view import PostView
from app.core.database import get_db


@pytest.fixture
def client():
    """Test client with mocked dependencies"""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock(spec=Session)


@pytest.fixture
def sample_users():
    """Sample users for testing"""
    users = []
    user_ids = [uuid4(), uuid4(), uuid4()]
    
    for i, (name, email) in enumerate([
        ("alice", "alice@example.com"),
        ("bob", "bob@example.com"), 
        ("charlie", "charlie@example.com")
    ]):
        user = Mock()
        user.user_id = user_ids[i]
        user.user_name = name
        user.email = email
        user.profile_picture = f"https://example.com/{name}.jpg" if name != "charlie" else None
        user.created_at = datetime.now() - timedelta(days=30-i*10)
        users.append(user)
    
    return users


@pytest.fixture
def sample_tags():
    """Sample tags for testing"""
    tags = []
    for name in ["python", "machine-learning", "web-development", "ai"]:
        tag = Mock()
        tag.tag_id = uuid4()
        tag.name = name
        tag.created_at = datetime.now()
        tags.append(tag)
    return tags


@pytest.fixture
def sample_posts(sample_users, sample_tags):
    """Sample posts with various characteristics for testing ranking"""
    now = datetime.now()
    posts = []
    
    post_data = [
        ("Amazing AI Breakthrough", "This is a groundbreaking discovery in AI...", 0, 2, True),
        ("Getting Started with Python", "Here's how to begin your Python journey...", 1, 0.5/60, False),
        ("Complete Web Development Guide", "Everything you need to know about web dev...", 2, 48, True),
        ("Understanding Machine Learning", "ML concepts explained simply...", 0, 12, True)
    ]
    
    for i, (title, content, user_idx, hours_ago, conversation_visible) in enumerate(post_data):
        post = Mock()
        post.post_id = uuid4()
        post.title = title
        post.content = content
        post.user_id = sample_users[user_idx].user_id
        post.created_at = now - timedelta(hours=hours_ago)
        post.updated_at = post.created_at
        post.is_conversation_visible = conversation_visible
        post.user = sample_users[user_idx]  # Add user reference for easier access
        posts.append(post)
    
    return posts


class TestGetPostsFeed:
    """Test class for GET /posts endpoint"""

    def test_get_posts_default_parameters_success(self, client, mock_db, sample_posts, sample_users):
        """Test GET /posts with default parameters returns hot-sorted posts"""
        
        # Mock database queries
        mock_db.query.return_value.join.return_value.outerjoin.return_value.group_by.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = sample_posts[:2]
        
        # Override database dependency
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.get("/api/v1/posts/")
            
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert data["success"] is True
            assert "data" in data
            assert "posts" in data["data"]
            assert data["message"] == "Posts retrieved successfully"
            assert data["errorCode"] is None
            
            # Check posts array
            posts = data["data"]["posts"]
            assert len(posts) == 2
            
            # Check first post structure
            post = posts[0]
            assert "postId" in post
            assert "title" in post
            assert "content" in post
            assert "createdAt" in post
            assert "user" in post
            assert "tags" in post
            assert "reactions" in post
            assert "userReaction" in post
            assert "commentCount" in post
            assert "viewCount" in post
            assert "userViewCount" in post
            assert "conversationId" in post
            
            # Check user structure
            user = post["user"]
            assert "userId" in user
            assert "userName" in user
            assert "profilePicture" in user
            
            # Check reactions structure
            reactions = post["reactions"]
            assert "upvote" in reactions
            assert "downvote" in reactions
            assert "heart" in reactions
            assert "insightful" in reactions
            assert "accurate" in reactions
            
        finally:
            app.dependency_overrides.clear()

    def test_get_posts_with_hot_sorting(self, client, mock_db, sample_posts):
        """Test GET /posts with hot sorting returns posts ranked by hot algorithm"""
        
        # Mock the ranking calculation - hot post should come first
        mock_db.query.return_value.join.return_value.outerjoin.return_value.group_by.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            sample_posts[0],  # Hot post with high score
            sample_posts[3],  # Moderate post
            sample_posts[1]   # New post with low score
        ]
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.get("/api/v1/posts/?sort=hot")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            posts = data["data"]["posts"]
            assert len(posts) == 3
            
            # First post should be the "hot" one (most recent with good engagement)
            assert posts[0]["title"] == "Amazing AI Breakthrough"
            
        finally:
            app.dependency_overrides.clear()

    def test_get_posts_with_new_sorting(self, client, mock_db, sample_posts):
        """Test GET /posts with new sorting returns posts by creation date"""
        
        # Mock sorted by creation date (newest first)
        sorted_posts = sorted(sample_posts, key=lambda p: p.created_at, reverse=True)
        mock_db.query.return_value.join.return_value.outerjoin.return_value.group_by.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = sorted_posts
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.get("/api/v1/posts/?sort=new")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            posts = data["data"]["posts"]
            
            # First post should be the newest one
            assert posts[0]["title"] == "Getting Started with Python"
            
        finally:
            app.dependency_overrides.clear()

    def test_get_posts_with_top_sorting_day_range(self, client, mock_db, sample_posts):
        """Test GET /posts with top sorting and day time range"""
        
        # Mock sorted by total reactions (upvotes - downvotes) within day range
        mock_db.query.return_value.join.return_value.outerjoin.return_value.filter.return_value.group_by.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            sample_posts[0],  # Highest scoring post in last day
            sample_posts[1]   # Second highest in last day
        ]
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.get("/api/v1/posts/?sort=top&time_range=day")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            posts = data["data"]["posts"]
            assert len(posts) == 2
            
        finally:
            app.dependency_overrides.clear()

    def test_get_posts_with_tag_filter(self, client, mock_db, sample_posts):
        """Test GET /posts with tag filtering"""
        
        # Mock posts filtered by specific tag
        filtered_posts = [sample_posts[0], sample_posts[3]]  # Posts with "ai" tag
        mock_db.query.return_value.join.return_value.outerjoin.return_value.filter.return_value.group_by.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = filtered_posts
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.get("/api/v1/posts/?tag=ai")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            posts = data["data"]["posts"]
            assert len(posts) == 2
            
        finally:
            app.dependency_overrides.clear()

    def test_get_posts_with_user_filter(self, client, mock_db, sample_posts, sample_users):
        """Test GET /posts with user ID filtering"""
        
        # Mock posts filtered by specific user
        alice_posts = [p for p in sample_posts if p.user_id == sample_users[0].user_id]
        mock_db.query.return_value.join.return_value.outerjoin.return_value.filter.return_value.group_by.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = alice_posts
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.get(f"/api/v1/posts/?userId={sample_users[0].user_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            posts = data["data"]["posts"]
            assert len(posts) == 2  # Alice has 2 posts
            
            # All posts should be from Alice
            for post in posts:
                assert post["user"]["userName"] == "alice"
            
        finally:
            app.dependency_overrides.clear()

    def test_get_posts_with_pagination(self, client, mock_db, sample_posts):
        """Test GET /posts with pagination parameters"""
        
        # Mock paginated results
        mock_db.query.return_value.join.return_value.outerjoin.return_value.group_by.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = sample_posts[1:3]  # Skip first, take 2
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.get("/api/v1/posts/?limit=2&offset=1")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            posts = data["data"]["posts"]
            assert len(posts) == 2
            
        finally:
            app.dependency_overrides.clear()

    def test_get_posts_empty_result(self, client, mock_db):
        """Test GET /posts with no posts available"""
        
        mock_db.query.return_value.join.return_value.outerjoin.return_value.group_by.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.get("/api/v1/posts/")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert data["data"]["posts"] == []
            assert data["message"] == "Posts retrieved successfully"
            
        finally:
            app.dependency_overrides.clear()

    def test_get_posts_invalid_sort_parameter(self, client, mock_db):
        """Test GET /posts with invalid sort parameter"""
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.get("/api/v1/posts/?sort=invalid")
            
            assert response.status_code == 422  # Validation error
            data = response.json()
            
            assert "detail" in data
            
        finally:
            app.dependency_overrides.clear()

    def test_get_posts_invalid_time_range_parameter(self, client, mock_db):
        """Test GET /posts with invalid time_range parameter"""
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.get("/api/v1/posts/?time_range=invalid")
            
            assert response.status_code == 422  # Validation error
            data = response.json()
            
            assert "detail" in data
            
        finally:
            app.dependency_overrides.clear()

    def test_get_posts_limit_too_high(self, client, mock_db):
        """Test GET /posts with limit exceeding maximum"""
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.get("/api/v1/posts/?limit=101")
            
            assert response.status_code == 422  # Validation error
            data = response.json()
            
            assert "detail" in data
            
        finally:
            app.dependency_overrides.clear()

    def test_get_posts_negative_offset(self, client, mock_db):
        """Test GET /posts with negative offset"""
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.get("/api/v1/posts/?offset=-1")
            
            assert response.status_code == 422  # Validation error
            data = response.json()
            
            assert "detail" in data
            
        finally:
            app.dependency_overrides.clear()

    def test_get_posts_database_error(self, client, mock_db):
        """Test GET /posts with database error"""
        
        # Mock database error
        mock_db.query.side_effect = Exception("Database connection failed")
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.get("/api/v1/posts/")
            
            assert response.status_code == 500
            data = response.json()
            
            assert data["success"] is False
            assert "Database connection failed" in data["message"]
            assert data["errorCode"] == "POST_RETRIEVAL_ERROR"
            
        finally:
            app.dependency_overrides.clear()

    def test_get_posts_with_complex_filtering(self, client, mock_db, sample_posts, sample_users):
        """Test GET /posts with multiple filters combined"""
        
        # Mock posts filtered by user and tag
        mock_db.query.return_value.join.return_value.outerjoin.return_value.filter.return_value.filter.return_value.group_by.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_posts[0]]
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.get(f"/api/v1/posts/?userId={sample_users[0].user_id}&tag=ai&sort=top&time_range=week&limit=10&offset=0")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            posts = data["data"]["posts"]
            assert len(posts) == 1
            
        finally:
            app.dependency_overrides.clear()
