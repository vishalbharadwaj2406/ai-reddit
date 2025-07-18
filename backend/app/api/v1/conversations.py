"""
Conversations API Routes

This module handles conversation-related endpoints:
- Create new conversations with AI
- Get conversation history
- Continue existing conversations
- Share conversations

Conversations are the core feature where users interact with AI.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import uuid4

from app.core.database import get_db
from app.schemas.conversation import ConversationCreate, ConversationResponse, ConversationListItem
from app.models.conversation import Conversation
from app.models.message import Message
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_create: ConversationCreate = ConversationCreate()
):
    """
    Create a new conversation.

    Starts a new AI conversation session for the user.
    """
    try:
        # Create conversation with validated data
        conversation = Conversation(
            conversation_id=uuid4(),
            user_id=current_user.user_id,
            title=conversation_create.title,  # Already validated by schema
            forked_from=conversation_create.forked_from,
            status="active"
        )

        # Save conversation to database
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        # Create initial system message
        system_message = Message(
            message_id=uuid4(),
            conversation_id=conversation.conversation_id,
            user_id=None,  # System message
            role="system",
            content="Conversation started",
            is_blog=False,
            status="active"
        )

        # Save system message
        db.add(system_message)
        db.commit()

        # Convert to response format
        conversation_response = ConversationResponse(
            conversation_id=str(conversation.conversation_id),
            user_id=str(conversation.user_id),
            title=conversation.title,
            forked_from=str(conversation.forked_from) if conversation.forked_from else None,
            status=conversation.status,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )

        return {
            "success": True,
            "data": {
                "conversation": conversation_response.model_dump()
            },
            "message": "Conversation created successfully",
            "errorCode": None
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CONVERSATION_CREATE_ERROR",
                "message": "Failed to create conversation",
                "details": str(e)
            }
        )


@router.get("/")
async def get_user_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0)
):
    """Get user's conversation history."""
    try:
        # Query user's conversations
        conversations = (
            db.query(Conversation)
            .filter(
                Conversation.user_id == current_user.user_id,
                Conversation.status == "active"
            )
            .order_by(Conversation.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        # Convert to response format
        conversation_list = []
        for conv in conversations:
            conversation_item = ConversationListItem(
                conversation_id=str(conv.conversation_id),
                title=conv.title,
                forked_from=str(conv.forked_from) if conv.forked_from else None,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=0  # TODO: Add message count query if needed
            )
            conversation_list.append(conversation_item.model_dump())

        return {
            "success": True,
            "data": conversation_list,
            "message": "Conversations retrieved successfully",
            "errorCode": None
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CONVERSATION_RETRIEVAL_ERROR",
                "message": "Failed to retrieve conversations",
                "details": str(e)
            }
        )


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific conversation with messages."""
    try:
        from uuid import UUID

        # Convert string to UUID for querying
        try:
            conv_uuid = UUID(conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "INVALID_UUID",
                    "message": "Invalid conversation ID format"
                }
            )

        # Query conversation with messages
        conversation = (
            db.query(Conversation)
            .filter(Conversation.conversation_id == conv_uuid)
            .first()
        )

        # Check if conversation exists
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Conversation not found"
                }
            )

        # Check if user owns this conversation
        if conversation.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Access denied to conversation"
                }
            )

        # Convert messages to response format
        message_responses = []
        for msg in conversation.messages:
            message_responses.append({
                "messageId": str(msg.message_id),
                "role": msg.role,
                "content": msg.content,
                "isBlog": msg.is_blog,
                "createdAt": msg.created_at.isoformat()
            })

        # Create simple response data
        conversation_data = {
            "conversationId": str(conversation.conversation_id),
            "title": conversation.title,
            "createdAt": conversation.created_at.isoformat(),
            "forkedFrom": str(conversation.forked_from) if conversation.forked_from else None,
            "messages": message_responses
        }

        return {
            "success": True,
            "data": conversation_data,
            "message": "Conversation retrieved successfully",
            "errorCode": None
        }

    except HTTPException:
        # Re-raise HTTP exceptions (404, 403)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CONVERSATION_RETRIEVAL_ERROR",
                "message": "Failed to retrieve conversation",
                "details": str(e)
            }
        )


@router.delete("/{conversation_id}")
async def archive_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Archive conversation.

    Sets the conversation status to 'archived' instead of actually deleting it.
    This allows for potential recovery and maintains data integrity.
    """
    try:
        from uuid import UUID

        # Convert string to UUID for querying
        try:
            conv_uuid = UUID(conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "INVALID_UUID",
                    "message": "Invalid conversation ID format"
                }
            )

        # Query conversation
        conversation = (
            db.query(Conversation)
            .filter(Conversation.conversation_id == conv_uuid)
            .first()
        )

        # Check if conversation exists
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Conversation not found"
                }
            )

        # Check if user owns this conversation
        if conversation.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Access denied to conversation"
                }
            )

        # Check if already archived
        if conversation.status == "archived":
            return {
                "success": True,
                "data": None,
                "message": "Conversation was already archived",
                "errorCode": None
            }

        # Archive the conversation
        conversation.status = "archived"
        db.commit()

        return {
            "success": True,
            "data": None,
            "message": "Conversation archived successfully",
            "errorCode": None
        }

    except HTTPException:
        # Re-raise HTTP exceptions (404, 403, 422)
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CONVERSATION_ARCHIVE_ERROR",
                "message": "Failed to archive conversation",
                "details": str(e)
            }
        )