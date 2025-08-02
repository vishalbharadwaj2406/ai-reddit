# Architecture Overview

System design and technical decisions optimized for scalability, performance, and maintainability.

## Core Architecture

### High-Level Design
Conversation-centric architecture where posts are derived from AI conversations, enabling contextual post forking and AI-assisted content creation.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   AI Service    │
                       │  (LangChain +   │
                       │  Gemini 2.5)    │
                       └─────────────────┘
```

## Technology Stack

### Backend Stack
- **API Framework**: FastAPI for high-performance async API
- **ORM**: SQLAlchemy 2.0 with async support
- **Database**: PostgreSQL 17 with UUID primary keys
- **Authentication**: Google OAuth 2.0 + JWT tokens
- **AI Integration**: LangChain + Google Gemini 2.5 Flash
- **Migration**: Alembic for database version control

### Frontend Stack
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript with strict type checking
- **Styling**: Tailwind CSS 4 with custom design system
- **Authentication**: NextAuth v5 with Google OAuth
- **State Management**: React Context with optimistic updates
- **Real-time**: Server-Sent Events for AI streaming

### Infrastructure
- **Database Hosting**: Supabase (PostgreSQL)
- **Authentication**: Google OAuth 2.0
- **AI Provider**: Google Gemini API
- **Development**: Local development with Docker support

## Key Design Decisions

### 1. Conversation-Centric Data Model
**Decision**: Posts are derived from AI conversations rather than standalone content.

**Rationale**:
- Maintains context and conversation flow
- Enables unique "expand post" functionality via forking
- Supports AI-assisted content refinement
- Creates natural content discovery through conversation threads

### 2. UUID Primary Keys
**Decision**: Use UUIDs instead of auto-incrementing integers.

**Rationale**:
- Enables distributed system scaling
- Prevents ID enumeration attacks
- Supports future microservice architecture
- Allows offline content creation

### 3. Soft Deletion Pattern
**Decision**: Use status fields instead of hard deletion.

**Rationale**:
- Preserves data integrity and relationships
- Enables content recovery and audit trails
- Supports content moderation workflows
- Maintains conversation context even with deleted messages

### 4. Real-time AI Streaming
**Decision**: Server-Sent Events for AI conversation streaming.

**Rationale**:
- Better user experience with immediate AI responses
- Lower complexity than WebSockets for this use case
- HTTP/2 multiplexing support
- Automatic reconnection handling

### 5. Provider-Agnostic AI Integration
**Decision**: LangChain abstraction layer for AI services.

**Rationale**:
- Easy switching between AI providers
- Consistent interface for different models
- Future-proof against provider changes
- Simplified testing with mock providers

## Database Design Philosophy

### Normalization Strategy
- **3NF Compliance**: Eliminates data duplication
- **Relationship Modeling**: Many-to-many joins for flexibility
- **Index Optimization**: Strategic indexing for query performance
- **Constraint Enforcement**: Foreign keys ensure data integrity

### Scalability Considerations
- **Horizontal Scaling**: UUID keys support database sharding
- **Read Replicas**: Schema designed for read/write splitting
- **Caching Layer**: Structure supports Redis integration
- **Archive Strategy**: Status fields enable data archiving

## API Design Principles

### RESTful Design
- **Resource-Based URLs**: Clear resource identification
- **HTTP Semantics**: Proper use of HTTP methods and status codes
- **Stateless Operations**: Each request contains complete information
- **Consistent Responses**: Standardized response formats

### Security First
- **JWT Authentication**: Stateless token-based authentication
- **Input Validation**: Pydantic schemas for all requests
- **Rate Limiting**: Protection against abuse
- **CORS Configuration**: Secure cross-origin requests

### Developer Experience
- **OpenAPI Documentation**: Auto-generated interactive docs
- **Type Safety**: Full type hints and validation
- **Error Handling**: Comprehensive error responses
- **Testing Support**: Extensive test coverage

## Frontend Architecture

### Component Design
- **Atomic Design**: Reusable component hierarchy
- **Type Safety**: TypeScript interfaces for all props
- **Performance**: Lazy loading and code splitting
- **Accessibility**: WCAG compliance and keyboard navigation

### State Management
- **Context API**: React Context for global state
- **Optimistic Updates**: Immediate UI feedback
- **Error Boundaries**: Graceful error handling
- **Persistence**: Local storage for user preferences

### Design System
- **Glass Morphism**: Custom backdrop-filter design language
- **Responsive Design**: Mobile-first approach
- **Dark Mode**: System preference detection
- **Animation**: Smooth transitions and micro-interactions

## Performance Optimizations

### Database Performance
- **Strategic Indexing**: Foreign keys and query-heavy fields
- **Query Optimization**: Efficient joins and relationship loading
- **Connection Pooling**: Async connection management
- **Pagination**: Limit large result sets

### API Performance
- **Async Framework**: FastAPI async/await support
- **Response Compression**: Gzip compression enabled
- **Caching Headers**: Appropriate cache control
- **Background Tasks**: Non-blocking operations

### Frontend Performance
- **Bundle Optimization**: Tree shaking and code splitting
- **Image Optimization**: Next.js automatic image optimization
- **Static Generation**: Pre-rendered pages where possible
- **Service Workers**: Offline support and caching

## Security Architecture

### Authentication Flow
1. **Google OAuth**: Secure third-party authentication
2. **JWT Tokens**: Stateless session management
3. **Token Refresh**: Automatic token rotation
4. **Secure Storage**: HTTP-only cookies option

### Data Protection
- **Input Sanitization**: XSS prevention
- **SQL Injection Prevention**: ORM parameterized queries
- **Privacy Controls**: User-level content visibility
- **Data Encryption**: Sensitive data protection

### API Security
- **Rate Limiting**: Request throttling
- **CORS Policy**: Restrictive cross-origin settings
- **Content Validation**: Comprehensive input validation
- **Error Handling**: No sensitive data in error responses

## Deployment Architecture

### Development Environment
- **Local Development**: Docker Compose setup
- **Hot Reloading**: Fast development iteration
- **Test Database**: Isolated testing environment
- **Environment Variables**: Secure configuration management

### Production Considerations
- **Horizontal Scaling**: Load balancer ready
- **Database Replication**: Read replica support
- **CDN Integration**: Static asset delivery
- **Monitoring**: Health checks and logging

---

Architecture provides foundation for current requirements and supports future expansion.
