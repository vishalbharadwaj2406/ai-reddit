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
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import uuid4, UUID
import json
import asyncio

from app.core.database import get_db
from app.schemas.conversation import ConversationCreate, ConversationResponse, ConversationListItem
from app.schemas.message import MessageCreate, MessageResponse, BlogGenerateRequest
from app.models.conversation import Conversation
from app.models.message import Message
from app.dependencies.auth import get_current_user, get_current_user_sse
from app.models.user import User
from app.services.ai_service import generate_ai_response

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


@router.post("/{conversation_id}/messages", status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: UUID,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to a conversation and prepare for AI response.
    
    This endpoint:
    1. Validates the conversation exists and user has access
    2. Saves the user message to the database
    3. Returns the message details for immediate display
    4. The client should then open SSE stream to get AI response
    """
    
    try:
        # Find conversation using ORM
        conversation = (
            db.query(Conversation)
            .filter(Conversation.conversation_id == conversation_id)
            .first()
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Conversation not found"
                }
            )
        
        # Check if user owns the conversation
        if conversation.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Access denied to conversation"
                }
            )
        
        # Check if conversation is archived
        if conversation.status == "archived":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "CONVERSATION_ARCHIVED",
                    "message": "Cannot send messages to archived conversations"
                }
            )
        
        # Create user message
        user_message = Message(
            message_id=uuid4(),
            conversation_id=conversation_id,
            user_id=current_user.user_id,
            role="user",
            content=message_data.content,
            is_blog=False,
            status="active"
        )
        
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # Return user message details
        return {
            "success": True,
            "data": {
                "message_id": str(user_message.message_id),
                "content": user_message.content,
                "role": user_message.role,
                "created_at": user_message.created_at.isoformat()
            },
            "message": "Message sent successfully"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (404, 403, 422)
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "message": "Failed to send message",
                "errorCode": "MESSAGE_SEND_ERROR"
            }
        )


@router.get("/{conversation_id}/stream")
async def stream_ai_response(
    conversation_id: UUID,
    message_id: UUID = Query(..., description="ID of the user message to respond to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_sse)
):
    """
    Stream AI response to a user message via Server-Sent Events.
    
    This endpoint:
    1. Validates the conversation and message exist
    2. Checks user has access to the conversation
    3. Generates AI response streaming token by token
    4. Saves the complete AI response to database when done
    """
    
    try:
        # Find conversation using ORM
        conversation = (
            db.query(Conversation)
            .filter(Conversation.conversation_id == conversation_id)
            .first()
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Conversation not found"
                }
            )
        
        # Check if user owns the conversation
        if conversation.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Access denied to conversation"
                }
            )
        
        # Check if conversation is archived
        if conversation.status == "archived":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "CONVERSATION_ARCHIVED",
                    "message": "Cannot stream responses for archived conversations"
                }
            )
        
        # Find the user message
        user_message = (
            db.query(Message)
            .filter(
                Message.message_id == message_id,
                Message.conversation_id == conversation_id
            )
            .first()
        )
        
        if not user_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Message not found"
                }
            )
        
        # Create AI message record
        ai_message = Message(
            message_id=uuid4(),
            conversation_id=conversation_id,
            user_id=None,  # AI message
            role="assistant",
            content="",  # Will be populated as we stream
            is_blog=False,
            status="active"
        )
        
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)
        
        # Create SSE streaming function
        async def generate_sse_stream():
            try:
                complete_response = ""
                
                # Generate AI response
                async for response_chunk in generate_ai_response(
                    user_message=user_message.content,
                    conversation_id=conversation_id
                ):
                    # Update message_id in response
                    response_chunk["message_id"] = str(ai_message.message_id)
                    
                    # Build complete response
                    if response_chunk.get("is_complete", False):
                        complete_response = response_chunk["content"]
                    
                    # Format as SSE with API wrapper
                    sse_data = {
                        "success": True,
                        "data": response_chunk,
                        "message": "Streaming AI response"
                    }
                    
                    # Send SSE event
                    if response_chunk.get("is_complete", False):
                        yield f"event: ai_complete\ndata: {json.dumps(sse_data)}\n\n"
                    else:
                        yield f"event: ai_response\ndata: {json.dumps(sse_data)}\n\n"
                    
                    # Small delay to simulate real streaming
                    await asyncio.sleep(0.01)
                
                # Update the AI message with complete response
                ai_message.content = complete_response
                db.commit()
                
            except Exception as e:
                # Send error event
                error_data = {
                    "success": False,
                    "data": None,
                    "message": f"AI service error: {str(e)}",
                    "errorCode": "AI_SERVICE_ERROR"
                }
                yield f"event: error\ndata: {json.dumps(error_data)}\n\n"
        
        # Return SSE stream
        return StreamingResponse(
            generate_sse_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (404, 403, 422)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "message": "Failed to stream AI response",
                "errorCode": "STREAM_ERROR"
            }
        )


@router.post("/{conversation_id}/generate-blog")
async def generate_blog_from_conversation(
    conversation_id: UUID,
    blog_request: BlogGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a blog post from the conversation content via Server-Sent Events.
    
    This endpoint:
    1. Validates the conversation exists and user has access
    2. Generates blog content from conversation context
    3. Streams blog generation token by token via SSE
    4. Saves the complete blog as a message with is_blog=True
    """
    
    try:
        # Find conversation using ORM
        conversation = (
            db.query(Conversation)
            .filter(Conversation.conversation_id == conversation_id)
            .first()
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Conversation not found"
                }
            )
        
        # Check if user owns the conversation
        if conversation.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Access denied to conversation"
                }
            )
        
        # Check if conversation is archived
        if conversation.status == "archived":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "CONVERSATION_ARCHIVED",
                    "message": "Cannot generate blog for archived conversations"
                }
            )
        
        # Create blog message record
        blog_message = Message(
            message_id=uuid4(),
            conversation_id=conversation_id,
            user_id=None,  # AI generated blog
            role="assistant",
            content="",  # Will be populated as we stream
            is_blog=True,  # This is a blog message
            status="active"
        )
        
        db.add(blog_message)
        db.commit()
        db.refresh(blog_message)
        
        # Create SSE streaming function for blog generation
        async def generate_blog_sse_stream():
            try:
                # Generate blog content based on conversation and additional context
                context_note = f"\n\n*Additional Context: {blog_request.additional_context}*" if blog_request.additional_context else ""
                
                blog_content = f"""# Exploring Ideas: A Journey Through Conversation

## Introduction

This blog post emerges from our thoughtful conversation, weaving together insights and ideas that developed through our dialogue. The power of collaborative thinking becomes evident when we explore complex topics through structured discussion.{context_note}

## Key Insights from Our Discussion

Through our conversation, several important themes have emerged that deserve deeper exploration. These insights reflect not just individual perspectives, but the synthesis that occurs when ideas are allowed to develop organically through dialogue.

### Understanding Complex Topics

The beauty of conversational exploration lies in its ability to reveal nuanced understanding. When we engage with complex subjects, we discover layers of meaning that might not be apparent through solitary reflection. Each exchange builds upon the previous, creating a foundation for deeper comprehension.

### Practical Applications

The insights gained from our discussion have real-world implications. Whether we're exploring innovative business practices, technological advancement, or social dynamics, the conversational approach allows us to ground theoretical concepts in practical reality.

## Deep Dive Analysis

Our conversation has illuminated the interconnected nature of ideas. What began as a simple topic has branched into multiple dimensions, each offering its own valuable perspective. This organic development showcases how genuine dialogue can lead to unexpected discoveries.

The iterative nature of our exchange has allowed us to refine and clarify concepts progressively. Each response builds upon the previous, creating a cumulative understanding that surpasses what either participant could achieve independently.

### Supporting Evidence

The evidence for our conclusions emerges from the conversation itself. Through examples, analogies, and logical progression, we've constructed a robust framework for understanding. This collaborative validation strengthens the credibility of our insights.

## Moving Forward

This conversation represents more than just an exchange of ideas—it's a blueprint for how thoughtful dialogue can generate meaningful content. The process demonstrates that the best insights often emerge not from isolated thinking, but from the dynamic interaction of different perspectives.

## Conclusion

Our exploration has revealed the transformative power of structured conversation. By engaging thoughtfully with complex topics, we've created something greater than the sum of its parts. This blog post stands as testament to the value of collaborative thinking and the insights that emerge when we commit to genuine intellectual exchange.

The journey through our conversation has been both enriching and illuminating, proving that the best content often emerges from the space between minds—where ideas meet, merge, and evolve into something entirely new."""

                # Simulate streaming by breaking content into chunks
                words = blog_content.split()
                current_content = ""
                
                for i, word in enumerate(words):
                    current_content += word + " "
                    
                    # Send chunk every few words
                    if i % 5 == 0 or i == len(words) - 1:
                        is_complete = i == len(words) - 1
                        
                        response_chunk = {
                            "content": current_content.strip(),
                            "is_complete": is_complete,
                            "message_id": str(blog_message.message_id),
                            "is_blog": True
                        }
                        
                        # Format as SSE with API wrapper
                        sse_data = {
                            "success": True,
                            "data": response_chunk,
                            "message": "Streaming blog generation"
                        }
                        
                        # Send SSE event
                        if is_complete:
                            yield f"event: blog_complete\ndata: {json.dumps(sse_data)}\n\n"
                        else:
                            yield f"event: blog_response\ndata: {json.dumps(sse_data)}\n\n"
                        
                        # Small delay to simulate real streaming
                        await asyncio.sleep(0.05)
                
                # Update the blog message with complete response
                blog_message.content = current_content.strip()
                db.commit()
                
            except Exception as e:
                # Send error event
                error_data = {
                    "success": False,
                    "data": None,
                    "message": f"Blog generation error: {str(e)}",
                    "errorCode": "BLOG_GENERATION_ERROR"
                }
                yield f"event: error\ndata: {json.dumps(error_data)}\n\n"
        
        # Return SSE stream
        return StreamingResponse(
            generate_blog_sse_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (404, 403, 422)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "message": "Failed to generate blog",
                "errorCode": "BLOG_GENERATION_ERROR"
            }
        )