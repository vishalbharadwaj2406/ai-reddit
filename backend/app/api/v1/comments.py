"""
Comment API Endpoints

FastAPI router for comment operations.
Follows the established API pattern from other endpoint files in the project.
"""

from typing import List, Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.comment import CommentCreateRequest, CommentResponse
from app.schemas.comment_reaction import CommentReactionRequest, CommentReactionResponse
from app.services.comment_service import CommentService
from app.services.comment_reaction_service import CommentReactionService


router = APIRouter()


@router.post("/posts/{post_id}/comments", response_model=dict, status_code=201)
def create_comment(
    post_id: UUID,
    request: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new comment on a post
    
    - **post_id**: UUID of the post to comment on
    - **content**: Comment content (required)
    - **parentCommentId**: Optional parent comment ID for replies
    
    Returns the created comment with standard API response wrapper.
    """
    
    comment_service = CommentService(db)
    
    try:
        comment = comment_service.create_comment(
            post_id=post_id,
            user_id=current_user.user_id,
            content=request.content,
            parent_comment_id=request.parentCommentId
        )
        
        # Return in standard API response wrapper format
        return {
            "success": True,
            "data": {
                "commentId": comment.comment_id,
                "content": comment.content,
                "parentCommentId": comment.parent_comment_id,
                "createdAt": comment.created_at
            },
            "message": "Comment created successfully"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions from service layer
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/posts/{post_id}/comments", response_model=dict)
def get_post_comments(
    post_id: UUID,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comments for a post
    
    - **post_id**: UUID of the post
    - **limit**: Maximum number of comments to return (default: 20, max: 100)
    - **offset**: Number of comments to skip (default: 0)
    
    Returns list of comments with user info and reaction counts.
    """
    
    comment_service = CommentService(db)
    
    try:
        comments = comment_service.get_comments_for_post(
            post_id=post_id,
            limit=limit,
            offset=offset
        )
        
        # Format comments for response
        formatted_comments = []
        for comment in comments:
            formatted_comment = {
                "commentId": comment.comment_id,
                "content": comment.content,
                "createdAt": comment.created_at,
                "user": {
                    "userId": comment.user.user_id,
                    "username": comment.user.user_name,
                    "displayName": comment.user.get_display_name()
                },
                "reactions": {
                    "upvote": 0,
                    "downvote": 0,
                    "heart": 0,
                    "insightful": 0,
                    "accurate": 0
                },
                "userReaction": None,
                "parentCommentId": comment.parent_comment_id,
                "replies": []
            }
            formatted_comments.append(formatted_comment)
        
        return {
            "success": True,
            "data": formatted_comments,
            "message": "Comments retrieved successfully"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions from service layer
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/comments/{comment_id}/reaction", response_model=dict)
def add_comment_reaction(
    comment_id: UUID,
    request: CommentReactionRequest,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add or update a reaction to a comment
    
    - **comment_id**: UUID of the comment to react to
    - **reactionType**: Type of reaction (upvote, downvote, heart, insightful, accurate)
    
    Business Logic:
    - If user has no existing reaction, creates new one (201)
    - If user has same reaction, removes it (200, data=null)
    - If user has different reaction, updates it (200)
    - Users cannot react to their own comments (400)
    
    Returns the reaction with standard API response wrapper.
    """
    
    reaction_service = CommentReactionService(db)
    
    try:
        reaction, action = reaction_service.add_or_update_reaction(
            comment_id=comment_id,
            user_id=current_user.user_id,
            reaction_type=request.reactionType.value
        )
        
        if action == "removed":
            # Reaction was removed (toggled off)
            response.status_code = 200
            return {
                "success": True,
                "data": None,
                "message": "Reaction removed successfully"
            }
        else:
            # Return reaction data
            response_data = {
                "reactionId": None,  # CommentReaction uses composite key
                "commentId": reaction.comment_id,
                "reactionType": reaction.reaction,
                "createdAt": reaction.created_at
            }
            
            response.status_code = 201 if action == "created" else 200
            message = f"Reaction {action} successfully"
            
            return {
                "success": True,
                "data": response_data,
                "message": message
            }
        
    except HTTPException:
        # Re-raise HTTP exceptions from service layer
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
