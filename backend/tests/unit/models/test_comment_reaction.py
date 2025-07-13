"""
CommentReaction Model Tests

Comprehensive test suite for the CommentReaction model.
Tests cover:
- Model creation and validation
- Reaction type constraints (same as PostReaction)
- User-comment reaction uniqueness
- Helper methods
- String representations
- Consistency with PostReaction behavior
"""

import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app.models.comment_reaction import CommentReaction
from app.models.comment import Comment
from app.models.user import User


class TestCommentReactionModel:
    """Comprehensive tests for CommentReaction model."""
    
    def test_comment_reaction_creation_basic(self, db_session, sample_user, sample_comment):
        """Test basic comment reaction creation."""
        reaction = CommentReaction(
            user_id=sample_user.user_id,
            comment_id=sample_comment.comment_id,
            reaction="upvote"
        )
        
        db_session.add(reaction)
        db_session.commit()
        
        # Verify reaction was created
        assert reaction.user_id == sample_user.user_id
        assert reaction.comment_id == sample_comment.comment_id
        assert reaction.reaction == "upvote"
        assert reaction.status == "active"  # Default value
        assert reaction.created_at is not None
        assert reaction.updated_at is not None
    
    def test_all_valid_reaction_types(self, db_session, sample_user, sample_post):
        """Test all valid reaction types can be created."""
        valid_reactions = ["upvote", "downvote", "heart", "insightful", "accurate"]
        
        for i, reaction_type in enumerate(valid_reactions):
            # Create a new comment for each reaction to avoid uniqueness conflicts
            comment = Comment(
                post_id=sample_post.post_id,
                user_id=sample_user.user_id,
                content=f"Test comment {i} for reaction {reaction_type}"
            )
            db_session.add(comment)
            db_session.commit()
            
            reaction = CommentReaction(
                user_id=sample_user.user_id,
                comment_id=comment.comment_id,
                reaction=reaction_type
            )
            db_session.add(reaction)
            db_session.commit()
            
            assert reaction.reaction == reaction_type
    
    def test_invalid_reaction_type_fails(self, db_session, sample_user, sample_comment):
        """Test that invalid reaction types are rejected."""
        reaction = CommentReaction(
            user_id=sample_user.user_id,
            comment_id=sample_comment.comment_id,
            reaction="invalid_reaction"
        )
        
        db_session.add(reaction)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_duplicate_user_comment_reaction_fails(self, db_session, sample_user, sample_comment):
        """Test that duplicate reactions from same user to same comment fail."""
        # Create first reaction
        reaction1 = CommentReaction(
            user_id=sample_user.user_id,
            comment_id=sample_comment.comment_id,
            reaction="upvote"
        )
        db_session.add(reaction1)
        db_session.commit()
        
        # Try to create duplicate reaction
        reaction2 = CommentReaction(
            user_id=sample_user.user_id,
            comment_id=sample_comment.comment_id,
            reaction="downvote"
        )
        db_session.add(reaction2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_reaction_update_allowed(self, db_session, sample_user, sample_comment):
        """Test that existing reactions can be updated."""
        reaction = CommentReaction(
            user_id=sample_user.user_id,
            comment_id=sample_comment.comment_id,
            reaction="upvote"
        )
        db_session.add(reaction)
        db_session.commit()
        
        # Update reaction type
        original_updated = reaction.updated_at
        reaction.reaction = "heart"
        db_session.commit()
        
        # Verify update
        assert reaction.reaction == "heart"
        assert reaction.updated_at > original_updated
    
    def test_comment_reaction_user_relationship(self, db_session, sample_user, sample_comment):
        """Test comment reaction-user relationship."""
        reaction = CommentReaction(
            user_id=sample_user.user_id,
            comment_id=sample_comment.comment_id,
            reaction="insightful"
        )
        db_session.add(reaction)
        db_session.commit()
        
        # Test relationship access
        assert reaction.user == sample_user
        assert reaction in sample_user.comment_reactions
    
    def test_comment_reaction_comment_relationship(self, db_session, sample_user, sample_comment):
        """Test comment reaction-comment relationship."""
        reaction = CommentReaction(
            user_id=sample_user.user_id,
            comment_id=sample_comment.comment_id,
            reaction="accurate"
        )
        db_session.add(reaction)
        db_session.commit()
        
        # Test relationship access
        assert reaction.comment == sample_comment
        assert reaction in sample_comment.reactions
    
    def test_reaction_without_user_fails(self, db_session, sample_comment):
        """Test that reaction creation fails without a valid user."""
        reaction = CommentReaction(
            user_id=None,  # Invalid
            comment_id=sample_comment.comment_id,
            reaction="upvote"
        )
        
        db_session.add(reaction)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_reaction_without_comment_fails(self, db_session, sample_user):
        """Test that reaction creation fails without a valid comment."""
        reaction = CommentReaction(
            user_id=sample_user.user_id,
            comment_id=None,  # Invalid
            reaction="upvote"
        )
        
        db_session.add(reaction)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_reaction_helper_methods(self, db_session, sample_user, sample_post):
        """Test reaction helper methods (should match PostReaction behavior)."""
        # Test positive reactions
        positive_reactions = ["upvote", "heart", "insightful", "accurate"]
        for i, reaction_type in enumerate(positive_reactions):
            # Create new comment for each test
            comment = Comment(
                post_id=sample_post.post_id,
                user_id=sample_user.user_id,
                content=f"Test comment {i} for {reaction_type}"
            )
            db_session.add(comment)
            db_session.commit()
            
            reaction = CommentReaction(
                user_id=sample_user.user_id,
                comment_id=comment.comment_id,
                reaction=reaction_type
            )
            db_session.add(reaction)
            db_session.commit()
            
            assert reaction.is_positive is True
            assert reaction.is_active is True
        
        # Test negative reaction
        comment = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="Test comment for downvote"
        )
        db_session.add(comment)
        db_session.commit()
        
        downvote = CommentReaction(
            user_id=sample_user.user_id,
            comment_id=comment.comment_id,
            reaction="downvote"
        )
        db_session.add(downvote)
        db_session.commit()
        
        assert downvote.is_positive is False
        assert downvote.is_quality_signal is False
    
    def test_quality_signal_reactions(self, db_session, sample_user, sample_post):
        """Test quality signal detection (should match PostReaction behavior)."""
        # Test quality signal reactions
        quality_reactions = ["insightful", "accurate"]
        for i, reaction_type in enumerate(quality_reactions):
            # Create new comment for each test
            comment = Comment(
                post_id=sample_post.post_id,
                user_id=sample_user.user_id,
                content=f"Test comment {i} for {reaction_type}"
            )
            db_session.add(comment)
            db_session.commit()
            
            reaction = CommentReaction(
                user_id=sample_user.user_id,
                comment_id=comment.comment_id,
                reaction=reaction_type
            )
            db_session.add(reaction)
            db_session.commit()
            
            assert reaction.is_quality_signal is True
    
    def test_get_valid_reactions_class_method(self):
        """Test the get_valid_reactions class method."""
        valid_reactions = CommentReaction.get_valid_reactions()
        expected_reactions = ["upvote", "downvote", "heart", "insightful", "accurate"]
        
        assert valid_reactions == expected_reactions
        assert len(valid_reactions) == 5
    
    def test_reaction_consistency_with_post_reactions(self):
        """Test that CommentReaction and PostReaction have consistent behavior."""
        from app.models.post_reaction import PostReaction
        
        # Both should have same valid reactions
        comment_reactions = CommentReaction.get_valid_reactions()
        post_reactions = PostReaction.get_valid_reactions()
        assert comment_reactions == post_reactions
    
    def test_reaction_status_validation(self, db_session, sample_user, sample_comment):
        """Test reaction status management."""
        reaction = CommentReaction(
            user_id=sample_user.user_id,
            comment_id=sample_comment.comment_id,
            reaction="upvote"
        )
        db_session.add(reaction)
        db_session.commit()
        
        # Test default status
        assert reaction.is_active is True
        assert reaction.status == "active"
        
        # Test status changes
        reaction.status = "archived"
        db_session.commit()
        assert reaction.status == "archived"
        assert reaction.is_active is False
        
        reaction.status = "active"
        db_session.commit()
        assert reaction.status == "active"
        assert reaction.is_active is True
    
    def test_reaction_string_representations(self, db_session, sample_user, sample_comment):
        """Test string representation methods."""
        reaction = CommentReaction(
            user_id=sample_user.user_id,
            comment_id=sample_comment.comment_id,
            reaction="heart"
        )
        db_session.add(reaction)
        db_session.commit()
        
        # Test __repr__
        repr_str = repr(reaction)
        assert "CommentReaction" in repr_str
        assert str(reaction.user_id) in repr_str
        assert str(reaction.comment_id) in repr_str
        assert "heart" in repr_str
        
        # Test __str__
        str_repr = str(reaction)
        assert "reacted" in str_repr
        assert "heart" in str_repr
    
    def test_reaction_timestamps(self, db_session, sample_user, sample_comment):
        """Test that timestamps are set correctly."""
        before_creation = datetime.now(timezone.utc)
        
        reaction = CommentReaction(
            user_id=sample_user.user_id,
            comment_id=sample_comment.comment_id,
            reaction="upvote"
        )
        db_session.add(reaction)
        db_session.commit()
        
        after_creation = datetime.now(timezone.utc)
        
        # Verify timestamps are within expected range
        assert before_creation <= reaction.created_at <= after_creation
        assert before_creation <= reaction.updated_at <= after_creation
        
        # Test that updated_at changes on modification
        original_updated = reaction.updated_at
        reaction.reaction = "downvote"
        db_session.commit()
        
        assert reaction.updated_at > original_updated
    
    def test_multiple_users_react_to_same_comment(self, db_session, sample_comment):
        """Test that multiple users can react to the same comment."""
        # Create additional users
        users = []
        for i in range(3):
            user = User(
                user_name=f"comment_reactor_user_{i}",
                email=f"comment_reactor{i}@example.com"
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()
        
        # Each user reacts to the same comment
        reactions = []
        reaction_types = ["upvote", "heart", "insightful"]
        for i, user in enumerate(users):
            reaction = CommentReaction(
                user_id=user.user_id,
                comment_id=sample_comment.comment_id,
                reaction=reaction_types[i]
            )
            reactions.append(reaction)
        
        db_session.add_all(reactions)
        db_session.commit()
        
        # Verify all reactions are linked to the comment
        assert len(sample_comment.reactions) >= 3
        for reaction in reactions:
            assert reaction in sample_comment.reactions
    
    def test_comment_threading_with_reactions(self, db_session, sample_user, sample_post):
        """Test that reactions work properly with comment threading."""
        # Create parent comment
        parent_comment = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="Parent comment"
        )
        db_session.add(parent_comment)
        db_session.commit()
        
        # Create reply comment
        reply_comment = Comment(
            post_id=sample_post.post_id,
            user_id=sample_user.user_id,
            content="Reply comment",
            parent_comment_id=parent_comment.comment_id
        )
        db_session.add(reply_comment)
        db_session.commit()
        
        # Create different users to react
        user1 = User(user_name="reactor1", email="reactor1@example.com")
        user2 = User(user_name="reactor2", email="reactor2@example.com")
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # React to parent comment
        parent_reaction = CommentReaction(
            user_id=user1.user_id,
            comment_id=parent_comment.comment_id,
            reaction="upvote"
        )
        
        # React to reply comment
        reply_reaction = CommentReaction(
            user_id=user2.user_id,
            comment_id=reply_comment.comment_id,
            reaction="heart"
        )
        
        db_session.add_all([parent_reaction, reply_reaction])
        db_session.commit()
        
        # Verify reactions are properly linked
        assert parent_reaction in parent_comment.reactions
        assert reply_reaction in reply_comment.reactions
        assert parent_reaction not in reply_comment.reactions
        assert reply_reaction not in parent_comment.reactions
