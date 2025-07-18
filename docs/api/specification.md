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

#### GET /users/me ✅ IMPLEMENTED
**Purpose**: Get current user profile
**Auth Required**: Yes
**Implementation Status**: Complete with 3 test cases
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
      "followingCount": 0,
      "isPrivate": false
    }
  },
  "message": "Profile retrieved successfully"
}
```

#### PATCH /users/me ✅ IMPLEMENTED
**Purpose**: Update current user profile
**Auth Required**: Yes
**Implementation Status**: Complete with 4 test cases
**Request Body**:
```json
{
  "userName": "string (optional)",
  "profilePicture": "string (optional)",
  "isPrivate": "boolean (optional)"
}
```
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
      "followingCount": 0,
      "isPrivate": false
    }
  },
  "message": "Profile updated successfully"
}
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
**Purpose**: Get user's followers list with privacy controls
**Auth Required**: Optional (required for private accounts)
**Query Parameters**:
- `limit`: integer (default: 20, max: 100)
- `offset`: integer (default: 0)
**Response**:
```json
{
  "success": true,
  "data": {
    "followers": [
      {
        "user_id": "uuid",
        "user_name": "string",
        "profile_picture": "string",
        "is_private": boolean,
        "followed_at": "timestamp",
        "follow_status": {
          "follow_status": "none" | "pending" | "accepted",
          "is_following": boolean,
          "request_pending": boolean,
          "follows_you": boolean
        }
      }
    ],
    "pagination": {
      "total_count": integer,
      "limit": integer,
      "offset": integer,
      "has_next": boolean,
      "has_previous": boolean
    }
  },
  "message": "Followers retrieved successfully"
}
```

**Privacy Behavior**:
- **Public accounts**: Anyone can view followers
- **Private accounts**: Only authenticated users who follow the account can view
- **Error responses**:
  - `403 Forbidden` with `PRIVATE_ACCOUNT_AUTH_REQUIRED` if unauthenticated
  - `403 Forbidden` with `PRIVATE_ACCOUNT_FOLLOW_REQUIRED` if not following

#### GET /users/{user_id}/following
**Purpose**: Get users that this user follows with privacy controls
**Auth Required**: Optional (required for private accounts)
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
        "user_id": "uuid",
        "user_name": "string",
        "profile_picture": "string",
        "is_private": boolean,
        "followed_at": "timestamp",
        "follow_status": {
          "follow_status": "none" | "pending" | "accepted",
          "is_following": boolean,
          "request_pending": boolean,
          "follows_you": boolean
        }
      }
    ],
    "pagination": {
      "total_count": integer,
      "limit": integer,
      "offset": integer,
      "has_next": boolean,
      "has_previous": boolean
    }
  },
  "message": "Following retrieved successfully"
}
```

**Privacy Behavior**: Same as followers endpoint

#### GET /users/me/follow-requests
**Purpose**: Get incoming follow requests for the authenticated user
**Auth Required**: Yes
**Response**:
```json
{
  "success": true,
  "data": {
    "requests": [
      {
        "follower_id": "uuid",
        "follower_name": "string",
        "profile_picture": "string",
        "requested_at": "timestamp"
      }
    ],
    "count": integer
  },
  "message": "Follow requests retrieved successfully"
}
```

#### PATCH /users/me/follow-requests/{follower_id}
**Purpose**: Accept or reject a follow request
**Auth Required**: Yes
**Request Body**:
```json
{
  "action": "accept" | "reject"
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "follow_id": "string",
    "status": "accepted" | "rejected",
    "updated_at": "timestamp"
  },
  "message": "Follow request accepted" | "Follow request rejected"
}
```
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

#### GET /conversations ✅ IMPLEMENTED
**Purpose**: Get user's conversations
**Auth Required**: Yes
**Implementation Status**: Complete with 3 test cases
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

#### POST /conversations ✅ IMPLEMENTED
**Purpose**: Explicitly create a new conversation (e.g., when user clicks 'Start Conversation')
**Auth Required**: Yes
**Implementation Status**: Complete with 6 test cases
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

#### GET /conversations/{conversation_id} ✅ IMPLEMENTED
**Purpose**: Get conversation details and messages
**Auth Required**: Yes (own conversations only)
**Implementation Status**: Complete with 9 test cases
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

#### DELETE /conversations/{conversation_id} ✅ IMPLEMENTED
**Purpose**: Archive conversation
**Auth Required**: Yes
**Implementation Status**: Complete with 7 test cases

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
        "reactions": {
          "upvote": 15, "downvote": 2, "heart": 8,
          "insightful": 12, "accurate": 5
        },
        "userReaction": "upvote" | "downvote" | "heart" | "insightful" | "accurate" | null,
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

#### POST /posts/{post_id}/reaction
**Purpose**: Add, change, or remove a reaction for a post
**Auth Required**: Yes
**Request Body**:
```json
{
  "reaction": "upvote" | "downvote" | "heart" | "insightful" | "accurate" | null
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "reaction": "upvote",
    "reactionCounts": {
      "upvote": 15,
      "downvote": 2,
      "heart": 8,
      "insightful": 12,
      "accurate": 5
    }
  },
  "message": "Reaction updated successfully"
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
        "reactions": {
          "upvote": 8, "downvote": 1, "heart": 3,
          "insightful": 5, "accurate": 2
        },
        "userReaction": "upvote" | "downvote" | "heart" | "insightful" | "accurate" | null,
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

#### POST /comments/{comment_id}/reaction
**Purpose**: Add, change, or remove a reaction for a comment
**Auth Required**: Yes
**Request Body**:
```json
{
  "reaction": "upvote" | "downvote" | "heart" | "insightful" | "accurate" | null
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "reaction": "insightful",
    "reactionCounts": {
      "upvote": 8,
      "downvote": 1,
      "heart": 3,
      "insightful": 6,
      "accurate": 2
    }
  },
  "message": "Reaction updated successfully"
}
```
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