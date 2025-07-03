# AI Social MVP - API Design

## API Design Philosophy
- **RESTful endpoints** with clear resource naming
- **JWT authentication** for all protected routes
- **Consistent error handling** with proper HTTP status codes
- **JSON request/response** format throughout
- **FastAPI async/await** patterns for performance

---

## Authentication
**Base URL**: `https://api.aisocial.dev`  
**Authentication**: `Authorization: Bearer <jwt_token>`

---

## Endpoints

### **1. Create Conversation**
**Endpoint**: `POST /conversations`  
**Use Case**: User starts a new AI conversation

**Request**:
```json
POST /conversations
Authorization: Bearer <jwt_token>

{}  // Empty body
```

**Response**:
```json
{
    "id": 123,
    "title": "Untitled Chat",
    "created_at": "2025-01-15T10:30:00Z",
    "user_id": 456
}
```

**Implementation Notes**:
- Default title: "Untitled Chat"
- Title auto-updates after first AI response via background task
- Users can manually edit titles later (stops auto-updates)
- Auto-generated titles: 3-5 words max

**Error Responses**:
- `401 Unauthorized`: Invalid/missing JWT token
- `500 Internal Server Error`: Database connection issues

---

### **2. AI Conversation Streaming**
**Endpoint**: `WebSocket /conversations/{id}/stream`  
**Use Case**: Real-time AI conversation with streaming responses

**FastAPI WebSocket Implementation**:
```python
@app.websocket("/conversations/{conversation_id}/stream")
async def conversation_stream(websocket: WebSocket, conversation_id: int):
    # JWT authentication
    # WebSocket connection management
    # Gemini streaming integration
    pass
```

**Message Flow**:
```json
// Client sends user message
{
    "type": "user_message",
    "content": "What do you think about AI ethics?"
}

// Server streams AI response
{"type": "ai_start", "message_id": 789}
{"type": "ai_chunk", "content": "AI ethics involves"}
{"type": "ai_chunk", "content": " several key considerations..."}
{"type": "ai_complete", "message_id": 789}
```

**Implementation Notes**:
- **Gemini Integration**: Uses `generate_content_stream()` for real-time responses
- **Connection Management**: Handle reconnection, timeouts, and errors
- **Context Preservation**: Maintain conversation history for AI context
- **Message Storage**: Save both user and AI messages to database
- **Title Auto-Update**: Background task updates conversation title after first exchange

**Error Handling**:
- `WebSocket Close 4001`: Invalid/expired JWT token
- `WebSocket Close 4004`: Conversation not found or unauthorized
- `WebSocket Close 4008`: AI service unavailable

---

### **3. Get Conversation Messages**
**Endpoint**: `GET /conversations/{id}/messages`  
**Use Case**: Retrieve conversation history for display or AI context

**FastAPI Implementation**:
```python
@app.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    # Return messages in chronological order (oldest first)
    pass
```

**Response**:
```json
{
    "messages": [
        {
            "id": 1,
            "role": "user", 
            "content": "What do you think about AI ethics?",
            "is_blog": false,
            "created_at": "2025-01-15T10:30:00Z"
        },
        {
            "id": 2,
            "role": "assistant",
            "content": "AI ethics involves several key considerations...",
            "is_blog": false,
            "created_at": "2025-01-15T10:30:15Z"
        },
        {
            "id": 3,
            "role": "assistant",
            "content": "AI Ethics: A Deep Dive\n\nIn today's digital age...",
            "is_blog": true,
            "created_at": "2025-01-15T10:45:00Z"
        }
    ],
    "total_count": 124,
    "has_more": true
}
```

**Implementation Notes**:
- **Ordering**: Chronological order (oldest first) for conversation flow
- **Pagination**: 50 messages per page, use offset for older messages
- **Authorization**: Verify user owns the conversation  
- **Performance**: Simple offset-based pagination for MVP
- **Blog Filtering**: Include `is_blog` field in response for UI handling

**Error Responses**:
- `401 Unauthorized`: Invalid JWT token
- `403 Forbidden`: User doesn't own this conversation
- `404 Not Found`: Conversation doesn't exist

---

### **4. Generate Blog Draft**
**Endpoint**: `POST /conversations/{id}/blog`  
**Use Case**: Generate AI blog draft from conversation history

**Request**:
```json
POST /conversations/123/blog
Authorization: Bearer <jwt_token>

{
    "prompt": "Create a blog post about the key insights from this conversation",
    "style": "professional" // optional: "casual", "academic", "professional"
}
```

**Response**:
```json
{
    "message_id": 456,
    "content": "AI Ethics: Key Considerations for Modern Technology\n\nIn our rapidly evolving digital landscape...",
    "conversation_id": 123,
    "created_at": "2025-01-15T10:45:00Z"
}
```

**Implementation Notes**:
- **AI Integration**: Uses conversation history as context for blog generation
- **Storage**: Blog draft saved as message with `is_blog=TRUE`, `role='assistant'`
- **Editability**: User can request new drafts or edit existing content
- **Context Window**: Uses recent conversation messages (last 20-30 exchanges)
- **Multiple Drafts**: Can generate multiple blog drafts per conversation

**Error Responses**:
- `401 Unauthorized`: Invalid JWT token
- `403 Forbidden`: User doesn't own this conversation
- `404 Not Found`: Conversation doesn't exist
- `400 Bad Request`: Conversation too short to generate meaningful blog

---

### **5. Get Blog Drafts**
**Endpoint**: `GET /conversations/{id}/blogs`  
**Use Case**: Retrieve all blog drafts for a conversation

**Response**:
```json
{
    "blogs": [
        {
            "message_id": 456,
            "content": "AI Ethics: Key Considerations...",
            "created_at": "2025-01-15T10:45:00Z"
        },
        {
            "message_id": 478,
            "content": "Revised: AI Ethics in Practice...",
            "created_at": "2025-01-15T11:15:00Z"
        }
    ],
    "total_count": 2
}
```

**Implementation Notes**:
- **Query**: `SELECT * FROM messages WHERE conversation_id = ? AND is_blog = TRUE`
- **Ordering**: Most recent drafts first
- **Authorization**: Verify user owns the conversation

---

### **6. Publish Post**
**Endpoint**: `POST /posts`  
**Use Case**: Create social post from edited blog content

**Request**:
```json
POST /posts
Authorization: Bearer <jwt_token>

{
    "conversation_id": 123,
    "title": "AI Ethics: A Developer's Perspective",
    "content": "In our rapidly evolving digital landscape, we must consider...",
    "tags": "ai,ethics,development,technology",
    "parent_post_id": null // for threaded replies, optional
}
```

**Response**:
```json
{
    "id": 789,
    "title": "AI Ethics: A Developer's Perspective",
    "content": "In our rapidly evolving digital landscape...",
    "tags": "ai,ethics,development,technology",
    "conversation_id": 123,
    "user_id": 456,
    "parent_post_id": null,
    "created_at": "2025-01-15T11:30:00Z"
}
```

**Implementation Notes**:
- **Content Flexibility**: Post content can be any text (edited from blog draft or original)
- **Required Fields**: title, content, conversation_id
- **Tag Validation**: Basic comma-separated string validation
- **Threading Support**: Optional parent_post_id for replies
- **Authorization**: User must own the referenced conversation

**Error Responses**:
- `401 Unauthorized`: Invalid JWT token
- `403 Forbidden`: User doesn't own the referenced conversation
- `400 Bad Request`: Missing required fields or invalid data
- `404 Not Found`: Referenced conversation or parent_post doesn't exist

---

## Next Endpoints to Design
- `GET /feed` - Personalized social feed
- `GET /posts/{id}` - Get specific post with thread context
- `POST /posts/{id}/reply` - Reply to existing post
