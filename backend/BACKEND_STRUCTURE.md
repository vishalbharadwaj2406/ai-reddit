# [APP_NAME] Backend Structure

## Overview

This document explains the FastAPI backend structure we've created for the [APP_NAME] MVP. The architecture follows industry best practices with a layered approach optimized for scalability and maintainability.

## Directory Structure

```
backend/
├── app/                          # Main application package
│   ├── __init__.py               # Package marker
│   ├── main.py                   # FastAPI app entry point & configuration
│   │
│   ├── core/                     # Core application utilities
│   │   ├── __init__.py
│   │   ├── config.py             # Environment & settings management
│   │   └── database.py           # Database connection & session management
│   │
│   ├── api/                      # API routes organized by version
│   │   ├── __init__.py
│   │   └── v1/                   # Version 1 API endpoints
│   │       ├── __init__.py
│   │       ├── auth.py           # Authentication endpoints
│   │       ├── users.py          # User management endpoints
│   │       ├── conversations.py  # Conversation endpoints
│   │       └── posts.py          # Post management endpoints
│   │
│   ├── models/                   # SQLAlchemy database models
│   │   ├── __init__.py           # Imports all models
│   │   ├── user.py               # User model (implemented)
│   │   ├── conversation.py       # Conversation model (skeleton)
│   │   ├── message.py            # Message model (skeleton)
│   │   ├── post.py               # Post model (skeleton)
│   │   ├── comment.py            # Comment model (skeleton)
│   │   ├── tag.py                # Tag model (skeleton)
│   │   └── associations.py       # Many-to-many relationship tables
│   │
│   ├── schemas/                  # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── auth.py               # Auth-related schemas
│   │   ├── user.py               # User-related schemas
│   │   ├── conversation.py       # Conversation schemas
│   │   └── post.py               # Post schemas
│   │
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py       # Authentication business logic
│   │   ├── user_service.py       # User management logic
│   │   ├── conversation_service.py # Conversation logic
│   │   ├── post_service.py       # Post management logic
│   │   └── ai_service.py         # AI integration (Gemini + LangChain)
│   │
│   ├── repositories/             # Data access layer
│   │   ├── __init__.py
│   │   ├── user_repository.py    # User database operations
│   │   ├── conversation_repository.py # Conversation database operations
│   │   ├── post_repository.py    # Post database operations
│   │   └── message_repository.py # Message database operations
│   │
│   └── dependencies/             # Shared dependencies for routes
│       ├── __init__.py
│       ├── auth.py               # Authentication dependencies
│       └── pagination.py        # Pagination helpers
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_main.py              # Basic app tests (implemented)
│   ├── conftest.py               # Test configuration & fixtures
│   ├── test_api/                 # API endpoint tests
│   ├── test_services/            # Business logic tests
│   ├── test_repositories/        # Database operation tests
│   └── test_models/              # Model tests
│
├── scripts/                      # Development & deployment scripts
│   ├── setup_dev.py              # Development environment setup
│   ├── migrate.py                # Database migration helper
│   └── seed_data.py              # Test data generation
│
├── alembic/                      # Database migrations (to be created)
│   ├── versions/                 # Migration files
│   └── alembic.ini               # Alembic configuration
│
├── requirements.txt              # Python dependencies
├── env.example                   # Environment variables template
├── README.md                     # Setup & usage instructions
└── BACKEND_STRUCTURE.md          # This file
```

## Architecture Layers

### 1. **API Layer** (`app/api/v1/`)
- **Purpose**: Handle HTTP requests and responses
- **Responsibilities**:
  - Request validation (via Pydantic schemas)
  - Response formatting
  - HTTP status codes
  - Authentication middleware
- **Organization**: Resources grouped by collection (users, posts, conversations)
- **Current Status**: Skeleton endpoints with proper error handling

### 2. **Service Layer** (`app/services/`)
- **Purpose**: Business logic and orchestration
- **Responsibilities**:
  - Core application logic
  - Coordination between repositories
  - External API integrations (Google OAuth, Gemini AI)
  - Transaction management
  - Complex data transformations
- **Current Status**: Package structure ready for implementation

### 3. **Repository Layer** (`app/repositories/`)
- **Purpose**: Data access abstraction
- **Responsibilities**:
  - Database queries and operations
  - Data persistence
  - Query optimization
  - Database transaction handling
- **Pattern**: One repository per main entity
- **Current Status**: Package structure ready for implementation

### 4. **Model Layer** (`app/models/`)
- **Purpose**: Database schema definition
- **Technology**: SQLAlchemy ORM
- **Features**:
  - Type safety with Python type hints
  - Relationship definitions
  - Database constraints
  - Automatic timestamps
- **Current Status**: User model implemented, others ready for implementation

### 5. **Schema Layer** (`app/schemas/`)
- **Purpose**: Data validation and serialization
- **Technology**: Pydantic
- **Features**:
  - Automatic request validation
  - Type conversion
  - Response serialization
  - API documentation generation
- **Current Status**: Package structure ready for implementation

## Key Features Implemented

### ✅ **Application Foundation**
- FastAPI app with proper configuration
- CORS middleware for frontend integration
- Environment-based configuration management
- Health check endpoints
- Automatic API documentation

### ✅ **Database Infrastructure**
- SQLAlchemy integration with PostgreSQL
- Connection pooling and session management
- Database utility functions
- Transaction support

### ✅ **User Model**
- Complete user model with all required fields
- Google OAuth integration fields
- Privacy settings
- Proper relationships setup
- Helper methods for common operations

### ✅ **API Structure**
- RESTful endpoint organization
- Proper HTTP status codes
- Error handling with meaningful messages
- Version-based routing (`/api/v1/`)
- Request/response documentation

### ✅ **Development Tools**
- Comprehensive test setup with pytest
- Development setup script
- Environment configuration template
- Package organization for easy navigation

## Technology Stack

- **Framework**: FastAPI (high-performance, automatic documentation)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens + Google OAuth
- **Validation**: Pydantic schemas
- **Testing**: pytest with async support
- **AI Integration**: Google Gemini + LangChain (ready for implementation)

## Next Steps for Implementation

### Phase 1: Core Models & Schemas
1. Implement remaining models (Conversation, Message, Post, Comment, Tag)
2. Create association tables for many-to-many relationships
3. Implement Pydantic schemas for all entities
4. Set up database migrations with Alembic

### Phase 2: Authentication System
1. Implement Google OAuth integration
2. Create JWT token management
3. Build authentication dependencies
4. Add user registration/login endpoints

### Phase 3: Core Features
1. Implement repository layer for data access
2. Build service layer for business logic
3. Complete API endpoints for all resources
4. Add WebSocket support for real-time features

### Phase 4: AI Integration
1. Integrate Google Gemini API
2. Implement LangChain for conversation management
3. Build conversation generation and continuation
4. Add post creation from conversations

## Development Workflow

1. **Start Development Server**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Run Tests**:
   ```bash
   pytest
   ```

3. **API Documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

4. **Database Operations**:
   ```bash
   python scripts/setup_dev.py  # Initial setup
   alembic upgrade head          # Run migrations
   ```

## Best Practices Implemented

- **Separation of Concerns**: Clear layer boundaries
- **Dependency Injection**: FastAPI's built-in DI system
- **Type Safety**: Full type hints throughout
- **Error Handling**: Consistent HTTP error responses
- **Documentation**: Comprehensive docstrings and comments
- **Testing**: Test structure ready for comprehensive coverage
- **Environment Management**: Secure configuration handling
- **Database**: Connection pooling and session management

## Security Considerations

- Environment variables for sensitive data
- JWT token-based authentication
- CORS configuration for frontend integration
- SQL injection prevention via ORM
- Input validation via Pydantic schemas
- Prepared for rate limiting implementation

This structure provides a solid foundation for rapid MVP development while maintaining production-ready code quality and scalability.