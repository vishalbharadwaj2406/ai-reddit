"""
Post API Schemas

Pydantic models for post-related API requests and responses.
Handles validation for post creation, updates, and responses.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Literal
from uuid import UUID
from datetime import datetime


class PostQueryParams(BaseModel):
    """Query parameters for filtering and sorting posts"""
    limit: int = Field(default=20, ge=1, le=100, description="Number of posts to return")
    offset: int = Field(default=0, ge=0, description="Number of posts to skip")
    sort: Literal["hot", "new", "top"] = Field(default="hot", description="Sort order for posts")
    time_range: Literal["hour", "day", "week", "month", "all"] = Field(default="all", description="Time range for 'top' sort")
    tag: Optional[str] = Field(None, description="Filter by tag name")
    userId: Optional[UUID] = Field(None, description="Filter by user ID")


class PostCreate(BaseModel):
    """Schema for creating a new post (either from conversation message or standalone)"""
    
    messageId: Optional[UUID] = Field(None, description="ID of the message to create post from (optional for standalone posts)")
    title: str = Field(..., min_length=1, max_length=200, description="Post title")
    content: str = Field(..., min_length=1, description="Post content (can be edited from original message)")
    tags: List[str] = Field(default=[], description="Tags for the post (auto-created if they don't exist)")
    isConversationVisible: bool = Field(default=True, description="Whether the source conversation is publicly viewable (ignored for standalone posts)")
    
    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v is None:
            return []
        # Remove duplicates and empty strings
        clean_tags = [tag.strip().lower() for tag in v if tag and tag.strip()]
        return list(dict.fromkeys(clean_tags))  # Remove duplicates while preserving order
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Understanding Machine Learning",
                    "description": "Message-based post example",
                    "value": {
                        "messageId": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Understanding Machine Learning",
                        "content": "Machine learning is a fascinating field that allows computers to learn from data...",
                        "tags": ["ai", "machine-learning", "technology"],
                        "isConversationVisible": True
                    }
                },
                {
                    "title": "Standalone Post",
                    "description": "Direct post creation example",
                    "value": {
                        "title": "My Thoughts on AI Development",
                        "content": "Today I want to share my thoughts on the current state of AI development...",
                        "tags": ["ai", "thoughts", "development"],
                        "isConversationVisible": False
                    }
                }
            ]
        }
    )


class UserSummary(BaseModel):
    """User summary for post responses"""
    userId: UUID = Field(..., description="User ID")
    userName: str = Field(..., description="Username")
    profilePicture: Optional[str] = Field(None, description="Profile picture URL")


class PostReactions(BaseModel):
    """Post reaction counts"""
    upvote: int = Field(default=0, description="Number of upvotes")
    downvote: int = Field(default=0, description="Number of downvotes")
    heart: int = Field(default=0, description="Number of heart reactions")
    insightful: int = Field(default=0, description="Number of insightful reactions")
    accurate: int = Field(default=0, description="Number of accurate reactions")


class PostResponse(BaseModel):
    """Schema for post data in API responses"""
    
    postId: UUID = Field(..., description="Unique identifier for the post")
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content")
    createdAt: datetime = Field(..., description="Post creation timestamp")
    user: UserSummary = Field(..., description="Post author information")
    tags: List[str] = Field(default=[], description="Post tags")
    reactions: PostReactions = Field(default_factory=PostReactions, description="Reaction counts")
    userReaction: Optional[str] = Field(None, description="Current user's reaction to this post")
    commentCount: int = Field(default=0, description="Number of comments")
    viewCount: int = Field(default=0, description="Total view count")
    shareCount: int = Field(default=0, description="Total share count")
    userViewCount: int = Field(default=0, description="Current user's view count")
    conversationId: Optional[UUID] = Field(None, description="Source conversation ID if viewable")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "postId": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Understanding Machine Learning",
                "content": "Machine learning is a fascinating field...",
                "createdAt": "2025-07-20T12:00:00Z",
                "user": {
                    "userId": "123e4567-e89b-12d3-a456-426614174002",
                    "userName": "johndoe",
                    "profilePicture": "https://example.com/profile.jpg"
                },
                "tags": ["ai", "machine-learning", "technology"],
                "reactions": {
                    "upvote": 15,
                    "downvote": 2,
                    "heart": 8,
                    "insightful": 12,
                    "accurate": 5
                },
                "userReaction": "upvote",
                "commentCount": 3,
                "viewCount": 147,
                "shareCount": 23,
                "userViewCount": 2,
                "conversationId": "123e4567-e89b-12d3-a456-426614174003"
            }
        }
    )


class PostCreateResponse(BaseModel):
    """Schema for successful post creation response"""
    
    postId: UUID = Field(..., description="ID of the newly created post")
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content")
    createdAt: datetime = Field(..., description="Post creation timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "postId": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Understanding Machine Learning",
                "content": "Machine learning is a fascinating field...",
                "createdAt": "2025-07-20T12:00:00Z"
            }
        }
    )


class PostListResponse(BaseModel):
    """Schema for paginated list of posts"""
    
    posts: List[PostResponse] = Field(..., description="List of posts")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "posts": [
                    {
                        "postId": "123e4567-e89b-12d3-a456-426614174001",
                        "title": "Understanding Machine Learning",
                        "content": "Machine learning is a fascinating field...",
                        "createdAt": "2025-07-20T12:00:00Z",
                        "user": {
                            "userId": "123e4567-e89b-12d3-a456-426614174002",
                            "userName": "johndoe",
                            "profilePicture": "https://example.com/profile.jpg"
                        },
                        "tags": ["ai", "machine-learning"],
                        "reactions": {
                            "upvote": 15,
                            "downvote": 2,
                            "heart": 8,
                            "insightful": 12,
                            "accurate": 5
                        },
                        "userReaction": "upvote",
                        "commentCount": 3,
                        "viewCount": 147,
                        "shareCount": 23,
                        "userViewCount": 2,
                        "conversationId": "123e4567-e89b-12d3-a456-426614174003"
                    }
                ]
            }
        }
    )


class PostUpdate(BaseModel):
    """Schema for updating an existing post"""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated post title")
    content: Optional[str] = Field(None, min_length=1, description="Updated post content")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    isConversationVisible: Optional[bool] = Field(None, description="Updated conversation visibility")
    
    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v
    
    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Content cannot be empty')
        return v.strip() if v else v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v is None:
            return v
        # Remove duplicates and empty strings
        clean_tags = [tag.strip().lower() for tag in v if tag and tag.strip()]
        return list(dict.fromkeys(clean_tags))  # Remove duplicates while preserving order


class PostReactionCreate(BaseModel):
    """Schema for creating a reaction to a post"""
    
    reactionType: str = Field(..., pattern="^(upvote|downvote|heart|insightful|accurate)$", 
                             description="Type of reaction")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reactionType": "upvote"
            }
        }
    )


class PostExpandRequest(BaseModel):
    """Schema for expanding a post into a new conversation"""
    
    title: Optional[str] = Field(None, max_length=200, description="Title for the new conversation")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Exploring this idea further"
            }
        }
    )


class CommentResponse(BaseModel):
    """Schema for comment data in API responses"""
    
    comment_id: UUID = Field(..., description="Comment unique identifier")
    content: str = Field(..., description="Comment content")
    created_at: datetime = Field(..., description="Comment creation timestamp")
    user: UserSummary = Field(..., description="Comment author information")
    reactions: PostReactions = Field(default_factory=PostReactions, description="Comment reaction counts")
    vote_count: int = Field(default=0, description="Net vote count (upvotes - downvotes)")
    parent_comment_id: Optional[UUID] = Field(None, description="Parent comment ID for nested replies")
    replies: List['CommentResponse'] = Field(default=[], description="Nested replies to this comment")
    
    model_config = ConfigDict(from_attributes=True)


class ConversationSummary(BaseModel):
    """Schema for conversation summary in post responses"""
    
    conversation_id: UUID = Field(..., description="Conversation unique identifier")
    title: str = Field(..., description="Conversation title")
    created_at: datetime = Field(..., description="Conversation creation timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class TagResponse(BaseModel):
    """Schema for tag data in API responses"""
    
    tag_id: UUID = Field(..., description="Tag unique identifier")
    name: str = Field(..., description="Tag name")
    
    model_config = ConfigDict(from_attributes=True)


class PostDetailResponse(BaseModel):
    """Schema for detailed post data with comments and full relationships"""
    
    post_id: UUID = Field(..., description="Post unique identifier")
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content")
    status: str = Field(..., description="Post status")
    is_conversation_visible: bool = Field(..., description="Whether source conversation is visible")
    created_at: datetime = Field(..., description="Post creation timestamp")
    updated_at: datetime = Field(..., description="Post last update timestamp")
    
    # User information
    user: UserSummary = Field(..., description="Post author information")
    
    # Tags
    tags: List[TagResponse] = Field(default=[], description="Post tags with full info")
    
    # Reactions and votes
    reactions: PostReactions = Field(default_factory=PostReactions, description="Reaction counts")
    vote_count: int = Field(default=0, description="Net vote count (upvotes - downvotes)")
    
    # Analytics
    viewCount: int = Field(default=0, description="Total view count")
    shareCount: int = Field(default=0, description="Total share count")
    userViewCount: int = Field(default=0, description="Current user's view count")
    
    # Comments
    comments: List[CommentResponse] = Field(default=[], description="Post comments with nested replies")
    
    # Conversation link (if visible)
    conversation_id: Optional[UUID] = Field(None, description="Source conversation ID")
    conversation: Optional[ConversationSummary] = Field(None, description="Source conversation summary")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "post_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Understanding Machine Learning",
                "content": "Machine learning is a fascinating field that combines statistics, computer science, and domain expertise...",
                "status": "published",
                "is_conversation_visible": True,
                "created_at": "2025-07-20T12:00:00Z",
                "updated_at": "2025-07-20T12:00:00Z",
                "user": {
                    "userId": "123e4567-e89b-12d3-a456-426614174002",
                    "userName": "johndoe",
                    "profilePicture": "https://example.com/profile.jpg"
                },
                "tags": [
                    {"tag_id": "123e4567-e89b-12d3-a456-426614174010", "name": "machine-learning"},
                    {"tag_id": "123e4567-e89b-12d3-a456-426614174011", "name": "ai"}
                ],
                "reactions": {
                    "upvote": 15,
                    "downvote": 2,
                    "heart": 8,
                    "insightful": 12,
                    "accurate": 5
                },
                "vote_count": 13,
                "viewCount": 147,
                "shareCount": 23,
                "userViewCount": 2,
                "comments": [
                    {
                        "comment_id": "123e4567-e89b-12d3-a456-426614174020",
                        "content": "Great explanation! Could you elaborate on neural networks?",
                        "created_at": "2025-07-20T12:30:00Z",
                        "user": {
                            "userId": "123e4567-e89b-12d3-a456-426614174003",
                            "userName": "alice",
                            "profilePicture": "https://example.com/alice.jpg"
                        },
                        "reactions": {"upvote": 3, "downvote": 0, "heart": 1, "insightful": 2, "accurate": 1},
                        "vote_count": 3,
                        "parent_comment_id": None,
                        "replies": []
                    }
                ],
                "conversation_id": "123e4567-e89b-12d3-a456-426614174003",
                "conversation": {
                    "conversation_id": "123e4567-e89b-12d3-a456-426614174003",
                    "title": "ML Discussion",
                    "created_at": "2025-07-20T11:30:00Z"
                }
            }
        }
    )


class PostDetailAPIResponse(BaseModel):
    """Complete API response for GET /posts/{post_id}"""
    
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Post retrieved successfully", description="Human-readable message")
    errorCode: Optional[str] = Field(None, description="Error code if applicable")
    data: dict = Field(..., description="Response data")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Post retrieved successfully",
                "errorCode": None,
                "data": {
                    "post": {
                        # PostDetailResponse example would go here
                    }
                }
            }
        }
    )


# Fix forward reference for CommentResponse
CommentResponse.model_rebuild()


# Fork Related Schemas

class PostForkRequest(BaseModel):
    """Schema for forking a post into a new conversation"""
    
    includeOriginalConversation: Optional[bool] = Field(
        None, 
        description="Whether to include the original conversation context. Defaults to True if original conversation is public, False otherwise."
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "includeOriginalConversation": True
            }
        }
    )


class PostForkResponse(BaseModel):
    """Schema for post fork response"""
    
    conversationId: UUID = Field(..., description="ID of the newly created forked conversation")
    title: str = Field(..., description="Title of the forked conversation")
    forkedFrom: UUID = Field(..., description="ID of the original post that was forked")
    includeOriginalConversation: bool = Field(..., description="Whether original conversation context was included")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conversationId": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Re: Original Post Title",
                "forkedFrom": "123e4567-e89b-12d3-a456-426614174000",
                "includeOriginalConversation": True
            }
        }
    )


class PostForkAPIResponse(BaseModel):
    """API wrapper for post fork response"""
    
    success: bool = Field(True, description="Whether the operation was successful")
    data: PostForkResponse = Field(..., description="Fork response data")
    message: str = Field(..., description="Human readable success message")
    errorCode: Optional[str] = Field(None, description="Error code if any")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": {
                    "conversationId": "550e8400-e29b-41d4-a716-446655440000",
                    "title": "Re: Original Post Title", 
                    "forkedFrom": "123e4567-e89b-12d3-a456-426614174000",
                    "includeOriginalConversation": True
                },
                "message": "Conversation forked successfully",
                "errorCode": None
            }
        }
    )
