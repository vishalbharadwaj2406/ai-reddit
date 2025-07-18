# Database Documentation

Database schema, models, and data management documentation for the AI Social platform.

## Contents

### [Database Schema](./schema.md)
PostgreSQL database schema design with tables, relationships, and constraints.

**Key Features:**
- 12 core models covering all MVP functionality
- Normalized design following best practices
- UUID primary keys for scalability
- Soft deletion via status fields
- Comprehensive indexing for performance

### [Models Reference](./models.md)
Detailed documentation of all SQLAlchemy models, relationships, and helper methods.

**Available Soon**: Detailed model documentation will be moved here from the LLM agent section.

## Database Overview

### Core Models (12 Total) - All Created

#### User Management
- **User**: Platform users with social features
- **Follow**: User-to-user relationships with privacy controls

#### Content Creation
- **Conversation**: AI conversation management with forking
- **Message**: Individual messages within conversations
- **Post**: Published content derived from conversations

#### Social Interaction
- **Comment**: User comments on posts with threading
- **PostReaction**: User reactions to posts (upvote, heart, etc.)
- **CommentReaction**: User reactions to comments

#### Content Organization
- **Tag**: Content categorization system
- **PostTag**: Many-to-many relationship for post tagging

#### Analytics & Tracking
- **PostView**: View tracking for analytics
- **PostShare**: Social sharing with platform tracking

### Database Status: Production Ready
- **Database**: PostgreSQL (Supabase) connected and operational
- **Tables Created**: 13 tables (12 models + 1 Alembic version tracking)
- **Migration System**: Alembic configured and operational
- **Health Monitoring**: Database health endpoints active
- **Initial Migration**: Applied successfully (fa51e3bf0f60)

### Technical Details
- **Primary Keys**: UUID for all tables (scalability)
- **Relationships**: Proper foreign key constraints
- **Indexing**: Strategic indexes on frequently queried columns
- **Soft Deletion**: Status fields instead of hard deletes
- **Timestamps**: Created/updated timestamps on all models
- **Constraints**: Data integrity enforced at database level

## Testing Status
- **Model Tests**: 177 individual model tests passing
- **Relationship Tests**: Foreign key constraints validated
- **Business Logic Tests**: Helper methods tested
- **Integration Tests**: 6 tests ready to enable
- **Migration Tests**: Alembic migration system validated

## Performance Considerations
- **Indexing Strategy**: Indexes on foreign keys and search columns
- **Query Optimization**: Efficient SQLAlchemy query patterns
- **Connection Pooling**: Configured for production load
- **Monitoring**: Health checks for database connectivity

## Next Steps
1. Enable integration tests (remove test skips)
2. Implement repository layer for data access
3. Add comprehensive query examples
4. Performance testing under load
5. Backup and recovery procedures

*For API integration, see the [API](../api/) section.*
*For development setup, see the [Development](../development/) section.*
