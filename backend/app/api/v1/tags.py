"""
Tags API Endpoints

FastAPI endpoints for tag management operations.
Follows the established API pattern from other endpoints in the project.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.tag_service import TagService
from app.schemas.tag import TagCreateRequest, TagsListResponse, TagCreateResponse
from app.core.exceptions import TagAlreadyExistsError, TagNotFoundError, InvalidTagNameError


router = APIRouter()


@router.get("/tags", response_model=dict)
async def get_all_tags(
    db: Session = Depends(get_db)
):
    """
    Get all tags with post counts
    
    No authentication required - public endpoint
    
    Returns:
        Dictionary with success status and tags data
    """
    try:
        tag_service = TagService(db)
        tags_data = tag_service.get_all_tags_with_counts()
        
        return {
            "success": True,
            "data": {"tags": tags_data},
            "message": "Tags retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/tags", response_model=dict, status_code=201)
async def create_tag(
    tag_request: TagCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new tag
    
    Requires authentication
    
    Args:
        tag_request: Tag creation request data
        current_user: Authenticated user (from JWT token)
        
    Returns:
        Dictionary with success status and created tag data
        
    Raises:
        409: If tag already exists
        422: If tag name is invalid
        500: If creation fails
    """
    try:
        tag_service = TagService(db)
        tag_data = tag_service.create_tag(tag_request.name)
        
        return {
            "success": True,
            "data": {"tag": tag_data},
            "message": "Tag created successfully"
        }
    except TagAlreadyExistsError as e:
        raise HTTPException(
            status_code=409,
            detail={
                "success": False,
                "data": None,
                "message": str(e.message),
                "errorCode": "TAG_ALREADY_EXISTS"
            }
        )
    except InvalidTagNameError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "data": None,
                "message": str(e.message),
                "errorCode": "INVALID_TAG_NAME"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
