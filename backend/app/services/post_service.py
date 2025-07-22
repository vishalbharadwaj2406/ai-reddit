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
from app.schemas.post import PostCreate, PostCreateResponse, PostResponse, UserSummary, PostReactions
from app.core.database import get_db


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
            from datetime import datetime, timedelta
            
            time_deltas = {
                "hour": timedelta(hours=1),
                "day": timedelta(days=1), 
                "week": timedelta(weeks=1),
                "month": timedelta(days=30)
            }
            
            if time_range in time_deltas:
                cutoff_time = datetime.utcnow() - time_deltas[time_range]
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
        
        # Get view count (total views)
        view_count = db.query(func.count(PostView.user_id)).filter(
            PostView.post_id == post.post_id
        ).scalar() or 0
        
        # For now, we don't have user-specific reaction or view count
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
            userViewCount=user_view_count,
            conversationId=conversation_id
        )

    async def _get_post_by_id(self, post_id: UUID, current_user: Optional[User] = None) -> Optional[Post]:
        """
        Get a single post by ID (placeholder for future implementation).
        """
        # TODO: Implement when needed
        return None


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
