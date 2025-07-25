"""
Comment Reaction Service

Business logic layer for CommentReaction operations.
Follows the established service pattern from other services in the project.
"""

from typing import Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.comment_reaction import CommentReaction
from app.repositories.comment_reaction_repository import CommentReactionRepository


class CommentReactionService:
    """Service for CommentReaction business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.reaction_repo = CommentReactionRepository(db)
    
    def add_or_update_reaction(
        self,
        comment_id: UUID,
        user_id: UUID,
        reaction_type: str
    ) -> tuple[Optional[CommentReaction], str]:
        """
        Add or update a user's reaction to a comment
        
        Business logic:
        - Users cannot react to their own comments
        - If user has no existing reaction, create new one
        - If user has same reaction, remove it (toggle off)
        - If user has different reaction, update it
        
        Args:
            comment_id: ID of the comment to react to
            user_id: ID of the user making the reaction
            reaction_type: Type of reaction
            
        Returns:
            Tuple of (CommentReaction object or None, action_type)
            action_type can be: "created", "updated", "removed"
            
        Raises:
            HTTPException: If comment doesn't exist or user tries to react to own comment
        """
        
        # Validate reaction type
        if not CommentReaction.is_valid_reaction(reaction_type):
            raise HTTPException(
                status_code=422,
                detail=f"Invalid reaction type: {reaction_type}"
            )
        
        # Verify comment exists
        if not self.reaction_repo.verify_comment_exists(comment_id):
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Prevent users from reacting to their own comments
        if self.reaction_repo.verify_comment_owner(comment_id, user_id):
            raise HTTPException(
                status_code=400,
                detail="Cannot react to your own comment"
            )
        
        try:
            # Check for existing reaction
            existing_reaction = self.reaction_repo.get_reaction(user_id, comment_id)
            
            if existing_reaction:
                if existing_reaction.reaction == reaction_type:
                    # Same reaction - toggle off (remove)
                    self.reaction_repo.delete_reaction(user_id, comment_id)
                    return None, "removed"
                else:
                    # Different reaction - update
                    updated_reaction = self.reaction_repo.update_reaction(
                        user_id, comment_id, reaction_type
                    )
                    return updated_reaction, "updated"
            else:
                # No existing reaction - create new
                new_reaction = self.reaction_repo.create_reaction(
                    user_id, comment_id, reaction_type
                )
                return new_reaction, "created"
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process reaction: {str(e)}"
            )
    
    def get_comment_reactions(
        self,
        comment_id: UUID
    ) -> dict:
        """
        Get reaction counts for a comment
        
        Args:
            comment_id: ID of the comment
            
        Returns:
            Dictionary with reaction counts
            
        Raises:
            HTTPException: If comment doesn't exist
        """
        
        # Verify comment exists
        if not self.reaction_repo.verify_comment_exists(comment_id):
            raise HTTPException(status_code=404, detail="Comment not found")
        
        try:
            return self.reaction_repo.get_reaction_counts(comment_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve reaction counts: {str(e)}"
            )
    
    def get_user_reaction(
        self,
        comment_id: UUID,
        user_id: UUID
    ) -> Optional[str]:
        """
        Get a user's reaction to a specific comment
        
        Args:
            comment_id: ID of the comment
            user_id: ID of the user
            
        Returns:
            Reaction type string if user has reacted, None otherwise
            
        Raises:
            HTTPException: If comment doesn't exist
        """
        
        # Verify comment exists
        if not self.reaction_repo.verify_comment_exists(comment_id):
            raise HTTPException(status_code=404, detail="Comment not found")
        
        try:
            reaction = self.reaction_repo.get_reaction(user_id, comment_id)
            return reaction.reaction if reaction else None
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve user reaction: {str(e)}"
            )
