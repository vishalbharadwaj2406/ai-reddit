"""
PostReaction Model for AI Social Platform

This module defines the PostReaction model for user reactions to posts.
Uses a universal reaction system with upvote, downvote, heart, insightful, accurate.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class PostReaction(Base):
    """
    PostReaction model for user reactions to posts.
    
    Each user can have only one reaction per post. Changing reaction
    updates the existing record. Setting reaction to null removes it.
    
    Attributes:
        user_id: User who made the reaction
        post_id: Post being reacted to
        reaction: Type of reaction (upvote, downvote, heart, insightful, accurate)
        created_at: When the reaction was first created
        updated_at: When the reaction was last changed
        status: Record status for soft deletion
    """
    
    __tablename__ = "post_reactions"
    
    # Composite primary key (user_id, post_id)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        primary_key=True,
        comment="User who made the reaction"
    )
    
    post_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("posts.post_id", ondelete="RESTRICT"),
        primary_key=True,
        comment="Post being reacted to"
    )
    
    # Reaction type
    reaction = Column(
        String,
        nullable=False,
        comment="Type of reaction: upvote, downvote, heart, insightful, accurate"
    )
    
    # Add constraint to ensure valid reaction types
    __table_args__ = (
        CheckConstraint(
            "reaction IN ('upvote', 'downvote', 'heart', 'insightful', 'accurate')",
            name="valid_reaction_type"
        ),
    )
    
    # Metadata fields
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="When the reaction was first created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="When the reaction was last changed"
    )
    
    status = Column(
        String,
        nullable=False,
        default="active",
        comment="Record status: 'active', 'archived', etc."
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="post_reactions"
    )
    
    post = relationship(
        "Post",
        back_populates="reactions"
    )
    
    def __repr__(self):
        """String representation of PostReaction for debugging."""
        return f"PostReaction(user_id={self.user_id}, post_id={self.post_id}, reaction='{self.reaction}')"
    
    def __str__(self):
        """Human-readable string representation."""
        user_name = self.user.user_name if self.user else "Unknown"
        return f"{user_name} reacted '{self.reaction}' to post"
    
    # Helper methods for common operations
    
    @property
    def is_active(self) -> bool:
        """Check if reaction is active."""
        return self.status == "active"
    
    @property
    def is_positive(self) -> bool:
        """Check if this is a positive reaction."""
        return self.reaction in ["upvote", "heart", "insightful", "accurate"]
    
    @property
    def is_negative(self) -> bool:
        """Check if this is a negative reaction."""
        return self.reaction == "downvote"
    
    @property
    def is_quality_signal(self) -> bool:
        """Check if this reaction indicates content quality."""
        return self.reaction in ["insightful", "accurate"]
    
    @classmethod
    def get_valid_reactions(cls) -> list:
        """Get list of valid reaction types."""
        return ["upvote", "downvote", "heart", "insightful", "accurate"]
    
    @classmethod
    def is_valid_reaction(cls, reaction: str) -> bool:
        """Check if a reaction type is valid."""
        return reaction in cls.get_valid_reactions()
