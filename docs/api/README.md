# API Documentation

API specification, endpoints, and integration guides for the AI Social platform.

## Contents

### [API Specification](./specification.md)
Complete REST API specification with endpoints, request/response formats, and authentication.

**Key Features:**
- RESTful design with OpenAPI documentation
- JWT-based authentication with Google OAuth
- SSE streaming support for real-time AI conversations
- Comprehensive error handling and validation
- Rate limiting and security controls

## API Overview

### Architecture
- **Framework**: FastAPI with automatic OpenAPI generation
- **Authentication**: JWT tokens via Google OAuth 2.0
- **Validation**: Pydantic schemas for all requests/responses
- **Documentation**: Interactive Swagger UI and ReDoc
- **Real-time**: SSE streaming connections for AI conversations

### Base URL
```
Development: http://localhost:8000
Production: TBD
```

### Authentication
All authenticated endpoints require JWT tokens obtained via Google OAuth:
```
Authorization: Bearer <jwt_token>
```

### Response Format
All API responses follow a standard wrapper format:
```json
{
  "success": boolean,
  "data": object | array | null,
  "message": string,
  "errorCode": string | null
}
```

## Endpoint Categories

### Authentication Endpoints
- `POST /auth/google` - Google OAuth authentication
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - Logout user

### User Management
- `GET /users/me` - Get current user profile
- `PATCH /users/me` - Update user profile
- `GET /users/{user_id}` - Get public user profile
- `POST /users/{user_id}/follow` - Follow/unfollow user

### Conversation Management
- `POST /conversations` - Create new conversation
- `GET /conversations/{id}` - Get conversation details
- `POST /conversations/{id}/messages` - Add message to conversation
- `GET /conversations/{id}/messages` - Get conversation messages
- `GET /conversations/{id}/stream` - Real-time SSE conversation streaming

### Content Management
- `GET /posts` - Get public feed
- `POST /posts` - Create new post
- `GET /posts/{id}` - Get post details
- `POST /posts/{id}/expand` - Fork post into new conversation
- `POST /posts/{id}/reaction` - Add/remove reaction
- `GET /posts/{id}/comments` - Get post comments
- `POST /posts/{id}/comments` - Add comment to post

### Social Features
- `GET /users/{id}/posts` - Get user's posts
- `GET /users/{id}/followers` - Get user's followers
- `GET /users/{id}/following` - Get users being followed
- `GET /feed/following` - Get personalized feed

### Health & System
- `GET /health` - Basic health check
- `GET /health/database` - Database connectivity check
- `GET /health/` - Comprehensive system health

## Implementation Status

### Complete
- Health check endpoints
- Authentication infrastructure (JWT + Google OAuth)
- Database models and relationships
- Request/response schemas
- Error handling framework
- Conversation Management: Complete (4 endpoints with comprehensive testing)

### Ready for Implementation
- User management endpoints
- Conversation and message endpoints
- Post creation and management
- Social interaction features
- SSE real-time communication

### Future Enhancements
- Advanced search capabilities
- Content recommendation algorithms
- Analytics and reporting endpoints
- Administrative management interfaces
- Third-party integrations

## Development Guidelines

### Request Validation
- All requests validated using Pydantic schemas
- Comprehensive error messages for invalid requests
- Type checking and automatic documentation

### Error Handling
- Consistent error response format across all endpoints
- HTTP status codes following REST conventions
- Detailed error codes for client-side handling

### Security
- JWT token validation on all protected endpoints
- Rate limiting to prevent abuse
- Input sanitization and SQL injection prevention
- CORS configuration for frontend integration

### Performance
- Efficient database queries with proper indexing
- Pagination for large result sets
- Caching strategies for frequently accessed data
- Async request handling where appropriate

## Testing Strategy

### API Testing
- Comprehensive endpoint testing with real database
- Authentication flow testing
- Error condition validation
- Performance and load testing

### Integration Testing
- End-to-end user workflow testing
- Third-party service integration testing
- Database transaction testing
- Real-time SSE streaming communication testing

*For database schema, see the [Database](../database/) section.*
*For system architecture, see the [Architecture](../architecture/) section.*
