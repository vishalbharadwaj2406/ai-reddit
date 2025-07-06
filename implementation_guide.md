# AIkya MVP Implementation Guide

## Project Overview
AIkya is an AI-powered conversation platform where users create blog posts through AI conversations and can fork/expand existing posts for deeper exploration. This guide provides a complete task breakdown for two engineers (Vishal and Aravind) to build the MVP.

**Tech Stack:**
- Backend: Python/FastAPI
- Frontend: Next.js/React
- Database: PostgreSQL
- AI: Google Gemini with LangChain
- Real-time: WebSocket with FastAPI
- Authentication: Google OAuth
- Testing: pytest (backend), Jest/React Testing Library (frontend)

---

## Development Phases

### Phase 1: Foundation Setup (Week 1)
### Phase 2: Core Backend API (Weeks 2-3)
### Phase 3: Frontend Core (Weeks 3-4)
### Phase 4: AI Integration (Week 4-5)
### Phase 5: Real-time Features (Week 5)
### Phase 6: Social Features (Week 6)
### Phase 7: Polish & Testing (Week 7)

---

## Task Breakdown

### PHASE 1: FOUNDATION SETUP

#### Task F1.1 - Project Structure Setup [Vishal]
**Tag:** `setup`, `infrastructure`
**Description:** Create the basic project structure with proper directory organization and Git setup
**Expected Outcome:**
- Root directory with `backend/` and `frontend/` folders
- Proper `.gitignore` files for both Python and Node.js
- README files with setup instructions
- Initial Git repository with main branch protection

**Deliverables:**
```
aikya/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
├── .gitignore
└── README.md
```

**Verification:** Project can be cloned and both backend/frontend folders have proper structure

#### Task F1.2 - Backend Environment Setup [Aravind]
**Tag:** `setup`, `backend`
**Description:** Set up Python FastAPI backend with virtual environment and basic dependencies
**Expected Outcome:** FastAPI server running on localhost:8000 with health check endpoint

**Deliverables:**
- `requirements.txt` with core dependencies
- Virtual environment setup instructions
- Basic FastAPI app with `/health` endpoint
- Environment variables setup with `.env.example`
- Docker setup (optional but recommended)

**Verification:** `curl http://localhost:8000/health` returns 200 OK

#### Task F1.3 - Frontend Environment Setup [Vishal]
**Tag:** `setup`, `frontend`
**Description:** Set up Next.js frontend with TypeScript and basic configuration
**Expected Outcome:** Next.js app running on localhost:3000 with basic routing

**Deliverables:**
- Next.js app with TypeScript configuration
- Basic folder structure (`components/`, `pages/`, `utils/`)
- Tailwind CSS setup for styling
- Basic layout component
- Environment variables setup

**Verification:** `npm run dev` starts the app successfully on localhost:3000

#### Task F1.4 - Database Setup [Aravind]
**Tag:** `setup`, `database`
**Description:** Set up PostgreSQL database with initial schema and connection
**Expected Outcome:** Database running locally with all tables created

**Deliverables:**
- PostgreSQL database running locally
- Database schema implementation (all tables from mvp_db_schema.md)
- Database connection utility in FastAPI
- Migration system setup (Alembic)
- Sample data insertion script

**Verification:** All tables exist and can be queried, FastAPI can connect to database

#### Task F1.5 - Google OAuth Setup [Vishal]
**Tag:** `setup`, `auth`
**Description:** Set up Google Cloud project and OAuth credentials
**Expected Outcome:** Google OAuth credentials ready for both development and production

**Deliverables:**
- Google Cloud project created
- OAuth 2.0 client credentials configured
- Redirect URIs set up for localhost and production
- Environment variables documented
- OAuth flow documentation

**Verification:** OAuth credentials can be used to authenticate with Google API

---

### PHASE 2: CORE BACKEND API

#### Task B2.1 - Authentication System [Aravind]
**Tag:** `backend`, `auth`
**Description:** Implement JWT-based authentication with Google OAuth
**Expected Outcome:** Complete authentication system with token management

**Deliverables:**
- JWT token generation and validation
- Google OAuth token verification
- User creation/retrieval on OAuth success
- `/auth/google` and `/auth/refresh` endpoints
- Middleware for protected routes
- User session management

**Verification:** Can authenticate with Google and receive JWT tokens

#### Task B2.2 - User Management API [Vishal]
**Tag:** `backend`, `users`
**Description:** Implement user-related endpoints for profile management
**Expected Outcome:** Complete user CRUD operations and profile management

**Deliverables:**
- `/users/me` endpoint (GET, PATCH)
- `/users/{user_id}` endpoint (GET)
- User profile update functionality
- Input validation and sanitization
- Error handling

**Verification:** User profile can be retrieved and updated via API

#### Task B2.3 - Database Models [Aravind]
**Tag:** `backend`, `database`
**Description:** Implement SQLAlchemy models for all database tables
**Expected Outcome:** Complete ORM models with relationships

**Deliverables:**
- SQLAlchemy models for all tables
- Proper relationships and foreign keys
- Database utility functions
- CRUD operations for each model
- Database session management

**Verification:** All models can perform CRUD operations without errors

#### Task B2.4 - Conversation API [Vishal]
**Tag:** `backend`, `conversations`
**Description:** Implement conversation management endpoints
**Expected Outcome:** Users can create and manage conversations

**Deliverables:**
- `/conversations` endpoints (GET, POST)
- `/conversations/{id}` endpoints (GET, DELETE)
- Conversation-message relationship handling
- Pagination implementation
- Input validation

**Verification:** Conversations can be created, retrieved, and managed via API

#### Task B2.5 - Message API [Aravind]
**Tag:** `backend`, `messages`
**Description:** Implement message management within conversations
**Expected Outcome:** Messages can be stored and retrieved with proper relationships

**Deliverables:**
- Message creation and retrieval
- Message-conversation relationship
- Role-based messages (user, assistant, system)
- Blog message flagging
- Message ordering and pagination

**Verification:** Messages can be added to conversations and retrieved in order

---

### PHASE 3: FRONTEND CORE

#### Task F3.1 - Authentication UI [Vishal]
**Tag:** `frontend`, `auth`
**Description:** Implement Google OAuth login flow and authentication state management
**Expected Outcome:** Complete authentication UI with session management

**Deliverables:**
- Google OAuth login button and flow
- JWT token storage and management
- Authentication state context/provider
- Login/logout functionality
- Protected route component
- User profile display

**Verification:** Users can log in with Google and access protected pages

#### Task F3.2 - Navigation and Layout [Aravind]
**Tag:** `frontend`, `layout`
**Description:** Create main navigation and layout components
**Expected Outcome:** Consistent navigation and layout across the app

**Deliverables:**
- Main navigation component
- Layout wrapper component
- Responsive design for mobile/desktop
- Navigation state management
- User menu with profile/logout options
- Loading states

**Verification:** Navigation works correctly and layout is responsive

#### Task F3.3 - User Profile Pages [Vishal]
**Tag:** `frontend`, `users`
**Description:** Create user profile viewing and editing pages
**Expected Outcome:** Users can view and edit their profiles

**Deliverables:**
- User profile page component
- Profile editing form
- Image upload handling (profile pictures)
- Form validation
- Error handling and loading states
- Public profile view

**Verification:** User can view and update their profile information

#### Task F3.4 - API Client Setup [Aravind]
**Tag:** `frontend`, `api`
**Description:** Set up API client with proper error handling and interceptors
**Expected Outcome:** Centralized API communication with proper error handling

**Deliverables:**
- Axios/fetch wrapper with base configuration
- Request/response interceptors
- Token management integration
- Error handling utilities
- API endpoint constants
- Response type definitions

**Verification:** API calls work correctly with proper error handling

#### Task F3.5 - Basic Components Library [Vishal]
**Tag:** `frontend`, `components`
**Description:** Create reusable UI components for the application
**Expected Outcome:** Consistent UI components library

**Deliverables:**
- Button component with variants
- Input/textarea components
- Modal component
- Loading spinner component
- Toast notification component
- Card component for posts/conversations

**Verification:** Components render correctly and are reusable

---

### PHASE 4: AI INTEGRATION

#### Task A4.1 - LangChain Setup [Aravind]
**Tag:** `backend`, `ai`
**Description:** Set up LangChain with Google Gemini integration
**Expected Outcome:** AI service ready for conversation handling

**Deliverables:**
- LangChain configuration with Gemini
- Conversation memory management
- AI response generation service
- Error handling for AI failures
- Token usage tracking
- Response streaming setup

**Verification:** AI can generate responses to user messages

#### Task A4.2 - AI Conversation Endpoints [Vishal]
**Tag:** `backend`, `ai`
**Description:** Implement AI conversation endpoints with proper integration
**Expected Outcome:** Users can send messages and receive AI responses

**Deliverables:**
- `/conversations/{id}/messages` POST endpoint
- AI response generation and storage
- Conversation context management
- Rate limiting for AI requests
- Error handling for AI failures
- Message validation

**Verification:** Users can send messages and receive AI responses

#### Task A4.3 - Blog Generation API [Aravind]
**Tag:** `backend`, `ai`
**Description:** Implement blog post generation from conversations
**Expected Outcome:** AI can generate blog posts from conversation context

**Deliverables:**
- `/conversations/{id}/generate-blog` endpoint
- Blog content generation logic
- Blog message creation and flagging
- Quality validation of generated content
- Error handling and retries
- Blog formatting utilities

**Verification:** Blog posts can be generated from conversation context

#### Task A4.4 - WebSocket Implementation [Vishal]
**Tag:** `backend`, `realtime`
**Description:** Implement WebSocket for real-time AI conversation streaming
**Expected Outcome:** Real-time streaming of AI responses

**Deliverables:**
- WebSocket endpoint setup
- Token authentication for WebSocket
- Message streaming implementation
- Connection management
- Error handling for disconnections
- Message queuing for offline users

**Verification:** AI responses stream in real-time via WebSocket

#### Task A4.5 - AI Chat Frontend [Aravind]
**Tag:** `frontend`, `ai`
**Description:** Create the AI conversation interface with real-time updates
**Expected Outcome:** Interactive AI chat interface

**Deliverables:**
- Chat interface component
- Message list with proper styling
- Message input with sending states
- WebSocket connection management
- Real-time message updates
- Typing indicators and loading states

**Verification:** Users can chat with AI in real-time

---

### PHASE 5: REAL-TIME FEATURES

#### Task R5.1 - WebSocket Client [Vishal]
**Tag:** `frontend`, `realtime`
**Description:** Implement WebSocket client with proper connection management
**Expected Outcome:** Stable WebSocket connection with reconnection logic

**Deliverables:**
- WebSocket client utility
- Connection state management
- Automatic reconnection logic
- Message queuing for failed sends
- Connection status indicators
- Error handling for connection failures

**Verification:** WebSocket maintains stable connection with proper error handling

#### Task R5.2 - Real-time Message UI [Aravind]
**Tag:** `frontend`, `realtime`
**Description:** Create UI components for real-time message display
**Expected Outcome:** Messages appear in real-time with proper animations

**Deliverables:**
- Message bubble components
- Streaming text animation
- Message status indicators
- Scroll management for new messages
- Optimistic UI updates
- Message retry functionality

**Verification:** Messages appear and update in real-time with smooth animations

---

### PHASE 6: SOCIAL FEATURES

#### Task S6.1 - Posts API [Vishal]
**Tag:** `backend`, `posts`
**Description:** Implement post creation and management endpoints
**Expected Outcome:** Complete post CRUD operations

**Deliverables:**
- `/posts` endpoints (GET, POST)
- `/posts/{id}` endpoints (GET)
- Post creation from conversations
- Post visibility settings
- Tag management for posts
- Pagination and filtering

**Verification:** Posts can be created, retrieved, and managed

#### Task S6.2 - Social Interactions API [Aravind]
**Tag:** `backend`, `social`
**Description:** Implement likes, follows, and comment endpoints
**Expected Outcome:** Complete social interaction system

**Deliverables:**
- Follow/unfollow endpoints
- Like/dislike endpoints
- Comment CRUD endpoints
- Reaction system for posts/comments
- View tracking
- Share tracking

**Verification:** Users can follow, like, comment, and share posts

#### Task S6.3 - Posts Frontend [Vishal]
**Tag:** `frontend`, `posts`
**Description:** Create post display and creation interfaces
**Expected Outcome:** Users can view and create posts

**Deliverables:**
- Post list component
- Individual post component
- Post creation form
- Tag selection interface
- Post actions (like, share, expand)
- Post filtering and search

**Verification:** Users can view, create, and interact with posts

#### Task S6.4 - Social Features Frontend [Aravind]
**Tag:** `frontend`, `social`
**Description:** Implement social interaction interfaces
**Expected Outcome:** Complete social features UI

**Deliverables:**
- Follow/unfollow buttons
- Like/dislike buttons with counts
- Comment section with replies
- User lists (followers, following)
- Activity indicators
- Social stats display

**Verification:** Users can follow others and interact with posts

#### Task S6.5 - Fork/Expand Feature [Vishal]
**Tag:** `backend`, `expansion`
**Description:** Implement post forking and expansion functionality
**Expected Outcome:** Users can fork posts to create new conversations

**Deliverables:**
- `/posts/{id}/expand` endpoint
- `/conversations/{id}/include-original` endpoint
- Fork relationship management
- Original conversation inclusion logic
- Conversation context preservation
- Access control for conversation viewing

**Verification:** Users can fork posts and continue conversations

#### Task S6.6 - Fork/Expand Frontend [Aravind]
**Tag:** `frontend`, `expansion`
**Description:** Create UI for post forking and expansion
**Expected Outcome:** Users can easily fork and expand posts

**Deliverables:**
- Expand post button and modal
- Fork conversation interface
- Original conversation display
- Fork relationship indicators
- Conversation navigation
- Fork history display

**Verification:** Users can fork posts and navigate between related conversations

---

### PHASE 7: POLISH & TESTING

#### Task P7.1 - Backend Testing [Vishal]
**Tag:** `testing`, `backend`
**Description:** Implement comprehensive backend testing suite
**Expected Outcome:** High test coverage for all backend functionality

**Deliverables:**
- Unit tests for all API endpoints
- Integration tests for database operations
- Authentication testing
- AI integration testing
- Test fixtures and utilities
- CI/CD pipeline setup

**Verification:** All tests pass and coverage is >80%

#### Task P7.2 - Frontend Testing [Aravind]
**Tag:** `testing`, `frontend`
**Description:** Implement frontend testing with Jest and React Testing Library
**Expected Outcome:** Comprehensive frontend test coverage

**Deliverables:**
- Component unit tests
- Integration tests for user flows
- API mocking for tests
- User interaction testing
- Accessibility testing
- Performance testing

**Verification:** All tests pass and components work correctly

#### Task P7.3 - Error Handling & Validation [Vishal]
**Tag:** `quality`, `backend`
**Description:** Implement comprehensive error handling and input validation
**Expected Outcome:** Robust error handling throughout the application

**Deliverables:**
- Input validation for all endpoints
- Proper error responses with codes
- Rate limiting implementation
- Security headers and CORS
- Logging and monitoring setup
- Data sanitization

**Verification:** Application handles errors gracefully and securely

#### Task P7.4 - UI/UX Polish [Aravind]
**Tag:** `quality`, `frontend`
**Description:** Polish the user interface and improve user experience
**Expected Outcome:** Professional, accessible, and responsive UI

**Deliverables:**
- Responsive design for all screen sizes
- Loading states and error boundaries
- Accessibility improvements (ARIA labels, keyboard navigation)
- Performance optimizations
- SEO meta tags
- Dark/light mode toggle

**Verification:** UI works well on all devices and passes accessibility audits

#### Task P7.5 - Documentation & Deployment [Both]
**Tag:** `deployment`, `documentation`
**Description:** Create deployment setup and comprehensive documentation
**Expected Outcome:** Application ready for production deployment

**Deliverables:**
- Deployment configuration (Docker, environment setup)
- API documentation (OpenAPI/Swagger)
- User guide and developer documentation
- Environment variable documentation
- Database migration scripts
- Production deployment checklist

**Verification:** Application can be deployed to production environment

---

## Git Workflow Best Practices

### Branch Strategy
- `main` branch: Production-ready code
- `develop` branch: Integration branch for features
- Feature branches: `feature/task-id-description`
- Bug fix branches: `bugfix/issue-description`

### Commit Guidelines
- Use conventional commits: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Example: `feat(auth): implement Google OAuth login`

### Pull Request Process
1. Create feature branch from `develop`
2. Implement feature with tests
3. Create PR to `develop` with clear description
4. Code review by the other engineer
5. Merge after approval and CI passes

### Code Review Checklist
- [ ] Code follows project conventions
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No sensitive information in code
- [ ] Performance considerations addressed

---

## Testing Strategy

### Backend Testing (pytest)
- **Unit Tests**: Individual functions and classes
- **Integration Tests**: API endpoints with database
- **Authentication Tests**: JWT and OAuth flows
- **AI Integration Tests**: Mocked AI responses

### Frontend Testing (Jest + React Testing Library)
- **Component Tests**: Individual component rendering
- **Integration Tests**: User interaction flows
- **API Tests**: Mocked API calls
- **Accessibility Tests**: Screen reader compatibility

### Test Data Management
- Use factories for creating test data
- Clean database between tests
- Mock external services (AI, OAuth)
- Environment-specific test configurations

---

## Development Guidelines

### Code Quality Standards
- **Python**: Follow PEP 8, use type hints, docstrings
- **TypeScript**: Strict mode, proper typing, JSDoc comments
- **Both**: Meaningful variable names, small functions, DRY principle

### Security Considerations
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection
- Rate limiting
- Secure headers

### Performance Guidelines
- Database query optimization
- Frontend bundle optimization
- Image optimization
- Caching strategies
- Lazy loading

---

## APPENDIX: Reading Materials & References

### A1. FastAPI Fundamentals
**Why FastAPI:** Modern, fast Python web framework with automatic API documentation and async support.

**Essential Reading:**
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/) - Complete official tutorial
- [Python Type Hints](https://docs.python.org/3/library/typing.html) - Required for FastAPI
- [Pydantic Models](https://pydantic-docs.helpmanual.io/) - Data validation in FastAPI

**Key Concepts:**
- Automatic API documentation with OpenAPI
- Dependency injection system
- Request/response models with Pydantic
- Async/await for better performance

### A2. PostgreSQL & SQLAlchemy
**Why PostgreSQL:** Reliable, feature-rich relational database with excellent Python support.

**Essential Reading:**
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)
- [PostgreSQL Tutorial](https://www.postgresql.org/docs/current/tutorial.html)
- [Alembic Migration Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

**Key Concepts:**
- ORM vs raw SQL
- Database relationships and foreign keys
- Migration management
- Connection pooling

### A3. Next.js & React
**Why Next.js:** React framework with built-in optimizations, routing, and SSR capabilities.

**Essential Reading:**
- [Next.js Learn Course](https://nextjs.org/learn) - Interactive tutorial
- [React Hooks Guide](https://reactjs.org/docs/hooks-intro.html)
- [TypeScript with React](https://react-typescript-cheatsheet.netlify.app/)

**Key Concepts:**
- Server-side rendering vs client-side rendering
- React hooks for state management
- Component composition patterns
- Routing in Next.js

### A4. Authentication & Security
**Why JWT + OAuth:** Industry-standard secure authentication without server-side sessions.

**Essential Reading:**
- [JWT.io Introduction](https://jwt.io/introduction/)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [OWASP Web Security](https://owasp.org/www-project-top-ten/)

**Key Concepts:**
- Stateless authentication
- Token refresh strategies
- OAuth 2.0 flow
- Security headers and CORS

### A5. WebSocket & Real-time
**Why WebSocket:** Enables real-time bidirectional communication for chat features.

**Essential Reading:**
- [WebSocket MDN Guide](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)
- [Real-time App Patterns](https://blog.pusher.com/websockets-from-scratch/)

**Key Concepts:**
- WebSocket vs HTTP
- Connection management
- Message queuing
- Reconnection strategies

### A6. AI Integration (LangChain + Gemini)
**Why LangChain:** Framework for building AI applications with conversation memory and flexibility.

**Essential Reading:**
- [LangChain Quickstart](https://python.langchain.com/docs/get_started/quickstart)
- [Google Gemini API Guide](https://ai.google.dev/docs)
- [Conversation Memory](https://python.langchain.com/docs/modules/memory/)

**Key Concepts:**
- Language model chains
- Conversation memory management
- Streaming responses
- Token usage optimization

### A7. Testing Best Practices
**Why Testing:** Ensures code reliability and enables confident refactoring.

**Essential Reading:**
- [pytest Documentation](https://docs.pytest.org/en/stable/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Test-Driven Development](https://www.obeythetestinggoat.com/)

**Key Concepts:**
- Unit vs integration vs end-to-end testing
- Test fixtures and mocking
- Continuous integration
- Test coverage metrics

### A8. Git & Collaboration
**Why Git Flow:** Structured approach to code collaboration and version control.

**Essential Reading:**
- [Git Flow Guide](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Code Review Best Practices](https://google.github.io/eng-practices/review/)

**Key Concepts:**
- Branching strategies
- Merge vs rebase
- Code review process
- Continuous integration/deployment

### A9. Database Design Principles
**Why Normalization:** Ensures data integrity and efficient querying.

**Essential Reading:**
- [Database Normalization](https://en.wikipedia.org/wiki/Database_normalization)
- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Database Indexing Explained](https://use-the-index-luke.com/)

**Key Concepts:**
- ACID properties
- Primary and foreign keys
- Index optimization
- Query performance

### A10. API Design Principles
**Why RESTful APIs:** Standardized, stateless communication between frontend and backend.

**Essential Reading:**
- [REST API Design Guide](https://restfulapi.net/)
- [HTTP Status Codes](https://httpstatuses.com/)
- [API Versioning Strategies](https://restfulapi.net/versioning/)

**Key Concepts:**
- Resource-based URLs
- HTTP methods and status codes
- Pagination and filtering
- Error handling patterns

---

## Quick Reference Commands

### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest

# Database migrations
alembic upgrade head
```

### Frontend Setup
```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

### Database Commands
```bash
# Connect to PostgreSQL
psql -U username -d database_name

# Create database
createdb aikya_db

# Run migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

This implementation guide provides a comprehensive roadmap for building the AIkya MVP with clear task distribution, deliverables, and learning resources. Each task is designed to be completed in 1-3 days by a single engineer, with proper verification criteria to ensure quality and progress tracking.