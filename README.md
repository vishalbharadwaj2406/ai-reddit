# AI Social

Social media platform combining AI-assisted content creation with threaded discussions.

## Overview

We present a social platform that transforms how content is created and discussed through AI conversation forking. Users develop ideas via interactive AI dialogue, then publish posts that can spawn new conversation threads while preserving full context and discussion lineage.

Our implementation introduces post forking with conversation lineage tracking, AI-based content development workflows, and a conversation-to-content pipeline that bridges private AI interaction with public community discussion.

### Features

- **AI Conversations**: Real-time chat interface with AI for content development
- **Post Forking**: Create new AI conversation threads from existing posts with context preservation
- **Reaction System**: Upvote, downvote, heart, insightful, and accurate reactions
- **Privacy Controls**: User privacy settings and conversation visibility management
- **Threaded Comments**: Nested comment system for discussions
- **Content Organization**: Tag-based categorization and filtering

## Technical Architecture

### Backend
- **Framework**: FastAPI with SQLAlchemy 2.0 ORM
- **Database**: PostgreSQL with 13 normalized tables
- **Authentication**: Google OAuth 2.0 + JWT token management
- **AI Integration**: LangChain + Google Gemini 2.5 Flash with streaming responses
- **API Design**: RESTful with OpenAPI documentation and SSE streaming

### Frontend
- **Framework**: Next.js 15 with App Router and TypeScript
- **Styling**: Tailwind CSS 4 with custom glass morphism design system
- **Authentication**: NextAuth v5 with Google OAuth integration
- **State Management**: React Context with optimistic updates
- **Real-time**: Server-Sent Events for AI conversation streaming

### Database Design
- **13 Production Tables**: Users, conversations, posts, comments, reactions, follows, tags
- **Scalable Architecture**: UUID primary keys, proper indexing, soft deletion
- **Relationship Modeling**: Many-to-many joins, foreign key constraints
- **Migration System**: Alembic for version-controlled schema changes

## Development Status

### Implementation Complete
- **Database Layer**: 13 tables implemented with 181 passing tests
- **Authentication**: Google OAuth + JWT implementation
- **AI Service**: LangChain + Gemini integration with streaming responses
- **API Foundation**: User management and social features
- **Frontend**: Next.js application with glass morphism design
- **Health Monitoring**: Database connectivity and system health endpoints

### Current Development
- **Content Management API**: Post creation, forking, and comment systems
- **Frontend Integration**: API connection and real-time features
- **Content Discovery**: Tag-based filtering and search

### Future Work
- Multi-user conversations and collaborative features
- Advanced content discovery with semantic search
- AI-generated content feedback and scoring
- Enhanced privacy and content moderation

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 17+
- Google API credentials for OAuth and Gemini

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Configure .env with database and API credentials
pytest tests/ -v  # Run test suite (181 tests)
uvicorn app.main:app --reload  # Start development server
```

### Frontend Setup
```bash
cd frontend/website
npm install
# Configure .env.local with authentication credentials
npm run dev  # Start development server
```

### Database Setup
- PostgreSQL database hosted on Supabase
- Run migrations: `alembic upgrade head`
- Verify setup: `pytest tests/test_database.py -v`

## API Documentation

Interactive API documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Key API features:
- JWT-based authentication with Google OAuth
- Server-Sent Events for real-time AI conversations
- RESTful endpoints with comprehensive validation
- Rate limiting and security controls

## Technical Highlights

### AI Integration
- **Streaming Responses**: Real-time conversation implementation using Server-Sent Events
- **Context Preservation**: Full conversation history maintained across post forks
- **Provider Abstraction**: LangChain framework enables model switching
- **Error Handling**: Comprehensive error handling and fallback strategies

### Data Architecture
- **Conversation-Centric Design**: Posts derived from AI conversations, maintaining context and enabling exploration pathways
- **Forking System**: Post expansion preserves conversation lineage, creating branching discussion trees
- **Context Preservation**: Full conversation history maintained across forks, enabling deep contextual exploration
- **Privacy Controls**: Granular visibility settings for users and conversations
- **Scalable Foundation**: UUID keys, proper indexing, soft deletion patterns

### Frontend Implementation
- **Glass Morphism UI**: Custom design system with backdrop-filter effects
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Type Safety**: Full TypeScript implementation with strict checking
- **Performance**: Optimized bundle splitting and lazy loading

## Repository Structure

```
├── backend/           # FastAPI application
│   ├── app/          # Application code
│   ├── tests/        # Test suite (181 tests)
│   └── alembic/      # Database migrations
├── frontend/         # Next.js application
│   └── website/      # Main web application
└── docs/            # Technical documentation
    ├── api/         # API specifications
    ├── database/    # Schema documentation
    └── architecture/ # System design
```

## Testing

- **Backend**: 181 comprehensive tests with pytest
- **Database**: Full model and relationship testing
- **API**: Endpoint validation and error handling
