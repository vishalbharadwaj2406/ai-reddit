"""
Post Model Tests

Test suite for the Post model implementation.

This file contains comprehensive tests for the Post model which handles
shareable content created from conversations. Posts are the main content
that users can interact with through reactions, comments, and shares.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from uuid import uuid4
from datetime import datetime, timezone

from app.models.post import Post


class TestPostModel:
    """Tests for Post model."""
    
    def test_post_creation_basic(self, db_session, sample_conversation):
        """Test basic post creation with required fields."""
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title="My First Post",
            content="This is the content of my first post. It's created from a conversation."
        )
        
        db_session.add(post)
        db_session.commit()
        
        # Verify post was created with correct values
        assert post.post_id is not None
        assert post.user_id == sample_conversation.user_id
        assert post.conversation_id == sample_conversation.conversation_id
        assert post.title == "My First Post"
        assert post.content == "This is the content of my first post. It's created from a conversation."
        assert post.is_conversation_visible is False  # Default value
        assert post.edited is False  # Default value
        assert post.status == "active"  # Default value
        assert post.created_at is not None
        assert post.updated_at is not None
    
    def test_post_creation_complete(self, db_session, sample_conversation):
        """Test post creation with all fields specified."""
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title="Complete Post",
            content="This post has all fields specified.",
            is_conversation_visible=True,
            edited=True,
            status="active"
        )
        
        db_session.add(post)
        db_session.commit()
        
        assert post.is_conversation_visible is True
        assert post.edited is True
        assert post.status == "active"
    
    def test_post_user_relationship(self, db_session, sample_conversation):
        """Test post belongs to user (foreign key relationship)."""
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title="User Relationship Test",
            content="Testing user relationship"
        )
        
        db_session.add(post)
        db_session.commit()
        
        # Verify the foreign key relationship
        assert post.user_id == sample_conversation.user_id
        
        # Test that the user_id must exist (will be enforced by foreign key)
        assert post.user_id is not None
    
    def test_post_conversation_relationship(self, db_session, sample_conversation):
        """Test post belongs to conversation (foreign key relationship)."""
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title="Conversation Relationship Test",
            content="Testing conversation relationship"
        )
        
        db_session.add(post)
        db_session.commit()
        
        # Verify the foreign key relationship
        assert post.conversation_id == sample_conversation.conversation_id
        
        # Test that the conversation_id must exist
        assert post.conversation_id is not None
    
    def test_post_without_user_fails(self, db_session, sample_conversation):
        """Test that posts require a user_id."""
        post = Post(
            user_id=None,  # Missing user
            conversation_id=sample_conversation.conversation_id,
            title="No User Post",
            content="This should fail"
        )
        
        db_session.add(post)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_post_without_conversation_fails(self, db_session, sample_conversation):
        """Test that posts require a conversation_id."""
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=None,  # Missing conversation
            title="No Conversation Post",
            content="This should fail"
        )
        
        db_session.add(post)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_post_with_invalid_user_fails(self, db_session, sample_conversation):
        """Test that posts fail with non-existent user_id."""
        invalid_user_id = uuid4()
        
        post = Post(
            user_id=invalid_user_id,
            conversation_id=sample_conversation.conversation_id,
            title="Invalid User Post",
            content="This should fail"
        )
        
        db_session.add(post)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_post_with_invalid_conversation_fails(self, db_session, sample_conversation):
        """Test that posts fail with non-existent conversation_id."""
        invalid_conversation_id = uuid4()
        
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=invalid_conversation_id,
            title="Invalid Conversation Post",
            content="This should fail"
        )
        
        db_session.add(post)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_post_title_required(self, db_session, sample_conversation):
        """Test that post title is required."""
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title=None,  # Missing title
            content="Content without title"
        )
        
        db_session.add(post)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_post_content_required(self, db_session, sample_conversation):
        """Test that post content is required."""
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title="Title Without Content",
            content=None  # Missing content
        )
        
        db_session.add(post)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_post_empty_title_fails(self, db_session, sample_conversation):
        """Test that post title cannot be empty."""
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title="",  # Empty title should fail
            content="Content with empty title"
        )
        
        db_session.add(post)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_post_empty_content_fails(self, db_session, sample_conversation):
        """Test that post content cannot be empty."""
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title="Title with Empty Content",
            content=""  # Empty content should fail
        )
        
        db_session.add(post)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_post_conversation_visibility_flag(self, db_session, sample_conversation):
        """Test is_conversation_visible flag functionality."""
        # Test default value (False)
        post1 = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title="Default Visibility",
            content="Default visibility test"
        )
        db_session.add(post1)
        db_session.commit()
        
        assert post1.is_conversation_visible is False
        
        # Test explicit True value
        post2 = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title="Visible Conversation",
            content="Conversation is visible",
            is_conversation_visible=True
        )
        db_session.add(post2)
        db_session.commit()
        
        assert post2.is_conversation_visible is True
    
    def test_post_edited_flag(self, db_session, sample_conversation):
        """Test edited flag functionality."""
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title="Edit Test Post",
            content="Original content"
        )
        db_session.add(post)
        db_session.commit()
        
        # Initially not edited
        assert post.edited is False
        
        # Mark as edited
        post.edited = True
        db_session.commit()
        
        assert post.edited is True
    
    def test_post_helper_methods(self, db_session, sample_conversation):
        """Test post helper methods."""
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title="Helper Methods Test",
            content="Testing helper methods"
        )
        db_session.add(post)
        db_session.commit()
        
        # Test helper methods
        assert post.is_active is True
        assert post.has_visible_conversation is False
        
        # Test after changing values
        post.status = "archived"
        post.is_conversation_visible = True
        
        assert post.is_active is False
        assert post.has_visible_conversation is True
    
    def test_post_status_validation(self, db_session, sample_conversation):
        """Test post status field validation."""
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title="Status Test",
            content="Testing status validation",
            status="active"
        )
        db_session.add(post)
        db_session.commit()
        
        assert post.status == "active"
        
        # Test changing status
        post.status = "archived"
        db_session.commit()
        
        assert post.status == "archived"
    
    def test_post_string_representations(self, db_session, sample_conversation):
        """Test __str__ and __repr__ methods."""
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title="String Representation Test",
            content="Testing string representations"
        )
        db_session.add(post)
        db_session.commit()
        
        # Test string representations
        assert "String Representation Test" in str(post)
        assert f"Post(id={post.post_id}" in repr(post)
    
    def test_post_timestamps(self, db_session, sample_conversation):
        """Test that timestamps are set correctly."""
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title="Timestamp Test",
            content="Testing timestamps"
        )
        
        # Store creation time with some buffer
        before_creation = datetime.now(timezone.utc)
        
        db_session.add(post)
        db_session.commit()
        
        after_creation = datetime.now(timezone.utc)
        
        # Verify timestamps are set and reasonable (with 5 second buffer for timing)
        assert post.created_at is not None
        assert post.updated_at is not None
        
        # Check timestamps are within reasonable bounds (database vs Python timing)
        time_diff_created = abs((post.created_at - before_creation).total_seconds())
        time_diff_updated = abs((post.updated_at - before_creation).total_seconds())
        
        assert time_diff_created < 5  # Within 5 seconds
        assert time_diff_updated < 5  # Within 5 seconds
        
        # Test updated_at changes on modification
        original_updated_at = post.updated_at
        
        # Add a small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        post.title = "Updated Title"
        db_session.commit()
        db_session.refresh(post)
        
        assert post.updated_at > original_updated_at
    
    def test_multiple_posts_per_user(self, db_session, sample_conversation):
        """Test that users can have multiple posts."""
        posts = []
        
        for i in range(3):
            post = Post(
                user_id=sample_conversation.user_id,
                conversation_id=sample_conversation.conversation_id,
                title=f"Post {i+1}",
                content=f"Content for post {i+1}"
            )
            posts.append(post)
            db_session.add(post)
        
        db_session.commit()
        
        # Verify all posts were created with different IDs
        for post in posts:
            assert post.post_id is not None
            assert post.user_id == sample_conversation.user_id
        
        # Verify they have different IDs
        post_ids = [post.post_id for post in posts]
        assert len(set(post_ids)) == 3  # All unique
    
    def test_multiple_posts_per_conversation(self, db_session, sample_conversation):
        """Test that conversations can have multiple posts."""
        posts = []
        
        for i in range(3):
            post = Post(
                user_id=sample_conversation.user_id,
                conversation_id=sample_conversation.conversation_id,
                title=f"Conversation Post {i+1}",
                content=f"Content from conversation {i+1}"
            )
            posts.append(post)
            db_session.add(post)
        
        db_session.commit()
        
        # Verify all posts reference the same conversation
        for post in posts:
            assert post.conversation_id == sample_conversation.conversation_id
        
        # Verify they have different IDs
        post_ids = [post.post_id for post in posts]
        assert len(set(post_ids)) == 3  # All unique
    
    def test_post_cascade_behavior(self, db_session, sample_conversation):
        """Test cascade behavior when related entities are deleted."""
        post = Post(
            user_id=sample_conversation.user_id,
            conversation_id=sample_conversation.conversation_id,
            title="Cascade Test",
            content="Testing cascade behavior"
        )
        db_session.add(post)
        db_session.commit()
        
        post_id = post.post_id
        
        # Verify post exists
        found_post = db_session.query(Post).filter(Post.post_id == post_id).first()
        assert found_post is not None
        
        # Note: We don't test actual cascade deletion since our schema uses
        # application-level handling rather than database CASCADE.
        # In real implementation, deletion would be handled by setting status
        # to "archived" rather than actual deletion.
        
        # Test archiving instead of deletion
        post.status = "archived"
        db_session.commit()
        
        archived_post = db_session.query(Post).filter(Post.post_id == post_id).first()
        assert archived_post.status == "archived"
