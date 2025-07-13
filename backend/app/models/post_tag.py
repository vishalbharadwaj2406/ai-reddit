"""
PostTag Model

Represents the many-to-many relationship between Posts and Tags.
Based on the post_tags table in mvp_db_schema.md.

This model handles:
- Post-Tag associations
- Many-to-many relationship management
- Tag-based content organization
"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class PostTag(Base):
    """
    PostTag model representing the post_tags junction table.
    
    This establishes many-to-many relationships between posts and tags,
    allowing posts to have multiple tags and tags to be applied to multiple posts.
    """
    
    __tablename__ = "post_tags"
    
    # Composite primary key
    post_id = Column(
        UUID(as_uuid=True),
        ForeignKey("posts.post_id", ondelete="CASCADE"),
        primary_key=True,
        comment="Post being tagged"
    )
    
    tag_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tags.tag_id", ondelete="CASCADE"),
        primary_key=True,
        comment="Tag applied to the post"
    )
    
    # Relationships
    post = relationship(
        "Post",
        back_populates="post_tags"
    )
    
    tag = relationship(
        "Tag",
        back_populates="post_tags"
    )
    
    def __repr__(self) -> str:
        return f"<PostTag(post_id={self.post_id}, tag_id={self.tag_id})>"
    
    def __str__(self) -> str:
        # This will work once relationships are loaded
        try:
            return f"Post '{self.post.title}' tagged with '{self.tag.name}'"
        except:
            return f"PostTag({self.post_id}, {self.tag_id})"
    
    # Helper methods
    @property
    def tag_name(self) -> str:
        """Get the tag name (requires tag relationship to be loaded)."""
        return self.tag.name if self.tag else None
    
    @property
    def post_title(self) -> str:
        """Get the post title (requires post relationship to be loaded)."""
        return self.post.title if self.post else None
