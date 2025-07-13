"""
Tests for PostView model.

Tests user engagement tracking for posts with composite primary key
design supporting multiple views per user-post combination.
"""

import pytest
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import IntegrityError
from app.models.post_view import PostView
from app.models.user import User
from app.models.post import Post
from app.models.conversation import Conversation


class TestPostView:
    """Test PostView model functionality."""

    def test_post_view_creation(self, db_session):
        """Test basic PostView creation with required fields."""
        # Create required parent objects
        user = User(user_name="viewer", email="viewer@test.com")
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

        # Create PostView
        view_time = datetime.now(timezone.utc)
        post_view = PostView(
            user_id=user.user_id,
            post_id=post.post_id,
            viewed_at=view_time
        )
        
        db_session.add(post_view)
        db_session.commit()

        # Verify creation
        assert post_view.user_id == user.user_id
        assert post_view.post_id == post.post_id
        assert post_view.viewed_at == view_time
        assert post_view.status == "active"
        assert post_view.is_active is True

    def test_post_view_composite_primary_key(self, db_session):
        """Test that PostView uses composite primary key with viewed_at."""
        user = User(user_name="viewer", email="viewer@test.com")
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

        # Create first view
        view1_time = datetime.now(timezone.utc)
        post_view1 = PostView(
            user_id=user.user_id,
            post_id=post.post_id,
            viewed_at=view1_time
        )
        
        # Create second view (same user and post, different time)
        view2_time = view1_time + timedelta(hours=1)
        post_view2 = PostView(
            user_id=user.user_id,
            post_id=post.post_id,
            viewed_at=view2_time
        )
        
        db_session.add_all([post_view1, post_view2])
        db_session.commit()

        # Both views should be saved successfully
        views = db_session.query(PostView).filter_by(
            user_id=user.user_id,
            post_id=post.post_id
        ).all()
        assert len(views) == 2

    def test_duplicate_view_same_timestamp_fails(self, db_session):
        """Test that duplicate views with same timestamp fail."""
        user = User(user_name="viewer", email="viewer@test.com")
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

        # Create first view
        view_time = datetime.now(timezone.utc)
        post_view1 = PostView(
            user_id=user.user_id,
            post_id=post.post_id,
            viewed_at=view_time
        )
        
        # Create duplicate view (same user, post, and timestamp)
        post_view2 = PostView(
            user_id=user.user_id,
            post_id=post.post_id,
            viewed_at=view_time
        )
        
        db_session.add_all([post_view1, post_view2])
        
        # Should raise integrity error due to duplicate primary key
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_post_view_relationships(self, db_session):
        """Test PostView relationships with User and Post."""
        user = User(user_name="viewer", email="viewer@test.com")
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

        # Create PostView
        post_view = PostView(
            user_id=user.user_id,
            post_id=post.post_id,
            viewed_at=datetime.now(timezone.utc)
        )
        
        db_session.add(post_view)
        db_session.commit()

        # Test relationships
        assert post_view.user == user
        assert post_view.post == post
        assert post_view in user.post_views
        assert post_view in post.post_views

    def test_post_view_foreign_key_constraints(self, db_session):
        """Test foreign key constraints are enforced."""
        # Try to create PostView with non-existent user_id
        non_existent_user_id = uuid.uuid4()
        non_existent_post_id = uuid.uuid4()
        
        with pytest.raises(IntegrityError):
            post_view = PostView(
                user_id=non_existent_user_id,  # Non-existent user UUID
                post_id=non_existent_post_id,  # Non-existent post UUID  
                viewed_at=datetime.now(timezone.utc)
            )
            db_session.add(post_view)
            db_session.commit()

        db_session.rollback()

        # Try to create PostView with valid user but non-existent post
        user = User(user_name="viewer", email="viewer@test.com")
        db_session.add(user)
        db_session.commit()

        with pytest.raises(IntegrityError):
            post_view = PostView(
                user_id=user.user_id,
                post_id=non_existent_post_id,  # Non-existent post UUID
                viewed_at=datetime.now(timezone.utc)
            )
            db_session.add(post_view)
            db_session.commit()

    def test_view_age_property(self, db_session):
        """Test view_age property calculation."""
        user = User(user_name="viewer", email="viewer@test.com")
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

        # Create view with specific timestamp
        past_time = datetime.now(timezone.utc) - timedelta(hours=2, minutes=30)
        post_view = PostView(
            user_id=user.user_id,
            post_id=post.post_id,
            viewed_at=past_time
        )
        
        db_session.add(post_view)
        db_session.commit()

        # Check view age (should be in seconds)
        age_seconds = post_view.view_age
        assert age_seconds >= 2.5 * 3600  # At least 2.5 hours in seconds
        assert age_seconds < 3 * 3600     # Less than 3 hours in seconds

    def test_is_active_property(self, db_session):
        """Test is_active property based on archived status."""
        user = User(user_name="viewer", email="viewer@test.com")
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

        # Create active view
        post_view = PostView(
            user_id=user.user_id,
            post_id=post.post_id,
            viewed_at=datetime.now(timezone.utc)
        )
        
        db_session.add(post_view)
        db_session.commit()

        # Initially active
        assert post_view.is_active is True

        # Archive the view
        post_view.archive()
        db_session.commit()

        # Now inactive
        assert post_view.is_active is False
        assert post_view.status == "archived"

    def test_archive_method(self, db_session):
        """Test archiving a post view."""
        user = User(user_name="viewer", email="viewer@test.com")
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

        # Create view
        post_view = PostView(
            user_id=user.user_id,
            post_id=post.post_id,
            viewed_at=datetime.now(timezone.utc)
        )
        
        db_session.add(post_view)
        db_session.commit()

        # Archive the view
        post_view.archive()

        # Check archived status
        assert post_view.status == "archived"
        assert post_view.is_active is False

    def test_activate_method(self, db_session):
        """Test activating an archived post view."""
        user = User(user_name="viewer", email="viewer@test.com")
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

        # Create and archive view
        post_view = PostView(
            user_id=user.user_id,
            post_id=post.post_id,
            viewed_at=datetime.now(timezone.utc),
            status="archived"
        )
        
        db_session.add(post_view)
        db_session.commit()

        # Activate the view
        post_view.activate()

        # Check activated status
        assert post_view.status == "active"
        assert post_view.is_active is True

    def test_create_view_class_method(self, db_session):
        """Test create_view class method."""
        user = User(user_name="viewer", email="viewer@test.com")
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

        # Create view using class method
        before_creation = datetime.now(timezone.utc)
        post_view = PostView.create_view(user.user_id, post.post_id)
        after_creation = datetime.now(timezone.utc)

        # Verify creation
        assert post_view.user_id == user.user_id
        assert post_view.post_id == post.post_id
        assert before_creation <= post_view.viewed_at <= after_creation
        assert post_view.status == "active"
        assert post_view.is_active is True

    def test_multiple_views_per_user_post(self, db_session):
        """Test that a user can have multiple views for the same post."""
        user = User(user_name="viewer", email="viewer@test.com")
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

        # Create multiple views at different times
        base_time = datetime.now(timezone.utc)
        views = []
        for i in range(3):
            view_time = base_time + timedelta(minutes=i*30)
            post_view = PostView(
                user_id=user.user_id,
                post_id=post.post_id,
                viewed_at=view_time
            )
            views.append(post_view)
        
        db_session.add_all(views)
        db_session.commit()

        # Verify all views exist
        saved_views = db_session.query(PostView).filter_by(
            user_id=user.user_id,
            post_id=post.post_id
        ).order_by(PostView.viewed_at).all()
        
        assert len(saved_views) == 3
        for i, view in enumerate(saved_views):
            expected_time = base_time + timedelta(minutes=i*30)
            assert view.viewed_at == expected_time

    def test_post_view_cascade_deletion(self, db_session):
        """Test that PostViews are deleted when User or Post is deleted."""
        user = User(user_name="viewer", email="viewer@test.com")
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

        # Create view
        post_view = PostView(
            user_id=user.user_id,
            post_id=post.post_id,
            viewed_at=datetime.now(timezone.utc)
        )
        
        db_session.add(post_view)
        db_session.commit()

        view_count = db_session.query(PostView).count()
        assert view_count == 1

        # Delete user - should cascade delete the view
        db_session.delete(user)
        db_session.commit()

        view_count = db_session.query(PostView).count()
        assert view_count == 0

    def test_post_view_string_representation(self, db_session):
        """Test PostView string representation methods."""
        user = User(user_name="viewer", email="viewer@test.com")
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

        # Create view
        view_time = datetime.now(timezone.utc)
        post_view = PostView(
            user_id=user.user_id,
            post_id=post.post_id,
            viewed_at=view_time
        )
        
        db_session.add(post_view)
        db_session.commit()

        # Test __repr__
        repr_str = repr(post_view)
        assert f"user_id={user.user_id}" in repr_str
        assert f"post_id={post.post_id}" in repr_str
        assert "PostView" in repr_str

        # Test __str__
        str_repr = str(post_view)
        assert "viewer" in str_repr.lower()
        assert "test post" in str_repr.lower()
        assert "viewed" in str_repr.lower()

    def test_edge_case_status_consistency(self, db_session):
        """Test that status field works correctly."""
        user = User(user_name="viewer", email="viewer@test.com")
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

        # Create view with specific status
        post_view = PostView(
            user_id=user.user_id,
            post_id=post.post_id,
            viewed_at=datetime.now(timezone.utc),
            status="archived"
        )
        
        db_session.add(post_view)
        db_session.commit()

        # is_active should be based on status field
        assert post_view.is_active is False
        assert post_view.status == "archived"
