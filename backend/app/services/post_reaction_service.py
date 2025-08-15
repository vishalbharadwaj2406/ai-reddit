"""
Post Reaction Service

Business logic layer for PostReaction operations.
Follows the established service pattern from other services in the project.
"""

from typing import Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.post_reaction import PostReaction
from app.repositories.post_reaction_repository import PostReactionRepository


class PostReactionService:
    """Service for PostReaction business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.reaction_repo = PostReactionRepository(db)
    
    def add_or_update_reaction(
        self,
        post_id: UUID,
        user_id: UUID,
        reaction_type: str
    ) -> tuple[Optional[PostReaction], str]:
        """
        Add or update a user's reaction to a post
        
        Business logic:
        - Users cannot react to their own posts
        - If user has no existing reaction, create new one
        - If user has same reaction, remove it (toggle off)
        - If user has different reaction, update it
        
        Args:
            post_id: ID of the post to react to
            user_id: ID of the user making the reaction
            reaction_type: Type of reaction
            
        Returns:
            Tuple of (PostReaction object or None, action_type)
            action_type can be: "created", "updated", "removed"
            
        Raises:
            HTTPException: If post doesn't exist or user tries to react to own post
        """
        
        # Validate reaction type
        if not PostReaction.is_valid_reaction(reaction_type):
            raise HTTPException(
                status_code=422,
                detail=f"Invalid reaction type: {reaction_type}"
            )
        
        # Verify post exists
        if not self.reaction_repo.verify_post_exists(post_id):
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Prevent users from reacting to their own posts
        if self.reaction_repo.verify_post_owner(post_id, user_id):
            raise HTTPException(
                status_code=400,
                detail="Cannot react to your own post"
            )
        
        try:
            # Check for existing reaction
            existing_reaction = self.reaction_repo.get_reaction(user_id, post_id)
            
            if existing_reaction:
                if existing_reaction.reaction == reaction_type:
                    # Same reaction - toggle off (remove)
                    self.reaction_repo.delete_reaction(user_id, post_id)
                    return None, "removed"
                else:
                    # Different reaction - update
                    updated_reaction = self.reaction_repo.update_reaction(
                        user_id, post_id, reaction_type
                    )
                    return updated_reaction, "updated"
            else:
                # No existing reaction - create new
                new_reaction = self.reaction_repo.create_reaction(
                    user_id, post_id, reaction_type
                )
                return new_reaction, "created"
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process reaction: {str(e)}"
            )
    
    def get_post_reactions(
        self,
        post_id: UUID
    ) -> dict:
        """
        Get reaction counts for a post
        
        Args:
            post_id: ID of the post
            
        Returns:
            Dictionary with reaction counts
            
        Raises:
            HTTPException: If post doesn't exist
        """
        
        # Verify post exists
        if not self.reaction_repo.verify_post_exists(post_id):
            raise HTTPException(status_code=404, detail="Post not found")
        
        try:
            return self.reaction_repo.get_reaction_counts(post_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve reaction counts: {str(e)}"
            )
    
    def get_user_reaction(
        self,
        post_id: UUID,
        user_id: UUID
    ) -> Optional[str]:
        """
        Get a user's reaction to a specific post
        
        Args:
            post_id: ID of the post
            user_id: ID of the user
            
        Returns:
            Reaction type string if user has reacted, None otherwise
            
        Raises:
            HTTPException: If post doesn't exist
        """
        
        # Verify post exists
        if not self.reaction_repo.verify_post_exists(post_id):
            raise HTTPException(status_code=404, detail="Post not found")
        
        try:
            reaction = self.reaction_repo.get_reaction(user_id, post_id)
            return reaction.reaction if reaction else None
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve user reaction: {str(e)}"
            )
