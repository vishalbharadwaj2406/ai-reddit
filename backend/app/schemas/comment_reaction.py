"""
Comment Reaction Schemas

Pydantic models for comment reaction API requests and responses.
Uses modern Pydantic V2 patterns with proper validation.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class ReactionType(str, Enum):
    """Valid reaction types for comments"""
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"
    HEART = "heart"
    INSIGHTFUL = "insightful"
    ACCURATE = "accurate"


class CommentReactionRequest(BaseModel):
    """Request model for adding/updating comment reactions"""
    
    reactionType: ReactionType = Field(
        ...,
        description="Type of reaction to add/update"
    )

    model_config = ConfigDict(str_strip_whitespace=True)


class CommentReactionResponse(BaseModel):
    """Response model for comment reaction operations"""
    
    reactionId: Optional[UUID] = Field(None, description="Reaction ID (null if removed)")
    commentId: UUID = Field(..., description="ID of the comment")
    reactionType: Optional[str] = Field(None, description="Type of reaction (null if removed)")
    createdAt: Optional[datetime] = Field(None, description="When reaction was created")
    
    model_config = ConfigDict(from_attributes=True)


class CommentReactionCountsResponse(BaseModel):
    """Response model for comment reaction counts"""
    
    commentId: UUID = Field(..., description="ID of the comment")
    reactions: dict = Field(
        default_factory=lambda: {
            "upvote": 0,
            "downvote": 0,
            "heart": 0,
            "insightful": 0,
            "accurate": 0
        },
        description="Reaction counts by type"
    )
    userReaction: Optional[str] = Field(None, description="Current user's reaction")
    
    model_config = ConfigDict(from_attributes=True)
