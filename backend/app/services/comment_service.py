"""
Comment Service

Business logic layer for Comment operations.
Follows the established service pattern from other services in the project.
"""

from typing import Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.repositories.comment_repository import CommentRepository


class CommentService:
    """Service for Comment business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.comment_repo = CommentRepository(db)
    
    def create_comment(
        self,
        post_id: UUID,
        user_id: UUID,
        content: str,
        parent_comment_id: Optional[UUID] = None
    ) -> Comment:
        """
        Create a new comment with business logic validation
        
        Args:
            post_id: ID of the post to comment on
            user_id: ID of the user creating the comment
            content: Comment content
            parent_comment_id: Optional parent comment for replies
            
        Returns:
            Created Comment object
            
        Raises:
            HTTPException: If post doesn't exist or parent comment validation fails
        """
        
        # Verify post exists
        if not self.comment_repo.verify_post_exists(post_id):
            raise HTTPException(status_code=404, detail="Post not found")
        
        # If parent comment specified, validate it
        if parent_comment_id:
            if not self.comment_repo.verify_parent_comment_belongs_to_post(
                parent_comment_id, post_id
            ):
                raise HTTPException(
                    status_code=400, 
                    detail="Parent comment must belong to the same post"
                )
        
        # Create the comment
        try:
            comment = self.comment_repo.create_comment(
                post_id=post_id,
                user_id=user_id,
                content=content,
                parent_comment_id=parent_comment_id
            )
            return comment
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create comment: {str(e)}"
            )
    
    def get_comments_for_post(
        self,
        post_id: UUID,
        limit: int = 20,
        offset: int = 0
    ):
        """
        Get comments for a post with pagination
        
        Args:
            post_id: ID of the post
            limit: Maximum number of comments to return
            offset: Number of comments to skip
            
        Returns:
            List of Comment objects
            
        Raises:
            HTTPException: If post doesn't exist
        """
        
        # Verify post exists
        if not self.comment_repo.verify_post_exists(post_id):
            raise HTTPException(status_code=404, detail="Post not found")
        
        try:
            comments = self.comment_repo.get_comments_by_post_id(
                post_id=post_id,
                limit=limit,
                offset=offset
            )
            return comments
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve comments: {str(e)}"
            )
