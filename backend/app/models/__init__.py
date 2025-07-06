"""
Database Models Package

This package contains all SQLAlchemy database models.
By importing all models here, we ensure they're available
when creating tables or running migrations.

Models represent the structure of our database tables and
define relationships between different entities.
"""

# Import all models so they're available when this package is imported
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.post import Post
from app.models.comment import Comment
from app.models.tag import Tag

# Import association tables for many-to-many relationships
from app.models.associations import (
    user_follows,
    post_reactions,
    comment_reactions,
    post_tags,
    post_views,
    post_shares
)

# List all models for easy iteration
__all__ = [
    "User",
    "Conversation",
    "Message",
    "Post",
    "Comment",
    "Tag",
    "user_follows",
    "post_reactions",
    "comment_reactions",
    "post_tags",
    "post_views",
    "post_shares"
]