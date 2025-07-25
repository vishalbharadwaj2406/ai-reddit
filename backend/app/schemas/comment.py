"""
Comment API Schemas

Pydantic models for Comment API request/response validation.
Follows the established pattern from other API schemas in the project.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class CommentCreateRequest(BaseModel):
    """Request schema for creating a comment"""
    content: str = Field(..., min_length=1, max_length=10000, description="Comment content")
    parentCommentId: Optional[UUID] = Field(None, description="Parent comment ID for replies")
    
    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        """Ensure content is not just whitespace"""
        if not v.strip():
            raise ValueError('Content cannot be empty or whitespace only')
        return v.strip()


class CommentResponse(BaseModel):
    """Response schema for comment data"""
    model_config = ConfigDict(from_attributes=True)
    
    commentId: UUID = Field(..., description="Unique comment identifier")
    content: str = Field(..., description="Comment content")
    parentCommentId: Optional[UUID] = Field(None, description="Parent comment ID if this is a reply")
    createdAt: datetime = Field(..., description="When the comment was created")


class UserBasicInfo(BaseModel):
    """Basic user info for comment responses"""
    model_config = ConfigDict(from_attributes=True)
    
    userId: UUID
    userName: str
    profilePicture: Optional[str] = None


class CommentWithUserResponse(BaseModel):
    """Extended comment response with user info and reactions"""
    model_config = ConfigDict(from_attributes=True)
    
    commentId: UUID
    content: str
    createdAt: datetime
    user: UserBasicInfo
    reactions: dict = Field(default_factory=dict, description="Reaction counts")
    userReaction: Optional[str] = Field(None, description="Current user's reaction")
    parentCommentId: Optional[UUID] = None
    replies: list = Field(default_factory=list, description="Reply comments")


class CommentsListResponse(BaseModel):
    """Response schema for comments list"""
    model_config = ConfigDict(from_attributes=True)
    
    comments: list[CommentWithUserResponse]
