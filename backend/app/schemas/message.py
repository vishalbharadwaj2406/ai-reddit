"""
Message Schemas

Pydantic models for message-related API requests and responses.
Matches the API specification for consistent data validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class MessageResponse(BaseModel):
    """Message response model for API responses"""
    model_config = ConfigDict(from_attributes=True)

    message_id: str = Field(..., description="Message unique identifier", alias="messageId")
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    is_blog: bool = Field(..., description="Whether message is a blog candidate", alias="isBlog")
    created_at: datetime = Field(..., description="Creation timestamp", alias="createdAt")


class MessageCreate(BaseModel):
    """Message creation request model"""
    content: str = Field(..., min_length=1, description="Message content")