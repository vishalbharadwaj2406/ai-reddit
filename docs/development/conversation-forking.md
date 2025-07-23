# Conversation Forking Implementation

## Overview

The conversation forking feature allows users to create new AI conversations based on existing posts. This enables branching discussions and exploration of ideas from published content.

## Implementation Details

### API Endpoint
```
POST /api/v1/posts/{post_id}/fork
```

### Request Schema
```python
class PostForkRequest(BaseModel):
    includeOriginalConversation: Optional[bool] = None
```

### Response Schema
```python
class PostForkResponse(BaseModel):
    conversationId: UUID
    title: str
    forkedFrom: UUID
    includeOriginalConversation: bool
```

## Core Components

### 1. Fork Prompts Service (`app/prompts/fork_prompts.py`)

Dedicated service for generating AI context and welcome messages for forked conversations.

#### Key Methods:
- `get_fork_context_prompt()`: Generates system context for AI including original post content and optional conversation history
- `get_fork_welcome_message()`: Creates adaptive welcome messages based on context inclusion
- `get_fork_system_prompt()`: Provides specialized AI behavior instructions for fork conversations

#### Example Usage:
```python
from app.prompts.fork_prompts import fork_prompts

# Generate context prompt
context = fork_prompts.get_fork_context_prompt(
    post_title="Machine Learning Basics",
    post_content="Introduction to ML concepts...",
    original_conversation="User: What is ML? AI: Machine Learning...",
    include_original_conversation=True
)

# Generate welcome message
welcome = fork_prompts.get_fork_welcome_message(
    post_title="Machine Learning Basics",
    include_original_conversation=True
)
```

### 2. Fork Logic (`app/services/post_service.py`)

#### Privacy-Aware Context Inclusion Logic:
```python
# User explicit choice takes precedence
if request.includeOriginalConversation is not None:
    include_original = request.includeOriginalConversation
else:
    # Default: include only if conversation exists and is public
    include_original = (
        post.conversation_id is not None and 
        original_conversation and 
        original_conversation.visibility == ConversationVisibility.PUBLIC
    )

# Only fetch context if requested AND conversation is public
context = None
if include_original and original_conversation and original_conversation.visibility == ConversationVisibility.PUBLIC:
    context = self._get_conversation_context(original_conversation.conversation_id)
```

#### Fork Creation Process:
1. Validate post exists and is accessible
2. Determine context inclusion based on user choice and privacy settings
3. Retrieve conversation context if applicable
4. Generate fork title with "Fork of:" prefix
5. Create new conversation with AI context
6. Create PostFork tracking record
7. Update post fork count
8. Return fork details

### 3. Database Integration

#### PostFork Model
Tracks fork relationships for analytics and genealogy:
```python
class PostFork(Base):
    user_id: UUID (FK to users)
    post_id: UUID (FK to posts)
    conversation_id: UUID (FK to conversations)
    forked_at: TIMESTAMP
    original_conversation_included: str
    status: str
```

#### Fork Count Tracking
Post model includes `fork_count` field automatically incremented on fork creation.

## Privacy Controls

### Context Inclusion Rules:
1. **Explicit False**: Never include context regardless of conversation state
2. **Explicit True**: Include context only if conversation exists and is public
3. **Not Specified**: Default to include only if conversation exists and is public

### Privacy Enforcement:
- Original conversation context only retrieved if conversation is public
- Private conversations never leak context to forks
- User choice respected while maintaining privacy boundaries

## Error Handling

### Duplicate Fork Protection:
- Same user can fork same post multiple times
- Timestamp-based primary key prevents exact duplicates
- Retry logic handles timing edge cases

### Standard Error Responses:
- 404: Post not found
- 401/403: Authentication/authorization failures
- 400: Invalid request data or constraint violations

## Testing

### Test Coverage (11 Tests):
- Basic fork functionality and response structure
- `includeOriginalConversation` logic validation
- Privacy control enforcement
- Error scenario handling
- Database integration verification

### Test Files:
- `tests/integration/test_fork_basic.py`: Core functionality tests
- `tests/integration/test_include_original_conversation_logic.py`: Privacy logic tests
- `tests/integration/test_post_fork_simple.py`: Simple integration test

## Post-MVP Features

### Prepared Services:
- `conversation_summarization_service.py`: Intelligent context summarization for long conversations
- `fork_analytics_service.py`: Fork genealogy tracking and trending analysis

### Future Enhancements:
- Fork tree visualization
- Conversation summarization for context
- Fork recommendation algorithms
- Advanced fork analytics and metrics

## Usage Examples

### Basic Fork without Context:
```python
# Request
POST /api/v1/posts/123/fork
{
  "includeOriginalConversation": false
}

# Response
{
  "success": true,
  "data": {
    "conversationId": "456",
    "title": "Fork of: Original Post Title",
    "forkedFrom": "123",
    "includeOriginalConversation": false
  }
}
```

### Fork with Context (if public):
```python
# Request
POST /api/v1/posts/123/fork
{
  "includeOriginalConversation": true
}

# AI receives original post + conversation context
# Welcome message indicates context inclusion
```

### Default Behavior:
```python
# Request (no includeOriginalConversation specified)
POST /api/v1/posts/123/fork
{}

# Automatically includes context if conversation is public
# Otherwise creates fresh fork without context
```
