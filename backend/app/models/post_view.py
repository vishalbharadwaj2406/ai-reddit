"""
PostView Model

Represents user views/reads of posts for engagement tracking.
Based on the post_views table in mvp_db_schema.md.

This model handles:
- User engagement tracking
- View analytics and metrics
- Reading behavior analysis
- Multiple views by same user tracking
- Anonymous views support
"""

from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class PostView(Base):
    """
    PostView model representing the post_views table.
    
    This tracks when users view posts, enabling analytics on content engagement,
    popular posts, and reading patterns. Allows multiple views by the same user
    and supports anonymous views.
    """
    
    __tablename__ = "post_views"
    
    # Primary key - single UUID for each view
    view_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for this view record"
    )
    
    # Foreign keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=True,  # Allow null for anonymous views
        comment="User who viewed the post (null for anonymous views)"
    )
    
    post_id = Column(
        UUID(as_uuid=True),
        ForeignKey("posts.post_id", ondelete="CASCADE"),
        nullable=False,
        comment="Post that was viewed"
    )
    
    viewed_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="When the post was viewed"
    )
    
    # Additional tracking fields
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last modification time"
    )
    
    status = Column(
        String,
        default="active",
        nullable=False,
        comment="Record status: 'active', 'archived', etc."
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="post_views"
    )
    
    post = relationship(
        "Post",
        back_populates="post_views"
    )
    
    def __repr__(self) -> str:
        return f"<PostView(user_id={self.user_id}, post_id={self.post_id}, viewed_at={self.viewed_at})>"
    
    def __str__(self) -> str:
        try:
            return f"User {self.user.user_name} viewed '{self.post.title}' at {self.viewed_at}"
        except:
            return f"PostView({self.user_id}, {self.post_id}, {self.viewed_at})"
    
    # Helper methods
    @property
    def is_active(self) -> bool:
        """Check if view record is active."""
        return self.status == "active"
    
    @property
    def view_age(self) -> int:
        """Get age of the view in seconds."""
        if self.viewed_at:
            return int((datetime.now(timezone.utc) - self.viewed_at).total_seconds())
        return 0
    
    def archive(self) -> None:
        """Archive this view record."""
        self.status = "archived"
    
    def activate(self) -> None:
        """Reactivate this view record."""
        self.status = "active"
    
    @classmethod
    def create_view(cls, user_id, post_id, viewed_at=None):
        """
        Convenience method to create a new post view.
        
        Args:
            user_id: UUID of the user viewing the post
            post_id: UUID of the post being viewed
            viewed_at: Optional timestamp, defaults to now()
        
        Returns:
            PostView instance
        """
        return cls(
            user_id=user_id,
            post_id=post_id,
            viewed_at=viewed_at or datetime.now(timezone.utc),
            status="active"
        )
