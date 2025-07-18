"""
User Schemas

Pydantic models for user-related API requests and responses.
Matches the API specification exactly for consistent data validation.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UserResponse(BaseModel):
    """User profile response model - matches API specification"""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str = Field(..., description="User's unique identifier")
    user_name: str = Field(..., description="User's display name")
    email: str = Field(..., description="User's email address")
    profile_picture: Optional[str] = Field(None, description="Profile picture URL")
    created_at: datetime = Field(..., description="Account creation timestamp")
    follower_count: int = Field(0, description="Number of followers")
    following_count: int = Field(0, description="Number of users following")
    is_private: bool = Field(False, description="Whether account is private")


class UserUpdate(BaseModel):
    """User profile update request model"""
    user_name: Optional[str] = Field(None, min_length=1, max_length=50, description="New display name")
    profile_picture: Optional[str] = Field(None, description="New profile picture URL")
    is_private: Optional[bool] = Field(None, description="Privacy setting")
    
    @field_validator('user_name')
    @classmethod
    def validate_username(cls, v):
        if v is not None:
            # Remove leading/trailing spaces
            v = v.strip()
            if not v:
                raise ValueError('Username cannot be empty')
            # Basic username validation
            if not v.replace(' ', '').replace('_', '').replace('-', '').isalnum():
                raise ValueError('Username can only contain letters, numbers, spaces, hyphens, and underscores')
        return v


class UserListItem(BaseModel):
    """User item for lists (followers, following, etc.)"""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str = Field(..., description="User's unique identifier")
    user_name: str = Field(..., description="User's display name")
    profile_picture: Optional[str] = Field(None, description="Profile picture URL")
    followed_at: Optional[datetime] = Field(None, description="When follow relationship was created")


class UserListResponse(BaseModel):
    """Response model for paginated user lists"""
    users: List[UserListItem] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    
    
class FollowersResponse(BaseModel):
    """Response model for followers list - matches API spec"""
    page_number: int = Field(..., description="Current page number")
    size: int = Field(..., description="Items per page")
    followers: List[UserListItem] = Field(..., description="List of followers")


class FollowingResponse(BaseModel):
    """Response model for following list - matches API spec"""
    following: List[UserListItem] = Field(..., description="List of users being followed")


class FollowRequestResponse(BaseModel):
    """Response model for follow requests"""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str = Field(..., description="User's unique identifier")
    user_name: str = Field(..., description="User's display name")
    profile_picture: Optional[str] = Field(None, description="Profile picture URL")
    requested_at: datetime = Field(..., description="When follow request was created")


class IncomingFollowRequestsResponse(BaseModel):
    """Response model for incoming follow requests"""
    incoming_requests: List[FollowRequestResponse] = Field(..., description="List of incoming follow requests")


class OutgoingFollowRequestsResponse(BaseModel):
    """Response model for outgoing follow requests"""
    outgoing_requests: List[FollowRequestResponse] = Field(..., description="List of outgoing follow requests")


class FollowResponse(BaseModel):
    """Response model for follow actions"""
    status: str = Field(..., description="Follow status: 'pending' or 'accepted'")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in ['pending', 'accepted']:
            raise ValueError('Status must be either "pending" or "accepted"')
        return v


class CommentResponse(BaseModel):
    """Response model for comments"""
    model_config = ConfigDict(from_attributes=True)
    
    comment_id: str = Field(..., description="Comment's unique identifier")
    content: str = Field(..., description="Comment content")
    created_at: datetime = Field(..., description="Comment creation timestamp")
    user: UserListItem = Field(..., description="Comment author")
    reactions: dict = Field(..., description="Reaction counts")
    user_reaction: Optional[str] = Field(None, description="Current user's reaction")
    parent_comment_id: Optional[str] = Field(None, description="Parent comment ID if this is a reply")
    replies: List['CommentResponse'] = Field([], description="Nested replies")


class CommentRequest(BaseModel):
    """Request model for creating comments"""
    content: str = Field(..., min_length=1, max_length=1000, description="Comment content")
    parent_comment_id: Optional[str] = Field(None, description="Parent comment ID for replies")


class ReactionRequest(BaseModel):
    """Request model for adding/updating reactions"""
    reaction: Optional[str] = Field(None, description="Reaction type or null to remove")
    
    @field_validator('reaction')
    @classmethod
    def validate_reaction(cls, v):
        if v is not None and v not in ['upvote', 'downvote', 'heart', 'insightful', 'accurate']:
            raise ValueError('Reaction must be one of: upvote, downvote, heart, insightful, accurate')
        return v


class ReactionResponse(BaseModel):
    """Response model for reaction updates"""
    reaction: Optional[str] = Field(None, description="Current user's reaction")
    reaction_counts: dict = Field(..., description="Updated reaction counts")


class TagResponse(BaseModel):
    """Response model for tags"""
    model_config = ConfigDict(from_attributes=True)
    
    tag_id: str = Field(..., description="Tag's unique identifier")
    name: str = Field(..., description="Tag name")
    post_count: int = Field(0, description="Number of posts with this tag")


class TagsResponse(BaseModel):
    """Response model for tag lists"""
    tags: List[TagResponse] = Field(..., description="List of tags")


# Update forward reference for recursive model
CommentResponse.model_rebuild()
