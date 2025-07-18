# AI Social Models Reference Guide for LLM Agents

## Overview
This document provides comprehensive information about all database models in the AI Social platform. Use this as a reference when implementing API endpoints, writing queries, or understanding relationships.

## Architecture Summary

### Core Entity Relationships
```
Users ←→ Conversations ←→ Messages
   ↓         ↓
Posts ←→ Comments ←→ Reactions
   ↓
Tags, Views, Shares
```

### Key Design Principles
1. **Conversation-Centric**: Posts emerge from AI conversations
2. **Fork-Based Exploration**: Posts can be "expanded" into new conversations
3. **Universal Reactions**: Same reaction system for posts and comments
4. **Soft Deletion**: Status fields instead of hard deletes
5. **Analytics Ready**: Comprehensive tracking for views, shares, engagement

## Complete Model Reference

### 1. User Model
**Purpose**: Platform user management with social features
**File**: `app/models/user.py`

**Key Fields**:
- `user_id` (UUID, PK): Immutable unique identifier
- `user_name` (VARCHAR, UNIQUE): Display name (modifiable)
- `email` (VARCHAR, UNIQUE): For authentication/notifications
- `google_id` (VARCHAR, UNIQUE): Google OAuth integration
- `is_private` (BOOLEAN): Privacy setting (default: False)
- `status` (VARCHAR): 'active', 'archived' for soft deletion

**Relationships**:
- `conversations`: One-to-many → Conversation
- `posts`: One-to-many → Post
- `comments`: One-to-many → Comment
- `post_reactions`: One-to-many → PostReaction
- `comment_reactions`: One-to-many → CommentReaction
- `followers`: Many-to-many → User (via Follow)
- `following`: Many-to-many → User (via Follow)
- `post_views`: One-to-many → PostView
- `shares_made`: One-to-many → PostShare

**Helper Methods**:
- `get_display_name()`: Returns user_name or email fallback
- `is_active()`: Checks if status == 'active'

**Usage in APIs**:
- User profiles, authentication, social features
- Privacy controls for content visibility
- Follow relationships and social graph

### 2. Conversation Model
**Purpose**: AI conversation management with forking capability
**File**: `app/models/conversation.py`

**Key Fields**:
- `conversation_id` (UUID, PK): Unique identifier
- `user_id` (UUID, FK): Creator reference → User
- `title` (VARCHAR): Conversation title
- `forked_from` (UUID, FK): Optional reference → Post (for expand feature)
- `status` (VARCHAR): 'active', 'archived'

**Relationships**:
- `user`: Many-to-one → User
- `messages`: One-to-many → Message
- `posts`: One-to-many → Post
- `forked_post`: Many-to-one → Post (via forked_from)

**Helper Methods**:
- `add_message(role, content)`: Create new message
- `get_latest_message()`: Get most recent message
- `archive()`: Soft delete conversation

**Usage in APIs**:
- WebSocket chat endpoints
- Post expansion/forking
- Conversation history retrieval

### 3. Message Model
**Purpose**: Individual messages within AI conversations
**File**: `app/models/message.py`

**Key Fields**:
- `message_id` (UUID, PK): Unique identifier
- `conversation_id` (UUID, FK): Parent conversation → Conversation
- `user_id` (UUID, FK): Author → User (nullable for AI messages)
- `role` (VARCHAR): 'user', 'assistant', 'system'
- `content` (TEXT): Message content
- `is_blog` (BOOLEAN): Flag for blog post candidates
- `status` (VARCHAR): 'active', 'archived'

**Relationships**:
- `conversation`: Many-to-one → Conversation
- `user`: Many-to-one → User (nullable)

**Helper Methods**:
- `is_from_user()`: Check if human message
- `is_from_ai()`: Check if AI response
- `mark_as_blog()`: Set is_blog flag

**Usage in APIs**:
- Chat message streaming
- Blog generation workflow
- Conversation context retrieval

### 4. Post Model
**Purpose**: Published content derived from conversations
**File**: `app/models/post.py`

**Key Fields**:
- `post_id` (UUID, PK): Unique identifier
- `user_id` (UUID, FK): Creator → User
- `conversation_id` (UUID, FK): Source conversation → Conversation
- `title` (VARCHAR): Post title
- `content` (TEXT): Post content
- `is_conversation_visible` (BOOLEAN): Privacy control for linked conversation
- `edited` (BOOLEAN): Edit tracking flag
- `status` (VARCHAR): 'active', 'archived'

**Relationships**:
- `user`: Many-to-one → User
- `conversation`: Many-to-one → Conversation
- `comments`: One-to-many → Comment
- `reactions`: One-to-many → PostReaction
- `tags`: Many-to-many → Tag (via PostTag)
- `views`: One-to-many → PostView
- `shares`: One-to-many → PostShare
- `forked_conversations`: One-to-many → Conversation (via forked_from)

**Helper Methods**:
- `get_reaction_count(reaction_type)`: Count specific reactions
- `get_share_count()`: Total share count
- `get_view_count()`: Total view count
- `is_visible_to(user)`: Privacy check

**Usage in APIs**:
- Public feed generation
- Post detail pages
- Social interaction tracking

### 5. Comment Model
**Purpose**: User comments on posts with threading support
**File**: `app/models/comment.py`

**Key Fields**:
- `comment_id` (UUID, PK): Unique identifier
- `post_id` (UUID, FK): Target post → Post
- `user_id` (UUID, FK): Comment author → User
- `parent_comment_id` (UUID, FK): For threaded replies → Comment (nullable)
- `content` (TEXT): Comment content
- `status` (VARCHAR): 'active', 'archived'

**Relationships**:
- `post`: Many-to-one → Post
- `user`: Many-to-one → User
- `parent_comment`: Many-to-one → Comment (self-referential)
- `replies`: One-to-many → Comment (via parent_comment_id)
- `reactions`: One-to-many → CommentReaction

**Helper Methods**:
- `get_reaction_count(reaction_type)`: Count specific reactions
- `is_reply()`: Check if comment is a reply
- `get_thread_depth()`: Calculate nesting level

**Usage in APIs**:
- Comment threads on posts
- Nested discussion workflows
- Social interaction features

### 6. PostReaction Model
**Purpose**: User reactions to posts (upvote, downvote, heart, etc.)
**File**: `app/models/post_reaction.py`

**Key Fields**:
- Primary Key: Composite (`user_id`, `post_id`)
- `user_id` (UUID, FK): Reactor → User
- `post_id` (UUID, FK): Target post → Post
- `reaction` (VARCHAR): 'upvote', 'downvote', 'heart', 'insightful', 'accurate'
- `status` (VARCHAR): 'active', 'archived'

**Relationships**:
- `user`: Many-to-one → User
- `post`: Many-to-one → Post

**Helper Methods**:
- `update_reaction(new_reaction)`: Change reaction type
- `remove_reaction()`: Archive reaction

**Usage in APIs**:
- Social interaction endpoints
- Reaction analytics
- Content quality signals

### 7. CommentReaction Model
**Purpose**: User reactions to comments (same system as posts)
**File**: `app/models/comment_reaction.py`

**Key Fields**:
- Primary Key: Composite (`user_id`, `comment_id`)
- `user_id` (UUID, FK): Reactor → User
- `comment_id` (UUID, FK): Target comment → Comment
- `reaction` (VARCHAR): 'upvote', 'downvote', 'heart', 'insightful', 'accurate'
- `status` (VARCHAR): 'active', 'archived'

**Relationships**:
- `user`: Many-to-one → User
- `comment`: Many-to-one → Comment

**Helper Methods**:
- `update_reaction(new_reaction)`: Change reaction type
- `remove_reaction()`: Archive reaction

**Usage in APIs**:
- Comment interaction endpoints
- Discussion quality metrics
- User engagement tracking

### 8. Follow Model
**Purpose**: User-to-user relationships with privacy controls
**File**: `app/models/follow.py`

**Key Fields**:
- Primary Key: Composite (`follower_id`, `following_id`)
- `follower_id` (UUID, FK): Following user → User
- `following_id` (UUID, FK): Followed user → User
- `status` (VARCHAR): 'pending', 'accepted', 'rejected', 'archived'

**Relationships**:
- `follower`: Many-to-one → User (via follower_id)
- `following`: Many-to-one → User (via following_id)

**Helper Methods**:
- `accept()`: Accept follow request
- `reject()`: Reject follow request
- `archive()`: Remove follow relationship
- `is_pending()`: Check if awaiting approval

**Usage in APIs**:
- Social graph management
- Privacy-controlled following
- User discovery features

### 9. Tag Model
**Purpose**: Content categorization system
**File**: `app/models/tag.py`

**Key Fields**:
- `tag_id` (UUID, PK): Unique identifier
- `name` (VARCHAR, UNIQUE): Tag name (e.g., "philosophy", "technology")
- `description` (TEXT): Optional tag description
- `status` (VARCHAR): 'active', 'archived'

**Relationships**:
- `posts`: Many-to-many → Post (via PostTag)

**Helper Methods**:
- `get_post_count()`: Count associated posts
- `is_active()`: Check if tag is active

**Usage in APIs**:
- Content discovery
- Tag-based filtering
- Content organization

### 10. PostTag Model
**Purpose**: Many-to-many relationship between posts and tags
**File**: `app/models/post_tag.py`

**Key Fields**:
- Primary Key: Composite (`post_id`, `tag_id`)
- `post_id` (UUID, FK): Tagged post → Post
- `tag_id` (UUID, FK): Applied tag → Tag

**Relationships**:
- `post`: Many-to-one → Post
- `tag`: Many-to-one → Tag

**Usage in APIs**:
- Post tagging workflow
- Tag-based content filtering
- Content categorization

### 11. PostView Model
**Purpose**: Analytics tracking for post views
**File**: `app/models/post_view.py`

**Key Fields**:
- Primary Key: Composite (`user_id`, `post_id`, `viewed_at`)
- `user_id` (UUID, FK): Viewer → User (nullable for anonymous)
- `post_id` (UUID, FK): Viewed post → Post
- `viewed_at` (TIMESTAMP): View timestamp

**Relationships**:
- `user`: Many-to-one → User (nullable)
- `post`: Many-to-one → Post

**Helper Methods**:
- `is_anonymous()`: Check if view is anonymous

**Usage in APIs**:
- Content analytics
- User engagement tracking
- Popular content identification

### 12. PostShare Model
**Purpose**: Social sharing tracking with platform attribution
**File**: `app/models/post_share.py`

**Key Fields**:
- `share_id` (UUID, PK): Unique identifier
- `user_id` (UUID, FK): Sharer → User (nullable for anonymous)
- `post_id` (UUID, FK): Shared post → Post
- `platform` (VARCHAR): 'twitter', 'linkedin', 'email', etc.
- `shared_at` (TIMESTAMP): Share timestamp

**Relationships**:
- `user`: Many-to-one → User (nullable)
- `post`: Many-to-one → Post

**Helper Methods**:
- `is_anonymous()`: Check if share is anonymous
- `get_platform_stats()`: Platform-specific analytics

**Usage in APIs**:
- Social sharing workflow
- Viral content tracking
- Platform distribution analytics

## Query Patterns and Best Practices

### Common Query Examples

#### User Authentication
```python
# Find user by Google ID
user = db.query(User).filter(User.google_id == google_id).first()

# Check if user is active
if user and user.is_active():
    # Proceed with authentication
```

#### Content Discovery
```python
# Get public feed with privacy respect
posts = db.query(Post).join(User)\
         .filter(
             and_(
                 Post.status == 'active',
                 or_(
                     User.is_private == False,
                     and_(
                         User.is_private == True,
                         exists().where(
                             and_(
                                 Follow.follower_id == current_user_id,
                                 Follow.following_id == User.user_id,
                                 Follow.status == 'accepted'
                             )
                         )
                     )
                 )
             )
         ).order_by(Post.created_at.desc())
```

#### Social Interactions
```python
# Get reaction counts for a post
reaction_counts = db.query(PostReaction.reaction, func.count())\
                   .filter(
                       and_(
                           PostReaction.post_id == post_id,
                           PostReaction.status == 'active'
                       )
                   ).group_by(PostReaction.reaction).all()

# Check if user already reacted
existing_reaction = db.query(PostReaction)\
                     .filter(
                         and_(
                             PostReaction.user_id == user_id,
                             PostReaction.post_id == post_id,
                             PostReaction.status == 'active'
                         )
                     ).first()
```

#### Conversation Management
```python
# Create new conversation with first message
conversation = Conversation(
    user_id=user_id,
    title=title,
    status='active'
)
db.add(conversation)
db.flush()  # Get the ID

# Add initial message
message = conversation.add_message('user', initial_content)
```

### Performance Optimization

#### Indexing Strategy
- Foreign keys automatically indexed
- Composite primary keys optimized for common queries
- Additional indexes on frequently filtered columns (status, created_at)
- Unique constraints for data integrity

#### Query Efficiency
- Use SQLAlchemy relationships instead of manual joins
- Leverage eager loading for related data
- Implement pagination for large result sets
- Use aggregation functions for counts and statistics

### Data Integrity Guidelines

#### Status Management
- Always check status fields in queries
- Use helper methods for status transitions
- Implement soft deletion consistently
- Maintain audit trails through timestamps

#### Relationship Constraints
- Respect foreign key constraints
- Use helper methods for relationship creation
- Implement proper error handling for constraint violations
- Validate business logic constraints in application layer

#### Privacy and Security
- Implement privacy checks before data access
- Use parameterized queries to prevent SQL injection
- Validate user permissions for all operations
- Implement proper authentication and authorization

This comprehensive reference provides all the information needed to work effectively with the AI Social database models. Use this as your primary guide for implementing API endpoints, writing queries, and understanding the system architecture.
