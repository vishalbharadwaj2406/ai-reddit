# Architecture Documentation

System design, technical decisions, and architectural patterns for the AI Social platform.

## Contents

### [Design Decisions](./design-decisions.md)
Documentation of key architectural decisions, rationales, and design philosophy behind the AI Social MVP API design.

**Key Topics:**
- Core platform vision and differentiators
- Conversation-centric data model
- Elegant repost implementation via forking
- Custom blog flow design
- Real-time streaming decisions
- Authentication & security strategy
- Rate limiting and API patterns

### [API-Database Alignment](./api-db-alignment.md)
Analysis of how the API design aligns with the database schema, ensuring consistency and optimal implementation.

**Key Topics:**
- Perfect alignments between API and DB
- Implementation advantages
- Quality assessment (9.5/10 alignment score)
- Zero schema changes needed
- Ready-to-implement features

## Architecture Principles

### 1. Conversation-Centric Design
- Posts emerge from AI conversations
- Maintains context and relationships
- Enables unique "expand post" functionality

### 2. Privacy-First Approach
- User privacy controls (public/private accounts)
- Conversation visibility settings
- Anonymous sharing support

### 3. Extensible Foundation
- UUID primary keys for distributed scaling
- Soft deletion via status fields
- JSON metadata fields for future extensions
- Modular API design for easy feature additions

### 4. Performance-Oriented
- Proper database indexing
- Efficient relationship queries
- Caching-ready architecture
- Rate limiting for resource protection

## Technical Stack

- **Backend**: FastAPI with SQLAlchemy 2.0
- **Database**: PostgreSQL (Supabase) with UUID primary keys
- **Authentication**: JWT with Google OAuth
- **Real-time**: WebSocket for AI conversations (ready for implementation)
- **AI Integration**: LangChain with Gemini (ready for implementation)
- **Testing**: Pytest with comprehensive coverage
- **Deployment**: Supabase PostgreSQL infrastructure

## Implementation Status

### Complete
- Database schema (12 models, 13 tables created)
- Model relationships and constraints
- Authentication system (Google OAuth + JWT)
- Health check endpoints
- Migration system (Alembic)
- Test framework (181 tests passing)
- Track A: User & Social APIs (40 tests passing)
- Track B: Conversation Management (4 endpoints, 7 tests passing)

### Ready for Implementation
- Post Management APIs (create, read, react, fork)
- Community Features (comments, sharing, analytics)
- WebSocket real-time features
- AI conversation integration
- Social interaction features
- Content management workflows

### Future Phases
- Frontend application
- Advanced AI features
- Scaling optimizations
- Production deployment

*For API specification, see the [API](../api/) section.*
*For database details, see the [Database](../database/) section.*
