"""
Follow Model Tests

Comprehensive test suite for the Follow model.
Tests cover:
- Follow relationship creation and validation
- Status management (pending, accepted, archived)
- Rejection handling (clean deletion)
- Constraint validation (no self-follows, no duplicates)
- Bidirectional relationships
- Cascade behavior
"""

import pytest
import uuid
import warnings
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models.follow import Follow
from app.models.user import User


class TestFollowModel:
    """Test cases for the Follow model."""

    def test_follow_creation_basic(self, db_session, sample_user):
        """Test basic follow relationship creation."""
        # Create a second user to follow
        followed_user = User(
            user_name="followed_user",
            email="followed@example.com",
            is_private=False,
            status="active"
        )
        db_session.add(followed_user)
        db_session.commit()

        # Create follow relationship
        follow = Follow(
            follower_id=sample_user.user_id,
            following_id=followed_user.user_id
        )
        
        db_session.add(follow)
        db_session.commit()

        # Verify creation
        assert follow.follower_id == sample_user.user_id
        assert follow.following_id == followed_user.user_id
        assert follow.status == "pending"  # Default status
        assert follow.created_at is not None
        assert follow.updated_at is not None

    def test_follow_creation_with_explicit_status(self, db_session, sample_user):
        """Test follow creation with explicit status."""
        followed_user = User(
            user_name="followed_user",
            email="followed@example.com",
            is_private=False,
            status="active"
        )
        db_session.add(followed_user)
        db_session.commit()

        follow = Follow(
            follower_id=sample_user.user_id,
            following_id=followed_user.user_id,
            status="accepted"
        )
        
        db_session.add(follow)
        db_session.commit()

        assert follow.status == "accepted"

    def test_follow_self_follow_prevention(self, db_session, sample_user):
        """Test that users cannot follow themselves."""
        follow = Follow(
            follower_id=sample_user.user_id,
            following_id=sample_user.user_id  # Same user
        )
        
        db_session.add(follow)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_follow_duplicate_prevention(self, db_session, sample_user):
        """Test that duplicate follows are prevented."""
        followed_user = User(
            user_name="followed_user",
            email="followed@example.com",
            is_private=False,
            status="active"
        )
        db_session.add(followed_user)
        db_session.commit()

        # Create first follow
        follow1 = Follow(
            follower_id=sample_user.user_id,
            following_id=followed_user.user_id
        )
        db_session.add(follow1)
        db_session.commit()

        # Try to create duplicate follow
        follow2 = Follow(
            follower_id=sample_user.user_id,
            following_id=followed_user.user_id
        )
        db_session.add(follow2)
        
        # Suppress the expected SQLAlchemy identity warning for duplicate test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=Warning)
            with pytest.raises(IntegrityError):
                db_session.commit()

    def test_follow_invalid_status(self, db_session, sample_user):
        """Test that invalid status values are rejected."""
        followed_user = User(
            user_name="followed_user",
            email="followed@example.com",
            is_private=False,
            status="active"
        )
        db_session.add(followed_user)
        db_session.commit()

        follow = Follow(
            follower_id=sample_user.user_id,
            following_id=followed_user.user_id,
            status="invalid_status"
        )
        
        db_session.add(follow)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_follow_status_properties(self, db_session, sample_user):
        """Test follow status property methods."""
        followed_user = User(
            user_name="followed_user",
            email="followed@example.com",
            is_private=False,
            status="active"
        )
        db_session.add(followed_user)
        db_session.commit()

        # Test pending status
        follow = Follow(
            follower_id=sample_user.user_id,
            following_id=followed_user.user_id,
            status="pending"
        )
        
        assert follow.is_pending is True
        assert follow.is_accepted is False
        assert follow.is_active is False
        assert follow.is_archived is False

        # Test accepted status
        follow.status = "accepted"
        assert follow.is_pending is False
        assert follow.is_accepted is True
        assert follow.is_active is True
        assert follow.is_archived is False

        # Test archived status
        follow.status = "archived"
        assert follow.is_pending is False
        assert follow.is_accepted is False
        assert follow.is_active is False
        assert follow.is_archived is True

    def test_follow_accept_method(self, db_session, sample_user):
        """Test accepting a follow request."""
        followed_user = User(
            user_name="followed_user",
            email="followed@example.com",
            is_private=False,
            status="active"
        )
        db_session.add(followed_user)
        db_session.commit()

        follow = Follow(
            follower_id=sample_user.user_id,
            following_id=followed_user.user_id,
            status="pending"
        )
        
        db_session.add(follow)
        db_session.commit()

        original_updated_at = follow.updated_at

        # Accept the follow
        follow.accept()
        db_session.commit()

        assert follow.status == "accepted"
        assert follow.is_accepted is True
        assert follow.updated_at > original_updated_at

    def test_follow_accept_only_pending(self, db_session, sample_user):
        """Test that only pending follows can be accepted."""
        followed_user = User(
            user_name="followed_user",
            email="followed@example.com",
            is_private=False,
            status="active"
        )
        db_session.add(followed_user)
        db_session.commit()

        follow = Follow(
            follower_id=sample_user.user_id,
            following_id=followed_user.user_id,
            status="accepted"  # Already accepted
        )
        
        db_session.add(follow)
        db_session.commit()

        # Try to accept already accepted follow
        follow.accept()
        db_session.commit()

        # Should remain accepted (no change)
        assert follow.status == "accepted"

    def test_follow_archive_method(self, db_session, sample_user):
        """Test archiving a follow relationship."""
        followed_user = User(
            user_name="followed_user",
            email="followed@example.com",
            is_private=False,
            status="active"
        )
        db_session.add(followed_user)
        db_session.commit()

        follow = Follow(
            follower_id=sample_user.user_id,
            following_id=followed_user.user_id,
            status="accepted"
        )
        
        db_session.add(follow)
        db_session.commit()

        original_updated_at = follow.updated_at

        # Archive the follow
        follow.archive()
        db_session.commit()

        assert follow.status == "archived"
        assert follow.is_archived is True
        assert follow.updated_at > original_updated_at

    def test_follow_relationships(self, db_session, sample_user):
        """Test bidirectional relationships between Follow and User."""
        followed_user = User(
            user_name="followed_user",
            email="followed@example.com",
            is_private=False,
            status="active"
        )
        db_session.add(followed_user)
        db_session.commit()

        follow = Follow(
            follower_id=sample_user.user_id,
            following_id=followed_user.user_id
        )
        
        db_session.add(follow)
        db_session.commit()

        # Test relationships
        assert follow.follower == sample_user
        assert follow.following == followed_user
        
        # Test reverse relationships
        assert follow in sample_user.following_relationships
        assert follow in followed_user.follower_relationships

    def test_follow_cascade_on_user_deletion(self, db_session):
        """Test that follows are deleted when users are deleted."""
        # Create two users
        follower = User(
            user_name="follower",
            email="follower@example.com",
            is_private=False,
            status="active"
        )
        followed = User(
            user_name="followed",
            email="followed@example.com",
            is_private=False,
            status="active"
        )
        
        db_session.add_all([follower, followed])
        db_session.commit()

        # Create follow relationship
        follow = Follow(
            follower_id=follower.user_id,
            following_id=followed.user_id
        )
        
        db_session.add(follow)
        db_session.commit()
        
        follow_id = (follow.follower_id, follow.following_id)

        # Delete the follower user
        db_session.delete(follower)
        db_session.commit()

        # Verify follow relationship is deleted
        deleted_follow = db_session.query(Follow).filter(
            Follow.follower_id == follow_id[0],
            Follow.following_id == follow_id[1]
        ).first()
        
        assert deleted_follow is None

    def test_follow_constraint_with_foreign_key_violation(self, db_session):
        """Test foreign key constraint when referencing non-existent user."""
        non_existent_user_id = uuid.uuid4()
        
        follow = Follow(
            follower_id=non_existent_user_id,
            following_id=non_existent_user_id
        )
        
        db_session.add(follow)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_follow_repr(self, db_session, sample_user):
        """Test string representation of Follow model."""
        followed_user = User(
            user_name="followed_user",
            email="followed@example.com",
            is_private=False,
            status="active"
        )
        db_session.add(followed_user)
        db_session.commit()

        follow = Follow(
            follower_id=sample_user.user_id,
            following_id=followed_user.user_id,
            status="accepted"
        )

        repr_str = repr(follow)
        assert "Follow(" in repr_str
        assert str(sample_user.user_id) in repr_str
        assert str(followed_user.user_id) in repr_str
        assert "accepted" in repr_str

    def test_follow_multiple_users_following_same_user(self, db_session):
        """Test multiple users can follow the same user."""
        # Create one user to be followed
        popular_user = User(
            user_name="popular_user",
            email="popular@example.com",
            is_private=False,
            status="active"
        )
        
        # Create multiple followers
        follower1 = User(
            user_name="follower1",
            email="follower1@example.com",
            is_private=False,
            status="active"
        )
        
        follower2 = User(
            user_name="follower2",
            email="follower2@example.com",
            is_private=False,
            status="active"
        )
        
        db_session.add_all([popular_user, follower1, follower2])
        db_session.commit()

        # Create follow relationships
        follow1 = Follow(
            follower_id=follower1.user_id,
            following_id=popular_user.user_id
        )
        
        follow2 = Follow(
            follower_id=follower2.user_id,
            following_id=popular_user.user_id
        )
        
        db_session.add_all([follow1, follow2])
        db_session.commit()

        # Verify both follows exist
        assert len(popular_user.follower_relationships) == 2
        assert follow1 in popular_user.follower_relationships
        assert follow2 in popular_user.follower_relationships

    def test_follow_user_following_multiple_users(self, db_session):
        """Test one user can follow multiple users."""
        # Create one follower
        follower = User(
            user_name="follower",
            email="follower@example.com",
            is_private=False,
            status="active"
        )
        
        # Create multiple users to follow
        followed1 = User(
            user_name="followed1",
            email="followed1@example.com",
            is_private=False,
            status="active"
        )
        
        followed2 = User(
            user_name="followed2",
            email="followed2@example.com",
            is_private=False,
            status="active"
        )
        
        db_session.add_all([follower, followed1, followed2])
        db_session.commit()

        # Create follow relationships
        follow1 = Follow(
            follower_id=follower.user_id,
            following_id=followed1.user_id
        )
        
        follow2 = Follow(
            follower_id=follower.user_id,
            following_id=followed2.user_id
        )
        
        db_session.add_all([follow1, follow2])
        db_session.commit()

        # Verify both follows exist
        assert len(follower.following_relationships) == 2
        assert follow1 in follower.following_relationships
        assert follow2 in follower.following_relationships
