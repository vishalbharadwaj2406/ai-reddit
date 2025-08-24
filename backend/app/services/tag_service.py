"""
Tag Service

Business logic layer for Tag operations.
Follows the established service pattern from other services in the project.
"""

from typing import List
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.repositories.tag_repository import TagRepository
from app.core.exceptions import TagAlreadyExistsError, TagNotFoundError, InvalidTagNameError


class TagService:
    """Service for Tag business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tag_repo = TagRepository(db)
    
    def get_all_tags_with_counts(self) -> List[dict]:
        """
        Get all tags with their post counts
        
        Returns:
            List of dictionaries with tag data and post counts
            
        Raises:
            HTTPException: If database operation fails
        """
        try:
            return self.tag_repo.get_all_tags_with_counts()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve tags: {str(e)}"
            )
    
    def create_tag(self, name: str) -> dict:
        """
        Create a new tag
        
        Args:
            name: Name of the tag to create
            
        Returns:
            Dictionary with created tag data
            
        Raises:
            TagAlreadyExistsError: If tag with this name already exists
            InvalidTagNameError: If tag name is invalid
            HTTPException: If database operation fails
        """
        
        # Validate tag name
        if not name or not name.strip():
            raise InvalidTagNameError("Tag name cannot be empty")
        
        # Normalize name for checking
        normalized_name = Tag.normalize_name(name)
        if not normalized_name:
            raise InvalidTagNameError("Tag name cannot be empty after normalization")
        
        # Check if tag already exists
        if self.tag_repo.tag_exists(name):
            raise TagAlreadyExistsError(f"Tag '{normalized_name}' already exists")
        
        try:
            # Create the tag
            tag = self.tag_repo.create_tag(name)
            
            return {
                "tagId": str(tag.tag_id),
                "name": tag.name,
                "postCount": 0  # New tags start with 0 posts
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create tag: {str(e)}"
            )
    
    def get_tag_by_id(self, tag_id: UUID) -> dict:
        """
        Get a tag by its ID
        
        Args:
            tag_id: ID of the tag
            
        Returns:
            Dictionary with tag data
            
        Raises:
            TagNotFoundError: If tag doesn't exist
            HTTPException: If database operation fails
        """
        try:
            tag = self.tag_repo.get_tag_by_id(tag_id)
            if not tag:
                raise TagNotFoundError(f"Tag with ID {tag_id} not found")
            
            post_count = self.tag_repo.get_tag_post_count(tag_id)
            
            return {
                "tagId": str(tag.tag_id),
                "name": tag.name,
                "postCount": post_count
            }
        except TagNotFoundError:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve tag: {str(e)}"
            )
    
    def get_tag_by_name(self, name: str) -> dict:
        """
        Get a tag by its name
        
        Args:
            name: Name of the tag
            
        Returns:
            Dictionary with tag data
            
        Raises:
            TagNotFoundError: If tag doesn't exist
            HTTPException: If database operation fails
        """
        try:
            tag = self.tag_repo.get_tag_by_name(name)
            if not tag:
                raise TagNotFoundError(f"Tag '{name}' not found")
            
            post_count = self.tag_repo.get_tag_post_count(tag.tag_id)
            
            return {
                "tagId": str(tag.tag_id),
                "name": tag.name,
                "postCount": post_count
            }
        except TagNotFoundError:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve tag: {str(e)}"
            )
