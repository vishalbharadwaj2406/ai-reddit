# [APP_NAME]

✨ Diverse Thoughts, Unified Wisdom ✨

[APP_NAME] is a revolutionary platform for thinkers, creators, and curious minds. Here, anyone—regardless of writing skill—can turn their thoughts into powerful, well-researched blogs and share them with a community that values substance, depth, and genuine discussion.

Unlike traditional social media, [APP_NAME] is built for meaningful, bias-free debate and collaborative exploration. Our AI helps you clarify, fact-check, and challenge your ideas before you share—so your voice is not just heard, but truly understood.

Whether you want to:
- Express a nuanced opinion,
- Explore philosophy, spirituality, politics, or any topic in depth,
- Engage in fact-driven debates with people of different perspectives,
- Or simply discover fresh, positive, and thought-provoking content—

[APP_NAME] gives you the tools to do it, and a community that welcomes it. Share not just posts, but the full context of your conversations. Move beyond sound bites and gotchas—here, real discussion thrives.

---

## Features

**MVP Features**

- Post concise, thoughtful blogs directly from your conversations with AI
- React to posts with upvote, downvote, heart, insightful, and accurate reactions
- Comment and share posts with meaningful engagement
- Explore more (fork) with any blog to start your own conversation with AI, exploring its merits or demerits
- When forking, you can choose to include just the blog or the full original conversation (if public)
- You can also form a new blog after exploring a post and posting a response. This feature is called "Repost"
- Tag your posts for better discovery and filter posts by tags
- All content is public and text-only for now
- Simple Google sign-in, unique user ID, and modifiable display name

**Planned / Future Features**

- Edit and archive posts and messages
- AI-powered fact checker and debate judge agents with different personas
- Multi-user (e.g., 2-person) conversations and collaborative debates
- Advanced topic discovery: trending tags, semantic search, recommendations
- AI-generated scores and feedback for debates
- More privacy controls and content moderation tools

---

[APP_NAME] is for anyone who wants to share, learn, and grow through real conversation. Move beyond the noise—start a conversation that matters.

---

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](./docs/) folder:

- **[📋 Documentation Overview](./docs/README.md)** - Start here for navigation
- **[🏗️ Architecture](./docs/architecture/)** - System design and technical decisions
- **[🔌 API](./docs/api/)** - Complete API specification and integration guides
- **[🗄️ Database](./docs/database/)** - Schema design and model documentation
- **[🛠️ Development](./docs/development/)** - Setup guides and testing strategies
- **[🤖 LLM Agent](./docs/llm-agent/)** - Specialized documentation for AI agents
- **[📱 Product](./docs/product/)** - Product requirements and user stories
- **[🚀 Deployment](./docs/deployment/)** - Production deployment and operations

### Quick Links
- **New Developers**: [Development Setup](./docs/development/README.md)
- **API Integration**: [API Specification](./docs/api/specification.md)
- **Database Work**: [Schema Design](./docs/database/schema.md)
- **LLM Agents**: [Models Reference](./docs/llm-agent/models-reference.md)

---

## 🚀 Current Status

- ✅ **Database Layer**: Complete (12/12 models, 181 tests passing)
- ✅ **Database Tables**: 13 tables created in PostgreSQL (Supabase)
- ✅ **Authentication System**: Google OAuth + JWT implementation complete
- ✅ **Health Monitoring**: Database and system health endpoints active
- ✅ **Migration System**: Alembic configured and operational
- ✅ **Testing Framework**: 181 tests passing with comprehensive coverage
- 🔄 **API Layer**: Ready for implementation with solid foundation
- ⏳ **Frontend**: Planned
- ⏳ **Deployment**: Planned

### Database Foundation Complete ✅
- **Tables Created**: 13 tables (12 models + 1 Alembic version tracking)
- **Migration Applied**: Initial migration `fa51e3bf0f60` successfully applied
- **Health Checks**: Database connectivity and table verification working
- **Test Coverage**: All models thoroughly tested with relationship validation

### Ready for CRUD API Development ✅
- **Database**: Production-ready PostgreSQL setup with Supabase
- **Models**: All SQLAlchemy models implemented and tested
- **Schemas**: Pydantic schemas for API request/response validation
- **Authentication**: Google OAuth and JWT token management
- **Health Monitoring**: Real-time database and system health endpoints
- **Migration System**: Alembic for database version control

---
