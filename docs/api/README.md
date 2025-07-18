# API Documentation

Complete API specification, endpoints, and integration guides for the AI Reddit platform.

## 📁 Contents

### [API Specification](./specification.md)
Complete REST API documentation with all endpoints, request/response formats, and authentication details.

**Key Features:**
- RESTful design with real-time WebSocket streaming
- Google OAuth authentication with JWT tokens
- Conversation-centric API with forking capabilities
- Universal reaction system (upvote, downvote, heart, insightful, accurate)
- Privacy controls and social features
- Comprehensive error handling and rate limiting

## 🔧 Implementation Methodology

### AI-Assisted Test-Driven Development (TDD)

We follow a modified TDD approach optimized for AI-assisted development:

#### **Red-Green-Refactor Cycle**
1. **Red Phase**: Write comprehensive test cases first
   - Test success scenarios with proper API response format
   - Test error cases (authentication, validation, edge cases)
   - Test authorization scenarios (unauthorized access)

2. **Green Phase**: Implement the minimal code to pass tests
   - Focus on API logic and response structure
   - Handle database operations with proper error handling
   - Maintain consistent response format across all endpoints

3. **Refactor Phase**: Optimize and clean up
   - Remove code duplication
   - Improve error handling
   - Enhance documentation

#### **Test Organization**
- **Unit Tests**: `/tests/unit/api/v1/` - API endpoint testing
- **Fixtures**: `/tests/fixtures/` - Reusable test data and mocks
- **Helpers**: `/tests/utils/` - Common testing utilities
- **Mock Strategy**: Mock database operations for fast, isolated tests

#### **Development Principles**
- **API-First**: Test and implement API endpoints before complex business logic
- **Incremental**: Build one endpoint at a time with full test coverage
- **Clean Tests**: Zero warnings, fast execution, clear output
- **Consistent Format**: All API responses follow standardized format

### Current Implementation Status

#### ✅ **Completed Endpoints**
- `GET /users/me` - User profile retrieval (3 test cases)
- `PATCH /users/me` - Profile updates (4 test cases)
- Authentication middleware with comprehensive error handling

#### 🔄 **In Progress**
- Track A: Core User & Social Features implementation
- Additional user endpoints (follow system, public profiles)

#### 📋 **Next Steps**
- Complete remaining Track A endpoints
- Implement comprehensive error handling
- Add integration tests for complex workflows

## 🔗 API Overview

### Authentication
- **Google OAuth**: Primary authentication method
- **JWT Tokens**: Bearer token format for API access
- **Public Access**: Read-only access to posts without authentication
- **Rate Limiting**: Generous MVP limits for testing and feedback

### Core Endpoints

#### User Management
- `GET /users/me` - Current user profile
- `PATCH /users/me` - Update profile
- `POST /users/{id}/follow` - Follow/unfollow users
- `GET /users/{id}/followers` - User's followers list

#### Conversations & AI Chat
- `POST /conversations` - Create new conversation
- `GET /conversations/{id}` - Get conversation details
- `POST /conversations/{id}/messages` - Send message (with AI response)
- `WebSocket /ws/conversations/{id}` - Real-time AI streaming

#### Posts & Content
- `GET /posts` - Public feed with filtering
- `POST /posts` - Create post from conversation
- `GET /posts/{id}` - Single post details
- `POST /posts/{id}/expand` - Fork conversation from post

#### Social Features
- `POST /posts/{id}/reaction` - Add/update reactions
- `GET /posts/{id}/comments` - Get comments
- `POST /posts/{id}/comments` - Create comment
- `POST /posts/{id}/share` - Track sharing

## 🔄 Real-time Features

### WebSocket Integration
- **Connection**: `/ws/conversations/{conversation_id}?token=jwt_token`
- **Streaming**: AI responses streamed sentence-by-sentence
- **Authentication**: JWT token in query parameter for MVP simplicity

### Response Format
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

## 🚦 Rate Limiting

### MVP Limits (Generous for Testing)
- **AI Messages**: 100/hour per user
- **Blog Generation**: 20/hour per user
- **Post Creation**: 10/hour per user
- **General API**: 2000/hour per user

## ❌ Error Handling

### Standard Error Response
```json
{
  "success": false,
  "data": null,
  "message": "Human readable error message",
  "errorCode": "SPECIFIC_ERROR_CODE"
}
```

### Error Code Categories
- **Authentication**: `AUTH_REQUIRED`, `INVALID_TOKEN`
- **Resources**: `NOT_FOUND`, `FORBIDDEN`
- **Validation**: `INVALID_INPUT`, `MISSING_FIELD`
- **Rate Limiting**: `RATE_LIMIT_EXCEEDED`
- **AI Services**: `AI_SERVICE_ERROR`, `AI_GENERATION_FAILED`

## 🔧 Implementation Status

- ✅ **Specification**: Complete and reviewed
- ✅ **Database Layer**: All 13 tables created via Alembic migrations
- ✅ **Health Endpoints**: Database and system health monitoring active
- ✅ **Authentication System**: Google OAuth and JWT implementation complete
- ✅ **Models & Schemas**: All SQLAlchemy models and Pydantic schemas implemented
- ✅ **Testing Framework**: 181 tests passing with comprehensive coverage
- ✅ **Migration System**: Alembic configured and operational
- 🔄 **CRUD Endpoints**: Ready for implementation with solid foundation
- 🔄 **WebSocket Integration**: Ready for real-time AI streaming
- 🔄 **Rate Limiting**: Ready for implementation
- 🔄 **Error Handling**: Ready for standardized error responses
- ✅ **Authentication**: Complete (Google OAuth + JWT)
- 🔄 **Core Endpoints**: User, conversation, post CRUD in development
- ⏳ **Advanced Features**: WebSocket streaming, AI integration planned
- ⏳ **Testing**: Integration tests planned after core endpoints
- ⏳ **Documentation**: Auto-generated OpenAPI planned

## 🔧 Implementation Methodology

### AI-Assisted Test-Driven Development (TDD)

We follow a modified TDD approach optimized for AI-assisted development:

#### **Red-Green-Refactor Cycle**
1. **Red Phase**: Write comprehensive test cases first
   - Test success scenarios with proper API response format
   - Test error cases (authentication, validation, edge cases)
   - Test authorization scenarios (unauthorized access)

2. **Green Phase**: Implement the minimal code to pass tests
   - Focus on API logic and response structure
   - Handle database operations with proper error handling
   - Maintain consistent response format across all endpoints

3. **Refactor Phase**: Optimize and clean up
   - Remove code duplication
   - Improve error handling
   - Enhance documentation

#### **Test Organization**
- **Unit Tests**: `/tests/unit/api/v1/` - API endpoint testing
- **Fixtures**: `/tests/fixtures/` - Reusable test data and mocks
- **Helpers**: `/tests/utils/` - Common testing utilities
- **Mock Strategy**: Mock database operations for fast, isolated tests

#### **Development Principles**
- **API-First**: Test and implement API endpoints before complex business logic
- **Incremental**: Build one endpoint at a time with full test coverage
- **Clean Tests**: Zero warnings, fast execution, clear output
- **Consistent Format**: All API responses follow standardized format

### Current Implementation Status

#### ✅ **Completed Endpoints**
- `GET /users/me` - User profile retrieval (3 test cases)
- `PATCH /users/me` - Profile updates (4 test cases)
- Authentication middleware with comprehensive error handling

#### 🔄 **In Progress**
- Track A: Core User & Social Features implementation
- Additional user endpoints (follow system, public profiles)

#### 📋 **Next Steps**
- Complete remaining Track A endpoints
- Implement comprehensive error handling
- Add integration tests for complex workflows

## 🎯 Key User Flows

### 1. AI-Assisted Content Creation
1. User starts conversation → WebSocket connection
2. AI streams responses in real-time
3. User generates blog post from conversation
4. User publishes post with tags and privacy settings

### 2. Content Discovery & Interaction
1. User browses public feed
2. User reacts to posts (upvote, insightful, etc.)
3. User comments on posts
4. User expands interesting posts into new conversations

### 3. Social Networking
1. User follows other users
2. User receives follow requests (for private accounts)
3. User's feed shows content from followed users
4. User shares posts to external platforms

---

*For implementation details, see the [Development](../development/) section.*
*For database integration, see the [Architecture](../architecture/) section.*
