"""
Follow Service

Business logic layer for follow/unfollow operations.
Handles Instagram-like follow system with privacy controls.
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from uuid import UUID

from app.repositories.follow_repository import FollowRepository
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.models.follow import Follow


class FollowService:
    """Service layer for follow operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.follow_repo = FollowRepository(db)
        self.user_repo = UserRepository(db)
    
    def follow_user(self, follower_id: UUID, following_id: UUID) -> Dict[str, Any]:
        """
        Follow a user (Instagram-like behavior).
        
        Args:
            follower_id: ID of the user who wants to follow
            following_id: ID of the user to be followed
            
        Returns:
            Dict with follow status and message
        """
        # Check if target user exists
        target_user = self.user_repo.get_by_id(following_id)
        if not target_user:
            return {
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        
        # Check if user is trying to follow themselves
        if follower_id == following_id:
            return {
                "success": False,
                "message": "Cannot follow yourself",
                "error_code": "SELF_FOLLOW_FORBIDDEN"
            }
        
        # Check if follow relationship already exists
        existing_follow = self.follow_repo.get_follow_relationship(follower_id, following_id)
        if existing_follow:
            if existing_follow.is_accepted:
                return {
                    "success": False,
                    "message": "Already following this user",
                    "error_code": "ALREADY_FOLLOWING"
                }
            elif existing_follow.is_pending:
                return {
                    "success": False,
                    "message": "Follow request already sent",
                    "error_code": "REQUEST_ALREADY_SENT"
                }
        
        # Create follow relationship based on target user privacy
        if target_user.is_private:
            # Private account - create pending request
            follow = self.follow_repo.create_follow_request(follower_id, following_id)
            return {
                "success": True,
                "message": "Follow request sent",
                "follow_status": "pending",
                "data": {
                    "follow_id": f"{follower_id}_{following_id}",
                    "status": follow.status,
                    "created_at": follow.created_at.isoformat()
                }
            }
        else:
            # Public account - instant follow
            follow = self.follow_repo.create_instant_follow(follower_id, following_id)
            return {
                "success": True,
                "message": "Now following user",
                "follow_status": "accepted",
                "data": {
                    "follow_id": f"{follower_id}_{following_id}",
                    "status": follow.status,
                    "created_at": follow.created_at.isoformat()
                }
            }
    
    def unfollow_user(self, follower_id: UUID, following_id: UUID) -> Dict[str, Any]:
        """
        Unfollow a user.
        
        Args:
            follower_id: ID of the user who wants to unfollow
            following_id: ID of the user to be unfollowed
            
        Returns:
            Dict with unfollow status and message
        """
        # Check if follow relationship exists
        follow = self.follow_repo.get_follow_relationship(follower_id, following_id)
        if not follow:
            return {
                "success": False,
                "message": "Not following this user",
                "error_code": "NOT_FOLLOWING"
            }
        
        # Remove follow relationship
        success = self.follow_repo.unfollow(follower_id, following_id)
        if success:
            return {
                "success": True,
                "message": "Unfollowed user successfully",
                "follow_status": "none"
            }
        else:
            return {
                "success": False,
                "message": "Failed to unfollow user",
                "error_code": "UNFOLLOW_FAILED"
            }
    
    def get_follow_status(self, follower_id: UUID, following_id: UUID) -> str:
        """
        Get follow status between two users.
        
        Args:
            follower_id: ID of the potential follower
            following_id: ID of the potential following
            
        Returns:
            Follow status: 'none', 'pending', 'accepted'
        """
        follow = self.follow_repo.get_follow_relationship(follower_id, following_id)
        if not follow:
            return "none"
        return follow.status
    
    def accept_follow_request(self, user_id: UUID, follower_id: UUID) -> Dict[str, Any]:
        """
        Accept a follow request.
        
        Args:
            user_id: ID of the user accepting the request
            follower_id: ID of the user who sent the request
            
        Returns:
            Dict with acceptance status and message
        """
        follow = self.follow_repo.accept_follow_request(follower_id, user_id)
        if follow:
            return {
                "success": True,
                "message": "Follow request accepted",
                "data": {
                    "follow_id": f"{follower_id}_{user_id}",
                    "status": follow.status,
                    "updated_at": follow.updated_at.isoformat()
                }
            }
        else:
            return {
                "success": False,
                "message": "Follow request not found or already processed",
                "error_code": "REQUEST_NOT_FOUND"
            }
    
    def reject_follow_request(self, user_id: UUID, follower_id: UUID) -> Dict[str, Any]:
        """
        Reject a follow request.
        
        Args:
            user_id: ID of the user rejecting the request
            follower_id: ID of the user who sent the request
            
        Returns:
            Dict with rejection status and message
        """
        success = self.follow_repo.reject_follow_request(follower_id, user_id)
        if success:
            return {
                "success": True,
                "message": "Follow request rejected"
            }
        else:
            return {
                "success": False,
                "message": "Follow request not found",
                "error_code": "REQUEST_NOT_FOUND"
            }
    
    def get_follow_requests(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get pending follow requests for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dict with list of pending requests
        """
        pending_requests = self.follow_repo.get_pending_requests(user_id)
        
        # Format request data
        requests_data = []
        for follow in pending_requests:
            follower = self.user_repo.get_by_id(follow.follower_id)
            if follower:
                requests_data.append({
                    "follower_id": str(follow.follower_id),
                    "follower_name": follower.user_name,
                    "profile_picture": follower.profile_picture,
                    "requested_at": follow.created_at.isoformat()
                })
        
        return {
            "success": True,
            "message": "Follow requests retrieved successfully",
            "data": {
                "requests": requests_data,
                "count": len(requests_data)
            }
        }
    
    def get_enhanced_follow_status(self, current_user_id: UUID, target_user_id: UUID) -> Dict[str, Any]:
        """
        Get enhanced follow status with context for UI.
        
        Args:
            current_user_id: ID of the current user
            target_user_id: ID of the target user
            
        Returns:
            Dict with follow status and UI context
        """
        follow_status = self.get_follow_status(current_user_id, target_user_id)
        reverse_follow_status = self.get_follow_status(target_user_id, current_user_id)
        
        return {
            "follow_status": follow_status,
            "is_following": follow_status == "accepted",
            "request_pending": follow_status == "pending",
            "follows_you": reverse_follow_status == "accepted",
            "ui_context": {
                "button_text": self._get_follow_button_text(follow_status),
                "button_action": self._get_follow_button_action(follow_status),
                "can_send_request": follow_status == "none"
            }
        }
    
    def _get_follow_button_text(self, status: str) -> str:
        """Get appropriate button text based on follow status"""
        if status == "none":
            return "Follow"
        elif status == "pending":
            return "Requested"
        elif status == "accepted":
            return "Following"
        return "Follow"
    
    def _get_follow_button_action(self, status: str) -> str:
        """Get appropriate button action based on follow status"""
        if status == "none":
            return "follow"
        elif status == "pending":
            return "cancel_request"
        elif status == "accepted":
            return "unfollow"
        return "follow"
    
    def get_followers_list(self, user_id: UUID, requesting_user_id: Optional[UUID] = None, 
                          limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Get followers list for a user with privacy controls.
        
        Args:
            user_id: ID of the user whose followers to get
            requesting_user_id: ID of the user making the request (optional)
            limit: Maximum number of followers to return
            offset: Number of followers to skip
            
        Returns:
            Dict with followers list and pagination info
        """
        # Check if target user exists
        target_user = self.user_repo.get_by_id(user_id)
        if not target_user:
            return {
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        
        # Privacy check: if user is private and requesting user is not following them
        if target_user.is_private and requesting_user_id != user_id:
            if not requesting_user_id:
                return {
                    "success": False,
                    "message": "Private account - authentication required",
                    "error_code": "PRIVATE_ACCOUNT_AUTH_REQUIRED"
                }
            
            # Check if requesting user is following the target user
            follow_status = self.get_follow_status(requesting_user_id, user_id)
            if follow_status != "accepted":
                return {
                    "success": False,
                    "message": "Private account - must be following to see followers",
                    "error_code": "PRIVATE_ACCOUNT_FOLLOW_REQUIRED"
                }
        
        # Get followers with pagination
        followers = self.follow_repo.get_followers(user_id, status="accepted")
        total_count = len(followers)
        
        # Apply pagination
        paginated_followers = followers[offset:offset + limit]
        
        # Format followers data
        followers_data = []
        for follow in paginated_followers:
            follower = self.user_repo.get_by_id(follow.follower_id)
            if follower:
                follower_data = {
                    "user_id": str(follower.user_id),
                    "user_name": follower.user_name,
                    "profile_picture": follower.profile_picture,
                    "is_private": follower.is_private,
                    "followed_at": follow.created_at.isoformat()
                }
                
                # Add follow status if requesting user is authenticated
                if requesting_user_id:
                    follower_data["follow_status"] = self.get_enhanced_follow_status(
                        requesting_user_id, follower.user_id
                    )
                
                followers_data.append(follower_data)
        
        return {
            "success": True,
            "message": "Followers retrieved successfully",
            "data": {
                "followers": followers_data,
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_next": offset + limit < total_count,
                    "has_previous": offset > 0
                }
            }
        }
    
    def get_following_list(self, user_id: UUID, requesting_user_id: Optional[UUID] = None,
                          limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Get following list for a user with privacy controls.
        
        Args:
            user_id: ID of the user whose following to get
            requesting_user_id: ID of the user making the request (optional)
            limit: Maximum number of following to return
            offset: Number of following to skip
            
        Returns:
            Dict with following list and pagination info
        """
        # Check if target user exists
        target_user = self.user_repo.get_by_id(user_id)
        if not target_user:
            return {
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        
        # Privacy check: if user is private and requesting user is not following them
        if target_user.is_private and requesting_user_id != user_id:
            if not requesting_user_id:
                return {
                    "success": False,
                    "message": "Private account - authentication required",
                    "error_code": "PRIVATE_ACCOUNT_AUTH_REQUIRED"
                }
            
            # Check if requesting user is following the target user
            follow_status = self.get_follow_status(requesting_user_id, user_id)
            if follow_status != "accepted":
                return {
                    "success": False,
                    "message": "Private account - must be following to see following",
                    "error_code": "PRIVATE_ACCOUNT_FOLLOW_REQUIRED"
                }
        
        # Get following with pagination
        following = self.follow_repo.get_following(user_id, status="accepted")
        total_count = len(following)
        
        # Apply pagination
        paginated_following = following[offset:offset + limit]
        
        # Format following data
        following_data = []
        for follow in paginated_following:
            following_user = self.user_repo.get_by_id(follow.following_id)
            if following_user:
                following_user_data = {
                    "user_id": str(following_user.user_id),
                    "user_name": following_user.user_name,
                    "profile_picture": following_user.profile_picture,
                    "is_private": following_user.is_private,
                    "followed_at": follow.created_at.isoformat()
                }
                
                # Add follow status if requesting user is authenticated
                if requesting_user_id:
                    following_user_data["follow_status"] = self.get_enhanced_follow_status(
                        requesting_user_id, following_user.user_id
                    )
                
                following_data.append(following_user_data)
        
        return {
            "success": True,
            "message": "Following retrieved successfully",
            "data": {
                "following": following_data,
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_next": offset + limit < total_count,
                    "has_previous": offset > 0
                }
            }
        }
    
    def get_followers_list(self, user_id: UUID, current_user_id: UUID = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Get followers list for a user with privacy controls.
        
        Args:
            user_id: ID of the user to get followers for
            current_user_id: ID of the current user (for privacy checks)
            limit: Maximum number of followers to return
            offset: Number of followers to skip
            
        Returns:
            Dict with followers list and pagination info
        """
        # Get target user
        target_user = self.user_repo.get_by_id(user_id)
        if not target_user:
            return {
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        
        # Privacy check: private accounts only show followers to the account owner or approved followers
        if target_user.is_private and current_user_id != user_id:
            if current_user_id is None:
                return {
                    "success": False,
                    "message": "This account is private",
                    "error_code": "PRIVATE_ACCOUNT"
                }
            
            # Check if current user is approved follower
            follow_status = self.get_follow_status(current_user_id, user_id)
            if follow_status != "accepted":
                return {
                    "success": False,
                    "message": "This account is private",
                    "error_code": "PRIVATE_ACCOUNT"
                }
        
        # Get followers with pagination
        followers = self.follow_repo.get_followers(user_id, status="accepted")
        total_count = len(followers)
        
        # Apply pagination
        paginated_followers = followers[offset:offset + limit]
        
        # Format follower data
        followers_data = []
        for follow in paginated_followers:
            follower = self.user_repo.get_by_id(follow.follower_id)
            if follower:
                follower_data = {
                    "user_id": str(follower.user_id),
                    "user_name": follower.user_name,
                    "profile_picture": follower.profile_picture,
                    "is_private": follower.is_private,
                    "followed_at": follow.created_at.isoformat()
                }
                
                # Add follow status if current user is authenticated
                if current_user_id:
                    follower_data["follow_status"] = self.get_enhanced_follow_status(
                        current_user_id, follower.user_id
                    )
                
                followers_data.append(follower_data)
        
        return {
            "success": True,
            "message": "Followers retrieved successfully",
            "data": {
                "followers": followers_data,
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_next": offset + limit < total_count,
                    "has_previous": offset > 0
                }
            }
        }
    
    def get_following_list(self, user_id: UUID, current_user_id: UUID = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Get following list for a user with privacy controls.
        
        Args:
            user_id: ID of the user to get following for
            current_user_id: ID of the current user (for privacy checks)
            limit: Maximum number of following to return
            offset: Number of following to skip
            
        Returns:
            Dict with following list and pagination info
        """
        # Get target user
        target_user = self.user_repo.get_by_id(user_id)
        if not target_user:
            return {
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        
        # Privacy check: private accounts only show following to the account owner or approved followers
        if target_user.is_private and current_user_id != user_id:
            if current_user_id is None:
                return {
                    "success": False,
                    "message": "This account is private",
                    "error_code": "PRIVATE_ACCOUNT"
                }
            
            # Check if current user is approved follower
            follow_status = self.get_follow_status(current_user_id, user_id)
            if follow_status != "accepted":
                return {
                    "success": False,
                    "message": "This account is private",
                    "error_code": "PRIVATE_ACCOUNT"
                }
        
        # Get following with pagination
        following = self.follow_repo.get_following(user_id, status="accepted")
        total_count = len(following)
        
        # Apply pagination
        paginated_following = following[offset:offset + limit]
        
        # Format following data
        following_data = []
        for follow in paginated_following:
            followed_user = self.user_repo.get_by_id(follow.following_id)
            if followed_user:
                following_item = {
                    "user_id": str(followed_user.user_id),
                    "user_name": followed_user.user_name,
                    "profile_picture": followed_user.profile_picture,
                    "is_private": followed_user.is_private,
                    "followed_at": follow.created_at.isoformat()
                }
                
                # Add follow status if current user is authenticated
                if current_user_id:
                    following_item["follow_status"] = self.get_enhanced_follow_status(
                        current_user_id, followed_user.user_id
                    )
                
                following_data.append(following_item)
        
        return {
            "success": True,
            "message": "Following retrieved successfully",
            "data": {
                "following": following_data,
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_next": offset + limit < total_count,
                    "has_previous": offset > 0
                }
            }
        }
