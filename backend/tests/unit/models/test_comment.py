"""
Comment Model Tests

Comprehensive test suite for the Comment model.
Tests cover:
- Model creation and validation
- Threading relationships (replies)
- Content constraints
- Helper methods
- String representations
- Reaction relationships
"""

import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app.models.comment import Comment
from app.models.user import User
from app.models.conversation import Conversation
from app.models.post import Post


class TestCommentModel:
    """Comprehensive tests for Comment model."""
    
    def test_comment_creation_basic(self, db_session, sample_user, sample_post):
        """Test basic comment creation with minimal fields."""
        comment = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="This is a test comment"
        )
        
        db_session.add(comment)
        db_session.commit()
        
        # Verify comment was created
        assert comment.comment_id is not None
        assert comment.post_id == sample_post.post_id
        assert comment.user_id == sample_user.user_id
        assert comment.content == "This is a test comment"
        assert comment.parent_comment_id is None  # Top-level comment
        assert comment.status == "active"  # Default value
        assert comment.created_at is not None
        assert comment.updated_at is not None
    
    def test_comment_creation_reply(self, db_session, sample_user, sample_post):
        """Test creating a reply comment."""
        # Create parent comment
        parent_comment = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="Parent comment"
        )
        db_session.add(parent_comment)
        db_session.commit()
        
        # Create reply
        reply_comment = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="Reply to parent",
            parent_comment_id=parent_comment.comment_id
        )
        db_session.add(reply_comment)
        db_session.commit()
        
        # Verify reply structure
        assert reply_comment.parent_comment_id == parent_comment.comment_id
        assert reply_comment.is_reply is True
        assert parent_comment.is_reply is False
    
    def test_comment_post_relationship(self, db_session, sample_user, sample_post):
        """Test comment-post relationship."""
        comment = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="Test relationship"
        )
        db_session.add(comment)
        db_session.commit()
        
        # Test relationship access
        assert comment.post == sample_post
        assert comment in sample_post.comments
    
    def test_comment_user_relationship(self, db_session, sample_user, sample_post):
        """Test comment-user relationship."""
        comment = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="Test user relationship"
        )
        db_session.add(comment)
        db_session.commit()
        
        # Test relationship access
        assert comment.user == sample_user
        assert comment in sample_user.comments
    
    def test_comment_without_post_fails(self, db_session, sample_user):
        """Test that comment creation fails without a valid post."""
        comment = Comment(
            post_id=None,  # Invalid
            user_id=sample_user.user_id,
            content="This should fail"
        )
        
        db_session.add(comment)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_comment_without_user_fails(self, db_session, sample_post):
        """Test that comment creation fails without a valid user."""
        comment = Comment(
            post_id=sample_post.post_id,
            user_id=None,  # Invalid
            content="This should fail"
        )
        
        db_session.add(comment)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_comment_content_required(self, db_session, sample_user, sample_post):
        """Test that content is required."""
        comment = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content=None
        )
        
        db_session.add(comment)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_comment_empty_content_fails(self, db_session, sample_user, sample_post):
        """Test that empty/whitespace-only content fails."""
        comment = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="   "  # Whitespace only
        )
        
        db_session.add(comment)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_comment_threading_relationships(self, db_session, sample_user, sample_post):
        """Test parent-child comment relationships."""
        # Create parent comment
        parent = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="Parent comment"
        )
        db_session.add(parent)
        db_session.commit()
        
        # Create multiple replies
        reply1 = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="First reply",
            parent_comment_id=parent.comment_id
        )
        reply2 = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="Second reply",
            parent_comment_id=parent.comment_id
        )
        db_session.add_all([reply1, reply2])
        db_session.commit()
        
        # Test parent-child relationships
        assert len(parent.replies) == 2
        assert reply1 in parent.replies
        assert reply2 in parent.replies
        assert reply1.parent_comment == parent
        assert reply2.parent_comment == parent
    
    def test_comment_helper_methods(self, db_session, sample_user, sample_post):
        """Test comment helper methods."""
        # Create parent comment
        parent = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="Parent comment"
        )
        db_session.add(parent)
        db_session.commit()
        
        # Create reply
        reply = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="Reply comment",
            parent_comment_id=parent.comment_id
        )
        db_session.add(reply)
        db_session.commit()
        
        # Test helper methods
        assert parent.is_reply is False
        assert reply.is_reply is True
        assert parent.is_active is True
        assert reply.can_be_edited_by(sample_user.user_id) is True
    
    def test_comment_status_validation(self, db_session, sample_user, sample_post):
        """Test comment status management."""
        comment = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="Status test comment"
        )
        db_session.add(comment)
        db_session.commit()
        
        # Test default status
        assert comment.is_active is True
        assert comment.status == "active"
        
        # Test status changes
        comment.status = "archived"
        db_session.commit()
        assert comment.status == "archived"
        assert comment.is_active is False
        
        comment.status = "active"
        db_session.commit()
        assert comment.status == "active"
        assert comment.is_active is True
    
    def test_comment_string_representations(self, db_session, sample_user, sample_post):
        """Test string representation methods."""
        comment = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="This is a test comment for string representation"
        )
        db_session.add(comment)
        db_session.commit()
        
        # Test __repr__
        repr_str = repr(comment)
        assert "Comment" in repr_str
        assert str(comment.comment_id) in repr_str
        
        # Test __str__
        str_repr = str(comment)
        assert "Comment by" in str_repr
        assert "This is a test comment" in str_repr
    
    def test_comment_timestamps(self, db_session, sample_user, sample_post):
        """Test that timestamps are set correctly."""
        before_creation = datetime.now(timezone.utc)
        
        comment = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="Timestamp test"
        )
        db_session.add(comment)
        db_session.commit()
        
        after_creation = datetime.now(timezone.utc)
        
        # Verify timestamps are within expected range
        assert before_creation <= comment.created_at <= after_creation
        assert before_creation <= comment.updated_at <= after_creation
        
        # Test that updated_at changes on modification
        original_updated = comment.updated_at
        comment.content = "Modified content"
        db_session.commit()
        
        assert comment.updated_at > original_updated
    
    def test_multiple_comments_per_post(self, db_session, sample_user, sample_post):
        """Test that multiple comments can be created for a single post."""
        comments = []
        for i in range(3):
            comment = Comment(
                post_id=sample_post.post_id,
                user_id=sample_user.user_id,
                content=f"Comment {i+1}"
            )
            comments.append(comment)
        
        db_session.add_all(comments)
        db_session.commit()
        
        # Verify all comments are linked to the post
        assert len(sample_post.comments) >= 3
        for comment in comments:
            assert comment in sample_post.comments
    
    def test_comment_cascade_behavior(self, db_session, sample_user, sample_post):
        """Test cascade deletion behavior for comment threads."""
        # Create parent comment
        parent = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="Parent comment"
        )
        db_session.add(parent)
        db_session.commit()
        
        # Create reply
        reply = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="Reply comment",
            parent_comment_id=parent.comment_id
        )
        db_session.add(reply)
        db_session.commit()
        
        reply_id = reply.comment_id
        
        # Delete parent comment
        db_session.delete(parent)
        db_session.commit()
        
        # The reply should be deleted due to cascade="all, delete-orphan"
        remaining_reply = db_session.get(Comment, reply_id)
        assert remaining_reply is None
