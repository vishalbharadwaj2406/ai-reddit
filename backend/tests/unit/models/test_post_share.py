"""
Tests for PostShare Model

Test the sharing functionality including privacy controls,
anonymous sharing, platform tracking, and relationship integrity.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.conversation import Conversation
from app.models.post import Post
from app.models.post_share import PostShare


class TestPostShareModel:
    """Test cases for PostShare model functionality."""

    def test_post_share_creation_basic(self, db_session):
        """Test basic PostShare creation."""
        # Create test data
        user = User(user_name="sharer", email="sharer@test.com")
        conversation = Conversation(title="Test Conv", status="active", user=user)
        post = Post(
            title="Test Post",
            content="Test content",
            conversation=conversation,
            user=user,
            status="published"
        )
        db_session.add_all([user, conversation, post])
        db_session.commit()

        # Create share
        share = PostShare(
            post_id=post.post_id,
            shared_by_user_id=user.user_id,
            platform="twitter",
            status="active"
        )
        db_session.add(share)
        db_session.commit()

        # Verify creation
        assert share.share_id is not None
        assert share.post_id == post.post_id
        assert share.shared_by_user_id == user.user_id
        assert share.platform == "twitter"
        assert share.status == "active"
        assert share.shared_at is not None
        assert share.share_metadata is None

    def test_post_share_anonymous_sharing(self, db_session):
        """Test anonymous sharing (no user_id)."""
        # Create test data
        user = User(user_name="author", email="author@test.com")
        conversation = Conversation(title="Test Conv", status="active", user=user)
        post = Post(
            title="Test Post",
            content="Test content",
            conversation=conversation,
            user=user,
            status="published"
        )
        db_session.add_all([user, conversation, post])
        db_session.commit()

        # Create anonymous share
        share = PostShare(
            post_id=post.post_id,
            shared_by_user_id=None,  # Anonymous
            platform="direct_link",
            status="active"
        )
        db_session.add(share)
        db_session.commit()

        # Verify anonymous share
        assert share.shared_by_user_id is None
        assert share.is_anonymous is True
        assert share.platform == "direct_link"

    def test_post_share_platform_tracking(self, db_session):
        """Test different platform tracking."""
        # Create test data
        user = User(user_name="sharer", email="sharer@test.com")
        conversation = Conversation(title="Test Conv", status="active", user=user)
        post = Post(
            title="Test Post",
            content="Test content",
            conversation=conversation,
            user=user,
            status="published"
        )
        db_session.add_all([user, conversation, post])
        db_session.commit()

        platforms = ["twitter", "facebook", "direct_link", "email", "whatsapp"]
        
        for platform in platforms:
            share = PostShare(
                post_id=post.post_id,
                shared_by_user_id=user.user_id,
                platform=platform,
                status="active"
            )
            db_session.add(share)
        
        db_session.commit()

        # Verify all platforms tracked
        shares = db_session.query(PostShare).filter(PostShare.post_id == post.post_id).all()
        assert len(shares) == 5
        tracked_platforms = [share.platform for share in shares]
        assert set(tracked_platforms) == set(platforms)

    def test_post_share_relationships(self, db_session):
        """Test PostShare relationships with Post and User."""
        # Create test data
        user = User(user_name="sharer", email="sharer@test.com")
        conversation = Conversation(title="Test Conv", status="active", user=user)
        post = Post(
            title="Test Post",
            content="Test content",
            conversation=conversation,
            user=user,
            status="published"
        )
        db_session.add_all([user, conversation, post])
        db_session.commit()

        # Create share
        share = PostShare(
            post_id=post.post_id,
            shared_by_user_id=user.user_id,
            platform="twitter"
        )
        db_session.add(share)
        db_session.commit()

        # Test relationships
        assert share.post == post
        assert share.shared_by == user
        assert share in post.shares
        assert share in user.shares_made

    def test_post_share_without_post_fails(self, db_session):
        """Test that PostShare requires a valid post."""
        fake_post_id = uuid4()
        
        share = PostShare(
            post_id=fake_post_id,
            platform="twitter"
        )
        db_session.add(share)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_post_share_with_invalid_user_fails(self, db_session):
        """Test that PostShare with invalid user_id fails."""
        # Create test data
        user = User(user_name="author", email="author@test.com")
        conversation = Conversation(title="Test Conv", status="active", user=user)
        post = Post(
            title="Test Post",
            content="Test content",
            conversation=conversation,
            user=user,
            status="published"
        )
        db_session.add_all([user, conversation, post])
        db_session.commit()

        fake_user_id = uuid4()
        
        share = PostShare(
            post_id=post.post_id,
            shared_by_user_id=fake_user_id,
            platform="twitter"
        )
        db_session.add(share)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_post_share_status_properties(self, db_session):
        """Test PostShare status properties and methods."""
        # Create test data
        user = User(user_name="sharer", email="sharer@test.com")
        conversation = Conversation(title="Test Conv", status="active", user=user)
        post = Post(
            title="Test Post",
            content="Test content",
            conversation=conversation,
            user=user,
            status="published"
        )
        db_session.add_all([user, conversation, post])
        db_session.commit()

        # Test active share
        share = PostShare(
            post_id=post.post_id,
            shared_by_user_id=user.user_id,
            platform="twitter",
            status="active"
        )
        
        assert share.is_active is True
        
        # Test archive method
        share.archive()
        assert share.status == "archived"
        assert share.is_active is False
        
        # Test activate method
        share.activate()
        assert share.status == "active"
        assert share.is_active is True

    def test_post_share_metadata_field(self, db_session):
        """Test PostShare share_metadata JSON field."""
        # Create test data
        user = User(user_name="sharer", email="sharer@test.com")
        conversation = Conversation(title="Test Conv", status="active", user=user)
        post = Post(
            title="Test Post",
            content="Test content",
            conversation=conversation,
            user=user,
            status="published"
        )
        db_session.add_all([user, conversation, post])
        db_session.commit()

        # Create share with metadata
        metadata = {
            "referrer": "https://twitter.com",
            "user_agent": "Mozilla/5.0...",
            "share_source": "share_button"
        }
        
        share = PostShare(
            post_id=post.post_id,
            shared_by_user_id=user.user_id,
            platform="twitter",
            share_metadata=metadata
        )
        db_session.add(share)
        db_session.commit()

        # Verify metadata storage
        retrieved_share = db_session.query(PostShare).filter(PostShare.share_id == share.share_id).first()
        assert retrieved_share.share_metadata == metadata
        assert retrieved_share.share_metadata["referrer"] == "https://twitter.com"

    def test_create_share_class_method(self, db_session):
        """Test create_share class method."""
        # Create test data
        user = User(user_name="sharer", email="sharer@test.com")
        conversation = Conversation(title="Test Conv", status="active", user=user)
        post = Post(
            title="Test Post",
            content="Test content",
            conversation=conversation,
            user=user,
            status="published"
        )
        db_session.add_all([user, conversation, post])
        db_session.commit()

        # Create share using class method
        share = PostShare.create_share(
            post_id=post.post_id,
            shared_by_user_id=user.user_id,
            platform="facebook"
        )

        # Verify creation
        assert share.post_id == post.post_id
        assert share.shared_by_user_id == user.user_id
        assert share.platform == "facebook"
        assert share.status == "active"

    def test_post_share_cascade_on_post_deletion(self, db_session):
        """Test CASCADE deletion when post is deleted."""
        # Create test data
        user = User(user_name="sharer", email="sharer@test.com")
        conversation = Conversation(title="Test Conv", status="active", user=user)
        post = Post(
            title="Test Post",
            content="Test content",
            conversation=conversation,
            user=user,
            status="published"
        )
        db_session.add_all([user, conversation, post])
        db_session.commit()

        # Create shares
        share1 = PostShare(post_id=post.post_id, platform="twitter")
        share2 = PostShare(post_id=post.post_id, platform="facebook")
        db_session.add_all([share1, share2])
        db_session.commit()

        share_ids = [share1.share_id, share2.share_id]

        # Delete post
        db_session.delete(post)
        db_session.commit()

        # Verify shares are deleted (CASCADE)
        remaining_shares = db_session.query(PostShare).filter(
            PostShare.share_id.in_(share_ids)
        ).all()
        assert len(remaining_shares) == 0

    def test_post_share_cascade_on_user_deletion(self, db_session):
        """Test SET NULL when user is deleted."""
        # Create test data
        author = User(user_name="author", email="author@test.com")
        sharer = User(user_name="sharer", email="sharer@test.com")
        conversation = Conversation(title="Test Conv", status="active", user=author)
        post = Post(
            title="Test Post",
            content="Test content",
            conversation=conversation,
            user=author,
            status="published"
        )
        db_session.add_all([author, sharer, conversation, post])
        db_session.commit()

        # Create share by user
        share = PostShare(
            post_id=post.post_id,
            shared_by_user_id=sharer.user_id,
            platform="twitter"
        )
        db_session.add(share)
        db_session.commit()

        share_id = share.share_id

        # Delete sharer
        db_session.delete(sharer)
        db_session.commit()

        # Verify share still exists but user_id is NULL
        remaining_share = db_session.query(PostShare).filter(PostShare.share_id == share_id).first()
        assert remaining_share is not None
        assert remaining_share.shared_by_user_id is None
        assert remaining_share.is_anonymous is True

    def test_post_get_share_count_method(self, db_session):
        """Test Post.get_share_count() method."""
        # Create test data
        user = User(user_name="sharer", email="sharer@test.com")
        conversation = Conversation(title="Test Conv", status="active", user=user)
        post = Post(
            title="Test Post",
            content="Test content",
            conversation=conversation,
            user=user,
            status="published"
        )
        db_session.add_all([user, conversation, post])
        db_session.commit()

        # Initially no shares
        assert post.get_share_count() == 0

        # Add active shares
        share1 = PostShare(post_id=post.post_id, platform="twitter", status="active")
        share2 = PostShare(post_id=post.post_id, platform="facebook", status="active")
        share3 = PostShare(post_id=post.post_id, platform="email", status="archived")  # Archived
        
        db_session.add_all([share1, share2, share3])
        db_session.commit()

        # Should count only active shares
        assert post.get_share_count() == 2

    def test_post_share_string_representation(self, db_session):
        """Test PostShare string representations."""
        # Create test data
        user = User(user_name="testuser", email="test@test.com")
        conversation = Conversation(title="Test Conv", status="active", user=user)
        post = Post(
            title="Test Post",
            content="Test content",
            conversation=conversation,
            user=user,
            status="published"
        )
        db_session.add_all([user, conversation, post])
        db_session.commit()

        # Test authenticated share representation
        share = PostShare(
            post_id=post.post_id,
            shared_by_user_id=user.user_id,
            platform="twitter"
        )
        
        repr_str = repr(share)
        assert "PostShare" in repr_str
        assert "twitter" in repr_str
        assert "user_" in repr_str

        # Test anonymous share representation
        anon_share = PostShare(
            post_id=post.post_id,
            shared_by_user_id=None,
            platform="direct_link"
        )
        
        repr_str = repr(anon_share)
        assert "PostShare" in repr_str
        assert "anonymous" in repr_str
        assert "direct_link" in repr_str

    def test_multiple_shares_per_post(self, db_session):
        """Test multiple shares for the same post."""
        # Create test data
        user1 = User(user_name="user1", email="user1@test.com")
        user2 = User(user_name="user2", email="user2@test.com")
        conversation = Conversation(title="Test Conv", status="active", user=user1)
        post = Post(
            title="Popular Post",
            content="This will be shared multiple times",
            conversation=conversation,
            user=user1,
            status="published"
        )
        db_session.add_all([user1, user2, conversation, post])
        db_session.commit()

        # Create multiple shares
        shares = [
            PostShare(post_id=post.post_id, shared_by_user_id=user1.user_id, platform="twitter"),
            PostShare(post_id=post.post_id, shared_by_user_id=user2.user_id, platform="facebook"),
            PostShare(post_id=post.post_id, shared_by_user_id=None, platform="direct_link"),
            PostShare(post_id=post.post_id, shared_by_user_id=user1.user_id, platform="email")
        ]
        
        db_session.add_all(shares)
        db_session.commit()

        # Verify all shares exist
        assert len(post.shares) == 4
        assert post.get_share_count() == 4

        # Verify platform diversity
        platforms = [share.platform for share in post.shares]
        assert "twitter" in platforms
        assert "facebook" in platforms
        assert "direct_link" in platforms
        assert "email" in platforms

    def test_post_share_edge_cases(self, db_session):
        """Test edge cases and data validation."""
        # Create test data
        user = User(user_name="edgeuser", email="edge@test.com")
        conversation = Conversation(title="Test Conv", status="active", user=user)
        post = Post(
            title="Edge Case Post",
            content="Testing edge cases",
            conversation=conversation,
            user=user,
            status="published"
        )
        db_session.add_all([user, conversation, post])
        db_session.commit()

        # Test with minimal data
        minimal_share = PostShare(post_id=post.post_id)
        db_session.add(minimal_share)
        db_session.commit()
        
        assert minimal_share.platform is None
        assert minimal_share.shared_by_user_id is None
        assert minimal_share.status == "active"  # Default value
        assert minimal_share.is_anonymous is True

        # Test long platform name
        long_platform_share = PostShare(
            post_id=post.post_id,
            platform="very_long_platform_name_that_might_exceed_limits"
        )
        db_session.add(long_platform_share)
        db_session.commit()
        
        # Should truncate or handle gracefully based on column definition
