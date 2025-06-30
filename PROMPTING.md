# Cursor AI Prompting Guide: AI Social Platform (FastAPI + React)

**Building a minimal text-based AI Reddit with FastAPI backend and React frontend**

---

## 📋 Project Context (Share this with Claude first)

```markdown
PROJECT: AI Social - Minimal Text-Based AI Reddit
CONCEPT: Users have conversations with AI, generate summaries, share in social feed
ARCHITECTURE: FastAPI (Python backend) + Next.js (React frontend)
SCOPE: Weekend MVP with two-phase development

PHASE 1 (Weekend 1): FastAPI Backend
- User authentication (JWT)
- Database models (SQLAlchemy)
- AI chat integration (OpenAI SDK)
- Complete API endpoints
- Backend deployment

PHASE 2 (Weekend 2): React Frontend  
- Next.js with TypeScript
- Chat interface with real-time streaming
- Social feed and content discovery
- Creator dashboard and profiles
- Frontend deployment

KEY FEATURES:
1. AI conversation interface with streaming responses
2. AI summary generation from conversations
3. Social feed with expandable content
4. Creator content management
5. User profiles and follow system

USER FLOWS:
- Producer: Chat → Generate Summary → Edit → Publish → Manage Content
- Consumer: Browse Feed → Filter Content → Preview → Expand Full Conversation → Follow Creators

TECH STACK:
- Backend: FastAPI + SQLAlchemy + PostgreSQL + OpenAI SDK
- Frontend: Next.js + TypeScript + Tailwind CSS + Axios
- Deploy: Railway/Render (backend) + Vercel (frontend)

DEVELOPER CONTEXT:
- Strong Python/FastAPI experience
- Learning React/JavaScript (beginner level)
- Familiar with databases and API design
```

---

## 🚀 Phase 1: FastAPI Backend Development

### Step 1: FastAPI Project Setup & Structure

**Prompt:**
```
I'm building the backend for "AI Social" - a platform where users chat with AI and share conversation summaries.

Please help me set up a FastAPI project with this structure:
1. FastAPI app with SQLAlchemy and PostgreSQL
2. Project structure for a social media API
3. Environment setup and dependencies
4. Basic configuration and database connection

Requirements:
- FastAPI with async support
- SQLAlchemy ORM with PostgreSQL
- Pydantic for validation
- JWT authentication
- OpenAI integration
- Alembic for migrations

Please provide:
1. Complete requirements.txt
2. Project folder structure
3. Basic FastAPI app setup
4. Database configuration
5. Environment variables template

Make it production-ready but simple to start with.
```

**Expected Output:**
- requirements.txt with all dependencies
- Organized project structure (/app, /models, /api, etc.)
- main.py with FastAPI app initialization
- Database connection setup
- .env template with required variables

**Success Criteria:** `uvicorn main:app --reload` starts server successfully

---

### Step 2: Database Models & Authentication

**Prompt:**
```
Create the database models and authentication system for AI Social.

Core entities needed:
- User (authentication + profile)
- Post (AI conversation summaries)
- Follow (user relationships)  
- PostTag (content categorization)

Requirements:
- SQLAlchemy models with proper relationships
- Pydantic schemas for API validation
- JWT-based authentication system
- Password hashing with passlib
- Database migration setup with Alembic

Database features:
- Users can create posts from AI conversations
- Posts store both summary and full conversation JSON
- Users can follow other users
- Posts can be tagged with topics
- Track analytics (view_count, expansion_count)

Please create:
1. Complete SQLAlchemy models with relationships
2. Pydantic schemas for request/response validation
3. JWT authentication utilities
4. Password hashing functions
5. Alembic migration setup
6. Database initialization

Keep relationships efficient for social media queries.
```

**Expected Output:**
- models.py with User, Post, Follow, PostTag models
- schemas.py with Pydantic validation models
- auth.py with JWT and password utilities
- Initial Alembic migration
- Database table creation scripts

**Success Criteria:** Database migrates successfully with all relationships

---

### Step 3: AI Integration & Core APIs

**Prompt:**
```
Implement AI chat integration and core API endpoints for AI Social.

Features needed:
1. OpenAI chat integration with streaming support
2. AI conversation summarization
3. User authentication endpoints
4. Post CRUD operations
5. Conversation storage and retrieval

AI Integration Requirements:
- Stream chat responses using OpenAI SDK
- Generate summaries from conversation history
- Store full conversations as JSON
- Handle API rate limits and errors

API Endpoints needed:
- POST /auth/register - User registration
- POST /auth/login - User login  
- POST /chat/message - Send message to AI
- POST /chat/summarize - Generate summary from conversation
- GET/POST /posts - List and create posts
- GET /posts/{id}/expand - Get full conversation

Please create:
1. OpenAI integration with streaming
2. Authentication endpoints with JWT
3. Chat endpoints with conversation management
4. Post management endpoints
5. Error handling and validation
6. API response formatting

Focus on clean, async code with proper error handling.
```

**Expected Output:**
- AI integration with streaming chat
- Complete authentication system
- Chat and summarization endpoints
- Post CRUD operations
- Error handling middleware
- Response formatting utilities

**Success Criteria:** Can chat with AI, generate summaries, and create posts via API

---

### Step 4: Social Features & Feed Generation

**Prompt:**
```
Build the social features and content discovery for AI Social.

Social Features:
1. Follow/unfollow system
2. Feed generation algorithm
3. Content filtering and search
4. User profiles and statistics
5. Content analytics tracking

Feed Algorithm (simple but effective):
- Show posts from followed users (chronological)
- Mix in popular posts from unfollowed users
- Filter by topics/tags when requested
- Track engagement for ranking

API Endpoints needed:
- POST /users/{id}/follow - Follow a user
- DELETE /users/{id}/follow - Unfollow a user
- GET /feed - Personalized feed
- GET /discover - Discovery feed
- GET /users/{id}/profile - User profile
- GET /posts/search - Search posts
- POST /posts/{id}/view - Track view
- POST /posts/{id}/expand - Track expansion

Please create:
1. Follow/unfollow system
2. Feed generation with basic algorithm
3. Search and filtering functionality
4. User profile endpoints
5. Analytics tracking
6. Performance optimization for feed queries

Make feeds efficient with proper database queries and pagination.
```

**Expected Output:**
- Follow system implementation
- Feed generation algorithm
- Search and filtering endpoints
- User profile management
- Analytics tracking
- Optimized database queries

**Success Criteria:** Can follow users, generate personalized feeds, search content

---

### Step 5: API Documentation & Testing

**Prompt:**
```
Complete the FastAPI backend with documentation, testing, and production setup.

Tasks needed:
1. Comprehensive API documentation
2. Basic testing for critical endpoints
3. Production configuration
4. Error handling and logging
5. Security hardening
6. Deployment preparation

Requirements:
- Auto-generated OpenAPI docs
- Basic test coverage for auth and core features
- Production database configuration
- Proper CORS setup for frontend
- Security middleware
- Logging configuration

Please create:
1. Enhanced API documentation with examples
2. Test suite for authentication and core endpoints
3. Production settings and configuration
4. CORS middleware for React frontend
5. Security enhancements (rate limiting, validation)
6. Deployment scripts and documentation

Focus on making this production-ready and easy to debug.
```

**Expected Output:**
- Complete API documentation
- Test suite with key endpoint coverage
- Production configuration
- Security middleware
- CORS setup for frontend
- Deployment preparation

**Success Criteria:** Backend is documented, tested, and ready for production deployment

---

## 🚀 Phase 2: React Frontend Development

### Step 6: Next.js Setup & Authentication UI

**Prompt:**
```
I'm a Python developer learning React to build the frontend for AI Social. I have a working FastAPI backend.

Please help me create a Next.js frontend with:
1. Project setup with TypeScript and Tailwind
2. Authentication UI (login/signup forms)
3. Protected routes and JWT token management
4. Basic layout and navigation
5. API integration utilities

Context: This connects to my FastAPI backend at localhost:8000

Frontend Requirements:
- Next.js 13+ with TypeScript
- Tailwind CSS for styling
- JWT token storage and management
- Protected routes for authenticated users
- Clean, minimal design
- Mobile-responsive layout

Please create:
1. Next.js project setup with proper dependencies
2. Authentication forms with validation
3. JWT token management (localStorage/cookies)
4. Protected route wrapper
5. Basic layout components
6. API client utilities for FastAPI backend

Explain React concepts as we go - I'm learning!
```

**Expected Output:**
- Next.js project with TypeScript and Tailwind
- Login/signup forms with validation
- JWT token management system
- Protected route components
- Basic layout and navigation
- API client setup

**Success Criteria:** Users can register, login, and access protected routes

---

### Step 7: Chat Interface & AI Integration

**Prompt:**
```
Create the core chat interface for AI Social - this is where users have conversations with AI.

Requirements:
1. Real-time chat interface with message bubbles
2. Streaming AI responses from FastAPI backend
3. "Generate Summary" functionality
4. Conversation history management
5. Mobile-responsive chat design

Chat Features:
- Clean message bubble design (user vs AI messages)
- Streaming text responses (like ChatGPT)
- Message history scrolling
- Input field with send button
- Generate summary button after conversation
- Save conversation functionality

I'm new to React, so please:
1. Explain component structure and state management
2. Show how to handle real-time updates
3. Demonstrate API integration patterns
4. Include error handling and loading states

Connect to my FastAPI endpoints:
- POST /chat/message - Send message and get AI response
- POST /chat/summarize - Generate summary from conversation

Please create functional, clean chat UI with modern design.
```

**Expected Output:**
- Chat interface component with message bubbles
- Real-time streaming integration
- Conversation state management
- Summary generation UI
- Mobile-responsive design
- Error handling and loading states

**Success Criteria:** Users can chat with AI and generate summaries

---

### Step 8: Social Feed & Content Discovery

**Prompt:**
```
Build the social feed where users discover and consume AI-generated content.

Requirements:
1. Card-based feed layout showing post summaries
2. "Expand to Full Conversation" functionality
3. Follow/unfollow buttons on posts
4. Content filtering (topics, recency, popularity)
5. Infinite scroll or pagination

Feed Features:
- Post cards with summary, author, tags, metrics
- Expandable full conversation view (modal or new page)
- Follow button with optimistic updates
- Filter dropdown for topics
- Sort options (recent, popular, most discussed)
- Engagement metrics display (views, expansions)

Please create:
1. Feed component with post cards
2. Post card component with all features
3. Full conversation modal/page
4. Filtering and sorting UI
5. Follow system integration
6. Responsive grid layout

I'm learning React patterns, so please explain:
- Component composition and reuse
- State management across components
- Event handling and user interactions
- API integration for dynamic content

Make this feel like a modern social media feed.
```

**Expected Output:**
- Social feed with card layout
- Post card components
- Conversation expansion functionality
- Filtering and sorting UI
- Follow system integration
- Responsive design

**Success Criteria:** Users can browse, filter, and engage with content

---

### Step 9: Creator Dashboard & Profile Management

**Prompt:**
```
Create the creator dashboard and user profile pages for AI Social.

Creator Dashboard Requirements:
1. Content management (published vs draft posts)
2. Basic analytics (views, followers, engagement)
3. Post editing and publishing workflow
4. Profile settings management
5. Clean, functional design

User Profile Pages:
1. Public profile showing user's posts
2. Bio, stats, and social information
3. Follow/unfollow functionality
4. Content filtering for user's posts
5. SEO-friendly URLs

Please create:
1. Creator dashboard with stats overview
2. Post management interface
3. Public profile page component
4. Profile editing forms
5. Navigation between different views
6. Mobile-responsive layouts

Dashboard Features:
- Stats cards (follower count, post count, total views)
- Post list with edit/delete actions
- Draft vs published post tabs
- Simple analytics visualization
- Profile management form

Profile Features:
- User bio and avatar
- Posts grid with filtering
- Follow button with state management
- Social stats display
- Clean, portfolio-like layout

Focus on essential creator and discovery features for MVP.
```

**Expected Output:**
- Creator dashboard with content management
- Post editing and publishing UI
- Public profile pages
- Profile management forms
- Analytics display components
- Mobile-responsive design

**Success Criteria:** Creators can manage content and users can discover profiles

---

### Step 10: Polish, Testing & Deployment

**Prompt:**
```
Polish the AI Social frontend for production deployment.

Tasks needed:
1. Mobile responsiveness audit and fixes
2. Loading states and error handling throughout
3. Performance optimization
4. SEO setup and meta tags
5. Production build and deployment to Vercel
6. Final testing and bug fixes

Polish Requirements:
- Smooth mobile experience on all screen sizes
- Loading spinners and skeleton screens
- Proper error boundaries and user feedback
- Fast loading times and optimized images
- SEO-friendly meta tags and URLs
- Clean code organization

Please help with:
1. Responsive design improvements
2. Loading states for all async operations
3. Error handling and user feedback
4. Performance optimization techniques
5. SEO setup with Next.js
6. Vercel deployment configuration
7. Final code cleanup and organization

Production Checklist:
- All components work on mobile
- No console errors or warnings
- Fast loading and smooth interactions
- Proper error messages for users
- SEO tags for social sharing
- Clean, maintainable code structure

Make this feel like a polished MVP worthy of a portfolio.
```

**Expected Output:**
- Mobile-responsive improvements
- Loading and error states
- Performance optimizations
- SEO configuration
- Deployment setup
- Production-ready code

**Success Criteria:** Production-ready app deployed successfully with smooth UX

---

## 🎯 Context Reminders for Each Step

### Always Mention These Context Points:
```
PROJECT GOAL: Weekend MVP showcasing FastAPI + React + AI integration
ARCHITECTURE: Separated frontend/backend for clean development
CORE CONCEPT: Chat with AI → Generate summaries → Social discovery
TARGET: Portfolio project demonstrating full-stack modern skills
SCOPE: Essential features only, clean code, production-ready
LEARNING: Teaching React to experienced Python developer
```

### Code Quality Expectations:
- **Python**: FastAPI best practices, async/await, type hints
- **React**: TypeScript, hooks, component composition
- **Database**: Efficient queries, proper relationships
- **API**: RESTful design, error handling, documentation
- **UI**: Clean design, mobile-first, accessibility

### Development Principles:
- **Backend first**: Nail the API before building frontend
- **Component thinking**: Reusable, composable React components
- **Error handling**: Graceful failures and user feedback
- **Performance**: Efficient queries and fast loading
- **Security**: Proper authentication and validation

---

## 🚨 Troubleshooting Prompts

### Backend Issues:
```
The FastAPI [feature/endpoint] isn't working as expected. Here's the error: [paste error]

Context: This is the backend for AI Social where [explain feature purpose].
Architecture: FastAPI + SQLAlchemy + PostgreSQL + OpenAI integration

Please debug and provide corrected code with explanations.
```

### Frontend Issues:
```
I'm having trouble with this React component: [describe issue]

Context: Learning React as Python developer for AI Social frontend.
Component purpose: [explain what it should do]
Backend API: [relevant endpoint details]

Please fix the issue and explain React concepts I'm missing.
```

### API Integration Issues:
```
The frontend can't connect to my FastAPI backend. Error: [paste error]

Frontend: Next.js on localhost:3000
Backend: FastAPI on localhost:8000
Issue: [CORS/authentication/data format/etc.]

Please help debug the connection between frontend and backend.
```

### Design/UX Issues:
```
The [component] doesn't look right on mobile/doesn't feel modern enough.

Context: Building AI Social - minimal, clean social media platform
Component: [describe current state]
Goal: [describe desired look/behavior]

Please improve the Tailwind CSS and React code for better UX.
```

---

## ✅ Success Checklist

### Phase 1 Completion (Backend):
- [ ] FastAPI server runs and serves docs at /docs
- [ ] Database connects and all migrations work
- [ ] Authentication (register/login) works with JWT
- [ ] Can chat with AI and get streaming responses
- [ ] AI summary generation works
- [ ] All CRUD operations for posts work
- [ ] Follow system functions correctly
- [ ] Feed generation returns relevant content
- [ ] Backend deployed and accessible

### Phase 2 Completion (Frontend):
- [ ] Next.js app builds and runs without errors
- [ ] User registration and login work
- [ ] Chat interface connects to FastAPI and streams responses
- [ ] Can generate summaries and create posts
- [ ] Social feed displays content from backend
- [ ] Can follow users and see personalized feed
- [ ] Creator dashboard manages content
- [ ] Profile pages showcase users effectively
- [ ] Mobile responsive on all screen sizes
- [ ] Frontend deployed and accessible

### Final MVP Verification:
- [ ] **End-to-End Flow**: New user can sign up → chat with AI → generate summary → publish → another user can discover and read
- [ ] **Cross-Device**: Works smoothly on desktop, tablet, and mobile
- [ ] **Performance**: Fast loading, smooth interactions
- [ ] **Error Handling**: Graceful failures with helpful messages
- [ ] **Production Ready**: No console errors, proper SEO, deployed successfully
- [ ] **Portfolio Worthy**: Clean code, modern design, impressive functionality

**Final Test**: Can you demo the complete user journey to someone without any bugs or awkward moments? If yes, your MVP is complete and ready for your portfolio!

---

**This guide ensures you build a modern, full-stack application that showcases both your Python expertise and new React skills, creating an impressive portfolio piece that demonstrates real-world development capabilities.**

---

## 🚀 Step-by-Step Prompting Guide

### Phase 1: FastAPI Backend Development (Weekend 1)
*Building the API foundation with your Python expertise*

### Phase 2: React Frontend Development (Weekend 2)  
*Learning React while building the UI layer*

---

## 🎯 Context Reminders for Each Step

### Always Mention These Context Points:
```
PROJECT GOAL: Weekend MVP showcasing AI integration + social features
TECH STACK: Next.js 14, TypeScript, Vercel AI SDK, Tailwind, PostgreSQL, Prisma
CORE CONCEPT: Chat with AI → Generate summaries → Social discovery
TARGET: Portfolio project demonstrating full-stack + AI skills
SCOPE: Essential features only, no over-engineering
```

### Code Quality Expectations:
- TypeScript throughout
- Clean component structure
- Responsive design
- Error handling
- Type safety
- Comments for complex logic

### UI/UX Principles:
- Minimal, clean design
- Mobile-first responsive
- Fast loading times
- Intuitive user flows
- Accessibility considerations

---

## 🚨 Troubleshooting Prompts

### If Code Doesn't Work:
```
The [component/feature] isn't working as expected. Here's the error: [paste error]

Context: This is part of the AI Social platform where [explain what this piece does].

Please debug and provide the corrected code with explanations of what was wrong.
```

### If Design Needs Improvement:
```
The current [component] design doesn't match the minimalist, modern aesthetic we're going for. 

Please improve the Tailwind CSS styling to make it:
1. More modern and clean
2. Better responsive design
3. Consistent with the overall app design

Reference: Think clean, modern social platforms with focus on readability.
```

### If Performance Issues:
```
The [feature] is running slowly. This is a weekend MVP that should feel snappy.

Please optimize for:
1. Faster load times
2. Better database queries
3. Efficient React rendering
4. Minimal bundle size

Keep solutions simple but effective.
```

---

## ✅ Success Checklist

After completing all steps, verify:

- [ ] Users can sign up and authenticate
- [ ] Chat interface works with AI streaming
- [ ] AI summary generation functions
- [ ] Social feed displays content properly
- [ ] Filtering and sorting work
- [ ] Follow system functions
- [ ] Creator dashboard manages content
- [ ] Profile pages showcase users
- [ ] Mobile responsive design
- [ ] Deployed successfully to Vercel

**Final Test:** Can a new user sign up, have an AI conversation, generate a summary, publish it, and have another user discover and read it? If yes, MVP is complete!

---

**This guide ensures you build a modern, full-stack application using FastAPI for the backend (your strength) and React for the frontend (new skill), creating an impressive portfolio piece that demonstrates both Python expertise and modern web development capabilities.**