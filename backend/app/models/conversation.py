"""
Conversation Model

Represents a conversation in our application.
Based on the conversations table in mvp_db_schema.md.

This model handles:
- AI conversations created by users
- Conversation metadata (title, creation time)
- Forking relationships (conversations forked from posts)
- User ownership
"""

from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Conversation(Base):
    """
    Conversation model representing the conversations table.

    This stores conversation metadata and relationships.
    The actual conversation content is stored in the messages table.
    """

    __tablename__ = "conversations"

    # Primary key - using UUID for better scalability
    conversation_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the conversation"
    )

    # Foreign key to user (creator of the conversation)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
        comment="Creator of the conversation"
    )

    # Conversation metadata
    title = Column(
        String,
        nullable=False,
        comment="Conversation title"
    )

    # Forking relationship - nullable reference to post_id
    forked_from = Column(
        UUID(as_uuid=True),
        # ForeignKey("posts.post_id", ondelete="SET NULL"),  # Comment out until Post model exists
        nullable=True,
        comment="Post ID this conversation was forked from (if any)"
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
        comment="When the conversation was created"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last time conversation was modified"
    )

    # Relationships
    # Note: We'll add these as we create the related models
    
    user = relationship(
        "User",
        back_populates="conversations"
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    posts = relationship(
        "Post",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )

    # posts = relationship(
    #     "Post",
    #     back_populates="conversation",
    #     cascade="all, delete-orphan"
    # )

    # forked_from_post = relationship(
    #     "Post",
    #     foreign_keys=[forked_from],
    #     remote_side="Post.post_id"
    # )

    def __repr__(self):
        """String representation of Conversation for debugging."""
        return f"<Conversation(id={self.conversation_id}, title={self.title})>"

    def __str__(self):
        """Human-readable string representation."""
        return self.title

    # Helper methods for common operations

    @property
    def is_active(self) -> bool:
        """Check if conversation is active."""
        return self.status == "active"

    @property
    def is_forked(self) -> bool:
        """Check if this conversation was forked from a post."""
        return self.forked_from is not None

    def get_display_title(self) -> str:
        """Get the title to display for this conversation."""
        return self.title or f"Conversation {str(self.conversation_id)[:8]}"

    def get_short_title(self, max_length: int = 50) -> str:
        """Get a shortened version of the title for display."""
        title = self.get_display_title()
        if len(title) <= max_length:
            return title
        return title[:max_length-3] + "..."

    def archive(self):
        """Archive this conversation (soft delete)."""
        self.status = "archived"

    def activate(self):
        """Reactivate an archived conversation."""
        self.status = "active"


# Example usage:
#
# # Create a new conversation
# conversation = Conversation(
#     user_id=user.user_id,
#     title="My AI Discussion"
# )
#
# # Add to database
# db.add(conversation)
# db.commit()
#
# # Create a forked conversation
# forked_conversation = Conversation(
#     user_id=user.user_id,
#     title="Expanding on Original Idea",
#     forked_from=original_post.post_id
# )
#
# # Query conversations
# user_conversations = db.query(Conversation).filter(
#     Conversation.user_id == user.user_id,
#     Conversation.status == "active"
# ).all()
