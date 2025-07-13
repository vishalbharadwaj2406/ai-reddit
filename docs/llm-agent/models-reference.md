# AI Reddit Models Reference Guide for LLM Agents

## 📋 Overview
This document provides comprehensive information about all database models in the AI Reddit platform. Use this as a reference when implementing API endpoints, writing queries, or understanding relationships.

---

## 🏗️ Architecture Summary

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

---

## 📊 Complete Model Reference

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
- `post_id` (UUID, FK): Parent post → Post
- `user_id` (UUID, FK): Author → User
- `parent_comment_id` (UUID, FK): For threaded replies → Comment
- `content` (TEXT): Comment content
- `status` (VARCHAR): 'active', 'archived'

**Relationships**:
- `post`: Many-to-one → Post
- `user`: Many-to-one → User
- `parent_comment`: Many-to-one → Comment (self-referential)
- `replies`: One-to-many → Comment (self-referential)
- `reactions`: One-to-many → CommentReaction

**Helper Methods**:
- `get_reply_count()`: Count direct replies
- `get_thread_depth()`: Calculate nesting level
- `is_top_level()`: Check if direct post comment

**Usage in APIs**:
- Comment threads
- Reply management
- Content moderation

### 6. PostReaction Model
**Purpose**: User reactions to posts (upvote, downvote, etc.)
**File**: `app/models/post_reaction.py`

**Key Fields**:
- `user_id` (UUID, FK): Reactor → User
- `post_id` (UUID, FK): Target post → Post  
- `reaction` (VARCHAR): 'upvote', 'downvote', 'heart', 'insightful', 'accurate'
- `status` (VARCHAR): 'active', 'archived'
- **Composite Primary Key**: (user_id, post_id)

**Relationships**:
- `user`: Many-to-one → User
- `post`: Many-to-one → Post

**Helper Methods**:
- `get_valid_reactions()`: List allowed reaction types
- `update_reaction(new_reaction)`: Change user's reaction
- `remove_reaction()`: Archive reaction

**Usage in APIs**:
- Reaction buttons
- Content ranking
- User engagement tracking

### 7. CommentReaction Model
**Purpose**: User reactions to comments (same system as posts)
**File**: `app/models/comment_reaction.py`

**Key Fields**: Same as PostReaction but for comments
**Relationships**: Similar pattern to PostReaction
**Usage**: Comment interaction tracking

### 8. Follow Model
**Purpose**: User follow relationships with privacy support
**File**: `app/models/follow.py`

**Key Fields**:
- `follower_id` (UUID, FK): Following user → User
- `following_id` (UUID, FK): Followed user → User
- `status` (VARCHAR): 'pending', 'accepted', 'rejected', 'archived'
- **Composite Primary Key**: (follower_id, following_id)
- **Constraint**: follower_id != following_id

**Relationships**:
- `follower`: Many-to-one → User
- `following`: Many-to-one → User

**Helper Methods**:
- `accept()`: Approve follow request
- `reject()`: Decline follow request
- `archive()`: Remove follow relationship
- `is_pending()`, `is_accepted()`: Status checks

**Usage in APIs**:
- Social graph management
- Follow request workflow
- Privacy controls

### 9. Tag Model
**Purpose**: Content categorization and discovery
**File**: `app/models/tag.py`

**Key Fields**:
- `tag_id` (UUID, PK): Unique identifier
- `name` (VARCHAR, UNIQUE): Tag text (normalized)

**Relationships**:
- `posts`: Many-to-many → Post (via PostTag)

**Helper Methods**:
- `normalize_name(name)`: Clean tag text
- `get_hashtag()`: Return #hashtag format
- `get_display_name()`: Formatted display

**Usage in APIs**:
- Content tagging
- Discovery features
- Trending topics

### 10. PostTag Model
**Purpose**: Many-to-many relationship between posts and tags
**File**: `app/models/post_tag.py`

**Key Fields**:
- `post_id` (UUID, FK): → Post
- `tag_id` (UUID, FK): → Tag
- **Composite Primary Key**: (post_id, tag_id)

**Usage**: Tag filtering, content categorization

### 11. PostView Model
**Purpose**: Analytics tracking for post views
**File**: `app/models/post_view.py`

**Key Fields**:
- `user_id` (UUID, FK): Viewer → User
- `post_id` (UUID, FK): Viewed post → Post
- `viewed_at` (TIMESTAMP): View timestamp
- `status` (VARCHAR): 'active', 'archived'
- **Composite Primary Key**: (user_id, post_id, viewed_at)

**Helper Methods**:
- `create_view(user_id, post_id)`: Record view
- `get_age()`: Time since view
- `archive()`: Soft delete view

**Usage in APIs**:
- Analytics endpoints
- View count tracking
- User engagement metrics

### 12. PostShare Model
**Purpose**: Social sharing tracking with platform analytics
**File**: `app/models/post_share.py`

**Key Fields**:
- `user_id` (UUID, FK): Sharer → User (nullable for anonymous)
- `post_id` (UUID, FK): Shared post → Post
- `shared_at` (TIMESTAMP): Share timestamp
- `platform` (VARCHAR): 'twitter', 'facebook', 'direct_link', etc.
- `share_metadata` (JSON): Additional platform-specific data
- `status` (VARCHAR): 'active', 'archived'
- **Composite Primary Key**: (post_id, user_id OR anonymous identifier)

**Relationships**:
- `user`: Many-to-one → User (nullable)
- `post`: Many-to-one → Post

**Helper Methods**:
- `create_share(post_id, user_id, platform)`: Record share
- `archive()`: Soft delete share
- `is_anonymous()`: Check if anonymous share

**Usage in APIs**:
- Share tracking
- Viral content analytics
- Platform-specific metrics

---

## 🔧 Common Query Patterns

### User Feed Generation
```python
# Get posts from followed users
posts = db.query(Post).join(User).join(Follow, Follow.following_id == User.user_id)
       .filter(Follow.follower_id == current_user_id, Follow.status == 'accepted')
       .order_by(Post.created_at.desc())
```

### Reaction Aggregation
```python
# Get reaction counts for a post
reactions = db.query(PostReaction.reaction, func.count())
           .filter(PostReaction.post_id == post_id, PostReaction.status == 'active')
           .group_by(PostReaction.reaction)
```

### Privacy-Aware Content
```python
# Respect user privacy settings
visible_posts = db.query(Post).join(User)
               .filter(or_(
                   User.is_private == False,
                   and_(User.is_private == True, Follow.follower_id == current_user_id)
               ))
```

### Conversation Forking
```python
# Create forked conversation from post
forked_conversation = Conversation(
    user_id=current_user_id,
    title=f"Expanding: {original_post.title}",
    forked_from=original_post.post_id
)
```

---

## 🚨 Important Constraints & Business Rules

### 1. Data Integrity
- All foreign keys have proper constraints
- No CASCADE deletes (handled at application level)
- Soft deletion via status fields

### 2. Privacy Logic
- `User.is_private == True` → Only followers see content
- `Post.is_conversation_visible == False` → Hide source conversation
- Anonymous sharing supported via nullable user_id

### 3. Unique Constraints
- One reaction per user per post/comment
- One follow relationship per user pair
- Unique tag names (normalized)
- Unique usernames and emails

### 4. Status Management
- 'active': Normal operation
- 'archived': Soft deleted
- 'pending': Awaiting approval (follows)
- 'accepted'/'rejected': Follow request states

---

## 🎯 API Implementation Guidelines

### 1. Always Check Status
```python
# Filter active records
.filter(Model.status == 'active')
```

### 2. Respect Privacy
```python
# Check user privacy before showing content
if user.is_private and not is_following(current_user, user):
    return forbidden_response()
```

### 3. Use Helper Methods
```python
# Leverage model methods
post.get_reaction_count('upvote')
user.get_display_name()
conversation.add_message('user', content)
```

### 4. Handle Soft Deletion
```python
# Archive instead of delete
model.status = 'archived'
db.commit()
```

This reference provides everything needed to implement the API layer efficiently while maintaining data integrity and business logic consistency.
