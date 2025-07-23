"""
Post Fork Model

Database model for tracking post fork relationships and analytics.
Follows the same pattern as other post interaction models (post_views, post_shares, post_reactions).
"""

from sqlalchemy import Column, String, UUID, ForeignKey, TIMESTAMP, text, Index
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class PostFork(Base):
    """
    Model for tracking when users fork posts into new conversations.
    
    This enables analytics like:
    - How many times a post has been forked
    - Which posts a user has forked
    - Fork relationship chains
    - Fork engagement tracking
    """
    
    __tablename__ = "post_forks"
    
    # Primary Key: Composite of user_id, post_id, and forked_at to allow multiple forks
    user_id = Column(
        PostgreSQLUUID(as_uuid=True), 
        ForeignKey("users.user_id"), 
        primary_key=True,
        nullable=False,
        comment="User who forked the post"
    )
    
    post_id = Column(
        PostgreSQLUUID(as_uuid=True), 
        ForeignKey("posts.post_id"), 
        primary_key=True,
        nullable=False,
        comment="Post that was forked"
    )
    
    forked_at = Column(
        TIMESTAMP(timezone=True), 
        primary_key=True,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="When the fork occurred"
    )
    
    # Additional fields
    conversation_id = Column(
        PostgreSQLUUID(as_uuid=True), 
        ForeignKey("conversations.conversation_id"), 
        nullable=False,
        comment="The new conversation created from the fork"
    )
    
    original_conversation_included = Column(
        String, 
        nullable=False,
        default="false",
        comment="Whether original conversation context was included (true/false as string for consistency)"
    )
    
    status = Column(
        String, 
        nullable=False, 
        default="active",
        comment="Fork status: 'active', 'archived', etc."
    )
    
    updated_at = Column(
        TIMESTAMP(timezone=True), 
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        comment="Last update timestamp"
    )
    
    # Relationships
    user = relationship("User", back_populates="post_forks")
    post = relationship("Post", back_populates="forks")
    conversation = relationship("Conversation", back_populates="forked_from_post_forks")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_post_forks_post_id', 'post_id'),
        Index('idx_post_forks_user_id', 'user_id'),
        Index('idx_post_forks_conversation_id', 'conversation_id'),
        Index('idx_post_forks_status', 'status'),
        Index('idx_post_forks_forked_at', 'forked_at'),
        {
            'comment': 'Tracks post fork relationships for analytics and engagement metrics'
        }
    )
    
    def __repr__(self):
        return f"<PostFork(user_id={self.user_id}, post_id={self.post_id}, conversation_id={self.conversation_id}, forked_at={self.forked_at})>"
    
    def __str__(self):
        return f"PostFork: User {self.user_id} forked Post {self.post_id} at {self.forked_at}"
    
    # Helper Properties
    @property
    def is_active(self) -> bool:
        """Check if this fork is active (not archived)"""
        return self.status == "active"
    
    @property
    def included_original_conversation(self) -> bool:
        """Check if original conversation was included in the fork"""
        return self.original_conversation_included.lower() == "true"
    
    @property
    def fork_age(self) -> int:
        """Get the age of this fork in seconds"""
        if self.forked_at:
            return int((datetime.now(timezone.utc) - self.forked_at).total_seconds())
        return 0
    
    # Helper Methods
    def archive(self):
        """Archive this fork (soft delete)"""
        self.status = "archived"
        self.updated_at = datetime.now(timezone.utc)
    
    def activate(self):
        """Activate this fork"""
        self.status = "active"
        self.updated_at = datetime.now(timezone.utc)
    
    @classmethod
    def create_fork(cls, user_id, post_id, conversation_id, include_original_conversation=False):
        """
        Class method to create a new fork record
        
        Args:
            user_id: ID of user creating the fork
            post_id: ID of post being forked
            conversation_id: ID of new conversation created
            include_original_conversation: Whether original conversation was included
            
        Returns:
            PostFork: New fork instance
        """
        return cls(
            user_id=user_id,
            post_id=post_id,
            conversation_id=conversation_id,
            original_conversation_included="true" if include_original_conversation else "false",
            forked_at=datetime.now(timezone.utc),
            status="active"
        )
