"""
Analytics Schema Definitions

Pydantic schemas for post analytics endpoints (view and share tracking).
"""

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class PostViewCreate(BaseModel):
    """Schema for creating a post view (no fields needed - just the action)"""
    pass


class PostViewResponse(BaseModel):
    """Response schema for post view tracking"""
    view_id: str = Field(..., description="Synthetic identifier for the view record")
    post_id: UUID = Field(..., description="ID of the post that was viewed")
    user_id: Optional[UUID] = Field(None, description="ID of user who viewed (null for anonymous)")
    viewed_at: datetime = Field(..., description="When the view occurred")
    
    class Config:
        from_attributes = True


class PostShareCreate(BaseModel):
    """Schema for creating a post share"""
    platform: Optional[str] = Field(
        "direct_link", 
        description="Platform where post was shared (twitter, facebook, direct_link, etc.)",
        max_length=50
    )


class PostShareResponse(BaseModel):
    """Response schema for post share tracking"""
    shareId: UUID = Field(..., description="Unique identifier for the share record")
    postId: UUID = Field(..., description="ID of the post that was shared")
    sharedBy: Optional[UUID] = Field(None, description="ID of user who shared")
    platform: str = Field(..., description="Platform where shared")
    sharedAt: datetime = Field(..., description="When the share occurred")
    
    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    """Standard analytics API response wrapper"""
    success: bool
    data: dict
    message: str
    errorCode: Optional[str] = None
