"""
Analytics Service

Business logic for tracking post views and shares.
Handles the creation and management of analytics data.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from app.models.post import Post
from app.models.post_view import PostView
from app.models.post_share import PostShare
from app.schemas.analytics import PostViewResponse, PostShareResponse


class AnalyticsServiceError(Exception):
    """Custom exception for analytics service errors"""
    pass


class AnalyticsService:
    """Service for handling post analytics operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def track_post_view(self, post_id: UUID, user_id: Optional[UUID] = None) -> PostViewResponse:
        """
        Track a view for a post.
        
        Args:
            post_id: UUID of the post being viewed
            user_id: UUID of the user viewing (None for anonymous views)
            
        Returns:
            PostViewResponse with view details
            
        Raises:
            AnalyticsServiceError: If post not found or other business logic errors
        """
        # Verify post exists
        post = self.db.query(Post).filter(
            Post.post_id == post_id,
            Post.status == "active"
        ).first()
        
        if not post:
            raise AnalyticsServiceError("Post not found")
        
        # Create view record
        view = PostView(
            post_id=post_id,
            user_id=user_id,
            viewed_at=datetime.now(timezone.utc),
            status="active"
        )
        
        self.db.add(view)
        self.db.commit()
        self.db.refresh(view)
        
        return PostViewResponse(
            view_id=str(view.view_id),
            post_id=view.post_id,
            user_id=view.user_id,
            viewed_at=view.viewed_at
        )
    
    def track_post_share(self, post_id: UUID, user_id: UUID, platform: str = "direct_link") -> PostShareResponse:
        """
        Track a share for a post.
        
        Args:
            post_id: UUID of the post being shared
            user_id: UUID of the user sharing
            platform: Platform where shared (twitter, facebook, etc.)
            
        Returns:
            PostShareResponse with share details
            
        Raises:
            AnalyticsServiceError: If post not found or other business logic errors
        """
        # Verify post exists
        post = self.db.query(Post).filter(
            Post.post_id == post_id,
            Post.status == "active"
        ).first()
        
        if not post:
            raise AnalyticsServiceError("Post not found")
        
        # Create share record
        share = PostShare(
            post_id=post_id,
            shared_by_user_id=user_id,
            platform=platform,
            shared_at=datetime.now(timezone.utc),
            status="active"
        )
        
        self.db.add(share)
        self.db.commit()
        self.db.refresh(share)
        
        return PostShareResponse(
            shareId=share.share_id,
            postId=share.post_id,
            sharedBy=share.shared_by_user_id,
            platform=share.platform,
            sharedAt=share.shared_at
        )
    
    def get_post_analytics(self, post_id: UUID) -> dict:
        """
        Get analytics summary for a post.
        
        Args:
            post_id: UUID of the post
            
        Returns:
            Dictionary with view count, share count, etc.
        """
        view_count = self.db.query(PostView).filter(
            PostView.post_id == post_id,
            PostView.status == "active"
        ).count()
        
        share_count = self.db.query(PostShare).filter(
            PostShare.post_id == post_id,
            PostShare.status == "active"
        ).count()
        
        return {
            "viewCount": view_count,
            "shareCount": share_count
        }
