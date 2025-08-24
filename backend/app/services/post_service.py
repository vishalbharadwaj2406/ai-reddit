"""
Post Service Layer

Business logic for post management including:
- Creating posts from conversation messages
- Validating post data and permissions
- Managing post tags (auto-creation)
- Handling post visibility settings
- Post CRUD operations
- Post ranking and feed generation

This service layer sits between the API endpoints and the database,
encapsulating all business rules and logic.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, case, and_, or_, desc, asc, text, extract

from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.post import Post
from app.models.tag import Tag
from app.models.post_tag import PostTag
from app.models.post_reaction import PostReaction
from app.models.comment import Comment
from app.models.post_view import PostView
from app.models.post_fork import PostFork
from app.schemas.post import (
    PostCreate, PostCreateResponse, PostResponse, UserSummary, PostReactions,
    PostForkRequest, PostForkResponse
)
from app.core.database import get_db
from app.prompts.fork_prompts import fork_prompts


logger = logging.getLogger(__name__)


class PostServiceError(Exception):
    """Custom exception for post service errors"""
    pass


class PostService:
    """Service class for post-related business logic"""

    def __init__(self, db: Session):
        self.db = db

    async def create_post_from_message(self, current_user: User, post_data: PostCreate) -> PostCreateResponse:
        """
        Create a new post from conversation message or as standalone post
        
        Args:
            current_user: The authenticated user creating the post
            post_data: Post creation data with optional message ID and content
            
        Returns:
            PostCreateResponse: Created post details
            
        Raises:
            PostServiceError: If post creation fails
        """
        
        try:
            conversation_id = None
            
            # 1. If messageId provided, validate and retrieve the message
            if post_data.messageId:
                message = await self._validate_message_access(current_user, post_data.messageId)
                
                # Check if conversation is active (not archived)
                if message.conversation.status == "archived":
                    raise PostServiceError("Cannot create posts from archived conversations")
                    
                conversation_id = message.conversation_id
            
            # 2. Create the post (with or without conversation linkage)
            post = Post(
                post_id=uuid4(),
                user_id=current_user.user_id,
                conversation_id=conversation_id,  # None for standalone posts
                title=post_data.title,
                content=post_data.content,
                is_conversation_visible=post_data.isConversationVisible if post_data.messageId else False,
                status="active"
            )
            
            self.db.add(post)
            self.db.flush()  # Get the post ID for tag relationships
            
            # 4. Handle tags (auto-create if needed)
            if post_data.tags:
                await self._handle_post_tags(post, post_data.tags)
            
            # 5. Commit the transaction
            self.db.commit()
            self.db.refresh(post)
            
            # 6. Return response
            return PostCreateResponse(
                postId=post.post_id,
                title=post.title,
                content=post.content,
                createdAt=post.created_at
            )
            
        except PostServiceError:
            # Re-raise our custom errors
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            # Handle database errors
            self.db.rollback()
            raise PostServiceError(f"Database error during post creation: {str(e)}")
        except Exception as e:
            # Handle unexpected errors
            self.db.rollback()
            raise PostServiceError(f"Unexpected error during post creation: {str(e)}")

    async def _validate_message_access(self, user: User, message_id: UUID) -> Message:
        """
        Validate that a user has access to a specific message
        
        Args:
            user: User requesting access
            message_id: ID of the message to validate
            
        Returns:
            Message: The validated message object
            
        Raises:
            PostServiceError: If message not found or access denied
        """
        
        # Join Message with Conversation to get user access in single query
        message = (
            self.db.query(Message)
            .join(Conversation)
            .filter(Message.message_id == message_id)
            .filter(Conversation.user_id == user.user_id)  # Only user's own conversations
            .first()
        )
        
        if not message:
            # Check if message exists but belongs to different user
            exists = self.db.query(Message).filter(Message.message_id == message_id).first()
            if exists:
                raise PostServiceError("Access denied: You can only create posts from your own messages", "FORBIDDEN")
            else:
                raise PostServiceError("Message not found", "MESSAGE_NOT_FOUND")
                
        return message

    async def _handle_post_tags(self, post: Post, tag_names: List[str]) -> None:
        """
        Handle post tags, creating new tags if they don't exist.
        
        Args:
            post: The post to associate tags with
            tag_names: List of tag names to associate
        """
        
        if not tag_names:
            return
        
        # Get existing tags
        existing_tags = (
            self.db.query(Tag)
            .filter(Tag.name.in_(tag_names))
            .all()
        )
        
        existing_tag_names = {tag.name for tag in existing_tags}
        
        # Create new tags for ones that don't exist
        new_tags = []
        for tag_name in tag_names:
            if tag_name not in existing_tag_names:
                new_tag = Tag(
                    tag_id=uuid4(),
                    name=tag_name
                )
                new_tags.append(new_tag)
                self.db.add(new_tag)
        
        # Flush to get IDs for new tags
        if new_tags:
            self.db.flush()
        
        # Create post-tag associations
        all_tags = existing_tags + new_tags
        for tag in all_tags:
            post_tag = PostTag(
                post_id=post.post_id,
                tag_id=tag.tag_id
            )
            self.db.add(post_tag)

    async def get_post_by_id(self, post_id: UUID, current_user: Optional[User] = None) -> Optional[Post]:
        """
        Retrieve a post by its ID.
        
        Args:
            post_id: ID of the post to retrieve
            current_user: Optional current user for permission checks
            
        Returns:
            Post or None if not found or access denied
        """
        
        query = self.db.query(Post).filter(Post.post_id == post_id)
        
        # Add visibility filters if user is not the owner
        post = query.first()
        if not post:
            return None
        
        # If user is not the owner, check visibility
        if current_user and post.user_id != current_user.user_id:
            # For now, all posts are visible (we can add privacy logic later)
            pass
        
        return post

    async def get_post_detail_by_id(self, post_id: UUID, current_user: Optional[User] = None) -> Optional[dict]:
        """
        Retrieve detailed post information including comments, reactions, tags, and user info.
        
        Args:
            post_id: ID of the post to retrieve
            current_user: Optional current user for permission checks
            
        Returns:
            Detailed post dict or None if not found
        """
        from app.models.comment import Comment
        from app.models.post_reaction import PostReaction
        from app.models.comment_reaction import CommentReaction
        from app.models.post_tag import PostTag
        from app.models.tag import Tag
        from app.models.conversation import Conversation
        from sqlalchemy.orm import joinedload
        from sqlalchemy import func, case
        
        # Get the post with all necessary relationships loaded
        post = self.db.query(Post).options(
            joinedload(Post.user),
            joinedload(Post.conversation)
        ).filter(Post.post_id == post_id).first()
        
        if not post:
            return None
        
        # Check visibility permissions
        if current_user and post.user_id != current_user.user_id:
            # For now, all posts are visible (add privacy logic later if needed)
            pass
        
        # Get post reactions with counts
        reaction_counts = self.db.query(
            PostReaction.reaction,
            func.count(PostReaction.user_id).label('count')
        ).filter(
            PostReaction.post_id == post_id
        ).group_by(PostReaction.reaction).all()
        
        # Create reactions dict
        reactions = {
            'upvote': 0,
            'downvote': 0,
            'heart': 0,
            'insightful': 0,
            'accurate': 0
        }
        
        for reaction, count in reaction_counts:
            if reaction in reactions:
                reactions[reaction] = count
        
        # Calculate vote count
        vote_count = reactions['upvote'] - reactions['downvote']
        
        # Get post tags
        post_tags = self.db.query(Tag).join(
            PostTag, Tag.tag_id == PostTag.tag_id
        ).filter(PostTag.post_id == post_id).all()
        
        tags = [{'tag_id': tag.tag_id, 'name': tag.name} for tag in post_tags]
        
        # Get comments with nested structure
        # First get all comments for this post
        comments_query = self.db.query(Comment).options(
            joinedload(Comment.user)
        ).filter(Comment.post_id == post_id).order_by(Comment.created_at)
        
        all_comments = comments_query.all()
        
        # Get comment reactions
        comment_reactions = {}
        if all_comments:
            comment_ids = [c.comment_id for c in all_comments]
            reactions_data = self.db.query(
                CommentReaction.comment_id,
                CommentReaction.reaction,
                func.count(CommentReaction.user_id).label('count')
            ).filter(
                CommentReaction.comment_id.in_(comment_ids)
            ).group_by(CommentReaction.comment_id, CommentReaction.reaction).all()
            
            for comment_id, reaction, count in reactions_data:
                if comment_id not in comment_reactions:
                    comment_reactions[comment_id] = {
                        'upvote': 0, 'downvote': 0, 'heart': 0, 
                        'insightful': 0, 'accurate': 0
                    }
                comment_reactions[comment_id][reaction] = count
        
        # Build comment tree structure
        comment_dict = {}
        root_comments = []
        
        for comment in all_comments:
            comment_reactions_data = comment_reactions.get(comment.comment_id, {
                'upvote': 0, 'downvote': 0, 'heart': 0, 'insightful': 0, 'accurate': 0
            })
            
            comment_data = {
                'comment_id': comment.comment_id,
                'content': comment.content,
                'created_at': comment.created_at,
                'user': {
                    'user_id': comment.user.user_id,
                    'user_name': comment.user.user_name,
                    'profile_picture': comment.user.profile_picture
                },
                'reactions': comment_reactions_data,
                'vote_count': comment_reactions_data['upvote'] - comment_reactions_data['downvote'],
                'parent_comment_id': comment.parent_comment_id,
                'replies': []
            }
            
            comment_dict[comment.comment_id] = comment_data
            
            if comment.parent_comment_id is None:
                root_comments.append(comment_data)
            else:
                # Add to parent's replies
                if comment.parent_comment_id in comment_dict:
                    comment_dict[comment.parent_comment_id]['replies'].append(comment_data)
        
        # Build conversation info if visible
        conversation_data = None
        if post.conversation_id and post.is_conversation_visible and post.conversation:
            conversation_data = {
                'conversation_id': post.conversation.conversation_id,
                'title': post.conversation.title,
                'created_at': post.conversation.created_at
            }
        
        # Build the detailed response
        result = {
            'post_id': post.post_id,
            'title': post.title,
            'content': post.content,
            'status': post.status,
            'is_conversation_visible': post.is_conversation_visible,
            'created_at': post.created_at,
            'updated_at': post.updated_at,
            'user': {
                'user_id': post.user.user_id,
                'user_name': post.user.user_name,
                'profile_picture': post.user.profile_picture
            },
            'tags': tags,
            'reactions': reactions,
            'vote_count': vote_count,
            'viewCount': self._get_post_view_count(post_id),
            'shareCount': self._get_post_share_count(post_id),
            'userViewCount': self._get_user_view_count(post_id, current_user.user_id if current_user else None),
            'comments': root_comments,
            'conversation_id': post.conversation_id,
            'conversation': conversation_data
        }
        
        return result

    async def get_posts_feed(
        self,
        db: Session,
        sort: str = "hot",
        time_range: str = "all",
        tag: Optional[str] = None,
        user_id: Optional[UUID] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[PostResponse]:
        """
        Get posts feed with ranking, filtering, and pagination.
        
        This is a clean implementation focusing on actual functionality.
        """
        # Build the base query with necessary joins
        query = db.query(Post).join(User, Post.user_id == User.user_id)
        
        # Apply filters
        if user_id:
            query = query.filter(Post.user_id == user_id)
            
        if tag:
            query = query.join(PostTag, Post.post_id == PostTag.post_id)\
                        .join(Tag, PostTag.tag_id == Tag.tag_id)\
                        .filter(Tag.name == tag)
        
        # Apply time range filter for "top" sorting
        if sort == "top" and time_range != "all":
            from datetime import datetime, timedelta, timezone
            
            time_deltas = {
                "hour": timedelta(hours=1),
                "day": timedelta(days=1), 
                "week": timedelta(weeks=1),
                "month": timedelta(days=30)
            }
            
            if time_range in time_deltas:
                cutoff_time = datetime.now(timezone.utc) - time_deltas[time_range]
                query = query.filter(Post.created_at >= cutoff_time)
        
        # Apply sorting
        if sort == "new":
            query = query.order_by(Post.created_at.desc())
        elif sort == "hot":
            # Hot algorithm: (upvotes - downvotes) / (age_in_hours + 2)^1.8
            # We'll calculate the hot score using SQL
            
            # Calculate age in hours
            age_in_hours = extract('epoch', func.now() - Post.created_at) / 3600.0
            
            # Calculate net votes (upvotes - downvotes)
            upvotes = func.count(case((PostReaction.reaction == 'upvote', PostReaction.user_id)))
            downvotes = func.count(case((PostReaction.reaction == 'downvote', PostReaction.user_id)))
            net_votes = upvotes - downvotes
            
            # Calculate hot score: net_votes / (age_in_hours + 2)^1.8
            hot_score = net_votes / func.power(age_in_hours + 2, 1.8)
            
            # Join with reactions for the calculation
            query = query.outerjoin(PostReaction, Post.post_id == PostReaction.post_id)\
                        .group_by(Post.post_id, User.user_id)\
                        .order_by(hot_score.desc())
        elif sort == "top":
            # Top sorting: order by net upvotes (upvotes - downvotes)
            upvotes = func.count(case((PostReaction.reaction == 'upvote', PostReaction.user_id)))
            downvotes = func.count(case((PostReaction.reaction == 'downvote', PostReaction.user_id)))
            net_votes = upvotes - downvotes
            
            query = query.outerjoin(PostReaction, Post.post_id == PostReaction.post_id)\
                        .group_by(Post.post_id, User.user_id)\
                        .order_by(net_votes.desc())
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        posts = query.all()
        
        # Convert to response format
        result = []
        for post in posts:
            post_response = await self._create_post_response(post, db)
            result.append(post_response)
            
        return result
    
    async def _create_post_response(self, post: Post, db: Session) -> PostResponse:
        """
        Create a PostResponse from a Post model.
        """
        # Get user information
        user = db.query(User).filter(User.user_id == post.user_id).first()
        
        user_summary = UserSummary(
            userId=post.user_id,
            userName=user.user_name if user else "Unknown User",
            profilePicture=user.profile_picture if user else None
        )
        
        # Get post tags
        tags = (db.query(Tag.name)
                .join(PostTag, Tag.tag_id == PostTag.tag_id)
                .filter(PostTag.post_id == post.post_id)
                .all())
        tag_names = [tag.name for tag in tags]
        
        # Get reaction counts
        reactions = db.query(
            PostReaction.reaction,
            func.count(PostReaction.user_id).label('count')
        ).filter(
            PostReaction.post_id == post.post_id
        ).group_by(PostReaction.reaction).all()
        
        # Build reactions object
        reaction_counts = {
            'upvote': 0,
            'downvote': 0, 
            'heart': 0,
            'insightful': 0,
            'accurate': 0
        }
        
        for reaction_type, count in reactions:
            if reaction_type in reaction_counts:
                reaction_counts[reaction_type] = count
        
        post_reactions = PostReactions(**reaction_counts)
        
        # Get comment count
        comment_count = db.query(func.count(Comment.comment_id)).filter(
            Comment.post_id == post.post_id
        ).scalar() or 0
        
        # Get analytics counts
        view_count = self._get_post_view_count(post.post_id)
        share_count = self._get_post_share_count(post.post_id)
        
        # For now, we don't have user-specific reaction or view count in list view
        # These would require a current_user parameter
        user_reaction = None
        user_view_count = 0
        
        # Determine if conversation should be visible
        conversation_id = None
        if hasattr(post, 'conversation') and post.conversation:
            # Add logic here for conversation visibility rules
            # For now, show conversation ID if it exists
            conversation_id = post.conversation_id
        
        return PostResponse(
            postId=post.post_id,
            title=post.title,
            content=post.content,
            createdAt=post.created_at,
            user=user_summary,
            tags=tag_names,
            reactions=post_reactions,
            userReaction=user_reaction,
            commentCount=comment_count,
            viewCount=view_count,
            shareCount=share_count,
            userViewCount=user_view_count,
            conversationId=conversation_id
        )

    async def _get_post_by_id(self, post_id: UUID, current_user: Optional[User] = None) -> Optional[Post]:
        """
        Get a single post by ID (placeholder for future implementation).
        """
        # TODO: Implement when needed
        return None

    def fork_post(self, post_id: UUID, user_id: UUID, request: PostForkRequest) -> PostForkResponse:
        """
        Fork a post by creating a new conversation with proper context integration.
        
        This implements the complete fork vision:
        - Creates new conversation with post context
        - Optionally includes full original conversation context
        - Sets up proper AI prompts for context-aware responses
        - Tracks fork relationship and analytics
        
        Args:
            post_id: UUID of the post to fork
            user_id: UUID of the user creating the fork
            request: Fork request containing context preferences
            
        Returns:
            PostForkResponse with conversation details
            
        Raises:
            PostServiceError: If post doesn't exist or fork creation fails
        """
        try:
            # Get the post to fork with full context
            post = self.db.query(Post).options(
                joinedload(Post.conversation)
            ).filter(
                Post.post_id == post_id,
                Post.status == "active"
            ).first()
            
            if not post:
                raise PostServiceError(f"Post with id {post_id} not found", "POST_NOT_FOUND")
            
            # Determine if we should include original conversation based on:
            # 1. User's explicit choice in the request
            # 2. Whether original conversation exists and is public
            include_original = False
            
            if request and request.includeOriginalConversation is not None:
                # User made an explicit choice
                include_original = request.includeOriginalConversation
            elif post.conversation_id and post.is_conversation_visible:
                # Default to True only if conversation exists and is public
                include_original = True
            # Otherwise defaults to False
            
            # Get original conversation context if requested, available, and public
            original_conversation_context = None
            if include_original and post.conversation_id and post.is_conversation_visible:
                original_conversation_context = self._get_conversation_context(post.conversation_id)
            
            # Create new conversation with post-aware title
            conversation = Conversation(
                conversation_id=uuid4(),
                user_id=user_id,
                title=f"Fork of: {post.title[:50]}{'...' if len(post.title) > 50 else ''}",
                forked_from=post_id,  # Set the forked_from relationship
                status="active"
            )
            
            self.db.add(conversation)
            self.db.flush()  # Get the conversation ID
            
            # Create proper context message using fork prompts
            context_prompt = fork_prompts.get_fork_context_prompt(
                post_title=post.title,
                post_content=post.content,
                original_conversation=original_conversation_context,
                include_original_conversation=include_original
            )
            
            # Create system message with fork context
            system_message = Message(
                message_id=uuid4(),
                conversation_id=conversation.conversation_id,
                user_id=None,  # System message
                role="system",
                content=context_prompt
            )
            
            self.db.add(system_message)
            
            # Create welcome message for the user
            welcome_message = fork_prompts.get_fork_welcome_message(
                post_title=post.title,
                include_original_conversation=include_original
            )
            
            # Create AI welcome message
            ai_welcome = Message(
                message_id=uuid4(),
                conversation_id=conversation.conversation_id,
                user_id=None,  # AI message
                role="assistant",
                content=welcome_message
            )
            
            self.db.add(ai_welcome)
            
            # Create fork record with proper context tracking
            fork = PostFork(
                user_id=user_id,
                post_id=post_id,
                conversation_id=conversation.conversation_id,
                original_conversation_included="true" if include_original else "false"
            )
            
            self.db.add(fork)
            
            # Update post fork count analytics
            post.fork_count = (post.fork_count or 0) + 1
            
            self.db.commit()
            
            return PostForkResponse(
                conversationId=conversation.conversation_id,
                title=conversation.title,
                forkedFrom=post_id,
                includeOriginalConversation=include_original
            )
            
        except PostServiceError:
            # Re-raise our custom errors
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            # Handle duplicate fork attempts
            if "duplicate key value violates unique constraint" in str(e) and "post_forks_pkey" in str(e):
                logger.info(f"User {user_id} attempted to fork post {post_id} multiple times - allowing duplicate fork")
                # For MVP: Allow multiple forks by same user to same post
                # This creates a new conversation each time
                # Alternative: Could return existing fork or prevent duplicates
                # But for now, we'll allow it by adding microsecond precision to avoid collision
                import time
                time.sleep(0.001)  # Small delay to ensure different timestamp
                # Retry the fork operation once
                try:
                    return self.fork_post(post_id, user_id, request)
                except Exception:
                    raise PostServiceError("Unable to create fork due to timing constraints. Please try again.")
            else:
                logger.error(f"Database error during post fork: {str(e)}")
                raise PostServiceError(f"Database error during post fork: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error during post fork: {str(e)}")
            raise PostServiceError(f"Unexpected error during post fork: {str(e)}")
    
    def _get_conversation_context(self, conversation_id: UUID) -> str:
        """
        Retrieve the full conversation context for fork integration.
        
        Args:
            conversation_id: ID of the conversation to retrieve
            
        Returns:
            Formatted conversation context string
        """
        try:
            # Get all messages in the conversation, ordered by creation time
            messages = self.db.query(Message).filter(
                Message.conversation_id == conversation_id,
                Message.role.in_(["user", "assistant"])  # Exclude system messages
            ).order_by(Message.created_at).all()
            
            if not messages:
                return ""
            
            # Format conversation as readable context
            context_lines = []
            for message in messages:
                role_label = "User" if message.role == "user" else "Assistant"
                context_lines.append(f"{role_label}: {message.content}")
            
            return "\n\n".join(context_lines)
            
        except Exception as e:
            logger.warning(f"Failed to retrieve conversation context for {conversation_id}: {str(e)}")
            return ""

    def _get_post_view_count(self, post_id: UUID) -> int:
        """Get total view count for a post."""
        return self.db.query(func.count(PostView.view_id)).filter(
            PostView.post_id == post_id
        ).scalar() or 0

    def _get_post_share_count(self, post_id: UUID) -> int:
        """Get total share count for a post."""
        from app.models.post_share import PostShare
        return self.db.query(func.count(PostShare.share_id)).filter(
            PostShare.post_id == post_id
        ).scalar() or 0

    def _get_user_view_count(self, post_id: UUID, user_id: Optional[UUID]) -> int:
        """Get view count for a specific user and post."""
        if not user_id:
            return 0
        return self.db.query(func.count(PostView.view_id)).filter(
            PostView.post_id == post_id,
            PostView.user_id == user_id
        ).scalar() or 0

    def get_post_conversation(self, post_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get the conversation for a specific post if it's publicly viewable.
        
        Args:
            post_id: UUID of the post to get conversation for
            
        Returns:
            Dict containing conversation data or None if not viewable/found
            
        Raises:
            PostServiceError: If post not found or conversation not viewable
        """
        try:
            # Get the post with conversation relationship
            post = (
                self.db.query(Post)
                .options(joinedload(Post.conversation))
                .filter(Post.post_id == post_id, Post.status == "active")
                .first()
            )
            
            if not post:
                raise PostServiceError("Post not found")
            
            # Check if conversation is visible
            if not post.is_conversation_visible:
                raise PostServiceError("Conversation not viewable")
            
            # Get the conversation with messages
            conversation = post.conversation
            if not conversation:
                raise PostServiceError("No conversation linked to this post")
            
            # Get all messages in the conversation
            messages = (
                self.db.query(Message)
                .filter(
                    Message.conversation_id == conversation.conversation_id,
                    Message.status == "active"
                )
                .order_by(Message.created_at)
                .all()
            )
            
            # Build conversation response
            message_data = []
            for message in messages:
                message_data.append({
                    "messageId": str(message.message_id),
                    "role": message.role,
                    "content": message.content,
                    "isBlog": message.is_blog,
                    "createdAt": message.created_at.isoformat()
                })
            
            conversation_data = {
                "conversationId": str(conversation.conversation_id),
                "title": conversation.title,
                "createdAt": conversation.created_at.isoformat(),
                "forkedFrom": str(conversation.forked_from) if conversation.forked_from else None,
                "messages": message_data
            }
            
            return conversation_data
            
        except PostServiceError:
            # Re-raise business logic errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting conversation for post {post_id}: {str(e)}")
            raise PostServiceError(f"Failed to retrieve conversation: {str(e)}")


def get_post_service(db: Session = None) -> PostService:
    """
    Factory function to get a PostService instance.
    
    Args:
        db: Optional database session (for dependency injection)
        
    Returns:
        PostService instance
    """
    if db is None:
        db = next(get_db())
    
    return PostService(db)
