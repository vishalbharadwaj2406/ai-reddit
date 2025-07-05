# AIkya MVP API Design

## Overview
This document defines the complete API specification for AIkya MVP backend. The API follows RESTful principles with real-time streaming for AI conversations.

---

## 🔐 Authentication

### JWT Token Flow
- **Google OAuth**: Users sign in with Google, backend validates and returns JWT
- **Auto Profile Creation**: First-time users get basic profile created automatically
- **Token Format**: Bearer token in Authorization header
- **Public Access**: Read-only access to posts without authentication

---

## 📋 API Response Format

### Standard Response Wrapper
```json
{
  "success": boolean,
  "data": object | array | null,
  "message": string,
  "error_code": string | null
}
```

### Error Response Format
```json
{
  "success": false,
  "data": null,
  "message": "Human readable error message",
  "error_code": "SPECIFIC_ERROR_CODE"
}
```

---

## 🔗 API Endpoints

### 1. Authentication Endpoints

#### POST /auth/google
**Purpose**: Authenticate user with Google OAuth token
**Auth Required**: No
**Request Body**:
```json
{
  "google_token": "string"
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token_here",
    "user": {
      "user_id": "uuid",
      "user_name": "string",
      "email": "string",
      "profile_picture": "string",
      "created_at": "timestamp"
    }
  },
  "message": "Authentication successful"
}
```

#### POST /auth/refresh
**Purpose**: Refresh JWT token
**Auth Required**: Yes
**Response**: Same as /auth/google

---

### 2. User Endpoints

#### GET /users/me
**Purpose**: Get current user profile
**Auth Required**: Yes
**Response**:
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "user_name": "string",
    "email": "string",
    "profile_picture": "string",
    "created_at": "timestamp",
    "follower_count": 0,
    "following_count": 0
  },
  "message": "Profile retrieved successfully"
}
```

#### GET /users/{user_id}
**Purpose**: Get public user profile
**Auth Required**: No
**Response**: Same as /users/me

#### PUT /users/me
**Purpose**: Update user profile
**Auth Required**: Yes
**Request Body**:
```json
{
  "user_name": "string",
  "profile_picture": "string"
}
```

#### POST /users/{user_id}/follow
**Purpose**: Follow/unfollow user
**Auth Required**: Yes
**Request Body**:
```json
{
  "action": "follow" | "unfollow"
}
```

#### GET /users/{user_id}/followers
**Purpose**: Get user's followers list
**Auth Required**: No
**Query Parameters**:
- `limit`: integer (default: 20, max: 100)
- `offset`: integer (default: 0)
**Response**:
```json
{
  "success": true,
  "data": [
    {
      "user_id": "uuid",
      "user_name": "string",
      "profile_picture": "string",
      "followed_at": "timestamp"
    }
  ],
  "message": "Followers retrieved successfully"
}
```

#### GET /users/{user_id}/following
**Purpose**: Get users that this user follows
**Auth Required**: No
**Query Parameters**:
- `limit`: integer (default: 20, max: 100)
- `offset`: integer (default: 0)
**Response**:
```json
{
  "success": true,
  "data": [
    {
      "user_id": "uuid",
      "user_name": "string",
      "profile_picture": "string",
      "followed_at": "timestamp"
    }
  ],
  "message": "Following retrieved successfully"
}
```

---

### 3. Conversation Endpoints

#### GET /conversations
**Purpose**: Get user's conversations
**Auth Required**: Yes
**Query Parameters**:
- `limit`: integer (default: 20, max: 100)
- `offset`: integer (default: 0)
**Response**:
```json
{
  "success": true,
  "data": [
    {
      "conversation_id": "uuid",
      "title": "string",
      "created_at": "timestamp",
      "updated_at": "timestamp",
      "message_count": 0,
      "forked_from": "uuid | null"
    }
  ],
  "message": "Conversations retrieved successfully"
}
```

#### POST /conversations
**Purpose**: Create new conversation (for custom blog flow)
**Auth Required**: Yes
**Request Body**:
```json
{
  "title": "string",
  "forked_from": "uuid | null"
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "conversation_id": "uuid",
    "title": "string",
    "created_at": "timestamp"
  },
  "message": "Conversation created successfully"
}
```

#### GET /conversations/{conversation_id}
**Purpose**: Get conversation details and messages
**Auth Required**: Yes (own conversations only)
**Response**:
```json
{
  "success": true,
  "data": {
    "conversation_id": "uuid",
    "title": "string",
    "created_at": "timestamp",
    "forked_from": "uuid | null",
    "messages": [
      {
        "message_id": "uuid",
        "role": "user" | "assistant",
        "content": "string",
        "is_blog": boolean,
        "created_at": "timestamp"
      }
    ]
  },
  "message": "Conversation retrieved successfully"
}
```

#### DELETE /conversations/{conversation_id}
**Purpose**: Archive conversation
**Auth Required**: Yes

---

### 4. AI Chat Endpoints

#### POST /conversations/{conversation_id}/messages
**Purpose**: Send message and get AI response
**Auth Required**: Yes
**Request Body**:
```json
{
  "content": "string"
}
```
**Response**:
- If conversation doesn't exist, creates it automatically
- Returns streaming response (see Streaming section)

#### POST /conversations/{conversation_id}/generate-blog
**Purpose**: Generate blog post from conversation
**Auth Required**: Yes
**Request Body**:
```json
{
  "additional_context": "string | null"
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "message_id": "uuid",
    "content": "string",
    "is_blog": true,
    "created_at": "timestamp"
  },
  "message": "Blog generated successfully"
}
```

---

### 5. Post Endpoints

#### GET /posts
**Purpose**: Get public feed of posts
**Auth Required**: No
**Query Parameters**:
- `limit`: integer (default: 20, max: 100)
- `offset`: integer (default: 0)
- `tag`: string (filter by tag)
- `user_id`: uuid (filter by user)
**Response**:
```json
{
  "success": true,
  "data": [
    {
      "post_id": "uuid",
      "title": "string",
      "content": "string",
      "created_at": "timestamp",
      "user": {
        "user_id": "uuid",
        "user_name": "string",
        "profile_picture": "string"
      },
      "tags": ["string"],
      "like_count": 0,
      "dislike_count": 0,
      "comment_count": 0,
      "view_count": 0,
      "user_interaction": {
        "liked": boolean | null,
        "viewed": boolean
      }
    }
  ],
  "message": "Posts retrieved successfully"
}
```

#### POST /posts
**Purpose**: Create post from conversation message
**Auth Required**: Yes
**Request Body**:
```json
{
  "message_id": "uuid",
  "title": "string",
  "content": "string",
  "tags": ["string"],
  "is_visible": boolean
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "post_id": "uuid",
    "title": "string",
    "content": "string",
    "created_at": "timestamp"
  },
  "message": "Post created successfully"
}
```

#### GET /posts/{post_id}
**Purpose**: Get single post details
**Auth Required**: No
**Response**: Same as single post in GET /posts

#### POST /posts/{post_id}/like
**Purpose**: Like/dislike post
**Auth Required**: Yes
**Request Body**:
```json
{
  "action": "like" | "dislike" | "remove"
}
```

#### POST /posts/{post_id}/view
**Purpose**: Track post view
**Auth Required**: No (but user_id if authenticated)

#### POST /posts/{post_id}/share
**Purpose**: Share post (track sharing activity)
**Auth Required**: Yes
**Request Body**:
```json
{
  "platform": "string | null"
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "share_id": "uuid",
    "shared_at": "timestamp"
  },
  "message": "Post shared successfully"
}
```

#### POST /posts/{post_id}/expand
**Purpose**: Create conversation forked from post
**Auth Required**: Yes
**Request Body**:
```json
{
  "include_original_conversation": boolean
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "conversation_id": "uuid",
    "title": "string",
    "forked_from": "uuid"
  },
  "message": "Conversation forked successfully"
}
```

---

### 6. Comment Endpoints

#### GET /posts/{post_id}/comments
**Purpose**: Get post comments
**Auth Required**: No
**Query Parameters**:
- `limit`: integer (default: 20, max: 100)
- `offset`: integer (default: 0)
**Response**:
```json
{
  "success": true,
  "data": [
    {
      "comment_id": "uuid",
      "content": "string",
      "created_at": "timestamp",
      "user": {
        "user_id": "uuid",
        "user_name": "string",
        "profile_picture": "string"
      },
      "like_count": 0,
      "dislike_count": 0,
      "parent_comment_id": "uuid | null",
      "replies": []
    }
  ],
  "message": "Comments retrieved successfully"
}
```

#### POST /posts/{post_id}/comments
**Purpose**: Create comment
**Auth Required**: Yes
**Request Body**:
```json
{
  "content": "string",
  "parent_comment_id": "uuid | null"
}
```

#### POST /comments/{comment_id}/like
**Purpose**: Like/dislike comment
**Auth Required**: Yes
**Request Body**:
```json
{
  "action": "like" | "dislike" | "remove"
}
```

---

### 7. Tag Endpoints

#### GET /tags
**Purpose**: Get all tags
**Auth Required**: No
**Response**:
```json
{
  "success": true,
  "data": [
    {
      "tag_id": "uuid",
      "name": "string",
      "post_count": 0
    }
  ],
  "message": "Tags retrieved successfully"
}
```

---

## 🔄 Real-time Streaming

### WebSocket Connection: /ws/conversations/{conversation_id}
**Purpose**: Real-time AI conversation streaming
**Auth Required**: Yes (via query param ?token=jwt_token)

### Message Format:
```json
{
  "type": "ai_response",
  "data": {
    "content": "partial sentence...",
    "is_complete": boolean,
    "message_id": "uuid"
  }
}
```

### Error Format:
```json
{
  "type": "error",
  "data": {
    "message": "Error description",
    "error_code": "SPECIFIC_ERROR"
  }
}
```

---

## 🚫 Rate Limiting

### Limits:
- **AI Messages**: 100 per user per hour
- **Blog Generation**: 20 per user per hour
- **Post Creation**: 10 per user per hour
- **General API**: 2000 requests per user per hour

### Rate Limit Headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1640995200
```

---

## ❌ Error Codes

### Authentication Errors:
- `AUTH_REQUIRED`: Authentication required
- `INVALID_TOKEN`: Invalid or expired token
- `GOOGLE_AUTH_FAILED`: Google authentication failed

### Resource Errors:
- `NOT_FOUND`: Resource not found
- `FORBIDDEN`: Access denied
- `ALREADY_EXISTS`: Resource already exists

### Validation Errors:
- `INVALID_INPUT`: Invalid request data
- `MISSING_FIELD`: Required field missing
- `INVALID_FORMAT`: Invalid data format

### Rate Limiting:
- `RATE_LIMIT_EXCEEDED`: Too many requests

### AI Errors:
- `AI_SERVICE_ERROR`: AI service unavailable
- `AI_GENERATION_FAILED`: AI response generation failed

---

## 🔄 Key User Flows

### 1. New User Registration
1. `POST /auth/google` → Auto-create profile
2. `GET /users/me` → Get profile details

### 2. Start Conversation & Create Post
1. User types message → `POST /conversations/{id}/messages` (creates conversation if needed)
2. AI streams response via WebSocket
3. User continues conversation...
4. `POST /conversations/{id}/generate-blog` → Generate blog candidate
5. `POST /posts` → Publish final post

### 3. Expand Post Flow
1. `POST /posts/{id}/expand` → Create forked conversation
2. `GET /conversations/{id}` → Load conversation with original post context
3. User continues chatting...

### 4. Custom Blog Flow
1. `POST /conversations` → Create empty conversation
2. User writes in text editor
3. `POST /posts` → Publish directly

---

## 🔧 Technical Implementation Notes

### Database Considerations:
- Use connection pooling for PostgreSQL
- Implement proper indexing for fast queries
- Use UUIDs for all primary keys
- Soft deletion with status fields

### AI Integration:
- Use LangChain with Gemini for model flexibility
- Implement proper error handling and retries
- Stream responses sentence-by-sentence
- Store conversation context efficiently

### Security:
- Validate JWT tokens on all protected endpoints
- Sanitize all user inputs
- Implement CORS properly
- Use HTTPS in production

### Performance:
- Cache frequently accessed data (tags, user profiles)
- Implement pagination for all list endpoints
- Use database indexes for common queries
- Consider CDN for static assets

---

This API design supports the complete AIkya MVP functionality with room for future expansion.