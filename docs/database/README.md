# Database Documentation

Comprehensive database schema, models, and data management documentation for the AI Reddit platform.

## 📁 Contents

### [Database Schema](./schema.md)
Complete PostgreSQL database schema design with tables, relationships, and constraints.

**Key Features:**
- 12 core models covering all MVP functionality
- Normalized design following best practices
- UUID primary keys for scalability
- Soft deletion via status fields
- Comprehensive indexing for performance

### [Models Reference](./models.md)
Detailed documentation of all SQLAlchemy models, relationships, and helper methods.

**Available Soon**: Detailed model documentation will be moved here from the LLM agent section.

## 🗄️ Database Overview

### Core Models (12 Total)

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

## 🏗️ Architecture Principles

### 1. Conversation-Centric Design
```
Users ←→ Conversations ←→ Messages
   ↓         ↓
Posts ←→ Comments ←→ Reactions
   ↓
Tags, Views, Shares
```

### 2. Relationship Integrity
- All foreign keys properly constrained
- No CASCADE deletes (application-level handling)
- Composite primary keys where appropriate
- Self-referential relationships for threading

### 3. Extensibility Features
- JSON metadata fields for future extensions
- Status fields for workflow management
- UUID keys for distributed scaling
- Normalized design for easy feature additions

### 4. Performance Optimization
- Strategic indexing on foreign keys
- Optimized queries for common operations
- Efficient many-to-many relationships
- Proper constraints to prevent data issues

## 📊 Database Statistics

- **Total Models**: 12
- **Test Coverage**: 181 tests passing
- **Relationship Types**: One-to-many, many-to-many, self-referential
- **Primary Key Type**: UUID (for scalability)
- **Deletion Strategy**: Soft delete via status fields

## 🔧 Key Design Decisions

### Privacy Controls
- `User.is_private`: Account-level privacy
- `Post.is_conversation_visible`: Conversation sharing control
- Status-based content filtering

### Social Features
- Universal reaction system across posts/comments
- Follow relationships with pending/accepted states
- Anonymous sharing support

### Analytics Foundation
- Composite keys for tracking (user, post, timestamp)
- Platform-specific sharing analytics
- View counting with user attribution

## 🧪 Testing Strategy

### Current Status: 181 Tests Passing ✅

#### Test Categories
- **Model Creation**: Basic instantiation and validation
- **Relationships**: Foreign key constraints and navigation
- **Business Logic**: Helper methods and computed properties
- **Data Integrity**: Constraint enforcement and edge cases
- **Integration**: Cross-model workflows and cascades

#### Test Coverage
- All 12 models have comprehensive unit tests
- Integration tests for complex workflows
- Edge case testing for data integrity
- Performance testing for query optimization

## 🔄 Migration Strategy

### Development Approach
- Alembic for version-controlled migrations
- Incremental schema changes
- Data preservation during updates
- Rollback capability for safety

### Production Considerations
- Zero-downtime migration planning
- Data backup strategies
- Performance impact assessment
- Rollback procedures

---

*For API integration, see the [API](../api/) section.*
*For implementation guides, see the [Development](../development/) section.*
