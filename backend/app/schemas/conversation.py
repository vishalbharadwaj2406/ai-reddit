"""
Conversation Schemas

Pydantic models for conversation-related API requests and responses.
Matches the API specification for consistent data validation.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ConversationCreate(BaseModel):
    """Conversation creation request model"""
    title: Optional[str] = Field("New Chat", description="Conversation title")
    forked_from: Optional[UUID] = Field(None, description="Post ID if forked from a post")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None:
            # Remove leading/trailing spaces
            v = v.strip()
            if not v:
                v = "New Chat"  # Default title if empty
        return v


class ConversationResponse(BaseModel):
    """Conversation response model"""
    model_config = ConfigDict(from_attributes=True)

    conversation_id: str = Field(..., description="Conversation unique identifier")
    user_id: str = Field(..., description="Creator's user ID")
    title: str = Field(..., description="Conversation title")
    forked_from: Optional[str] = Field(None, description="Post ID if forked from a post")
    status: str = Field(..., description="Conversation status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ConversationListItem(BaseModel):
    """Conversation item for lists"""
    model_config = ConfigDict(from_attributes=True)

    conversation_id: str = Field(..., description="Conversation unique identifier")
    title: str = Field(..., description="Conversation title")
    forked_from: Optional[str] = Field(None, description="Post ID if forked from a post")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: Optional[int] = Field(0, description="Number of messages in conversation")


class MessageInConversation(BaseModel):
    """Message model for inclusion in conversation responses"""
    model_config = ConfigDict(from_attributes=True)

    message_id: str = Field(..., description="Message unique identifier", alias="messageId")
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    is_blog: bool = Field(..., description="Whether message is a blog candidate", alias="isBlog")
    created_at: datetime = Field(..., description="Creation timestamp", alias="createdAt")


class ConversationWithMessagesResponse(BaseModel):
    """Conversation response model with messages included"""
    model_config = ConfigDict(from_attributes=True)

    conversation_id: str = Field(..., description="Conversation unique identifier", alias="conversationId")
    title: str = Field(..., description="Conversation title")
    created_at: datetime = Field(..., description="Creation timestamp", alias="createdAt")
    forked_from: Optional[str] = Field(None, description="Post ID if forked from a post", alias="forkedFrom")
    messages: List[MessageInConversation] = Field(..., description="Messages in the conversation")