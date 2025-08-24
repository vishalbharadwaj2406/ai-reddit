"""
Tag Repository

Data access layer for Tag operations.
Follows the established repository pattern from other repositories in the project.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.tag import Tag
from app.models.post_tag import PostTag
from app.models.post import Post


class TagRepository:
    """Repository for Tag data access operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_tags(self) -> List[Tag]:
        """
        Get all tags
        
        Returns:
            List of Tag objects
        """
        return self.db.query(Tag).all()
    
    def get_all_tags_with_counts(self) -> List[dict]:
        """
        Get all tags with their post counts
        
        Returns:
            List of dictionaries with tag info and post counts
        """
        # Query tags with their post counts using LEFT JOIN
        query = (
            self.db.query(
                Tag.tag_id,
                Tag.name,
                func.count(PostTag.post_id).label('post_count')
            )
            .outerjoin(PostTag, Tag.tag_id == PostTag.tag_id)
            .outerjoin(Post, and_(
                PostTag.post_id == Post.post_id,
                Post.status == "active"
            ))
            .group_by(Tag.tag_id, Tag.name)
            .order_by(func.count(PostTag.post_id).desc(), Tag.name)
        )
        
        results = query.all()
        
        return [
            {
                "tagId": str(result.tag_id),
                "name": result.name,
                "postCount": result.post_count or 0
            }
            for result in results
        ]
    
    def get_tag_by_id(self, tag_id: UUID) -> Optional[Tag]:
        """
        Get tag by ID
        
        Args:
            tag_id: ID of the tag
            
        Returns:
            Tag object if found, None otherwise
        """
        return self.db.query(Tag).filter(Tag.tag_id == tag_id).first()
    
    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """
        Get tag by name (case-insensitive)
        
        Args:
            name: Name of the tag
            
        Returns:
            Tag object if found, None otherwise
        """
        return self.db.query(Tag).filter(Tag.name == name.lower()).first()
    
    def create_tag(self, name: str) -> Tag:
        """
        Create a new tag
        
        Args:
            name: Name of the tag
            
        Returns:
            Created Tag object
        """
        # Normalize the name using the Tag model's method
        normalized_name = Tag.normalize_name(name)
        
        tag = Tag(name=normalized_name)
        
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag
    
    def tag_exists(self, name: str) -> bool:
        """
        Check if a tag with the given name already exists
        
        Args:
            name: Name to check
            
        Returns:
            True if tag exists, False otherwise
        """
        normalized_name = Tag.normalize_name(name)
        return self.get_tag_by_name(normalized_name) is not None
    
    def get_tag_post_count(self, tag_id: UUID) -> int:
        """
        Get the number of active posts for a tag
        
        Args:
            tag_id: ID of the tag
            
        Returns:
            Number of active posts with this tag
        """
        count = (
            self.db.query(func.count(PostTag.post_id))
            .join(Post, and_(
                PostTag.post_id == Post.post_id,
                Post.status == "active"
            ))
            .filter(PostTag.tag_id == tag_id)
            .scalar()
        )
        
        return count or 0
