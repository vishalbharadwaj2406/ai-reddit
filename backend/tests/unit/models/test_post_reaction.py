"""
PostReaction Model Tests

Comprehensive test suite for the PostReaction model.
Tests cover:
- Model creation and validation
- Reaction type constraints
- User-post reaction uniqueness
- Helper methods
- String representations
"""

import pytest
import warnings
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app.models.post_reaction import PostReaction
from app.models.user import User
from app.models.post import Post


class TestPostReactionModel:
    """Comprehensive tests for PostReaction model."""
    
    def test_post_reaction_creation_basic(self, db_session, sample_user, sample_post):
        """Test basic post reaction creation."""
        reaction = PostReaction(
            user_id=sample_user.user_id,
            post_id=sample_post.post_id,
            reaction="upvote"
        )
        
        db_session.add(reaction)
        db_session.commit()
        
        # Verify reaction was created
        assert reaction.user_id == sample_user.user_id
        assert reaction.post_id == sample_post.post_id
        assert reaction.reaction == "upvote"
        assert reaction.status == "active"  # Default value
        assert reaction.created_at is not None
        assert reaction.updated_at is not None
    
    def test_all_valid_reaction_types(self, db_session, sample_user, sample_post):
        """Test all valid reaction types can be created."""
        valid_reactions = ["upvote", "downvote", "heart", "insightful", "accurate"]
        
        for i, reaction_type in enumerate(valid_reactions):
            # Create a new post for each reaction to avoid uniqueness conflicts
            from app.models.conversation import Conversation
            conversation = Conversation(
                user_id=sample_user.user_id,
                title=f"Test Conversation {i}"
            )
            db_session.add(conversation)
            db_session.commit()
            
            post = Post(
                user_id=sample_user.user_id,
                conversation_id=conversation.conversation_id,
                title=f"Test Post {i}",
                content=f"Content for reaction test {i}"
            )
            db_session.add(post)
            db_session.commit()
            
            reaction = PostReaction(
                user_id=sample_user.user_id,
                post_id=post.post_id,
                reaction=reaction_type
            )
            db_session.add(reaction)
            db_session.commit()
            
            assert reaction.reaction == reaction_type
    
    def test_invalid_reaction_type_fails(self, db_session, sample_user, sample_post):
        """Test that invalid reaction types are rejected."""
        reaction = PostReaction(
            user_id=sample_user.user_id,
            post_id=sample_post.post_id,
            reaction="invalid_reaction"
        )
        
        db_session.add(reaction)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_duplicate_user_post_reaction_fails(self, db_session, sample_user, sample_post):
        """Test that duplicate reactions from same user to same post fail."""
        # Create first reaction
        reaction1 = PostReaction(
            user_id=sample_user.user_id,
            post_id=sample_post.post_id,
            reaction="upvote"
        )
        db_session.add(reaction1)
        db_session.commit()
        
        # Try to create duplicate reaction
        reaction2 = PostReaction(
            user_id=sample_user.user_id,
            post_id=sample_post.post_id,
            reaction="downvote"
        )
        db_session.add(reaction2)
        # Suppress the expected SQLAlchemy identity warning for duplicate test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=Warning)
            with pytest.raises(IntegrityError):
                db_session.commit()
    
    def test_reaction_update_allowed(self, db_session, sample_user, sample_post):
        """Test that existing reactions can be updated."""
        reaction = PostReaction(
            user_id=sample_user.user_id,
            post_id=sample_post.post_id,
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
    
    def test_post_reaction_user_relationship(self, db_session, sample_user, sample_post):
        """Test post reaction-user relationship."""
        reaction = PostReaction(
            user_id=sample_user.user_id,
            post_id=sample_post.post_id,
            reaction="insightful"
        )
        db_session.add(reaction)
        db_session.commit()
        
        # Test relationship access
        assert reaction.user == sample_user
        assert reaction in sample_user.post_reactions
    
    def test_post_reaction_post_relationship(self, db_session, sample_user, sample_post):
        """Test post reaction-post relationship."""
        reaction = PostReaction(
            user_id=sample_user.user_id,
            post_id=sample_post.post_id,
            reaction="accurate"
        )
        db_session.add(reaction)
        db_session.commit()
        
        # Test relationship access
        assert reaction.post == sample_post
        assert reaction in sample_post.reactions
    
    def test_reaction_without_user_fails(self, db_session, sample_post):
        """Test that reaction creation fails without a valid user."""
        reaction = PostReaction(
            user_id=None,  # Invalid
            post_id=sample_post.post_id,
            reaction="upvote"
        )
        
        db_session.add(reaction)
        # Suppress expected SQLAlchemy warning for validation test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=Warning)
            with pytest.raises(IntegrityError):
                db_session.commit()
    
    def test_reaction_without_post_fails(self, db_session, sample_user):
        """Test that reaction creation fails without a valid post."""
        reaction = PostReaction(
            user_id=sample_user.user_id,
            post_id=None,  # Invalid
            reaction="upvote"
        )
        
        db_session.add(reaction)
        # Suppress expected SQLAlchemy warning for validation test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=Warning)
            with pytest.raises(IntegrityError):
                db_session.commit()
    
    def test_reaction_helper_methods(self, db_session, sample_user, sample_post):
        """Test reaction helper methods."""
        # Test positive reactions
        positive_reactions = ["upvote", "heart", "insightful", "accurate"]
        for reaction_type in positive_reactions:
            # Create new post for each test
            from app.models.conversation import Conversation
            conversation = Conversation(
                user_id=sample_user.user_id,
                title=f"Test Conversation for {reaction_type}"
            )
            db_session.add(conversation)
            db_session.commit()
            
            post = Post(
                user_id=sample_user.user_id,
                conversation_id=conversation.conversation_id,
                title=f"Test Post for {reaction_type}",
                content="Test content"
            )
            db_session.add(post)
            db_session.commit()
            
            reaction = PostReaction(
                user_id=sample_user.user_id,
                post_id=post.post_id,
                reaction=reaction_type
            )
            db_session.add(reaction)
            db_session.commit()
            
            assert reaction.is_positive is True
            assert reaction.is_active is True
        
        # Test negative reaction
        from app.models.conversation import Conversation
        conversation = Conversation(
            user_id=sample_user.user_id,
            title="Test Conversation for downvote"
        )
        db_session.add(conversation)
        db_session.commit()
        
        post = Post(
            user_id=sample_user.user_id,
            conversation_id=conversation.conversation_id,
            title="Test Post for downvote",
            content="Test content"
        )
        db_session.add(post)
        db_session.commit()
        
        downvote = PostReaction(
            user_id=sample_user.user_id,
            post_id=post.post_id,
            reaction="downvote"
        )
        db_session.add(downvote)
        db_session.commit()
        
        assert downvote.is_positive is False
        assert downvote.is_quality_signal is False
    
    def test_quality_signal_reactions(self, db_session, sample_user, sample_post):
        """Test quality signal detection."""
        # Test quality signal reactions
        quality_reactions = ["insightful", "accurate"]
        for reaction_type in quality_reactions:
            # Create new post for each test
            from app.models.conversation import Conversation
            conversation = Conversation(
                user_id=sample_user.user_id,
                title=f"Test Conversation for {reaction_type}"
            )
            db_session.add(conversation)
            db_session.commit()
            
            post = Post(
                user_id=sample_user.user_id,
                conversation_id=conversation.conversation_id,
                title=f"Test Post for {reaction_type}",
                content="Test content"
            )
            db_session.add(post)
            db_session.commit()
            
            reaction = PostReaction(
                user_id=sample_user.user_id,
                post_id=post.post_id,
                reaction=reaction_type
            )
            db_session.add(reaction)
            db_session.commit()
            
            assert reaction.is_quality_signal is True
    
    def test_get_valid_reactions_class_method(self):
        """Test the get_valid_reactions class method."""
        valid_reactions = PostReaction.get_valid_reactions()
        expected_reactions = ["upvote", "downvote", "heart", "insightful", "accurate"]
        
        assert valid_reactions == expected_reactions
        assert len(valid_reactions) == 5
    
    def test_reaction_status_validation(self, db_session, sample_user, sample_post):
        """Test reaction status management."""
        reaction = PostReaction(
            user_id=sample_user.user_id,
            post_id=sample_post.post_id,
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
    
    def test_reaction_string_representations(self, db_session, sample_user, sample_post):
        """Test string representation methods."""
        reaction = PostReaction(
            user_id=sample_user.user_id,
            post_id=sample_post.post_id,
            reaction="heart"
        )
        db_session.add(reaction)
        db_session.commit()
        
        # Test __repr__
        repr_str = repr(reaction)
        assert "PostReaction" in repr_str
        assert str(reaction.user_id) in repr_str
        assert str(reaction.post_id) in repr_str
        assert "heart" in repr_str
        
        # Test __str__
        str_repr = str(reaction)
        assert "reacted" in str_repr
        assert "heart" in str_repr
    
    def test_reaction_timestamps(self, db_session, sample_user, sample_post):
        """Test that timestamps are set correctly."""
        before_creation = datetime.now(timezone.utc)
        
        reaction = PostReaction(
            user_id=sample_user.user_id,
            post_id=sample_post.post_id,
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
    
    def test_multiple_users_react_to_same_post(self, db_session, sample_post):
        """Test that multiple users can react to the same post."""
        # Create additional users
        users = []
        for i in range(3):
            user = User(
                user_name=f"reactor_user_{i}",
                email=f"reactor{i}@example.com"
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()
        
        # Each user reacts to the same post
        reactions = []
        reaction_types = ["upvote", "heart", "insightful"]
        for i, user in enumerate(users):
            reaction = PostReaction(
                user_id=user.user_id,
                post_id=sample_post.post_id,
                reaction=reaction_types[i]
            )
            reactions.append(reaction)
        
        db_session.add_all(reactions)
        db_session.commit()
        
        # Verify all reactions are linked to the post
        assert len(sample_post.reactions) >= 3
        for reaction in reactions:
            assert reaction in sample_post.reactions
