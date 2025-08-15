"""
Post Reaction Repository

Data access layer for PostReaction operations.
Follows the established repository pattern from other repositories in the project.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.post_reaction import PostReaction
from app.models.post import Post
from app.models.user import User


class PostReactionRepository:
    """Repository for PostReaction data access operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_reaction(
        self,
        user_id: UUID,
        post_id: UUID
    ) -> Optional[PostReaction]:
        """
        Get a user's reaction to a specific post
        
        Args:
            user_id: ID of the user
            post_id: ID of the post
            
        Returns:
            PostReaction object if found, None otherwise
        """
        return self.db.query(PostReaction).filter(
            and_(
                PostReaction.user_id == user_id,
                PostReaction.post_id == post_id,
                PostReaction.status == "active"
            )
        ).first()
    
    def create_reaction(
        self,
        user_id: UUID,
        post_id: UUID,
        reaction_type: str
    ) -> PostReaction:
        """
        Create a new post reaction
        
        Args:
            user_id: ID of the user making the reaction
            post_id: ID of the post being reacted to
            reaction_type: Type of reaction
            
        Returns:
            Created PostReaction object
        """
        reaction = PostReaction(
            user_id=user_id,
            post_id=post_id,
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
        post_id: UUID,
        reaction_type: str
    ) -> PostReaction:
        """
        Update an existing post reaction
        
        Args:
            user_id: ID of the user
            post_id: ID of the post
            reaction_type: New reaction type
            
        Returns:
            Updated PostReaction object
        """
        reaction = self.get_reaction(user_id, post_id)
        if reaction:
            reaction.reaction = reaction_type
            self.db.commit()
            self.db.refresh(reaction)
        return reaction
    
    def delete_reaction(
        self,
        user_id: UUID,
        post_id: UUID
    ) -> bool:
        """
        Delete (soft delete) a post reaction
        
        Args:
            user_id: ID of the user
            post_id: ID of the post
            
        Returns:
            True if reaction was deleted, False if not found
        """
        reaction = self.get_reaction(user_id, post_id)
        if reaction:
            reaction.status = "deleted"
            self.db.commit()
            return True
        return False
    
    def get_post_reactions(
        self,
        post_id: UUID
    ) -> List[PostReaction]:
        """
        Get all active reactions for a post
        
        Args:
            post_id: ID of the post
            
        Returns:
            List of PostReaction objects
        """
        return self.db.query(PostReaction).filter(
            and_(
                PostReaction.post_id == post_id,
                PostReaction.status == "active"
            )
        ).all()
    
    def get_reaction_counts(
        self,
        post_id: UUID
    ) -> dict:
        """
        Get reaction counts for a post
        
        Args:
            post_id: ID of the post
            
        Returns:
            Dictionary with reaction counts
        """
        reactions = self.get_post_reactions(post_id)
        
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
    
    def verify_post_exists(self, post_id: UUID) -> bool:
        """
        Verify that a post exists and is active
        
        Args:
            post_id: ID of the post to verify
            
        Returns:
            True if post exists and is active, False otherwise
        """
        return self.db.query(Post).filter(
            and_(
                Post.post_id == post_id,
                Post.status == "active"
            )
        ).first() is not None
    
    def verify_post_owner(
        self,
        post_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Verify if a user owns a specific post
        
        Args:
            post_id: ID of the post
            user_id: ID of the user
            
        Returns:
            True if user owns the post, False otherwise
        """
        post = self.db.query(Post).filter(
            and_(
                Post.post_id == post_id,
                Post.status == "active"
            )
        ).first()
        
        return post is not None and post.user_id == user_id
