# Development Documentation

Developer setup, testing strategies, and contribution guidelines for the AI Reddit platform.

## 📁 Contents

### [API Implementation Plan](./api-implementation-plan.md)
Comprehensive 10-day plan for implementing the complete API layer with testing and deployment preparation.

**Phase Breakdown:**
- **Days 1-3**: Foundation setup (dependencies, auth, core structure)
- **Days 4-7**: Content management APIs (users, conversations, posts, social features)
- **Days 8-10**: Integration testing, performance optimization, deployment prep

## 🛠️ Development Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 17.4+
- Node.js 18+ (for frontend, future)
- Git for version control

### Backend Setup
```bash
# Clone repository
git clone https://github.com/vishalbharadwaj2406/ai-reddit.git
cd ai-reddit/backend

# Create virtual environment
python -m venv ai-social
ai-social\Scripts\activate  # Windows
source ai-social/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup database
# (Database configuration details in deployment docs)

# Run tests
pytest tests/ -v
```

## 🧪 Testing Strategy

### Current Status: 181 Tests Passing ✅

#### Test Pyramid Approach
```
Unit Tests (30%):     Repository & Service logic
Integration Tests (50%): API endpoints with real DB  
Contract Tests (15%):    API spec compliance
E2E Tests (5%):         Critical user journeys
```

#### Testing Philosophy: Modern TDD
- **Not Pure TDD**: Balanced approach for MVP speed
- **Test Critical Paths**: Focus on business logic and workflows
- **Integration-First**: API testing with real database
- **Leverage Tools**: FastAPI's automatic validation for basics

### Test Categories

#### Database Layer (✅ Complete)
- **Model Tests**: 177 individual model tests
- **Relationship Tests**: Foreign key constraints and navigation
- **Business Logic**: Helper methods and computed properties
- **Integration Tests**: 6 tests (currently skipped, ready to enable)

#### API Layer (🔄 Planned)
- **Endpoint Tests**: Request/response validation
- **Authentication Tests**: OAuth flow and JWT handling
- **Business Logic Tests**: Critical user workflows
- **Performance Tests**: Response time and load testing

### Quality Gates
- [ ] All API endpoints match design specification
- [ ] 95%+ test coverage on business logic
- [ ] Response times < 200ms for 95% of requests
- [ ] Zero SQL injection vulnerabilities
- [ ] Proper error handling and logging
- [ ] Rate limiting functional
- [ ] Authentication security validated

## 🏗️ Development Workflow

### Git Workflow
1. **Feature Branches**: Create from `main` for new features
2. **Testing**: Ensure all tests pass before PR
3. **Code Review**: Peer review for quality assurance
4. **Integration**: Merge to `main` after approval

### Code Standards

#### Python (Backend)
- **Style**: PEP 8 with Black formatting
- **Type Hints**: Required for all functions
- **Docstrings**: Google-style documentation
- **Testing**: Pytest with comprehensive coverage

#### Database
- **Migrations**: Alembic for version control
- **Naming**: Snake_case for tables and columns
- **Constraints**: Explicit foreign key definitions
- **Indexing**: Strategic performance optimization

#### API
- **Design**: RESTful with OpenAPI documentation
- **Validation**: Pydantic schemas for all endpoints
- **Error Handling**: Consistent error response format
- **Security**: Proper authentication and authorization

## 🔧 Development Tools

### Required Tools
- **IDE**: VS Code with Python extensions
- **Database**: PostgreSQL with pgAdmin (optional)
- **API Testing**: Postman or Thunder Client
- **Version Control**: Git with conventional commits

### Recommended Extensions (VS Code)
- Python Extension Pack
- SQLAlchemy Extension
- REST Client for API testing
- GitLens for enhanced Git integration

### Database Tools
- **pgAdmin**: GUI for PostgreSQL management
- **DBeaver**: Universal database tool
- **Alembic**: Migration management
- **SQLAlchemy**: ORM and query builder

## 📊 Performance Considerations

### Database Optimization
- **Indexing**: Strategic indexes on foreign keys and frequent queries
- **Query Optimization**: Use SQLAlchemy efficiently
- **Connection Pooling**: Proper database connection management
- **Caching**: Redis integration for future scaling

### API Performance
- **Response Times**: Target < 200ms for most endpoints
- **Rate Limiting**: Protect against abuse
- **Pagination**: Efficient large data handling
- **Async Support**: FastAPI's async capabilities

## 🔐 Security Guidelines

### Authentication
- **JWT Tokens**: Secure implementation with proper expiration
- **Google OAuth**: Trusted third-party authentication
- **Session Management**: Proper token refresh handling

### Data Protection
- **Input Validation**: Sanitize all user inputs
- **SQL Injection**: Use parameterized queries only
- **CORS**: Proper cross-origin request handling
- **HTTPS**: Enforce secure connections in production

### Privacy
- **User Data**: Respect privacy settings and controls
- **Soft Deletion**: Preserve data for potential recovery
- **Anonymization**: Support anonymous interactions where appropriate

## 🚀 Next Steps

### Immediate Priorities
1. **Enable Integration Tests**: Remove skips from existing 6 tests
2. **API Foundation**: Setup FastAPI structure and dependencies
3. **Authentication**: Implement JWT and Google OAuth

### Week 1 Goals
- Complete authentication infrastructure
- Implement core user management endpoints
- Setup WebSocket for AI conversations

### Week 2 Goals
- Complete conversation and post management APIs
- Implement social features (follow, reactions, comments)
- Add comprehensive API testing

---

*For deployment instructions, see the [Deployment](../deployment/) section.*
*For architecture details, see the [Architecture](../architecture/) section.*
