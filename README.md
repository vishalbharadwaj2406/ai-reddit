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
- **Health Monitoring**: Database and system health endpoints active
- **Migration System**: Alembic configured and operational
- **Testing Framework**: 181 tests passing with comprehensive coverage
- **API Layer**: Ready for implementation with solid foundation
- **Frontend**: Planned
- **Deployment**: Planned

### Database Foundation Complete
- **Tables Created**: 13 tables (12 models + 1 Alembic version tracking)
- **Migration Applied**: Initial migration `fa51e3bf0f60` successfully applied
- **Health Checks**: Database connectivity and table verification working
- **Test Coverage**: All models thoroughly tested with relationship validation

### Ready for CRUD API Development
- **Database**: Production-ready PostgreSQL setup with Supabase
- **Models**: All SQLAlchemy models implemented and tested
- **Schemas**: Pydantic schemas for API request/response validation
- **Authentication**: Google OAuth and JWT token management
- **Health Monitoring**: Real-time database and system health endpoints
- **Migration System**: Alembic for database version control

## Technical Stack

- **Backend**: FastAPI with SQLAlchemy 2.0
- **Database**: PostgreSQL (Supabase)
- **Authentication**: Google OAuth 2.0 + JWT
- **Testing**: Pytest with 181 tests passing
- **Deployment**: Planned (cloud infrastructure)
- **AI Integration**: Google Gemini API (planned)

## Development

### Prerequisites
- Python 3.12+
- PostgreSQL 17.4+
- Git

### Setup
```bash
git clone https://github.com/vishalbharadwaj2406/ai-reddit.git
cd ai-reddit/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pytest tests/ -v
```

### Database
- PostgreSQL database hosted on Supabase
- 13 tables created via Alembic migrations
- Health monitoring endpoints active
- 181 tests passing for all models and relationships

*Last Updated: July 18, 2025*
