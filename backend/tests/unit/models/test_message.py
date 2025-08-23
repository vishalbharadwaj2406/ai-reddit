"""
Message Model Tests

Comprehensive test suite for the Message model.
Tests cover:
- Model creation and validation
- Conversation and User relationships
- Role validation (user, assistant, system)
- Content requirements
- AI vs Human message handling
- Database constraints
- Helper methods
- Timestamps and status management
"""

import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from app.models.message import Message


class TestMessageModel:
    """Comprehensive tests for Message model."""
    
    def test_message_creation_basic(self, db_session, sample_conversation):
        """Test basic message creation with minimal fields."""
        message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=sample_conversation.user_id,  # Human message
            role="user",
            content="Hello, this is my first message!"
        )
        
        db_session.add(message)
        db_session.commit()
        
        # Verify message was created
        assert message.message_id is not None
        assert message.conversation_id == sample_conversation.conversation_id
        assert message.user_id == sample_conversation.user_id
        assert message.role == "user"
        assert message.content == "Hello, this is my first message!"
        assert message.is_blog is False  # Default value
        assert message.status == "active"  # Default value
        assert message.created_at is not None
        assert message.updated_at is not None
    
    def test_message_creation_ai_assistant(self, db_session, sample_conversation):
        """Test AI assistant message creation (null user_id)."""
        message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=None,  # AI message
            role="assistant",
            content="Hello! I'm an AI assistant. How can I help you today?"
        )
        
        db_session.add(message)
        db_session.commit()
        
        # Verify AI message was created
        assert message.message_id is not None
        assert message.conversation_id == sample_conversation.conversation_id
        assert message.user_id is None  # AI message
        assert message.role == "assistant"
        assert message.content == "Hello! I'm an AI assistant. How can I help you today?"
        assert message.status == "active"
    
    def test_message_creation_system(self, db_session, sample_conversation):
        """Test system message creation."""
        message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=None,  # System message
            role="system",
            content="This conversation was created from a forked post."
        )
        
        db_session.add(message)
        db_session.commit()
        
        # Verify system message was created
        assert message.role == "system"
        assert message.user_id is None
        assert message.content == "This conversation was created from a forked post."
    
    def test_message_conversation_relationship(self, db_session, sample_conversation):
        """Test message belongs to conversation (foreign key relationship)."""
        message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=sample_conversation.user_id,
            role="user",
            content="Testing conversation relationship"
        )
        
        db_session.add(message)
        db_session.commit()
        
        # Test foreign key relationship
        assert message.conversation_id == sample_conversation.conversation_id
        
        # Test SQLAlchemy relationship (when we add it)
        # assert message.conversation == sample_conversation
    
    def test_message_user_relationship(self, db_session, sample_conversation, conversation_user):
        """Test message belongs to user (nullable for AI messages)."""
        # Test human message
        human_message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=conversation_user.user_id,
            role="user",
            content="Human message"
        )
        
        db_session.add(human_message)
        db_session.commit()
        
        # Test foreign key relationship
        assert human_message.user_id == conversation_user.user_id
        
        # Test AI message (null user_id)
        ai_message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=None,
            role="assistant",
            content="AI message"
        )
        
        db_session.add(ai_message)
        db_session.commit()
        
        assert ai_message.user_id is None
    
    def test_message_without_conversation_fails(self, db_session):
        """Test that message requires a valid conversation_id."""
        fake_conversation_id = uuid.uuid4()
        
        message = Message(
            conversation_id=fake_conversation_id,
            user_id=None,
            role="assistant",
            content="Invalid conversation test"
        )
        
        db_session.add(message)
        
        # Should fail due to foreign key constraint
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_message_with_invalid_user_fails(self, db_session, sample_conversation):
        """Test that message with user_id requires valid user."""
        fake_user_id = uuid.uuid4()
        
        message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=fake_user_id,
            role="user",
            content="Invalid user test"
        )
        
        db_session.add(message)
        
        # Should fail due to foreign key constraint
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_message_role_validation(self, db_session, sample_conversation):
        """Test message role validation."""
        valid_roles = ["user", "assistant", "system"]
        
        for role in valid_roles:
            message = Message(
                conversation_id=sample_conversation.conversation_id,
                user_id=None if role in ["assistant", "system"] else sample_conversation.user_id,
                role=role,
                content=f"Testing {role} role"
            )
            db_session.add(message)
            db_session.commit()
            
            assert message.role == role
            db_session.delete(message)
            db_session.commit()
    
    def test_message_content_required(self, db_session, sample_conversation):
        """Test that message content is required."""
        message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=sample_conversation.user_id,
            role="user",
            content=None  # Should fail
        )
        
        db_session.add(message)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_message_empty_content_fails(self, db_session, sample_conversation):
        """Test that message content cannot be empty."""
        message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=sample_conversation.user_id,
            role="user",
            content=""  # Empty content should fail
        )
        
        db_session.add(message)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_message_blog_candidate_flag(self, db_session, sample_conversation):
        """Test is_blog flag for blog candidate messages."""
        message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=None,  # AI message
            role="assistant",
            content="This is a high-quality response that could become a blog post.",
            is_blog=True
        )
        
        db_session.add(message)
        db_session.commit()
        
        assert message.is_blog is True
        
        # Test default value
        regular_message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=sample_conversation.user_id,
            role="user",
            content="Regular message"
        )
        
        db_session.add(regular_message)
        db_session.commit()
        
        assert regular_message.is_blog is False
    
    def test_message_helper_methods(self, db_session, sample_conversation):
        """Test message helper methods."""
        # Test human message
        human_message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=sample_conversation.user_id,
            role="user",
            content="Human message"
        )
        db_session.add(human_message)
        db_session.commit()
        
        # Test AI message  
        ai_message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=None,
            role="assistant",
            content="AI message"
        )
        db_session.add(ai_message)
        db_session.commit()
        
        # Test helper methods
        assert human_message.is_human_message is True
        assert human_message.is_ai_message is False
        assert human_message.is_system_message is False
        assert human_message.is_active is True
        
        assert ai_message.is_human_message is False
        assert ai_message.is_ai_message is True
        assert ai_message.is_system_message is False
        
        # Test with archived status
        ai_message.status = "archived"
        assert ai_message.is_active is False
    
    def test_message_ordering_in_conversation(self, db_session, sample_conversation):
        """Test multiple messages in conversation maintain order."""
        messages = []
        
        for i in range(3):
            # Alternate between human and AI messages
            is_human = i % 2 == 0
            message = Message(
                conversation_id=sample_conversation.conversation_id,
                user_id=sample_conversation.user_id if is_human else None,
                role="user" if is_human else "assistant",
                content=f"Message {i+1}"
            )
            messages.append(message)
            db_session.add(message)
        
        db_session.commit()
        
        # Verify all messages were created with different timestamps
        for msg in messages:
            assert msg.message_id is not None
            assert msg.conversation_id == sample_conversation.conversation_id
        
        # Verify they have different IDs
        message_ids = [msg.message_id for msg in messages]
        assert len(set(message_ids)) == 3  # All unique
    
    def test_message_string_representations(self, db_session, sample_conversation):
        """Test __str__ and __repr__ methods."""
        message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=sample_conversation.user_id,
            role="user",
            content="Test message for string representation"
        )
        db_session.add(message)
        db_session.commit()
        
        # Test string representations
        assert "Test message for string representation" in str(message)
        assert "user" in str(message)
        assert f"Message(id={message.message_id}" in repr(message)
    
    def test_message_timestamps(self, db_session, sample_conversation):
        """Test that timestamps are set correctly."""
        message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=sample_conversation.user_id,
            role="user",
            content="Timestamp test message"
        )
        
        # Store creation time
        before_creation = datetime.now(timezone.utc)
        
        db_session.add(message)
        db_session.commit()
        
        after_creation = datetime.now(timezone.utc)
        
        # Verify timestamps are set and reasonable
        assert message.created_at is not None
        assert message.updated_at is not None
        # Allow for database timestamps to be slightly different due to timing
        assert abs((message.created_at - before_creation).total_seconds()) < 5
        assert abs((message.updated_at - before_creation).total_seconds()) < 5
        
        # Test updated_at changes on update
        original_updated_at = message.updated_at
        
        # Add a small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        message.content = "Updated message content"
        db_session.commit()
        db_session.refresh(message)
        
        # updated_at should have changed
        assert message.updated_at > original_updated_at
    
    def test_message_status_validation(self, db_session, sample_conversation):
        """Test message status field validation."""
        valid_statuses = ["active", "archived", "deleted"]
        
        for status in valid_statuses:
            message = Message(
                conversation_id=sample_conversation.conversation_id,
                user_id=sample_conversation.user_id,
                role="user",
                content=f"Status test {status}",
                status=status
            )
            db_session.add(message)
            db_session.commit()
            
            assert message.status == status
            db_session.delete(message)
            db_session.commit()
    
    def test_message_cascade_behavior(self, db_session, sample_conversation, conversation_user):
        """Test what happens when parent records are deleted."""
        message = Message(
            conversation_id=sample_conversation.conversation_id,
            user_id=conversation_user.user_id,
            role="user",
            content="Cascade test message"
        )
        
        db_session.add(message)
        db_session.commit()
        
        message_id = message.message_id
        
        # Delete the conversation
        db_session.delete(sample_conversation)
        
        # This should handle cascade behavior appropriately
        # (Messages should be deleted when conversation is deleted)
        db_session.commit()
        
        # Verify message is gone
        deleted_message = db_session.get(Message, message_id)
        assert deleted_message is None
