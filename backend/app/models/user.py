"""
User Model

Represents a user in our application.
Based on the users table in mvp_db_schema.md.

This model handles:
- User profile information
- Google OAuth integration
- Privacy settings
- Relationships with other users (follows)
"""

from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class User(Base):
    """
    User model representing the users table.

    This stores all user information including profile data,
    authentication details, and privacy settings.
    """

    __tablename__ = "users"

    # Primary key - using UUID for better scalability
    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the user"
    )

    # Profile Information
    user_name = Column(
        String,
        unique=True,
        nullable=False,
        comment="Display name - user can modify this"
    )

    email = Column(
        String,
        unique=True,
        nullable=True,  # Optional for now
        comment="User's email address"
    )

    phone = Column(
        String,
        unique=True,
        nullable=True,
        comment="User's phone number (optional)"
    )

    profile_picture = Column(
        String,
        nullable=True,
        comment="URL to user's profile picture"
    )

    gender = Column(
        String,
        nullable=True,
        comment="User's gender (optional)"
    )

    # Authentication
    google_id = Column(
        String,
        unique=True,
        nullable=True,
        comment="Google OAuth ID for authentication"
    )

    # Privacy & Settings
    is_private = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="If True, user's content is only visible to followers"
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
        comment="When the user account was created"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last time user data was modified"
    )

    # Relationships
    # Note: We define relationships here but the actual foreign keys
    # are in the related tables
    # TODO: Uncomment these as we create the related models

    # conversations = relationship(
    #     "Conversation",
    #     back_populates="user",
    #     cascade="all, delete-orphan"
    # )

    # messages = relationship(
    #     "Message",
    #     back_populates="user",
    #     cascade="all, delete-orphan"
    # )

    # posts = relationship(
    #     "Post",
    #     back_populates="user",
    #     cascade="all, delete-orphan"
    # )

    # comments = relationship(
    #     "Comment",
    #     back_populates="user",
    #     cascade="all, delete-orphan"
    # )

    # Follow relationships (many-to-many)
    # These will be defined in associations.py

    def __repr__(self):
        """String representation of User for debugging."""
        return f"<User(id={self.user_id}, username={self.user_name})>"

    def __str__(self):
        """Human-readable string representation."""
        return self.user_name

    # Helper methods for common operations

    @property
    def is_active(self) -> bool:
        """Check if user account is active."""
        return self.status == "active"

    def get_display_name(self) -> str:
        """Get the name to display for this user."""
        return self.user_name or f"User {str(self.user_id)[:8]}"

    def has_profile_picture(self) -> bool:
        """Check if user has a profile picture set."""
        return self.profile_picture is not None and self.profile_picture.strip() != ""


# Example usage:
#
# # Create a new user
# user = User(
#     user_name="john_doe",
#     email="john@example.com",
#     google_id="google_oauth_id_123"
# )
#
# # Add to database
# db.add(user)
# db.commit()
#
# # Query users
# active_users = db.query(User).filter(User.status == "active").all()
# user_by_email = db.query(User).filter(User.email == "john@example.com").first()