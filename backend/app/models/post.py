"""
Post Model

Represents a shareable post created from a conversation.
Based on the posts table in mvp_db_sc    # Relationships
    user = relationship(
        "User",
        back_populates="posts"
    )

    conversation = relationship(
        "Conversation",
        back_populates="posts"
    )

    # Comments relationship
    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan"
    )

    # Reactions relationship
    reactions = relationship(
        "PostReaction",
        back_populates="post",
        cascade="all, delete-orphan"
    )

    # forked_conversations = relationship(
    #     "Conversation",
    #     foreign_keys="Conversation.forked_from",
    #     back_populates="source_post"
    # ) model handles:
- Blog posts created from high-quality conversations
- User-generated content for sharing
- Post privacy and visibility settings
- Edit tracking and status management
- Source for conversation forking
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, func, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Post(Base):
    """
    Post model for shareable content.
    
    Posts are created from conversations and represent the main content
    that users can interact with. They support privacy settings,
    edit tracking, and can serve as sources for new conversations.
    """
    
    __tablename__ = "posts"

    # Primary key
    post_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the post"
    )

    # Foreign key relationships
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
        comment="Creator of the post"
    )

    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.conversation_id", ondelete="RESTRICT"),
        nullable=False,
        comment="Source conversation for this post"
    )

    # Content fields
    title = Column(
        String,
        CheckConstraint("LENGTH(TRIM(title)) > 0", name="title_not_empty"),
        nullable=False,
        comment="Post title"
    )

    content = Column(
        Text,
        CheckConstraint("LENGTH(TRIM(content)) > 0", name="post_content_not_empty"),
        nullable=False,
        comment="Post content"
    )

    # Visibility and settings
    is_conversation_visible = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="If TRUE, the conversation linked to this post is viewable by others"
    )

    # Edit tracking
    edited = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="True if post has been edited"
    )

    # Status management
    status = Column(
        String,
        default="active",
        nullable=False,
        comment="Record status: 'active', 'archived', etc."
    )

    # Analytics
    fork_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of times this post has been forked"
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When the post was created"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last time post was modified"
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="posts"
    )

    conversation = relationship(
        "Conversation",
        back_populates="posts"
    )

    # Comments and reactions relationships
    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan"
    )
    
    reactions = relationship(
        "PostReaction",
        back_populates="post",
        cascade="all, delete-orphan"
    )

    # Tag relationships
    post_tags = relationship(
        "PostTag",
        back_populates="post",
        cascade="all, delete-orphan"
    )

    # Engagement relationships
    post_views = relationship(
        "PostView",
        back_populates="post",
        cascade="all, delete-orphan"
    )

    shares = relationship(
        "PostShare",
        back_populates="post",
        cascade="all, delete-orphan",
        doc="Shares of this post"
    )

    # Fork tracking relationships
    forks = relationship(
        "PostFork",
        back_populates="post",
        cascade="all, delete-orphan",
        doc="Fork records tracking when this post was forked into new conversations"
    )

    # forked_conversations = relationship(
    #     "Conversation",
    #     foreign_keys="Conversation.forked_from",
    #     back_populates="source_post"
    # )

    def __repr__(self):
        """String representation of Post for debugging."""
        title_preview = self.title[:30] + "..." if len(self.title) > 30 else self.title
        return f"<Post(id={self.post_id}, title='{title_preview}', status={self.status})>"

    def __str__(self):
        """Human-readable string representation."""
        return f"{self.title}"

    # Helper methods for common operations

    @property
    def is_active(self) -> bool:
        """Check if post is active."""
        return self.status == "active"

    @property
    def has_visible_conversation(self) -> bool:
        """Check if the source conversation is visible to others."""
        return self.is_conversation_visible

    def get_content_preview(self, max_length: int = 150) -> str:
        """Get a truncated version of the content for previews."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length-3] + "..."

    def mark_as_edited(self):
        """Mark this post as edited."""
        self.edited = True

    def show_conversation(self):
        """Make the source conversation visible to others."""
        self.is_conversation_visible = True

    def hide_conversation(self):
        """Hide the source conversation from others."""
        self.is_conversation_visible = False

    def archive(self):
        """Archive this post (soft delete)."""
        self.status = "archived"

    def activate(self):
        """Reactivate an archived post."""
        self.status = "active"

    def get_share_count(self) -> int:
        """Get total number of times this post has been shared."""
        return len([share for share in self.shares if share.status == "active"])

    def get_author_display(self) -> str:
        """Get a display name for the post author."""
        # Will be enhanced when we add user relationship
        return f"User {str(self.user_id)[:8]}"


# Example usage:
#
# # Create a post from a conversation
# post = Post(
#     user_id=user.user_id,
#     conversation_id=conversation.conversation_id,
#     title="How to Learn Python Effectively",
#     content="Based on my conversation with AI, here are the key strategies...",
#     is_conversation_visible=True  # Allow others to see the source conversation
# )
#
# # Add to database
# db.add(post)
# db.commit()
#
# # Query posts by user
# user_posts = db.query(Post).filter(
#     Post.user_id == user.user_id,
#     Post.status == "active"
# ).order_by(Post.created_at.desc()).all()
#
# # Query posts with visible conversations
# posts_with_conversations = db.query(Post).filter(
#     Post.is_conversation_visible == True,
#     Post.status == "active"
# ).all()
