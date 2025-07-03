# AI Social MVP - Progress Log

## Project Overview
**Goal:** Build a powerful portfolio project for SOFTWARE ENGINEERING roles (backend/AI focus)
**Timeline:** 1.5 months, 2 engineers
**Core Concept:** Real-time AI conversation platform that transforms private chats into discoverable social content

## Key Decisions Made

### Target Audience & Positioning
- **Primary Target:** Backend/AI engineering roles (NOT frontend/product roles)
- **Approach:** Build a quality, usable product first, then tailor narrative to specific job applications
- **Portfolio Narrative:** Focus on technical excellence over frontend polish

### Technical Focus Areas
- **Primary:** WebSocket streaming, AI integration, scalable backend architecture
- **Secondary:** Database design, API architecture, real-time systems
- **Frontend:** Attractive and professional, but not overly complex features

### Scope Decisions
- **Full System Design:** Design for social features upfront (database, API) but implement incrementally
- **MVP Features:** AI chat + WebSocket streaming + basic social posting + simple feed
- **Deferred:** Advanced feed ranking, user discovery, detailed analytics

### Architecture Philosophy
- **Quality Over Speed:** Real performance metrics, production-level code
- **Scalable Patterns:** Design patterns that could actually scale
- **Technical Depth:** Focus on hard problems that demonstrate engineering competence

### API Design Decisions Made
- **WebSocket + REST Hybrid:** WebSocket for AI streaming, REST for CRUD operations
- **JWT Authentication:** Bearer tokens for all protected routes
- **Gemini Integration:** Real-time streaming with generate_content_stream()
- **Message Ordering:** Auto-incrementing IDs for chronological conversation replay
- **Error Handling:** Proper HTTP status codes and WebSocket close codes
- **Conversation Forking:** Copy-on-fork approach for data isolation

## Current Status
- **Completed:** 
  - Project planning, scope definition, target role clarification
  - Database schema design (5 tables locked and approved)
  - Core API architecture design (3 key endpoints designed)
  - WebSocket streaming approach defined
  - Authentication strategy (JWT) established
- **In Progress:** API design completion (core endpoints done, need publish/social endpoints)
- **Next Steps:** 
  1. Complete remaining API endpoints (POST /conversations/{id}/summaries, POST /posts)
  2. Begin FastAPI implementation starting with WebSocket streaming
  3. Set up development environment and project structure
  4. Implement core conversation flow (create → stream → save messages)

## Technical Stack (Planned)
- **Backend:** FastAPI + PostgreSQL + Redis
- **Frontend:** React + Next.js + Tailwind CSS
- **AI:** Gemini Python SDK with streaming (switched from OpenAI)
- **Auth:** JWT tokens
- **Deployment:** Railway/Render (backend) + Vercel (frontend)

## Interview Talking Points to Develop
- **WebSocket Architecture:** Connection management, streaming implementation, error handling and reconnection
- **AI Integration:** Gemini streaming API, conversation context preservation, real-time response handling
- **Database Design:** Message ordering strategies, conversation forking architecture, social graph modeling
- **API Design:** RESTful patterns, async/await optimization, authentication flow
- **Real-time Systems:** WebSocket vs REST trade-offs, connection pooling, message ordering
- **Error Handling:** WebSocket close codes, graceful degradation, AI service failure recovery

## Technical Decisions Documented

### Database Schema (LOCKED)
- 5 tables: users, conversations, messages, posts, follows
- Auto-incrementing message IDs for ordering
- Conversation forking with copy-on-fork strategy
- Simple comma-separated tags for MVP

### API Endpoints Designed
1. **POST /conversations** - Create new conversation
2. **WebSocket /conversations/{id}/stream** - Real-time AI chat with streaming
3. **GET /conversations/{id}/messages** - Paginated message history

### Streaming Architecture
- Gemini `generate_content_stream()` for real-time responses
- WebSocket message types: user_message, ai_start, ai_chunk, ai_complete
- JWT authentication over WebSocket
- Background title auto-update after first exchange

## Notes
- User has no intention to apply for product engineer or frontend-focused roles
- Emphasis should be on backend technical challenges and AI integration
- Frontend needs to be functional but backend needs to be production-quality
- Switched from OpenAI to Gemini for streaming implementation

## Next Session Goals
- Complete remaining API endpoints (POST /conversations/{id}/summaries, POST /posts, GET /feed)
- Set up FastAPI project structure with proper async patterns
- Begin implementation with the hardest piece: WebSocket streaming with Gemini integration
- Implement conversation creation and message persistence