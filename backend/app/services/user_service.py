"""
User Service

Business logic for user operations.
Handles user profile management and social features.
"""

from typing import Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.models.user import User


class UserService:
    """Service for user business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_user_profile_data(self, user: User) -> Dict[str, Any]:
        """Get formatted user profile data with counts"""
        follower_count = self.user_repo.get_follower_count(user.user_id)
        following_count = self.user_repo.get_following_count(user.user_id)
        
        return {
            "user_id": str(user.user_id),
            "user_name": user.user_name,
            "email": user.email or "",
            "profile_picture": user.profile_picture,
            "created_at": user.created_at.isoformat(),
            "follower_count": follower_count,
            "following_count": following_count,
            "is_private": user.is_private
        }

    def update_user_profile(self, user: User, update_data: Dict[str, Any]) -> User:
        """Update user profile with given data"""
        return self.user_repo.update_user(user, update_data)
