# API Documentation

REST API specification with JWT authentication, real-time streaming, and social features.

## API Overview

### Architecture
- **Framework**: FastAPI with automatic OpenAPI generation
- **Authentication**: JWT tokens via Google OAuth 2.0
- **Documentation**: Interactive Swagger UI at `/docs`
- **Validation**: Pydantic schemas for all requests/responses
- **Real-time**: Server-Sent Events for AI conversations

### Base URL
```
Development: http://localhost:8000
Production: TBD
```

## Authentication

### OAuth Flow
1. **Google OAuth**: Users authenticate via Google OAuth 2.0
2. **JWT Tokens**: API returns access and refresh tokens
3. **Token Usage**: Include `Authorization: Bearer <token>` in requests
4. **Token Refresh**: Automatic refresh token rotation

### Protected Endpoints
Most endpoints require authentication. Public endpoints include:
- `GET /health` - System health check
- `POST /auth/google` - Google OAuth login
- `GET /posts` - Public post feed (limited)

## Core Endpoints

### User Management
- `POST /auth/google` - Google OAuth authentication
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile
- `POST /users/{user_id}/follow` - Follow/unfollow user
- `GET /users/{user_id}/followers` - Get user followers
- `GET /users/{user_id}/following` - Get users being followed

### Content Creation
- `POST /conversations` - Create new AI conversation
- `POST /conversations/{id}/messages` - Send message to AI
- `GET /conversations/{id}/stream` - SSE stream for real-time AI responses
- `POST /posts` - Create post from conversation
- `PUT /posts/{id}` - Update post content
- `DELETE /posts/{id}` - Soft delete post

### Social Interactions
- `GET /posts` - Get post feed with filtering and pagination
- `GET /posts/{id}` - Get specific post with comments
- `POST /posts/{id}/fork` - Fork post into new conversation
- `POST /posts/{id}/reactions` - Add/update post reaction
- `POST /posts/{id}/comments` - Add comment to post
- `PUT /comments/{id}` - Update comment
- `POST /comments/{id}/reactions` - Add/update comment reaction

### Content Discovery
- `GET /tags` - Get available tags
- `GET /posts/tagged/{tag}` - Get posts by tag
- `GET /search/posts` - Search posts by content
- `GET /users/{id}/posts` - Get user's posts

## Request/Response Format

### Standard Response Structure
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2025-08-01T21:30:00Z"
}
```

### Error Response Structure
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": { ... }
  },
  "timestamp": "2025-08-01T21:30:00Z"
}
```

### Pagination
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## Real-time Features

### AI Conversation Streaming
- **Endpoint**: `GET /conversations/{id}/stream`
- **Protocol**: Server-Sent Events (SSE)
- **Format**: JSON chunks with message deltas
- **Connection**: Persistent connection for real-time AI responses

### Example SSE Response
```
event: message_chunk
data: {"type": "chunk", "content": "Here's my response...", "conversation_id": "123"}

event: message_complete
data: {"type": "complete", "message_id": "456", "conversation_id": "123"}
```

## Rate Limiting

- **Authentication**: 100 requests per minute
- **Post Creation**: 10 posts per hour
- **AI Conversations**: 50 messages per hour
- **Reactions**: 200 reactions per minute
- **Comments**: 30 comments per hour

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

## Data Validation

### Post Creation
```json
{
  "title": "string (1-200 chars)",
  "content": "string (1-10000 chars)",
  "conversation_id": "uuid",
  "is_conversation_visible": "boolean",
  "tags": ["string array (max 5 tags)"]
}
```

### Comment Creation
```json
{
  "content": "string (1-2000 chars)",
  "parent_comment_id": "uuid (optional)"
}
```

### User Profile Update
```json
{
  "user_name": "string (3-30 chars, alphanumeric + underscore)",
  "profile_picture": "string (valid URL, optional)",
  "is_private": "boolean"
}
```

## Security Features

### Input Validation
- All inputs validated with Pydantic schemas
- SQL injection prevention via ORM
- XSS protection with content sanitization
- File upload validation (future feature)

### Authentication Security
- JWT token expiration (15 minutes access, 7 days refresh)
- Token rotation on refresh
- Secure HTTP-only cookie option
- CORS configuration for web clients

### Privacy Controls
- User privacy settings (public/private accounts)
- Conversation visibility controls
- Content access based on follow relationships
- Anonymous post sharing support

---

Interactive API documentation available at `/docs` endpoint.
