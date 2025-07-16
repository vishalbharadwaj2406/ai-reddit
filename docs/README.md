# AI Reddit Documentation

Welcome to the comprehensive documentation for the AI Reddit platform - an innovative social media platform that combines AI-assisted content creation with meaningful discourse.

## 📁 Documentation Structure

### 🏗️ [Architecture](./architecture/)
High-level system design, technical decisions, and architectural patterns.
- **System Overview**: Complete platform architecture
- **Design Decisions**: Rationale behind key technical choices
- **Data Flow**: How information moves through the system

### 🔌 [API](./api/)
Complete API specification, endpoints, and integration guides.
- **API Specification**: Full REST API documentation
- **Authentication**: OAuth flow and security
- **WebSocket**: Real-time communication protocols

### 🗄️ [Database](./database/)
Database schema, models, and data management.
- **Schema Design**: Complete database structure
- **Model Reference**: Detailed model documentation
- **Migrations**: Database change management

### 🛠️ [Development](./development/)
Developer setup, testing, and contribution guidelines.
- **Setup Guide**: Local development environment
- **Testing Strategy**: Comprehensive testing approach
- **Coding Standards**: Code quality guidelines

### 🤖 [LLM Agent](./llm-agent/)
Specialized documentation for AI agents working on this codebase.
- **Senior Developer Handoff**: Comprehensive context and methodology for LLM agents
- **Models Reference**: Complete model guide for LLM agents
- **API Implementation**: Step-by-step API development
- **Best Practices**: Guidelines for AI-assisted development

### 📱 [Product](./product/)
Product requirements, user stories, and business logic.
- **Product Vision**: Platform goals and differentiation
- **User Stories**: Feature requirements and workflows
- **MVP Scope**: Current development focus

### 🚀 [Deployment](./deployment/)
Production deployment, scaling, and operations.
- **Infrastructure**: Server and database setup
- **Monitoring**: Health checks and analytics
- **Scaling**: Performance optimization strategies

---

## 🚀 Quick Start

1. **New Developers**: Start with [Development Setup](./development/setup.md)
2. **API Integration**: Check [API Specification](./api/specification.md)
3. **Database Work**: Review [Model Reference](./database/models.md)
4. **LLM Agents**: Use [Models Reference](./llm-agent/models-reference.md)

## 📋 Current Status

**As of July 15, 2025:**

- ✅ **Database Layer**: Complete (12/12 models, 181 tests passing)
- ✅ **Authentication System**: Complete (Google OAuth + JWT)
- ✅ **Database Tables**: Complete (13 tables created via Alembic migrations)
- ✅ **Health Check API**: Complete (Database connectivity + table verification)
- ✅ **Migration System**: Complete (Alembic configured and working)
- 🔄 **API Layer**: Core CRUD endpoints ready for development
- ⏳ **Frontend**: Planned
- ⏳ **Deployment**: Infrastructure ready (Supabase PostgreSQL)

## 🔗 External Links

- [GitHub Repository](https://github.com/vishalbharadwaj2406/ai-reddit)
- [Project Board](https://github.com/vishalbharadwaj2406/ai-reddit/projects)
- [Issues](https://github.com/vishalbharadwaj2406/ai-reddit/issues)

---

## 📝 Documentation Guidelines

### For Contributors
- Keep documentation up-to-date with code changes
- Use clear, concise language
- Include code examples where relevant
- Follow the established structure

### For LLM Agents
- Use the specialized LLM Agent documentation
- Reference the Models Reference for database queries
- Follow the API Implementation guide for endpoints
- Maintain consistency with established patterns

---

*Last Updated: July 15, 2025*
*Documentation Version: 1.1*
