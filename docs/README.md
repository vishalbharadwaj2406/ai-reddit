# AI Social Documentation

Technical documentation for AI Social platform - a social media platform combining AI-assisted content creation with threaded discussions.

## Documentation Structure

### [Architecture](./architecture/)
System design, technical decisions, and architectural patterns.
- **System Overview**: Platform architecture
- **Design Decisions**: Technical choices and rationale
- **Data Flow**: Information flow through the system

### [API](./api/)
API specification, endpoints, and integration guides.
- **API Specification**: REST API documentation
- **Authentication**: OAuth flow and security
- **WebSocket**: Real-time communication protocols

### [Database](./database/)
Database schema, models, and data management.
- **Schema Design**: Database structure
- **Model Reference**: Model documentation
- **Migrations**: Database change management

### [Development](./development/)
Developer setup, testing, and contribution guidelines.
- **Setup Guide**: Local development environment
- **Testing Strategy**: Testing approach
- **Coding Standards**: Code quality guidelines

### [LLM Agent](./llm-agent/)
Documentation for AI agents working on this codebase.
- **Senior Developer Handoff**: Context and methodology for LLM agents
- **Models Reference**: Model guide for LLM agents
- **API Implementation**: API development guide
- **Best Practices**: Guidelines for AI-assisted development

### [Product](./product/)
Product requirements, user stories, and business logic.
- **Product Vision**: Platform goals and differentiation
- **User Stories**: Feature requirements and workflows
- **MVP Scope**: Current development focus

### [Deployment](./deployment/)
Production deployment, scaling, and operations.
- **Infrastructure**: Server and database setup
- **Monitoring**: Health checks and analytics
- **Scaling**: Performance optimization strategies

## Quick Start

1. **New Developers**: [Development Setup](./development/README.md)
2. **API Integration**: [API Specification](./api/specification.md)
3. **Database Work**: [Schema Design](./database/schema.md)
4. **LLM Agents**: [Models Reference](./llm-agent/models-reference.md)

## Current Status

**As of July 18, 2025:**

- **Database Layer**: Complete (12/12 models, 181 tests passing)
- **Authentication System**: Complete (Google OAuth + JWT)
- **Database Tables**: Complete (13 tables created via Alembic migrations)
- **Health Check API**: Complete (Database connectivity + table verification)
- **Migration System**: Complete (Alembic configured and working)
- **Track A: User & Social APIs**: Complete (40/40 tests passing)
  - Instagram-like Follow System with privacy controls
  - User profile management with comprehensive validation
  - Follower/Following lists with pagination support
  - Production-ready privacy model matching Instagram behavior
- **Track B: Content & Community**: In Progress
  - Conversation Management: Complete (4/4 endpoints, 7 tests passing)
  - Post Management: Next (posts, reactions, comments)
  - Real-time Features: Planned (WebSocket chat, AI integration)
- **Frontend**: Planned
- **Deployment**: Infrastructure ready (Supabase PostgreSQL)

## External Links

- [GitHub Repository](https://github.com/vishalbharadwaj2406/ai-reddit)
- [Project Board](https://github.com/vishalbharadwaj2406/ai-reddit/projects)
- [Issues](https://github.com/vishalbharadwaj2406/ai-reddit/issues)

## Documentation Guidelines

### For Contributors
- Keep documentation updated with code changes
- Use clear, concise language
- Include code examples where relevant
- Follow the established structure

### For LLM Agents
- Use the specialized LLM Agent documentation
- Reference the Models Reference for database queries
- Follow the API Implementation guide for endpoints
- Maintain consistency with established patterns

*Last Updated: July 18, 2025*
*Documentation Version: 2.0*
*Track A (User & Social): Complete - Track B (Content & Community): In Progress*
