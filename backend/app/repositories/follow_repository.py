"""
Follow Repository

Repository layer for follow relationship operations.
Handles database interactions for follow/unfollow functionality.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from uuid import UUID

from app.models.follow import Follow
from app.models.user import User


class FollowRepository:
    """Repository for follow relationship operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_follow_relationship(self, follower_id: UUID, following_id: UUID) -> Optional[Follow]:
        """
        Get follow relationship between two users.
        
        Args:
            follower_id: ID of the user who is following
            following_id: ID of the user being followed
            
        Returns:
            Follow object if relationship exists, None otherwise
        """
        return self.db.query(Follow).filter(
            and_(
                Follow.follower_id == follower_id,
                Follow.following_id == following_id
            )
        ).first()
    
    def create_follow_request(self, follower_id: UUID, following_id: UUID) -> Follow:
        """
        Create a new follow request.
        
        Args:
            follower_id: ID of the user who wants to follow
            following_id: ID of the user to be followed
            
        Returns:
            Created Follow object
        """
        follow = Follow(
            follower_id=follower_id,
            following_id=following_id,
            status="pending"
        )
        self.db.add(follow)
        self.db.commit()
        self.db.refresh(follow)
        return follow
    
    def create_instant_follow(self, follower_id: UUID, following_id: UUID) -> Follow:
        """
        Create an instant follow (for public accounts).
        
        Args:
            follower_id: ID of the user who wants to follow
            following_id: ID of the user to be followed
            
        Returns:
            Created Follow object with accepted status
        """
        follow = Follow(
            follower_id=follower_id,
            following_id=following_id,
            status="accepted"
        )
        self.db.add(follow)
        self.db.commit()
        self.db.refresh(follow)
        return follow
    
    def accept_follow_request(self, follower_id: UUID, following_id: UUID) -> Optional[Follow]:
        """
        Accept a pending follow request.
        
        Args:
            follower_id: ID of the follower
            following_id: ID of the user being followed
            
        Returns:
            Updated Follow object if found and was pending, None otherwise
        """
        follow = self.get_follow_relationship(follower_id, following_id)
        if follow and follow.is_pending:
            follow.accept()
            self.db.commit()
            self.db.refresh(follow)
            return follow
        return None
    
    def reject_follow_request(self, follower_id: UUID, following_id: UUID) -> bool:
        """
        Reject a follow request (deletes the record for clean re-request).
        
        Args:
            follower_id: ID of the follower
            following_id: ID of the user being followed
            
        Returns:
            True if request was found and rejected, False otherwise
        """
        follow = self.get_follow_relationship(follower_id, following_id)
        if follow and follow.is_pending:
            self.db.delete(follow)
            self.db.commit()
            return True
        return False
    
    def unfollow(self, follower_id: UUID, following_id: UUID) -> bool:
        """
        Unfollow a user (deletes the relationship).
        
        Args:
            follower_id: ID of the follower
            following_id: ID of the user being followed
            
        Returns:
            True if relationship was found and deleted, False otherwise
        """
        follow = self.get_follow_relationship(follower_id, following_id)
        if follow:
            self.db.delete(follow)
            self.db.commit()
            return True
        return False
    
    def get_followers(self, user_id: UUID, status: str = "accepted") -> List[Follow]:
        """
        Get all followers of a user.
        
        Args:
            user_id: ID of the user
            status: Follow status to filter by
            
        Returns:
            List of Follow objects
        """
        return self.db.query(Follow).filter(
            and_(
                Follow.following_id == user_id,
                Follow.status == status
            )
        ).all()
    
    def get_following(self, user_id: UUID, status: str = "accepted") -> List[Follow]:
        """
        Get all users that a user is following.
        
        Args:
            user_id: ID of the user
            status: Follow status to filter by
            
        Returns:
            List of Follow objects
        """
        return self.db.query(Follow).filter(
            and_(
                Follow.follower_id == user_id,
                Follow.status == status
            )
        ).all()
    
    def get_pending_requests(self, user_id: UUID) -> List[Follow]:
        """
        Get all pending follow requests for a user.
        
        Args:
            user_id: ID of the user being followed
            
        Returns:
            List of pending Follow objects
        """
        return self.get_followers(user_id, status="pending")
    
    def get_follower_count(self, user_id: UUID) -> int:
        """
        Get count of accepted followers for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Count of accepted followers
        """
        return self.db.query(Follow).filter(
            and_(
                Follow.following_id == user_id,
                Follow.status == "accepted"
            )
        ).count()
    
    def get_following_count(self, user_id: UUID) -> int:
        """
        Get count of accepted following for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Count of accepted following
        """
        return self.db.query(Follow).filter(
            and_(
                Follow.follower_id == user_id,
                Follow.status == "accepted"
            )
        ).count()
