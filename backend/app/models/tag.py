"""
Tag Model

Represents content tags in our application.
Based on the tags table in mvp_db_schema.md.

This model handles:
- Content categorization and organization
- Tag creation and management
- Unique tag name enforcement
"""

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Tag(Base):
    """
    Tag model representing the tags table.
    
    This stores unique tags that can be applied to posts for categorization.
    Tags are permanent and don't have status management.
    """
    
    __tablename__ = "tags"
    
    # Primary key
    tag_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the tag"
    )
    
    # Tag name - must be unique
    name = Column(
        String,
        unique=True,
        nullable=False,
        comment="Unique tag name/text"
    )
    
    # Relationships
    post_tags = relationship(
        "PostTag", 
        back_populates="tag",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Tag(tag_id={self.tag_id}, name='{self.name}')>"
    
    def __str__(self) -> str:
        return f"#{self.name}"
    
    # Helper methods
    @property
    def hashtag(self) -> str:
        """Return tag formatted as hashtag."""
        return f"#{self.name}"
    
    @classmethod
    def normalize_name(cls, name: str) -> str:
        """
        Normalize tag name for consistency.
        
        - Convert to lowercase
        - Strip whitespace
        - Replace spaces with hyphens
        """
        if not name:
            return ""
        
        normalized = name.strip().lower()
        # Replace spaces and multiple spaces with single hyphen
        normalized = "-".join(normalized.split())
        return normalized
    
    @property
    def display_name(self) -> str:
        """Return user-friendly display name."""
        # Convert hyphens back to spaces for display
        return self.name.replace("-", " ").title()
