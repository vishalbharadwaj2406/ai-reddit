# LLM Agent Documentation

Documentation for AI agents working on this codebase.

## Contents

### [Senior Developer Handoff](./handoff-prompt.md)
Context and methodology for LLM agents working on the AI Social platform.

**Key Information:**
- Complete project context and current status
- Development methodologies and best practices
- Database models and API patterns
- Testing strategies and implementation guidelines

### [Models Reference](./models-reference.md)
Model guide for LLM agents including database schema, relationships, and query patterns.

**Key Information:**
- Complete model documentation with relationships
- Helper methods and business logic
- Query examples and database patterns
- Integration points between models

## Purpose

This documentation section provides specialized information for AI agents (like Claude) to effectively work on the AI Social codebase. It includes comprehensive context about the project structure, implementation patterns, and best practices.

## Key Features for AI Agents

### Database Context
- Complete model reference with 12 core models
- Relationship mappings and foreign key constraints
- Helper methods and computed properties
- Query patterns and optimization guidelines

### API Patterns
- Consistent request/response formats
- Authentication and authorization patterns
- Error handling strategies
- Testing methodologies

### Development Guidelines
- Code organization and architectural patterns
- Testing strategies with 181 tests passing
- Database migration procedures
- Implementation best practices

## Current Implementation Status

### Database Foundation (Complete)
- All 13 models implemented and tested (including comments)
- 14 tables created via Alembic migrations
- Foreign key relationships established
- Helper methods and business logic implemented

### Authentication System (Complete)
- Google OAuth integration
- JWT token management
- Authentication middleware
- Security validation

### Comments System (Complete)
- Complete CRUD operations with threading
- Emoji reactions with validation
- Service/repository architecture
- 160 unit tests with 100% pass rate

### Content Management (Complete)
- Post creation, retrieval, and forking
- Hot ranking algorithm implementation
- Tag filtering and user filtering
- Comprehensive test coverage

### Health Monitoring (Complete)
- Database connectivity checks
- System health endpoints
- Migration status verification
- Comprehensive health reporting

### Current Status: 232/259 Tests Passing (90% Success Rate)
- Unit tests: 160/160 (100%)
- E2E tests: 15/15 (100%)
- Integration tests: 51/72 (71% - 21 tests need fixture updates)

### Ready for Development
- Advanced social features and real-time updates
- Integration test modernization (21 tests to fix)
- Comments router registration
- SSE real-time features
- AI conversation integration enhancement

## Usage Guidelines for AI Agents

### Model Queries
Reference the Models Reference for:
- Proper model instantiation
- Relationship navigation
- Helper method usage
- Query optimization

### API Implementation
Follow established patterns for:
- Request validation using Pydantic schemas
- Response formatting with standard wrapper
- Error handling with consistent codes
- Authentication and authorization

### Testing Approach
Maintain testing standards with:
- Comprehensive test coverage (232/259 tests passing - 90% success rate)
- Database transaction testing
- Authentication flow validation
- Error condition testing
- TDD methodology for new features
- Integration test fixture modernization

### Code Quality
Adhere to established standards:
- Type hints for all functions
- Proper docstring documentation
- Consistent naming conventions
- Clean architectural patterns

## Implementation Priorities

### Immediate Tasks
1. Enable integration tests (remove skips from 6 existing tests)
2. Implement core CRUD API endpoints
3. Add SSE support for real-time features
4. Integrate AI conversation capabilities

### Development Workflow
1. Reference existing models and patterns
2. Follow established testing methodologies
3. Maintain consistent code organization
4. Update documentation as needed

*For technical architecture, see the [Architecture](../architecture/) section.*
*For API specifications, see the [API](../api/) section.*
