"""
Tag API Schemas

Pydantic models for Tag API request/response validation.
Follows the established pattern from other API schemas in the project.
"""

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict


class TagCreateRequest(BaseModel):
    """Request schema for creating a tag"""
    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and normalize tag name"""
        if not v.strip():
            raise ValueError('Tag name cannot be empty or whitespace only')
        
        # Basic validation - no special characters except hyphens
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-]+$', v.strip()):
            raise ValueError('Tag name can only contain letters, numbers, spaces, and hyphens')
        
        return v.strip()


class TagResponse(BaseModel):
    """Response schema for tag data"""
    model_config = ConfigDict(from_attributes=True)
    
    tagId: UUID = Field(..., description="Unique tag identifier")
    name: str = Field(..., description="Tag name")
    postCount: int = Field(0, description="Number of posts with this tag")


class TagsListResponse(BaseModel):
    """Response schema for tags list"""
    
    tags: list[TagResponse]


class TagCreateResponse(BaseModel):
    """Response schema for tag creation"""
    
    tag: TagResponse
