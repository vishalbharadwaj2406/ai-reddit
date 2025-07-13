"""
Comment Model for AI Social Platform

This module defines the Comment model for user comments on posts.
Comments support threading (replies) and are linked to posts and users.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Comment(Base):
    """
    Comment model for post comments and replies.
    
    A comment belongs to a post and optionally to a parent comment (for replies).
    Comments can be reacted to by users and have their own reaction counts.
    
    Attributes:
        comment_id: Unique identifier for the comment
        post_id: Reference to the post this comment belongs to
        user_id: Reference to the user who created this comment
        parent_comment_id: Reference to parent comment for replies (nullable)
        content: The comment text content
        created_at: When the comment was created
        updated_at: When the comment was last modified
        status: Record status for soft deletion
    """
    
    __tablename__ = "comments"
    
    # Primary key
    comment_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the comment"
    )
    
    # Foreign keys
    post_id = Column(
        UUID(as_uuid=True),
        ForeignKey("posts.post_id", ondelete="RESTRICT"),
        nullable=False,
        comment="Post this comment belongs to"
    )
    
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
        comment="Author of the comment"
    )
    
    parent_comment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("comments.comment_id", ondelete="RESTRICT"),
        nullable=True,
        comment="Parent comment for replies (null for top-level comments)"
    )
    
    # Content fields
    content = Column(
        Text,
        nullable=False,
        comment="Comment content"
    )
    
    # Add constraint to ensure content is not empty
    __table_args__ = (
        CheckConstraint(
            "LENGTH(TRIM(content)) > 0",
            name="content_not_empty"
        ),
    )
    
    # Metadata fields
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="When the comment was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="Last time comment was modified"
    )
    
    status = Column(
        String,
        nullable=False,
        default="active",
        comment="Record status: 'active', 'archived', etc."
    )
    
    # Relationships
    post = relationship(
        "Post",
        back_populates="comments"
    )
    
    user = relationship(
        "User", 
        back_populates="comments"
    )
    
    # Self-referential relationship for replies
    parent_comment = relationship(
        "Comment",
        remote_side=[comment_id],
        back_populates="replies"
    )
    
    replies = relationship(
        "Comment",
        back_populates="parent_comment",
        cascade="all, delete-orphan"
    )
    
    # Reactions relationship (will be defined when CommentReaction model is created)
    reactions = relationship(
        "CommentReaction",
        back_populates="comment",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        """String representation of Comment for debugging."""
        return f"Comment(id={self.comment_id}, post_id={self.post_id}, content='{self.content[:50]}...')"
    
    def __str__(self):
        """Human-readable string representation."""
        author = self.user.user_name if self.user else "Unknown"
        return f"Comment by {author}: {self.content[:100]}..."
    
    # Helper methods for common operations
    
    @property
    def is_active(self) -> bool:
        """Check if comment is active."""
        return self.status == "active"
    
    @property
    def is_reply(self) -> bool:
        """Check if this is a reply to another comment."""
        return self.parent_comment_id is not None
    
    @property
    def is_top_level(self) -> bool:
        """Check if this is a top-level comment (not a reply)."""
        return self.parent_comment_id is None
    
    def get_reaction_counts(self) -> dict:
        """
        Get aggregated reaction counts for this comment.
        Returns a dictionary with reaction types as keys and counts as values.
        """
        from collections import Counter
        active_reactions = [r.reaction for r in self.reactions if r.status == "active"]
        return dict(Counter(active_reactions))
    
    def get_reply_count(self) -> int:
        """Get the number of active replies to this comment."""
        return len([reply for reply in self.replies if reply.is_active])
    
    def can_be_edited_by(self, user_id: uuid.UUID) -> bool:
        """Check if a user can edit this comment."""
        return self.user_id == user_id and self.is_active
