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
            "created_at": "2025-01-15T10:30:00Z"
        },
        {
            "id": 2,
            "role": "assistant",
            "content": "AI ethics involves several key considerations...",
            "created_at": "2025-01-15T10:30:15Z"
        }
    ],
    "total_count": 124,
    "has_more": true
}
```

**Implementation Notes**:
- **Ordering**: Newest first (most recent messages at top)
- **Pagination**: 50 messages per page, use offset for older messages
- **Authorization**: Verify user owns the conversation  
- **Performance**: Simple offset-based pagination for MVP

**Error Responses**:
- `401 Unauthorized`: Invalid JWT token
- `403 Forbidden`: User doesn't own this conversation
- `404 Not Found`: Conversation doesn't exist

---

## Next Endpoints to Design
- `POST /conversations/{id}/summaries` - Generate AI summary
- `POST /posts` - Publish conversation as social post
