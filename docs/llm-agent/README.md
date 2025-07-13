# LLM Agent Documentation

Specialized documentation for AI agents working on the AI Reddit codebase. This section provides comprehensive references and guidelines optimized for LLM-assisted development.

## 📁 Contents

### [Senior Developer Handoff](./handoff-prompt.md)
Comprehensive context and methodology for AI agents taking lead engineering roles. This is your primary starting point for understanding project status, technical decisions, and development approach.

### [Models Reference](./models-reference.md)
Complete database model documentation specifically designed for LLM agents, including relationships, helper methods, and usage patterns.

**Key Features:**
- Detailed model specifications for all 12 database models
- Relationship mapping and navigation
- Helper method documentation
- Common query patterns
- Business logic implementation guidelines

## 🤖 LLM Agent Guidelines

### Using This Documentation

#### For Database Queries
- Reference the Models Reference for exact field names and relationships
- Use the provided query patterns for efficient database operations
- Follow the established naming conventions and constraints

#### For API Implementation
- Use the comprehensive model documentation to understand data relationships
- Follow the helper method patterns for consistent business logic
- Maintain the established architectural patterns

### Key Principles for LLM Agents

#### 1. Data Integrity
- Always check foreign key constraints before creating relationships
- Use the provided helper methods instead of direct field manipulation
- Respect the soft deletion pattern via status fields

#### 2. Relationship Navigation
- Understand the conversation-centric design pattern
- Use the established relationship paths for data access
- Follow the privacy logic embedded in model methods

#### 3. Query Efficiency
- Use the provided query patterns for optimal performance
- Leverage SQLAlchemy relationships instead of manual joins
- Follow the indexing strategy for fast queries

## 🗄️ Model Quick Reference

### Core Entities
```python
# Primary models and their key relationships
User → Conversations → Messages
User → Posts → Comments → Reactions
Post → Tags (via PostTag)
Post → Views, Shares (analytics)
User ↔ User (via Follow for social graph)
```

### Key Helper Methods
```python
# User helpers
user.get_display_name()
user.is_active()

# Post helpers  
post.get_reaction_count('upvote')
post.get_share_count()
post.is_visible_to(user)

# Conversation helpers
conversation.add_message(role, content)
conversation.get_latest_message()

# Follow helpers
follow.accept()
follow.archive()
follow.is_pending()
```

## 🔧 Implementation Patterns

### Creating Relationships
```python
# Always use helper methods when available
conversation.add_message('user', 'Hello AI!')

# For direct creation, respect constraints
post_reaction = PostReaction(
    user_id=user.user_id,
    post_id=post.post_id,
    reaction='upvote',
    status='active'
)
```

### Privacy Checks
```python
# Use built-in privacy logic
if post.is_visible_to(current_user):
    return post_data
else:
    return forbidden_response()

# Respect user privacy settings
if user.is_private and not is_following(current_user, user):
    return limited_profile()
```

### Query Optimization
```python
# Use relationships for efficient queries
user.posts.filter(Post.status == 'active')

# Aggregate queries with proper joins
reaction_counts = db.query(PostReaction.reaction, func.count())
                   .filter(PostReaction.post_id == post_id)
                   .group_by(PostReaction.reaction)
```

## 📊 Data Validation Rules

### Required Fields
- All models require explicit status field ('active' by default)
- Foreign keys must reference existing records
- Unique constraints must be respected (usernames, emails, etc.)

### Business Logic Constraints
- Users cannot follow themselves
- Only one reaction per user per post/comment
- Conversations can be forked from posts only
- Anonymous sharing allows null user_id

### Status Management
- 'active': Normal operational state
- 'archived': Soft deleted (hidden from normal queries)
- 'pending': Awaiting approval (follows)
- 'accepted'/'rejected': Follow request outcomes

## 🎯 Common Use Cases

### User Authentication Flow
```python
# Google OAuth → User creation/retrieval
user = User.query.filter_by(google_id=google_id).first()
if not user:
    user = User(google_id=google_id, email=email, ...)
```

### Content Creation Workflow
```python
# Conversation → Message → Post
conversation = Conversation(user_id=user_id, title=title)
message = conversation.add_message('assistant', blog_content)
post = Post(user_id=user_id, conversation_id=conversation.conversation_id, ...)
```

### Social Interaction
```python
# Follow request handling
follow = Follow(follower_id=current_user_id, following_id=target_user_id)
if target_user.is_private:
    follow.status = 'pending'
else:
    follow.status = 'accepted'
```

### Content Discovery
```python
# Public feed with privacy respect
posts = db.query(Post).join(User)
         .filter(or_(
             User.is_private == False,
             and_(User.is_private == True, 
                  Follow.follower_id == current_user_id,
                  Follow.status == 'accepted')
         ))
```

## ⚠️ Important Constraints

### Database-Level
- UUID primary keys (never use auto-increment IDs)
- Composite primary keys for tracking tables
- Foreign key constraints enforced
- Unique constraints on usernames, emails

### Application-Level
- Soft deletion only (never hard delete)
- Privacy checks before data access
- Rate limiting on user actions
- Input validation and sanitization

### Performance
- Use indexes for frequent queries
- Limit result sets with pagination
- Avoid N+1 queries with proper eager loading
- Cache frequent lookups where appropriate

## 🔄 Error Handling

### Common Scenarios
- **Foreign Key Violations**: Check existence before creation
- **Unique Constraint Violations**: Handle gracefully with user feedback
- **Privacy Violations**: Return appropriate error codes
- **Rate Limiting**: Respect limits and provide clear feedback

### Best Practices
- Use try-catch blocks for database operations
- Provide specific error messages for debugging
- Log errors with context for monitoring
- Return consistent error response format

---

*This documentation is specifically designed for LLM agents. For human developer documentation, see the [Development](../development/) section.*
