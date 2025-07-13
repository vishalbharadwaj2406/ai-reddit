"""
Conversation Model Tests

Comprehensive test suite for the Conversation model.
Tests cover:
- Model creation and validation
- User relationships
- Database constraints
- Helper methods
- Forking functionality
- Timestamps and status management
"""

import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models.conversation import Conversation


class TestConversationModel:
    """Comprehensive tests for Conversation model."""
    
    def test_conversation_creation_basic(self, db_session, conversation_user):
        """Test basic conversation creation with minimal fields."""
        conversation = Conversation(
            user_id=conversation_user.user_id,
            title="Test Conversation"
        )
        
        db_session.add(conversation)
        db_session.commit()
        
        # Verify conversation was created
        assert conversation.conversation_id is not None
        assert conversation.user_id == conversation_user.user_id
        assert conversation.title == "Test Conversation"
        assert conversation.forked_from is None  # Not forked
        assert conversation.status == "active"  # Default value
        assert conversation.created_at is not None
        assert conversation.updated_at is not None
    
    def test_conversation_creation_complete(self, db_session, conversation_user):
        """Test conversation creation with all fields."""
        conversation = Conversation(
            user_id=conversation_user.user_id,
            title="Complete Conversation",
            forked_from=None,  # Will test forking separately
            status="active"
        )
        
        db_session.add(conversation)
        db_session.commit()
        
        # Verify all fields
        assert conversation.user_id == conversation_user.user_id
        assert conversation.title == "Complete Conversation"
        assert conversation.forked_from is None
        assert conversation.status == "active"
    
    def test_conversation_user_relationship(self, db_session, conversation_user):
        """Test conversation belongs to user (foreign key relationship)."""
        conversation = Conversation(
            user_id=conversation_user.user_id,
            title="Relationship Test"
        )
        
        db_session.add(conversation)
        db_session.commit()
        
        # Test foreign key relationship
        assert conversation.user_id == conversation_user.user_id
        
        # Test SQLAlchemy relationship (when we add it)
        # assert conversation.user == conversation_user
    
    def test_conversation_without_user_fails(self, db_session):
        """Test that conversation requires a valid user_id."""
        fake_user_id = uuid.uuid4()
        
        conversation = Conversation(
            user_id=fake_user_id,
            title="Invalid User Test"
        )
        
        db_session.add(conversation)
        
        # Should fail due to foreign key constraint
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_conversation_title_required(self, db_session, conversation_user):
        """Test that conversation title is required."""
        conversation = Conversation(
            user_id=conversation_user.user_id,
            title=None  # Should fail
        )
        
        db_session.add(conversation)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_conversation_helper_methods(self, db_session, conversation_user):
        """Test conversation helper methods."""
        conversation = Conversation(
            user_id=conversation_user.user_id,
            title="Helper Test"
        )
        db_session.add(conversation)
        db_session.commit()
        
        # Test helper methods
        assert conversation.is_active is True
        assert conversation.is_forked is False
        assert conversation.get_display_title() == "Helper Test"
        
        # Test with archived status
        conversation.status = "archived"
        assert conversation.is_active is False
    
    def test_conversation_forked_relationship(self, db_session, conversation_user):
        """Test conversation can be forked from a post."""
        # This test will be enhanced when we have Post model
        # For now, test the forked_from field accepts UUID
        fake_post_id = uuid.uuid4()
        
        conversation = Conversation(
            user_id=conversation_user.user_id,
            title="Forked Conversation",
            forked_from=fake_post_id
        )
        
        db_session.add(conversation)
        db_session.commit()
        
        # Verify forked_from is stored correctly
        assert conversation.forked_from == fake_post_id
        assert conversation.is_forked is True
    
    def test_conversation_string_representations(self, db_session, conversation_user):
        """Test __str__ and __repr__ methods."""
        conversation = Conversation(
            user_id=conversation_user.user_id,
            title="String Test"
        )
        db_session.add(conversation)
        db_session.commit()
        
        # Test string representations
        assert str(conversation) == "String Test"
        assert repr(conversation) == f"<Conversation(id={conversation.conversation_id}, title=String Test)>"
    
    def test_conversation_timestamps(self, db_session, conversation_user):
        """Test that timestamps are set correctly."""
        conversation = Conversation(
            user_id=conversation_user.user_id,
            title="Timestamp Test"
        )
        
        # Store creation time in UTC to match database (with small buffer)
        before_creation = datetime.now(timezone.utc)
        
        db_session.add(conversation)
        db_session.commit()
        
        after_creation = datetime.now(timezone.utc)
        
        # Verify timestamps are set and reasonable (allow for small timing differences)
        assert conversation.created_at is not None
        assert conversation.updated_at is not None
        # Allow for database timestamps to be slightly different due to timing
        assert abs((conversation.created_at - before_creation).total_seconds()) < 5  # Within 5 seconds
        assert abs((conversation.updated_at - before_creation).total_seconds()) < 5  # Within 5 seconds
        
        # Test updated_at changes on update
        original_updated_at = conversation.updated_at
        conversation.title = "Updated Title"
        db_session.commit()
        
        # updated_at should have changed
        assert conversation.updated_at > original_updated_at
    
    def test_conversation_status_validation(self, db_session, conversation_user):
        """Test conversation status field validation."""
        # Test valid statuses
        valid_statuses = ["active", "archived", "deleted"]
        
        for status in valid_statuses:
            conversation = Conversation(
                user_id=conversation_user.user_id,
                title=f"Status Test {status}",
                status=status
            )
            db_session.add(conversation)
            db_session.commit()
            
            assert conversation.status == status
            db_session.delete(conversation)
            db_session.commit()
    
    def test_multiple_conversations_per_user(self, db_session, conversation_user):
        """Test that a user can have multiple conversations."""
        conversations = []
        
        for i in range(3):
            conv = Conversation(
                user_id=conversation_user.user_id,
                title=f"Conversation {i+1}"
            )
            conversations.append(conv)
            db_session.add(conv)
        
        db_session.commit()
        
        # Verify all conversations were created
        for conv in conversations:
            assert conv.conversation_id is not None
            assert conv.user_id == conversation_user.user_id
        
        # Verify they are distinct
        conversation_ids = [conv.conversation_id for conv in conversations]
        assert len(set(conversation_ids)) == 3  # All unique
    
    def test_conversation_cascade_behavior(self, db_session, conversation_user):
        """Test what happens when user is deleted (cascade behavior)."""
        conversation = Conversation(
            user_id=conversation_user.user_id,
            title="Cascade Test"
        )
        
        db_session.add(conversation)
        db_session.commit()
        
        # Store the user_id for verification
        user_id = conversation_user.user_id
        conversation_id = conversation.conversation_id
        
        # Clear the session to avoid SQLAlchemy's deletion order optimization
        db_session.expunge(conversation)
        
        # Delete the user directly with raw SQL to test the actual constraint
        # This should fail due to foreign key constraint (RESTRICT)
        with pytest.raises(IntegrityError):
            db_session.execute(
                text("DELETE FROM users WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            db_session.commit()
