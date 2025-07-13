"""
Follow Model

Represents user follow relationships in our application.
Based on the follows table in mvp_db_schema.md.

This model handles:
- User following/follower relationships
- Follow request status management (pending, accepted)
- Rejection handling (clean deletion for re-request capability)
- Bidirectional relationship queries
"""

from sqlalchemy import Column, String, DateTime, func, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone

from app.core.database import Base


class Follow(Base):
    """
    Follow model representing the follows table.

    This stores user follow relationships with status management.
    Rejected follows are deleted to allow re-requests.
    """

    __tablename__ = "follows"

    # Composite primary key - follower and following user
    follower_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        primary_key=True,
        comment="User who is following"
    )

    following_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        primary_key=True,
        comment="User being followed"
    )

    # Follow status - no 'rejected' status (those are deleted)
    status = Column(
        String,
        nullable=False,
        default="pending",
        comment="Follow status: 'pending', 'accepted', 'archived'"
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="When the follow request was created"
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last time follow status was modified"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "follower_id != following_id",
            name="no_self_follow"
        ),
        CheckConstraint(
            "status IN ('pending', 'accepted', 'archived')",
            name="valid_follow_status"
        ),
    )

    # Relationships
    follower = relationship(
        "User",
        foreign_keys=[follower_id],
        back_populates="following_relationships"
    )

    following = relationship(
        "User", 
        foreign_keys=[following_id],
        back_populates="follower_relationships"
    )

    def __repr__(self) -> str:
        return f"<Follow(follower_id={self.follower_id}, following_id={self.following_id}, status='{self.status}')>"

    # Status check properties
    @property
    def is_pending(self) -> bool:
        """Check if follow request is pending approval."""
        return self.status == "pending"

    @property
    def is_accepted(self) -> bool:
        """Check if follow request has been accepted."""
        return self.status == "accepted"

    @property
    def is_active(self) -> bool:
        """Check if follow relationship is active (accepted)."""
        return self.status == "accepted"

    @property
    def is_archived(self) -> bool:
        """Check if follow relationship has been archived."""
        return self.status == "archived"

    # Status management methods
    def accept(self) -> None:
        """Accept the follow request."""
        if self.status == "pending":
            self.status = "accepted"
            # SQLAlchemy's onupdate will handle updated_at automatically

    def archive(self) -> None:
        """Archive the follow relationship (soft delete)."""
        self.status = "archived"
        # SQLAlchemy's onupdate will handle updated_at automatically

    # Note: reject() method will be handled by deletion in the service layer
    # This provides clean slate for re-requests as requested
