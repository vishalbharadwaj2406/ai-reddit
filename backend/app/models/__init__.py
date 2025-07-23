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
from app.models.post_reaction import PostReaction
from app.models.comment_reaction import CommentReaction
from app.models.follow import Follow
from app.models.tag import Tag
from app.models.post_tag import PostTag
from app.models.post_view import PostView
from app.models.post_share import PostShare
from app.models.post_fork import PostFork

# TODO: Import these as we create the models
# from app.models.post_share import PostShare
# from app.models.post_share import PostShare

# Import association tables for many-to-many relationships
# TODO: Import these as we create them
# from app.models.associations import (
#     user_follows,
#     post_reactions,
#     comment_reactions,
#     post_tags,
#     post_views,
#     post_shares
# )

# List all models for easy iteration
__all__ = [
    "User",
    "Conversation",
    "Message",
    "Post",
    "Comment",
    "PostReaction",
    "CommentReaction",
    "Follow",
    "Tag",
    "PostTag",
    "PostView",
    "PostShare",
    # TODO: Add these as we create models
]