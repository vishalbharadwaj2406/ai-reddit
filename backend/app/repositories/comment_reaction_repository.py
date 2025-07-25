"""
Comment Reaction Repository

Data access layer for CommentReaction operations.
Follows the established repository pattern from other repositories in the project.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.comment_reaction import CommentReaction
from app.models.comment import Comment
from app.models.user import User


class CommentReactionRepository:
    """Repository for CommentReaction data access operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_reaction(
        self,
        user_id: UUID,
        comment_id: UUID
    ) -> Optional[CommentReaction]:
        """
        Get a user's reaction to a specific comment
        
        Args:
            user_id: ID of the user
            comment_id: ID of the comment
            
        Returns:
            CommentReaction object if found, None otherwise
        """
        return self.db.query(CommentReaction).filter(
            and_(
                CommentReaction.user_id == user_id,
                CommentReaction.comment_id == comment_id,
                CommentReaction.status == "active"
            )
        ).first()
    
    def create_reaction(
        self,
        user_id: UUID,
        comment_id: UUID,
        reaction_type: str
    ) -> CommentReaction:
        """
        Create a new comment reaction
        
        Args:
            user_id: ID of the user making the reaction
            comment_id: ID of the comment being reacted to
            reaction_type: Type of reaction
            
        Returns:
            Created CommentReaction object
        """
        reaction = CommentReaction(
            user_id=user_id,
            comment_id=comment_id,
            reaction=reaction_type,
            status="active"
        )
        
        self.db.add(reaction)
        self.db.commit()
        self.db.refresh(reaction)
        return reaction
    
    def update_reaction(
        self,
        user_id: UUID,
        comment_id: UUID,
        reaction_type: str
    ) -> CommentReaction:
        """
        Update an existing comment reaction
        
        Args:
            user_id: ID of the user
            comment_id: ID of the comment
            reaction_type: New reaction type
            
        Returns:
            Updated CommentReaction object
        """
        reaction = self.get_reaction(user_id, comment_id)
        if reaction:
            reaction.reaction = reaction_type
            self.db.commit()
            self.db.refresh(reaction)
        return reaction
    
    def delete_reaction(
        self,
        user_id: UUID,
        comment_id: UUID
    ) -> bool:
        """
        Delete (soft delete) a comment reaction
        
        Args:
            user_id: ID of the user
            comment_id: ID of the comment
            
        Returns:
            True if reaction was deleted, False if not found
        """
        reaction = self.get_reaction(user_id, comment_id)
        if reaction:
            reaction.status = "deleted"
            self.db.commit()
            return True
        return False
    
    def get_comment_reactions(
        self,
        comment_id: UUID
    ) -> List[CommentReaction]:
        """
        Get all active reactions for a comment
        
        Args:
            comment_id: ID of the comment
            
        Returns:
            List of CommentReaction objects
        """
        return self.db.query(CommentReaction).filter(
            and_(
                CommentReaction.comment_id == comment_id,
                CommentReaction.status == "active"
            )
        ).all()
    
    def get_reaction_counts(
        self,
        comment_id: UUID
    ) -> dict:
        """
        Get reaction counts for a comment
        
        Args:
            comment_id: ID of the comment
            
        Returns:
            Dictionary with reaction counts
        """
        reactions = self.get_comment_reactions(comment_id)
        
        counts = {
            "upvote": 0,
            "downvote": 0,
            "heart": 0,
            "insightful": 0,
            "accurate": 0
        }
        
        for reaction in reactions:
            if reaction.reaction in counts:
                counts[reaction.reaction] += 1
        
        return counts
    
    def verify_comment_exists(self, comment_id: UUID) -> bool:
        """
        Verify that a comment exists and is active
        
        Args:
            comment_id: ID of the comment to verify
            
        Returns:
            True if comment exists and is active, False otherwise
        """
        return self.db.query(Comment).filter(
            and_(
                Comment.comment_id == comment_id,
                Comment.status == "active"
            )
        ).first() is not None
    
    def verify_comment_owner(
        self,
        comment_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Verify if a user owns a specific comment
        
        Args:
            comment_id: ID of the comment
            user_id: ID of the user
            
        Returns:
            True if user owns the comment, False otherwise
        """
        comment = self.db.query(Comment).filter(
            and_(
                Comment.comment_id == comment_id,
                Comment.status == "active"
            )
        ).first()
        
        return comment is not None and comment.user_id == user_id
