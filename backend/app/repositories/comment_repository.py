"""
Comment Repository

Data access layer for Comment operations.
Follows the established repository pattern from other repositories in the project.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.comment import Comment
from app.models.user import User
from app.models.post import Post


class CommentRepository:
    """Repository for Comment data access operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_comment(
        self,
        post_id: UUID,
        user_id: UUID,
        content: str,
        parent_comment_id: Optional[UUID] = None
    ) -> Comment:
        """Create a new comment"""
        comment = Comment(
            post_id=post_id,
            user_id=user_id,
            content=content,
            parent_comment_id=parent_comment_id
        )
        
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment
    
    def get_comment_by_id(self, comment_id: UUID) -> Optional[Comment]:
        """Get comment by ID"""
        return self.db.query(Comment).filter(
            and_(
                Comment.comment_id == comment_id,
                Comment.status == "active"
            )
        ).first()
    
    def get_comments_by_post_id(
        self,
        post_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[Comment]:
        """Get comments for a post with pagination"""
        return self.db.query(Comment)\
            .options(joinedload(Comment.user))\
            .filter(
                and_(
                    Comment.post_id == post_id,
                    Comment.status == "active"
                )
            )\
            .order_by(Comment.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
    
    def verify_post_exists(self, post_id: UUID) -> bool:
        """Verify that a post exists and is active"""
        return self.db.query(Post).filter(
            and_(
                Post.post_id == post_id,
                Post.status == "active"
            )
        ).first() is not None
    
    def verify_parent_comment_belongs_to_post(
        self,
        parent_comment_id: UUID,
        post_id: UUID
    ) -> bool:
        """Verify that parent comment belongs to the same post"""
        parent_comment = self.db.query(Comment).filter(
            and_(
                Comment.comment_id == parent_comment_id,
                Comment.status == "active"
            )
        ).first()
        
        if not parent_comment:
            return False
            
        return parent_comment.post_id == post_id
