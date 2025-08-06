# AI Social

Social media platform combining AI-assisted content creation with threaded discussions.

## Overview

AI Social allows users to engage in conversations with AI to develop and refine their thoughts, then share those insights with a community. Key features include AI-powered content creation, fork-based exploration of ideas, and privacy-first social networking.

### Core Features

- **AI Conversations**: Real-time chat with AI to develop ideas into structured content
- **Post Forking**: Expand any post into a new AI conversation thread
- **Quality Reactions**: Upvote, downvote, heart, insightful, and accurate reactions
- **Privacy Controls**: User privacy settings and conversation visibility controls
- **Threaded Discussions**: Nested comment system for in-depth conversations

### Planned Features

- Multi-user (e.g., 2-person) conversations and collaborative debates
- Advanced topic discovery: trending tags, semantic search, recommendations
- AI-generated scores and feedback for debates
- More privacy controls and content moderation tools

## Documentation

Technical documentation is available in the [`docs/`](./docs/) folder:

- **[Documentation Overview](./docs/README.md)** - Navigation and structure
- **[Architecture](./docs/architecture/)** - System design and technical decisions
- **[API](./docs/api/)** - API specification and integration guides
- **[Database](./docs/database/)** - Schema design and model documentation
- **[Development](./docs/development/)** - Setup guides and testing strategies
- **[LLM Agent](./docs/llm-agent/)** - Documentation for AI agents
- **[Product](./docs/product/)** - Product requirements and user stories
- **[Deployment](./docs/deployment/)** - Production deployment and operations

### Quick Links
- **New Developers**: [Development Setup](./docs/development/README.md)
- **API Integration**: [API Specification](./docs/api/specification.md)
- **Database Work**: [Schema Design](./docs/database/schema.md)
- **LLM Agents**: [Models Reference](./docs/llm-agent/models-reference.md)

## Current Status

- **Database Layer**: Complete (12/12 models, 181 tests passing)
- **Database Tables**: 13 tables created in PostgreSQL (Supabase)
- **Authentication System**: Google OAuth + JWT implementation complete
- **AI Integration**: LangChain + Gemini 2.5 Flash complete (Phase 2.1) - streaming responses, blog generation, 61 comprehensive tests
- **Health Monitoring**: Database and system health endpoints active
- **Migration System**: Alembic configured and operational
- **Testing Framework**: 413+ tests passing with comprehensive coverage including AI
- **API Layer**: Track A (User & Social) complete, Track B (Content) in progress
- **Frontend**: Next.js 15 application with glass morphism design - mostly complete (1 known glass effect issue)
- **Deployment**: Infrastructure ready

### Database Foundation Complete
- **Tables Created**: 13 tables (12 models + 1 Alembic version tracking)
- **Migration Applied**: Initial migration `fa51e3bf0f60` successfully applied
- **Health Checks**: Database connectivity and table verification working
- **Test Coverage**: All models thoroughly tested with relationship validation

### AI Integration Complete
- **Framework**: LangChain abstraction layer for future-proof provider switching
- **Model**: Google Gemini 2.5 Flash for optimal cost-performance balance
- **Features**: Real-time streaming responses via SSE, conversation context preservation, blog generation
- **Production Status**: Fully functional with comprehensive error handling and graceful fallback
- **Testing**: 61 comprehensive AI-specific tests covering unit/integration/e2e scenarios

### Ready for Content API Development
- **Database**: Production-ready PostgreSQL setup with Supabase
- **Models**: All SQLAlchemy models implemented and tested
- **Schemas**: Pydantic schemas for API request/response validation
- **Authentication**: Google OAuth and JWT token management
- **AI Service**: LangChain + Gemini streaming responses working
- **Health Monitoring**: Real-time database and system health endpoints
- **Migration System**: Alembic for database version control

## Technical Stack

- **Backend**: FastAPI with SQLAlchemy 2.0
- **Frontend**: Next.js 15 with App Router, Tailwind CSS 4, TypeScript
- **Authentication**: Google OAuth 2.0 + JWT (NextAuth v5)
- **Database**: PostgreSQL (Supabase)
- **AI Integration**: LangChain + Google Gemini 2.5 Flash with streaming responses (production ready)
- **Design System**: Royal Ink Glass morphism with backdrop-filter effects
- **Testing**: Pytest (backend) + Vitest (frontend) with comprehensive coverage (413+ tests)
- **Deployment**: Infrastructure ready (cloud deployment planned)

## Development

### Prerequisites
- Python 3.12+
- PostgreSQL 17.4+
- Git
- Google API key for Gemini (for AI features)

### Setup
```bash
git clone https://github.com/vishalbharadwaj2406/ai-reddit.git
cd ai-reddit/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
# Copy .env.example to .env and add your API keys
pytest tests/ -v
```

### Database
- PostgreSQL database hosted on Supabase
- 13 tables created via Alembic migrations
- Health monitoring endpoints active
- 181 tests passing for all models and relationships

### AI Service
- LangChain framework with Gemini 2.5 Flash model
- Real-time streaming responses via Server-Sent Events
- Blog generation from conversation content
- Production-ready with comprehensive error handling
- Future-proof architecture for easy provider switching
- 61 comprehensive tests covering all AI integration scenarios

*Last Updated: August 5, 2025*
