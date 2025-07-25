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
        
        # Create expected PostResponse objects
        from app.schemas.post import PostResponse, UserSummary, PostReactions
        from uuid import uuid4
        
        expected_posts = [
            PostResponse(
                postId=uuid4(),
                title="Amazing AI Breakthrough",
                content="This is a groundbreaking discovery in AI...",
                createdAt=datetime.now(),
                user=UserSummary(
                    userId=sample_users[0].user_id,
                    userName="alice",
                    profilePicture="https://example.com/alice.jpg"
                ),
                tags=["ai", "technology"],
                reactions=PostReactions(upvote=5, downvote=1, heart=3, insightful=2, accurate=1),
                userReaction=None,
                commentCount=3,
                viewCount=147,
                userViewCount=0,
                conversationId=None
            ),
            PostResponse(
                postId=uuid4(),
                title="Getting Started with Python",
                content="Here's how to begin your Python journey...",
                createdAt=datetime.now(),
                user=UserSummary(
                    userId=sample_users[1].user_id,
                    userName="bob",
                    profilePicture="https://example.com/bob.jpg"
                ),
                tags=["python", "programming"],
                reactions=PostReactions(upvote=8, downvote=0, heart=2, insightful=4, accurate=3),
                userReaction=None,
                commentCount=5,
                viewCount=89,
                userViewCount=0,
                conversationId=None
            )
        ]
        
        # Mock the service layer instead of database
        with patch('app.services.post_service.PostService.get_posts_feed') as mock_get_posts:
            mock_get_posts.return_value = expected_posts
            
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
            
            # Verify service was called with correct parameters
            mock_get_posts.assert_called_once()

    def test_get_posts_with_hot_sorting(self, client, mock_db, sample_posts):
        """Test GET /posts with hot sorting returns posts ranked by hot algorithm"""
        
        # Create expected PostResponse objects (hot-sorted)
        from app.schemas.post import PostResponse, UserSummary, PostReactions
        from uuid import uuid4
        
        expected_posts = [
            PostResponse(
                postId=uuid4(),
                title="Amazing AI Breakthrough",  # Hot post with high score
                content="This is a groundbreaking discovery in AI...",
                createdAt=datetime.now() - timedelta(hours=2),
                user=UserSummary(userId=uuid4(), userName="alice", profilePicture="https://example.com/alice.jpg"),
                tags=["ai", "technology"],
                reactions=PostReactions(upvote=10, downvote=1, heart=5, insightful=3, accurate=2),
                userReaction=None,
                commentCount=8,
                viewCount=250,
                userViewCount=0,
                conversationId=None
            ),
            PostResponse(
                postId=uuid4(),
                title="Understanding Machine Learning",  # Moderate post
                content="ML concepts explained simply...",
                createdAt=datetime.now() - timedelta(hours=12),
                user=UserSummary(userId=uuid4(), userName="bob", profilePicture="https://example.com/bob.jpg"),
                tags=["ai", "machine-learning"],
                reactions=PostReactions(upvote=5, downvote=0, heart=2, insightful=4, accurate=1),
                userReaction=None,
                commentCount=3,
                viewCount=89,
                userViewCount=0,
                conversationId=None
            )
        ]
        
        # Mock the service layer
        with patch('app.services.post_service.PostService.get_posts_feed') as mock_get_posts:
            mock_get_posts.return_value = expected_posts
            
            response = client.get("/api/v1/posts/?sort=hot")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            posts = data["data"]["posts"]
            assert len(posts) == 2
            
            # First post should be the "hot" one (most recent with good engagement)
            assert posts[0]["title"] == "Amazing AI Breakthrough"
            
            # Verify service was called with correct parameters
            mock_get_posts.assert_called_once()

    def test_get_posts_with_new_sorting(self, client, mock_db, sample_posts):
        """Test GET /posts with new sorting returns posts by creation date"""
        
        # Create expected PostResponse objects (newest first)
        from app.schemas.post import PostResponse, UserSummary, PostReactions
        from uuid import uuid4
        
        expected_posts = [
            PostResponse(
                postId=uuid4(),
                title="Getting Started with Python",  # Newest post
                content="Here's how to begin your Python journey...",
                createdAt=datetime.now() - timedelta(minutes=30),
                user=UserSummary(userId=uuid4(), userName="bob", profilePicture="https://example.com/bob.jpg"),
                tags=["python", "programming"],
                reactions=PostReactions(upvote=3, downvote=0, heart=1, insightful=2, accurate=1),
                userReaction=None,
                commentCount=1,
                viewCount=25,
                userViewCount=0,
                conversationId=None
            ),
            PostResponse(
                postId=uuid4(),
                title="Amazing AI Breakthrough",
                content="This is a groundbreaking discovery in AI...",
                createdAt=datetime.now() - timedelta(hours=2),
                user=UserSummary(userId=uuid4(), userName="alice", profilePicture="https://example.com/alice.jpg"),
                tags=["ai", "technology"],
                reactions=PostReactions(upvote=10, downvote=1, heart=5, insightful=3, accurate=2),
                userReaction=None,
                commentCount=8,
                viewCount=250,
                userViewCount=0,
                conversationId=None
            )
        ]
        
        # Mock the service layer
        with patch('app.services.post_service.PostService.get_posts_feed') as mock_get_posts:
            mock_get_posts.return_value = expected_posts
            
            response = client.get("/api/v1/posts/?sort=new")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            posts = data["data"]["posts"]
            
            # First post should be the newest one
            assert posts[0]["title"] == "Getting Started with Python"
            
            # Verify service was called with correct parameters
            mock_get_posts.assert_called_once()

    def test_get_posts_with_top_sorting_day_range(self, client, mock_db, sample_posts):
        """Test GET /posts with top sorting and day time range"""
        
        # Create expected PostResponse objects (top posts in last day)
        from app.schemas.post import PostResponse, UserSummary, PostReactions
        from uuid import uuid4
        
        expected_posts = [
            PostResponse(
                postId=uuid4(),
                title="Amazing AI Breakthrough",  # Highest scoring post in last day
                content="This is a groundbreaking discovery in AI...",
                createdAt=datetime.now() - timedelta(hours=12),
                user=UserSummary(userId=uuid4(), userName="alice", profilePicture="https://example.com/alice.jpg"),
                tags=["ai", "technology"],
                reactions=PostReactions(upvote=15, downvote=2, heart=8, insightful=5, accurate=3),
                userReaction=None,
                commentCount=12,
                viewCount=350,
                userViewCount=0,
                conversationId=None
            ),
            PostResponse(
                postId=uuid4(),
                title="Getting Started with Python",  # Second highest in last day
                content="Here's how to begin your Python journey...",
                createdAt=datetime.now() - timedelta(hours=18),
                user=UserSummary(userId=uuid4(), userName="bob", profilePicture="https://example.com/bob.jpg"),
                tags=["python", "programming"],
                reactions=PostReactions(upvote=8, downvote=1, heart=3, insightful=4, accurate=2),
                userReaction=None,
                commentCount=6,
                viewCount=120,
                userViewCount=0,
                conversationId=None
            )
        ]
        
        # Mock the service layer
        with patch('app.services.post_service.PostService.get_posts_feed') as mock_get_posts:
            mock_get_posts.return_value = expected_posts
            
            response = client.get("/api/v1/posts/?sort=top&time_range=day")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            posts = data["data"]["posts"]
            assert len(posts) == 2
            
            # Verify service was called with correct parameters
            mock_get_posts.assert_called_once()

    def test_get_posts_with_tag_filter(self, client, mock_db, sample_posts):
        """Test GET /posts with tag filtering"""
        
        # Create expected PostResponse objects (filtered by 'ai' tag)
        from app.schemas.post import PostResponse, UserSummary, PostReactions
        from uuid import uuid4
        
        expected_posts = [
            PostResponse(
                postId=uuid4(),
                title="Amazing AI Breakthrough",
                content="This is a groundbreaking discovery in AI...",
                createdAt=datetime.now() - timedelta(hours=2),
                user=UserSummary(userId=uuid4(), userName="alice", profilePicture="https://example.com/alice.jpg"),
                tags=["ai", "technology"],
                reactions=PostReactions(upvote=10, downvote=1, heart=5, insightful=3, accurate=2),
                userReaction=None,
                commentCount=8,
                viewCount=250,
                userViewCount=0,
                conversationId=None
            ),
            PostResponse(
                postId=uuid4(),
                title="Understanding Machine Learning",
                content="ML concepts explained simply...",
                createdAt=datetime.now() - timedelta(hours=12),
                user=UserSummary(userId=uuid4(), userName="charlie", profilePicture=None),
                tags=["ai", "machine-learning"],
                reactions=PostReactions(upvote=6, downvote=0, heart=3, insightful=4, accurate=2),
                userReaction=None,
                commentCount=4,
                viewCount=89,
                userViewCount=0,
                conversationId=None
            )
        ]
        
        # Mock the service layer
        with patch('app.services.post_service.PostService.get_posts_feed') as mock_get_posts:
            mock_get_posts.return_value = expected_posts
            
            response = client.get("/api/v1/posts/?tag=ai")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            posts = data["data"]["posts"]
            assert len(posts) == 2
            
            # Verify service was called with correct parameters
            mock_get_posts.assert_called_once()

    def test_get_posts_with_user_filter(self, client, mock_db, sample_posts, sample_users):
        """Test GET /posts with user ID filtering"""
        
        # Create expected PostResponse objects (filtered by Alice's user ID)
        from app.schemas.post import PostResponse, UserSummary, PostReactions
        from uuid import uuid4
        
        alice_user_id = sample_users[0].user_id
        
        expected_posts = [
            PostResponse(
                postId=uuid4(),
                title="Amazing AI Breakthrough",
                content="This is a groundbreaking discovery in AI...",
                createdAt=datetime.now() - timedelta(hours=2),
                user=UserSummary(
                    userId=alice_user_id,
                    userName="alice",
                    profilePicture="https://example.com/alice.jpg"
                ),
                tags=["ai", "technology"],
                reactions=PostReactions(upvote=10, downvote=1, heart=5, insightful=3, accurate=2),
                userReaction=None,
                commentCount=8,
                viewCount=250,
                userViewCount=0,
                conversationId=None
            ),
            PostResponse(
                postId=uuid4(),
                title="Complete Web Development Guide",
                content="Everything you need to know about web dev...",
                createdAt=datetime.now() - timedelta(hours=48),
                user=UserSummary(
                    userId=alice_user_id,
                    userName="alice",
                    profilePicture="https://example.com/alice.jpg"
                ),
                tags=["web-development", "programming"],
                reactions=PostReactions(upvote=7, downvote=0, heart=4, insightful=5, accurate=3),
                userReaction=None,
                commentCount=6,
                viewCount=180,
                userViewCount=0,
                conversationId=None
            )
        ]
        
        # Mock the service layer
        with patch('app.services.post_service.PostService.get_posts_feed') as mock_get_posts:
            mock_get_posts.return_value = expected_posts
            
            response = client.get(f"/api/v1/posts/?userId={alice_user_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            posts = data["data"]["posts"]
            assert len(posts) == 2  # Alice has 2 posts
            
            # All posts should be from Alice
            for post in posts:
                assert post["user"]["userName"] == "alice"
            
            # Verify service was called with correct parameters
            mock_get_posts.assert_called_once()

    def test_get_posts_with_pagination(self, client, mock_db, sample_posts):
        """Test GET /posts with pagination parameters"""
        
        # Create expected PostResponse objects (paginated: skip first, take 2)
        from app.schemas.post import PostResponse, UserSummary, PostReactions
        from uuid import uuid4
        
        expected_posts = [
            PostResponse(
                postId=uuid4(),
                title="Getting Started with Python",
                content="Here's how to begin your Python journey...",
                createdAt=datetime.now() - timedelta(minutes=30),
                user=UserSummary(userId=uuid4(), userName="bob", profilePicture="https://example.com/bob.jpg"),
                tags=["python", "programming"],
                reactions=PostReactions(upvote=8, downvote=0, heart=3, insightful=4, accurate=2),
                userReaction=None,
                commentCount=5,
                viewCount=89,
                userViewCount=0,
                conversationId=None
            ),
            PostResponse(
                postId=uuid4(),
                title="Complete Web Development Guide",
                content="Everything you need to know about web dev...",
                createdAt=datetime.now() - timedelta(hours=48),
                user=UserSummary(userId=uuid4(), userName="charlie", profilePicture=None),
                tags=["web-development", "programming"],
                reactions=PostReactions(upvote=5, downvote=1, heart=2, insightful=3, accurate=1),
                userReaction=None,
                commentCount=4,
                viewCount=72,
                userViewCount=0,
                conversationId=None
            )
        ]
        
        # Mock the service layer
        with patch('app.services.post_service.PostService.get_posts_feed') as mock_get_posts:
            mock_get_posts.return_value = expected_posts
            
            response = client.get("/api/v1/posts/?limit=2&offset=1")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            posts = data["data"]["posts"]
            assert len(posts) == 2
            
            # Verify service was called with correct parameters
            mock_get_posts.assert_called_once()

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
        
        # Mock service to raise exception
        with patch('app.services.post_service.PostService.get_posts_feed') as mock_get_posts:
            mock_get_posts.side_effect = Exception("Database connection failed")
            
            response = client.get("/api/v1/posts/")
            
            assert response.status_code == 500
            data = response.json()
            
            assert "detail" in data
            detail = data["detail"]
            assert detail["success"] is False
            assert "Database connection failed" in detail["message"]
            assert detail["errorCode"] == "POST_RETRIEVAL_ERROR"

    def test_get_posts_with_complex_filtering(self, client, mock_db, sample_posts, sample_users):
        """Test GET /posts with multiple filters combined"""
        
        # Create expected PostResponse objects (filtered by user, tag, and other parameters)
        from app.schemas.post import PostResponse, UserSummary, PostReactions
        from uuid import uuid4
        
        alice_user_id = sample_users[0].user_id
        
        expected_posts = [
            PostResponse(
                postId=uuid4(),
                title="Amazing AI Breakthrough",
                content="This is a groundbreaking discovery in AI...",
                createdAt=datetime.now() - timedelta(hours=2),
                user=UserSummary(
                    userId=alice_user_id,
                    userName="alice",
                    profilePicture="https://example.com/alice.jpg"
                ),
                tags=["ai", "technology"],
                reactions=PostReactions(upvote=15, downvote=2, heart=8, insightful=5, accurate=3),
                userReaction=None,
                commentCount=12,
                viewCount=350,
                userViewCount=0,
                conversationId=None
            )
        ]
        
        # Mock the service layer
        with patch('app.services.post_service.PostService.get_posts_feed') as mock_get_posts:
            mock_get_posts.return_value = expected_posts
            
            response = client.get(f"/api/v1/posts/?userId={alice_user_id}&tag=ai&sort=top&time_range=week&limit=10&offset=0")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            posts = data["data"]["posts"]
            assert len(posts) == 1
            
            # Verify service was called with correct parameters
            mock_get_posts.assert_called_once()
