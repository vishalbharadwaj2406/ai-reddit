"""
PostShare Model

Tracks post sharing events for analytics and future features.
Enables sharing functionality while maintaining privacy controls.

Schema alignment with mvp_db_schema.md:
- Composite tracking of share events
- Anonymous sharing support
- Platform tracking for analytics
- Future-proofing with metadata field
"""

from datetime import datetime
from uuid import uuid4, UUID
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class PostShare(Base):
    """
    Track post sharing events.
    
    Supports both authenticated and anonymous sharing while providing
    analytics data for product insights and future feature development.
    """
    __tablename__ = "post_shares"
    
    # Primary key
    share_id: UUID = Column(
        PostgresUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4,
        comment="Unique identifier for the share event"
    )
    
    # Foreign keys
    post_id: UUID = Column(
        PostgresUUID(as_uuid=True),
        ForeignKey("posts.post_id", ondelete="CASCADE"),
        nullable=False,
        comment="Post being shared"
    )
    
    shared_by_user_id: UUID = Column(
        PostgresUUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,  # Allow anonymous shares
        comment="User who shared the post (null for anonymous shares)"
    )
    
    # Share metadata
    platform: str = Column(
        String(50),
        nullable=True,
        comment="Platform where post was shared: 'direct_link', 'twitter', 'facebook', etc."
    )
    
    # Timestamps
    shared_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When the share was created"
    )
    
    # Status and metadata
    status: str = Column(
        String(20),
        default="active",
        nullable=False,
        comment="Share status: 'active', 'archived'"
    )
    
    share_metadata: dict = Column(
        JSON,
        nullable=True,
        comment="Additional metadata for future extensions (referrer, analytics, etc.)"
    )
    
    # Relationships
    post = relationship(
        "Post",
        back_populates="shares",
        doc="The post being shared"
    )
    
    shared_by = relationship(
        "User",
        back_populates="shares_made",
        doc="User who created the share (if authenticated)"
    )
    
    # Helper methods
    @property
    def is_active(self) -> bool:
        """Check if share record is active."""
        return self.status == "active"
    
    @property
    def is_anonymous(self) -> bool:
        """Check if this was an anonymous share."""
        return self.shared_by_user_id is None
    
    def archive(self):
        """Mark share as archived."""
        self.status = "archived"
    
    def activate(self):
        """Mark share as active."""
        self.status = "active"
    
    @classmethod
    def create_share(cls, post_id: UUID, shared_by_user_id: UUID = None, platform: str = "direct_link"):
        """
        Convenience method to create a new share record.
        
        Args:
            post_id: UUID of the post being shared
            shared_by_user_id: Optional UUID of user sharing (null for anonymous)
            platform: Platform where shared ('direct_link', 'twitter', etc.)
        
        Returns:
            PostShare instance
        """
        return cls(
            post_id=post_id,
            shared_by_user_id=shared_by_user_id,
            platform=platform,
            status="active"
        )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        shared_by = f"user_{str(self.shared_by_user_id)[:8]}" if self.shared_by_user_id else "anonymous"
        return f"<PostShare(post_id={str(self.post_id)[:8]}, shared_by={shared_by}, platform={self.platform})>"
