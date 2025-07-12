"""
Message Model

Represents an individual message within a conversation.
Based on the messages table in mvp_db_schema.md.

This model handles:
- Individual messages in conversations
- User messages and AI assistant responses
- System messages for conversation metadata
- Message roles (user, assistant, system)
- Blog candidate flagging for high-quality AI responses
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, func, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Message(Base):
    """
    Message model representing the messages table.

    This stores individual messages within conversations.
    Messages can be from humans (user_id set) or AI (user_id null).
    """

    __tablename__ = "messages"

    # Primary key - using UUID for better scalability
    message_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the message"
    )

    # Foreign key to conversation (required)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.conversation_id", ondelete="CASCADE"),
        nullable=False,
        comment="Conversation this message belongs to"
    )

    # Foreign key to user (nullable for AI messages)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="Author of the message (null for AI messages)"
    )

    # Message metadata
    role = Column(
        String,
        nullable=False,
        comment="Message role: 'user', 'assistant', 'system'"
    )

    content = Column(
        Text,
        CheckConstraint("LENGTH(TRIM(content)) > 0", name="content_not_empty"),
        nullable=False,
        comment="Message content"
    )

    # Blog candidate flag for high-quality AI responses
    is_blog = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="True if this message is a candidate for blog post creation"
    )

    # Record Management
    status = Column(
        String,
        default="active",
        nullable=False,
        comment="Record status: 'active', 'archived', etc."
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When the message was created"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last time message was modified"
    )

    # Relationships
    # Note: We'll add these as we test them
    
    # conversation = relationship(
    #     "Conversation",
    #     back_populates="messages"
    # )

    # user = relationship(
    #     "User",
    #     back_populates="messages"
    # )

    def __repr__(self):
        """String representation of Message for debugging."""
        role_display = self.role.capitalize() if self.role else "Unknown"
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message(id={self.message_id}, role={role_display}, content='{content_preview}')>"

    def __str__(self):
        """Human-readable string representation."""
        return f"{self.role}: {self.content}"

    # Helper methods for common operations

    @property
    def is_active(self) -> bool:
        """Check if message is active."""
        return self.status == "active"

    @property
    def is_human_message(self) -> bool:
        """Check if this message is from a human user."""
        return self.user_id is not None and self.role == "user"

    @property
    def is_ai_message(self) -> bool:
        """Check if this message is from AI assistant."""
        return self.user_id is None and self.role == "assistant"

    @property
    def is_system_message(self) -> bool:
        """Check if this message is a system message."""
        return self.role == "system"

    def get_author_display(self) -> str:
        """Get a display name for the message author."""
        if self.is_human_message:
            # Will be enhanced when we add user relationship
            return f"User {str(self.user_id)[:8]}"
        elif self.is_ai_message:
            return "AI Assistant"
        elif self.is_system_message:
            return "System"
        else:
            return "Unknown"

    def get_content_preview(self, max_length: int = 100) -> str:
        """Get a truncated version of the content for previews."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length-3] + "..."

    def mark_as_blog_candidate(self):
        """Mark this message as a candidate for blog post creation."""
        self.is_blog = True

    def unmark_as_blog_candidate(self):
        """Remove blog candidate flag from this message."""
        self.is_blog = False

    def archive(self):
        """Archive this message (soft delete)."""
        self.status = "archived"

    def activate(self):
        """Reactivate an archived message."""
        self.status = "active"


# Example usage:
#
# # Create a human message
# user_message = Message(
#     conversation_id=conversation.conversation_id,
#     user_id=user.user_id,
#     role="user",
#     content="Hello, can you help me with Python?"
# )
#
# # Create an AI response
# ai_response = Message(
#     conversation_id=conversation.conversation_id,
#     user_id=None,  # AI message
#     role="assistant",
#     content="Of course! I'd be happy to help you with Python. What specific topic would you like to explore?",
#     is_blog=True  # High-quality response
# )
#
# # Create a system message
# system_message = Message(
#     conversation_id=conversation.conversation_id,
#     user_id=None,
#     role="system",
#     content="This conversation was created from a forked post about Python programming."
# )
#
# # Add to database
# db.add_all([user_message, ai_response, system_message])
# db.commit()
#
# # Query messages in conversation order
# messages = db.query(Message).filter(
#     Message.conversation_id == conversation.conversation_id,
#     Message.status == "active"
# ).order_by(Message.created_at).all()
