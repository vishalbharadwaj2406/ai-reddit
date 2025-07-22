"""
Posts API Routes

This module handles post-related endpoints:
- Create posts from conversations
- Get public posts feed
- Get specific posts
- Fork existing posts
- React to posts (like/dislike)

Posts are created from AI conversations and shared publicly.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.core.database import get_db
from app.schemas.post import PostCreate, PostCreateResponse, PostListResponse
from app.services.post_service import PostService, PostServiceError
from app.dependencies.auth import get_current_user, get_current_user_optional
from app.models.user import User

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a post from a conversation message.

    Converts a conversation message into a public post with user-edited content.
    
    **Business Flow:**
    1. User has a conversation with AI
    2. User selects a message to turn into a post
    3. User edits the content in UI text box
    4. User clicks "Post" button which calls this API
    5. Post is created and can be shared publicly
    
    **Validation:**
    - Message must exist and belong to user
    - Conversation must not be archived
    - Title and content cannot be empty
    - Tags are auto-created if they don't exist
    """
    try:
        # Initialize post service
        post_service = PostService(db)
        
        # Create the post
        created_post = await post_service.create_post_from_message(
            current_user=current_user,
            post_data=post_data
        )
        
        # Return success response with standard wrapper
        return {
            "success": True,
            "data": created_post.model_dump(),
            "message": "Post created successfully",
            "errorCode": None
        }
        
    except PostServiceError as e:
        # Handle business logic errors
        error_message = str(e)
        
        if "Message not found" in error_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "message": "Message not found",
                    "errorCode": "MESSAGE_NOT_FOUND"
                }
            )
        elif "Access denied" in error_message:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "success": False,
                    "data": None,
                    "message": "Access denied to message",
                    "errorCode": "FORBIDDEN"
                }
            )
        elif "archived conversation" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "data": None,
                    "message": "Cannot create posts from archived conversations",
                    "errorCode": "CONVERSATION_ARCHIVED"
                }
            )
        else:
            # Generic service error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "success": False,
                    "data": None,
                    "message": f"Failed to create post: {error_message}",
                    "errorCode": "POST_CREATION_ERROR"
                }
            )
    
    except ValueError as e:
        # Handle validation errors (from Pydantic)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "success": False,
                "data": None,
                "message": f"Validation error: {str(e)}",
                "errorCode": "VALIDATION_ERROR"
            }
        )
        
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "message": f"Failed to create post: {str(e)}",
                "errorCode": "POST_CREATION_ERROR"
            }
        )


@router.get("/")
async def get_posts_feed(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100, description="Number of posts to return"),
    offset: int = Query(default=0, ge=0, description="Number of posts to skip"),
    sort: str = Query(default="hot", pattern="^(hot|new|top)$", description="Sort order"),
    time_range: str = Query(default="all", pattern="^(hour|day|week|month|all)$", description="Time range for top sort"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    userId: Optional[UUID] = Query(None, description="Filter by user ID"),
    current_user: Optional[User] = Depends(get_current_user_optional)  # Optional auth for public feed
):
    """
    Get public posts feed with ranking, filtering, and pagination.
    
    **Features:**
    - **Hot Ranking**: Time-decay algorithm favoring recent posts with good engagement
    - **New Sorting**: Posts sorted by creation date (newest first)
    - **Top Sorting**: Posts sorted by total upvotes within time range
    - **Tag Filtering**: Filter posts by specific tags
    - **User Filtering**: Filter posts by specific user
    - **Pagination**: Limit and offset for efficient loading
    
    **Hot Algorithm:**
    Uses the formula: (upvotes - downvotes) / (age_in_hours + 2)^1.8
    This gives higher scores to posts that are both recent and well-received.
    
    **Public Access:**
    This endpoint doesn't require authentication, but authenticated users
    get additional information like their own reactions and view counts.
    """
    try:
        # Initialize post service
        post_service = PostService(db)
        
        # Get posts with ranking and filtering
        posts = await post_service.get_posts_feed(
            db=db,
            limit=limit,
            offset=offset,
            sort=sort,
            time_range=time_range,
            tag=tag,
            user_id=userId
        )
        
        # Return success response with standard wrapper
        return {
            "success": True,
            "data": {
                "posts": [post.model_dump() for post in posts]
            },
            "message": "Posts retrieved successfully",
            "errorCode": None
        }
        
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "success": False,
                "data": None,
                "message": f"Validation error: {str(e)}",
                "errorCode": "VALIDATION_ERROR"
            }
        )
        
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "message": f"Failed to retrieve posts: {str(e)}",
                "errorCode": "POST_RETRIEVAL_ERROR"
            }
        )


@router.get("/{post_id}")
async def get_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get specific post with full details including comments, reactions, and tags.
    
    **Business Flow:**
    1. Validates post_id as valid UUID
    2. Retrieves post with all related data (comments, reactions, tags, user info)
    3. Builds nested comment structure with replies
    4. Calculates reaction counts and vote scores
    5. Includes conversation link if visible
    
    **Response includes:**
    - Post content and metadata
    - Author information
    - All tags associated with post
    - Reaction counts (upvote, downvote, heart, insightful, accurate)
    - Complete comment tree with nested replies
    - Source conversation link (if visible)
    
    **Permissions:**
    - Public endpoint - no authentication required
    - All published posts are visible to everyone
    - Private posts may be added later with user permissions
    """
    from app.services.post_service import get_post_service
    from app.schemas.post import PostDetailAPIResponse
    from uuid import UUID
    
    # Validate UUID format
    try:
        post_uuid = UUID(post_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "success": False,
                "data": None,
                "message": "Invalid post ID format. Must be a valid UUID.",
                "errorCode": "INVALID_POST_ID"
            }
        )
    
    try:
        post_service = get_post_service(db)
        
        # Get detailed post data
        post_data = await post_service.get_post_detail_by_id(post_uuid, current_user)
        
        if not post_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "message": "Post not found or access denied.",
                    "errorCode": "POST_NOT_FOUND"
                }
            )
        
        # Return structured response
        return {
            "success": True,
            "data": {
                "post": post_data
            },
            "message": "Post retrieved successfully",
            "errorCode": None
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except PostServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "data": None,
                "message": f"Failed to retrieve post: {str(e)}",
                "errorCode": "POST_SERVICE_ERROR"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "message": f"Failed to get post: {str(e)}",
                "errorCode": "INTERNAL_SERVER_ERROR"
            }
        )


@router.post("/{post_id}/fork")
async def fork_post(
    post_id: str,
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_user)
):
    """Fork an existing post to continue the conversation."""
    try:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Fork post not yet implemented"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fork post: {str(e)}"
        )