"""
Integration Tests for Post Service

Tests the integration between PostService and its dependencies (database repositories).
These tests use real database operations but don't involve HTTP layer.
"""

import pytest
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.services.post_service import PostService
from app.models.user import User
from app.models.post import Post
from app.models.tag import Tag
from app.models.post_tag import PostTag
from app.models.post_reaction import PostReaction
from app.models.conversation import Conversation


@pytest.fixture
def test_users(db_session):
    """Create test users for posts."""
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
    """Create test tags."""
    tag_names = ["ai", "tech", "python"]
    tags = []
    
    for name in tag_names:
        tag = Tag(name=name)
        db_session.add(tag)
        tags.append(tag)
    
    db_session.commit()
    return tags


@pytest.fixture
def test_conversations(db_session, test_users):
    """Create test conversations."""
    conversations = []
    for i, user in enumerate(test_users):
        conversation = Conversation(
            user_id=user.user_id,
            title=f"Test Conversation {i}"
        )
        db_session.add(conversation)
        conversations.append(conversation)
    
    db_session.commit()
    return conversations


@pytest.fixture
def test_posts(db_session, test_users, test_conversations):
    """Create test posts with different timestamps."""
    posts = []
    base_time = datetime.now(timezone.utc)
    
    for i in range(6):
        post = Post(
            user_id=test_users[i % 3].user_id,
            conversation_id=test_conversations[i % 3].conversation_id,
            title=f"Test Post {i}",
            content=f"Content for test post {i}",
            created_at=base_time - timedelta(hours=i)
        )
        db_session.add(post)
        posts.append(post)
    
    db_session.commit()
    return posts


class TestPostServiceIntegration:
    """Test PostService integration with database layer."""

    @pytest.mark.asyncio
    async def test_get_posts_feed_basic(self, db_session, test_posts):
        """Test basic get_posts_feed functionality."""
        service = PostService(db_session)
        
        posts = await service.get_posts_feed(
            db=db_session,
            limit=10,
            offset=0,
            sort="new",
            time_range="all",
            tag=None,
            user_id=None
        )
        
        assert len(posts) == 6
        assert all(hasattr(post, 'postId') for post in posts)
        assert all(hasattr(post, 'title') for post in posts)

    @pytest.mark.asyncio
    async def test_get_posts_feed_pagination(self, db_session, test_posts):
        """Test pagination in service layer."""
        service = PostService(db_session)
        
        # First page
        first_page = await service.get_posts_feed(
            db=db_session,
            limit=3,
            offset=0,
            sort="new",
            time_range="all",
            tag=None,
            user_id=None
        )
        
        # Second page
        second_page = await service.get_posts_feed(
            db=db_session,
            limit=3,
            offset=3,
            sort="new",
            time_range="all",
            tag=None,
            user_id=None
        )
        
        assert len(first_page) == 3
        assert len(second_page) == 3
        
        # Ensure no overlap
        first_ids = {post.postId for post in first_page}
        second_ids = {post.postId for post in second_page}
        assert len(first_ids.intersection(second_ids)) == 0

    @pytest.mark.asyncio
    async def test_get_posts_feed_user_filtering(self, db_session, test_posts, test_users):
        """Test user filtering in service layer."""
        service = PostService(db_session)
        
        user_id = test_users[0].user_id
        posts = await service.get_posts_feed(
            db=db_session,
            limit=10,
            offset=0,
            sort="new",
            time_range="all",
            tag=None,
            user_id=user_id
        )
        
        # Should get posts only from this user
        assert len(posts) == 2  # User 0 should have 2 posts (indices 0 and 3)
        for post in posts:
            assert post.user.userId == user_id

    @pytest.mark.asyncio
    async def test_get_posts_feed_sorting_chronological(self, db_session, test_posts):
        """Test chronological sorting in service layer."""
        service = PostService(db_session)
        
        posts = await service.get_posts_feed(
            db=db_session,
            limit=10,
            offset=0,
            sort="new",
            time_range="all",
            tag=None,
            user_id=None
        )
        
        # Posts should be in descending chronological order (newest first)
        for i in range(len(posts) - 1):
            current_time = posts[i].createdAt
            next_time = posts[i + 1].createdAt
            assert current_time >= next_time

    @pytest.mark.asyncio
    async def test_get_posts_feed_with_tags(self, db_session, test_posts, test_tags):
        """Test tag filtering integration."""
        service = PostService(db_session)
        
        # Add tags to some posts
        post_tag = PostTag(post_id=test_posts[0].post_id, tag_id=test_tags[0].tag_id)
        db_session.add(post_tag)
        db_session.commit()
        
        # Filter by tag
        posts = await service.get_posts_feed(
            db=db_session,
            limit=10,
            offset=0,
            sort="new",
            time_range="all",
            tag=test_tags[0].name,
            user_id=None
        )
        
        assert len(posts) == 1
        assert test_tags[0].name in posts[0].tags

    @pytest.mark.asyncio
    async def test_get_posts_feed_time_range_filtering(self, db_session, test_posts):
        """Test time range filtering in service layer."""
        service = PostService(db_session)
        
        # Get recent posts (within last day)
        posts = await service.get_posts_feed(
            db=db_session,
            limit=10,
            offset=0,
            sort="new",
            time_range="day",
            tag=None,
            user_id=None
        )
        
        # Should get only posts created within last day
        assert len(posts) > 0
        for post in posts:
            time_diff = datetime.now(timezone.utc) - post.createdAt
            assert time_diff.total_seconds() <= 24 * 3600

    @pytest.mark.asyncio
    async def test_service_handles_empty_database(self, db_session):
        """Test service behavior with empty database."""
        service = PostService(db_session)
        
        posts = await service.get_posts_feed(
            db=db_session,
            limit=10,
            offset=0,
            sort="new",
            time_range="all",
            tag=None,
            user_id=None
        )
        
        assert len(posts) == 0
        assert isinstance(posts, list)
