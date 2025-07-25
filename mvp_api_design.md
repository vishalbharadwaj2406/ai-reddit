# [APP_NAME] MVP API Design

## Overview
This document defines the complete API specification for [APP_NAME] MVP backend. The API follows RESTful principles with real-time streaming for AI conversations.

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
  "errorCode": string | null
}
```

### Error Response Format
```json
{
  "success": false,
  "data": null,
  "message": "Human readable error message",
  "errorCode": "SPECIFIC_ERROR_CODE"
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
  "googleToken": "string"
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "accessToken": "jwt_token_here",
    "user": {
      "userId": "uuid",
      "userName": "string",
      "email": "string",
      "profilePicture": "string",
      "createdAt": "timestamp"
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
    "user": {
      "userId": "uuid",
      "userName": "string",
      "email": "string",
      "profilePicture": "string",
      "createdAt": "timestamp",
      "followerCount": 0,
      "followingCount": 0
    }
  },
  "message": "Profile retrieved successfully"
}
```

#### GET /users/{user_id}
**Purpose**: Get public user profile
**Auth Required**: No
**Response**: Same as /users/me

#### PATCH /users/me
**Purpose**: Update user profile (partial update)
**Auth Required**: Yes
**Request Body**:
```json
{
  "userName": "string",
  "profilePicture": "string"
}
```

#### POST /users/{user_id}/follow
**Purpose**: Send a follow request or follow a user (depending on privacy)
**Auth Required**: Yes
**Response**:
```json
{
  "success": true,
  "data": {
    "status": "pending" | "accepted"
  },
  "message": "Follow request sent or follow successful"
}
```

#### DELETE /users/{user_id}/follow
**Purpose**: Unfollow a user or cancel a pending follow request
**Auth Required**: Yes
**Response**:
```json
{
  "success": true,
  "data": null,
  "message": "Unfollowed or follow request cancelled successfully"
}
```

#### GET /users/me/follow-requests/incoming
**Purpose**: List incoming follow requests
**Auth Required**: Yes
**Response**:
```json
{
  "success": true,
  "data": {
    "incomingRequests": [
      {
        "userId": "uuid",
        "userName": "string",
        "profilePicture": "string",
        "requestedAt": "timestamp"
      }
    ]
  },
  "message": "Incoming follow requests retrieved successfully"
}
```

#### GET /users/me/follow-requests/outgoing
**Purpose**: List outgoing follow requests
**Auth Required**: Yes
**Response**:
```json
{
  "success": true,
  "data": {
    "outgoingRequests": [
      {
        "userId": "uuid",
        "userName": "string",
        "profilePicture": "string",
        "requestedAt": "timestamp"
      }
    ]
  },
  "message": "Outgoing follow requests retrieved successfully"
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
  "data": {
    "pageNumber": 1,
    "size": 20,
    "followers": [
      {
        "userId": "uuid",
        "userName": "string",
        "profilePicture": "string",
        "followedAt": "timestamp"
      }
    ]
  },
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
  "data": {
    "following": [
      {
        "userId": "uuid",
        "userName": "string",
        "profilePicture": "string",
        "followedAt": "timestamp"
      }
    ]
  },
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
      "conversationId": "uuid",
      "title": "string",
      "createdAt": "timestamp",
      "updatedAt": "timestamp",
      "forkedFrom": "uuid | null"
    }
  ],
  "message": "Conversations retrieved successfully"
}
```

#### POST /conversations
**Purpose**: Explicitly create a new conversation (e.g., when user clicks 'Start Conversation')
**Auth Required**: Yes
**Request Body**:
```json
{
  "title": "string",
  "forkedFrom": "uuid | null"
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "conversationId": "uuid",
    "title": "string",
    "createdAt": "timestamp"
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
    "conversationId": "uuid",
    "title": "string",
    "createdAt": "timestamp",
    "forkedFrom": "uuid | null",
    "messages": [
      {
        "messageId": "uuid",
        "role": "user" | "assistant",
        "content": "string",
        "isBlog": boolean,
        "createdAt": "timestamp"
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
**Purpose**: Send message and get AI response (conversation must already exist)
**Auth Required**: Yes
**Request Body**:
```json
{
  "content": "string"
}
```
**Response**:
- Returns streaming response (see Streaming section)
- Returns 404 Not Found if the conversation does not exist

#### POST /conversations/{conversation_id}/generate-blog
**Purpose**: Generate blog post from conversation
**Auth Required**: Yes
**Request Body**:
```json
{
  "additionalContext": "string | null"
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "messageId": "uuid",
    "content": "string",
    "createdAt": "timestamp"
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
- `userId`: uuid (filter by user)
**Response**:
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "postId": "uuid",
        "title": "string",
        "content": "string",
        "createdAt": "timestamp",
        "user": {
          "userId": "uuid",
          "userName": "string",
          "profilePicture": "string"
        },
        "tags": ["string"],
        "reactions": { "like": 10, "love": 2 },
        "userReaction": "like" | "love" | null,
        "commentCount": 0,
        "viewCount": 0,
        "userViewCount": 0,
        "conversationId": "uuid | null" // null if conversation is not viewable
      }
    ]
  },
  "message": "Posts retrieved successfully"
}
```

#### POST /posts
**Purpose**: Create post from conversation message
**Auth Required**: Yes
**Request Body**:
```json
{
  "messageId": "uuid",
  "title": "string",
  "content": "string",
  "tags": ["string"],
  "isVisible": boolean
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "postId": "uuid",
    "title": "string",
    "content": "string",
    "createdAt": "timestamp"
  },
  "message": "Post created successfully"
}
```

#### GET /posts/{post_id}
**Purpose**: Get single post details
**Auth Required**: No
**Response**: Same as single post in GET /posts, but wrapped as `{ "data": { "post": { ... } } }`

#### GET /posts/{post_id}/conversation
**Purpose**: Get the conversation for a post (if viewable)
**Auth Required**: No (viewable only if allowed by post owner)
**Response**:
```json
{
  "success": true,
  "data": {
    "conversation": {
      "conversationId": "uuid",
      "title": "string",
      "createdAt": "timestamp",
      "forkedFrom": "uuid | null",
      "messages": [
        {
          "messageId": "uuid",
          "role": "user" | "assistant",
          "content": "string",
          "isBlog": boolean,
          "createdAt": "timestamp"
        }
      ]
    }
  },
  "message": "Conversation retrieved successfully"
}
```
- Returns 404 or omits conversation if not viewable.

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
    "shareId": "uuid",
    "sharedAt": "timestamp"
  },
  "message": "Post shared successfully"
}
```

#### POST /posts/{post_id}/expand
**Purpose**: Create a new conversation forked from a post (does not include the original conversation by default)
**Auth Required**: Yes
**Request Body**: (empty)
**Response**:
```json
{
  "success": true,
  "data": {
    "conversationId": "uuid",
    "title": "string",
    "forkedFrom": "uuid"
  },
  "message": "Conversation forked successfully"
}
```

#### POST /conversations/{conversation_id}/include-original
**Purpose**: Include the original conversation into the expanded conversation (optional, second step)
**Auth Required**: Yes
**Request Body**: (empty)
**Response**:
```json
{
  "success": true,
  "data": {
    "conversationId": "uuid",
    "included": true
  },
  "message": "Original conversation included successfully"
}
```

#### POST /conversations/{conversation_id}/uninclude-original
**Purpose**: Remove the original conversation from the expanded conversation (undo the include-original action)
**Auth Required**: Yes
**Request Body**: (empty)
**Response**:
```json
{
  "success": true,
  "data": {
    "conversationId": "uuid",
    "included": false
  },
  "message": "Original conversation removed successfully"
}
```

---

### 6. Comment Endpoints

#### GET /posts/{post_id}/comments
**Purpose**: Get post comments (with reactions)
**Auth Required**: No
**Query Parameters**:
- `limit`: integer (default: 20, max: 100)
- `offset`: integer (default: 0)
**Response**:
```json
{
  "success": true,
  "data": {
    "comments": [
      {
        "commentId": "uuid",
        "content": "string",
        "createdAt": "timestamp",
        "user": {
          "userId": "uuid",
          "userName": "string",
          "profilePicture": "string"
        },
        "reactions": { "like": 3, "love": 1 },
        "userReaction": "like" | "love" | null,
        "parentCommentId": "uuid | null",
        "replies": []
      }
    ]
  },
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
  "parentCommentId": "uuid | null"
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

#### POST /comments/{comment_id}/reaction
**Purpose**: Add, change, or remove a reaction for a comment
**Auth Required**: Yes
**Request Body**:
```json
{
  "reaction": "like" | "love" | "laugh" | "sad" | null
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
  "data": {
    "tags": [
      {
        "tagId": "uuid",
        "name": "string",
        "postCount": 0
      }
    ]
  },
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
  "type": "aiResponse",
  "data": {
    "content": "partial sentence...",
    "isComplete": boolean,
    "messageId": "uuid"
  }
}
```

### Error Format:
```json
{
  "type": "error",
  "data": {
    "message": "Error description",
    "errorCode": "SPECIFIC_ERROR"
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

This API design supports the complete [APP_NAME] MVP functionality with room for future expansion.