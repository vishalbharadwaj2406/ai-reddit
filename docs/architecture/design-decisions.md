# [APP_NAME] MVP API Design Decisions

## 📋 Document Purpose
This document captures key design decisions, rationales, and architectural choices made during the [APP_NAME] MVP API design process. Use this as a reference for understanding **why** certain decisions were made and **how** they support the platform's unique value proposition.

---

## 🎯 Core Platform Vision & Design Philosophy

### **Platform Differentiators**
- **AI-Assisted Content Creation**: Transform thoughts into well-structured content regardless of writing skill
- **Conversation-Centric**: Posts emerge from AI conversations, not standalone creation
- **Fork-Based Exploration**: Users can "expand" posts to explore different perspectives
- **Meaningful Discourse**: Focus on depth over superficial engagement

### **MVP Design Principles**
1. **Novelty First**: Prioritize unique AI conversation features over traditional social media features
2. **Minimal Complexity**: Avoid over-engineering for MVP phase
3. **Extensible Architecture**: Design for easy future expansion
4. **Data Integrity**: Maintain conversation context and relationships

---

## 🏗️ Core Architectural Decisions

### **1. Conversation-Centric Data Model**
**Decision**: Make `conversations` the central entity, with `posts` derived from conversations
**Rationale**:
- Supports the core value proposition of AI-assisted content creation
- Maintains context between AI interactions and published content
- Enables "expand post" functionality naturally
- Allows users to continue conversations after posting

**Implementation**:
```
conversations → messages → posts
     ↓
  forked_from (posts) → enables repost/expand functionality
```

### **2. Elegant Repost Implementation**
**Decision**: Use `forked_from` field in conversations instead of separate repost endpoint
**Rationale**:
- **Single Responsibility**: One endpoint handles both expand and repost scenarios
- **Data Integrity**: Relationship maintained in database schema
- **No API Bloat**: Avoids redundant endpoints
- **Normalized Design**: Follows DRY principles

**Flow**:
```
Original Post → Expand → Conversation (forked_from: post_id) → New Post (inherits relationship)
```

### **3. Custom Blog Flow Design**
**Decision**: Empty conversations as placeholders, populate on publish
**Rationale**:
- **Efficiency**: No intermediate API calls needed
- **Simplicity**: User writes in frontend, backend handles persistence
- **Consistency**: Maintains conversation-centric model even for custom posts
- **Atomic Operations**: Both conversation and post created simultaneously

**Flow**:
```
User writes in frontend → POST /posts → Creates both conversation + post
```

### **4. Content Editing Deferred for MVP**
**Decision**: No edit/delete endpoints for posts and messages in MVP
**Rationale**:
- **MVP Scope**: Focus on core AI conversation features first
- **Development Priority**: Defer complex content management to post-MVP
- **Simplicity**: Reduces initial API complexity and edge cases
- **Faster Launch**: Enables quicker MVP validation and user feedback

**Note**: Content editing is planned for future versions - this is a scope decision, not a philosophical stance on immutability.

---

## 🔄 Real-Time & Streaming Decisions

### **Server-Sent Events for AI Conversations**
**Decision**: Use Server-Sent Events (SSE) with standard Authorization headers
**Rationale**:
- **Industry Standard**: ChatGPT, Claude, and major AI platforms use SSE for response streaming
- **Simplicity**: Unidirectional streaming perfect for AI responses (no bidirectional communication needed)
- **Built-in Browser Support**: Native `EventSource` API with automatic reconnection
- **HTTP/2 Compatible**: Benefits from multiplexing and standard HTTP infrastructure
- **Easier Authentication**: Standard Bearer tokens in headers vs query parameters
- **Stateless**: Each response stream is independent, improving scalability

**Implementation**:
```
POST /conversations/{conversation_id}/messages  # Send user message
GET /conversations/{conversation_id}/stream     # SSE endpoint for AI responses
```

**SSE Response Format** (with standard API wrapper):
```
event: ai_response
data: {"success": true, "data": {"content": "token...", "is_complete": false}, "message": "Streaming"}
```

---

## 🔐 Authentication & Security Decisions

### **Google OAuth Only**
**Decision**: Single sign-on with Google OAuth
**Rationale**:
- **MVP Simplicity**: Reduces authentication complexity
- **User Trust**: Leverages established Google identity
- **Auto-Profile Creation**: Streamlines onboarding
- **Future Extensibility**: Can add more providers later

### **JWT Token Strategy**
**Decision**: Bearer tokens with refresh capability
**Rationale**:
- **Stateless**: Supports horizontal scaling
- **Standard Practice**: Well-understood security model
- **Flexible**: Works with both REST and SSE streaming
- **Refresh Support**: Maintains session continuity

---

## 📊 Data & Pagination Decisions

### **UUID Primary Keys**
**Decision**: Use UUIDs for all primary keys
**Rationale**:
- **Scalability**: Supports distributed systems and sharding
- **Security**: Non-sequential IDs prevent enumeration attacks
- **Future-Proof**: Enables microservices architecture
- **Merge Capability**: Simplifies data migration/merging

### **Standardized Pagination**
**Decision**: Consistent limit/offset with max bounds
**Rationale**:
- **Performance**: Prevents expensive large queries
- **Consistency**: Same pattern across all list endpoints
- **Client Predictability**: Easier frontend implementation
- **Resource Protection**: Prevents abuse

**Standard**:
```
limit: integer (default: 20, max: 100)
offset: integer (default: 0)
```

---

## 🚦 Rate Limiting Strategy

### **Generous MVP Limits**
**Decision**: Higher limits during MVP phase
**Rationale**:
- **User Testing**: Allows thorough feature exploration
- **Feedback Collection**: Reduces friction during validation
- **AI Experimentation**: Users can iterate on conversations
- **Future Adjustment**: Can tighten based on usage patterns

**Limits**:
- AI Messages: 100/hour (vs. typical 50)
- Blog Generation: 20/hour (vs. typical 10)
- Post Creation: 10/hour (vs. typical 5)
- General API: 2000/hour (vs. typical 1000)

---

## 🔗 API Design Patterns

### **Consistent Response Format**
**Decision**: Standardized wrapper for all responses
**Rationale**:
- **Client Simplicity**: Predictable response structure
- **Error Handling**: Consistent error format
- **Extensibility**: Easy to add metadata fields
- **Debugging**: Clear success/failure indication

**Format**:
```json
{
  "success": boolean,
  "data": object | array | null,
  "message": string,
  "error_code": string | null
}
```

### **RESTful Resource Design**
**Decision**: Standard REST patterns with logical nesting
**Rationale**:
- **Predictability**: Follows established conventions
- **Discoverability**: URLs reflect resource relationships
- **Tooling Support**: Works with standard HTTP libraries
- **Documentation**: Self-documenting URL structure

**Examples**:
```
GET /posts/{post_id}/comments
POST /users/{user_id}/follow
GET /conversations/{conversation_id}/messages
```

---

## 🎨 Frontend-Backend Contract

### **Public Read Access**
**Decision**: Most content accessible without authentication
**Rationale**:
- **Discovery**: Enables content sharing and viral growth
- **SEO**: Supports search engine indexing
- **Reduced Friction**: Users can explore before signing up
- **Platform Growth**: Lowers barrier to content consumption

### **User Interaction Tracking**
**Decision**: Optional user context for analytics
**Rationale**:
- **Personalization**: Enables future recommendation features
- **Analytics**: Tracks engagement patterns
- **Privacy-Conscious**: Works with or without user auth
- **Flexible**: Supports both anonymous and authenticated users

---

## 📱 Social Features Design

### **Lightweight Social Graph**
**Decision**: Simple follow/unfollow with count aggregation
**Rationale**:
- **MVP Scope**: Focuses on core conversation features
- **Performance**: Efficient count queries with proper indexing
- **Extensibility**: Easy to add recommendations later
- **User Experience**: Clear social connections without complexity

### **Engagement Metrics**
**Decision**: Universal reaction system with intellectual focus
**Rationale**:
- **Quality Signals**: Reactions help surface valuable content
- **Intellectual Discourse**: Specific reactions (upvote/downvote, insightful, accurate) promote thoughtful engagement
- **Normalized Design**: Single reaction table eliminates count column redundancy
- **Flexibility**: VARCHAR reaction field allows easy addition of new reaction types
- **User Experience**: Clear quality indicators beyond simple like/dislike

**Reaction Set**: `upvote`, `downvote`, `heart`, `insightful`, `accurate`
- **User Feedback**: Provides engagement indicators
- **Algorithm Ready**: Supports future recommendation systems
- **Balanced**: Avoids pure popularity contests

---

## 🔄 Content Lifecycle Design

### **Post Creation Flows**
**Decision**: Two distinct paths - AI-assisted and custom
**Rationale**:
- **User Choice**: Accommodates different creation preferences
- **Platform Differentiation**: Showcases AI capabilities
- **Flexibility**: Supports various content types
- **Unified Backend**: Both flows use same data model

**Flows**:
1. **AI-Assisted**: Conversation → Generate Blog → Post
2. **Custom**: Direct Writing → Post (with placeholder conversation)

### **Content Expansion Model**
**Decision**: Fork conversations from posts for exploration
**Rationale**:
- **Unique Value**: Differentiates from traditional social media
- **Context Preservation**: Maintains original post context
- **AI Integration**: Natural integration with conversation system
- **User Agency**: Allows deep exploration of ideas

---

## 🚀 Scalability Considerations

### **Database Design**
**Decision**: Normalized schema with proper indexing
**Rationale**:
- **Performance**: Efficient queries for common operations
- **Consistency**: Avoids data duplication
- **Extensibility**: Easy to add new features
- **Maintenance**: Clear data relationships

### **Soft Deletion Strategy**
**Decision**: Status fields instead of hard deletes
**Rationale**:
- **Data Integrity**: Preserves conversation context
- **Audit Trail**: Maintains history for debugging
- **User Experience**: Enables "archive" functionality
- **Compliance**: Supports data retention policies

---

## 🔧 Technical Implementation Notes

### **AI Integration Strategy**
**Decision**: LangChain with Gemini for flexibility
**Rationale**:
- **Model Flexibility**: Easy to switch AI providers
- **Feature Rich**: Supports conversation memory and context
- **Streaming**: Enables real-time response delivery
- **Extensibility**: Can add specialized AI agents later

### **Error Handling Philosophy**
**Decision**: Specific error codes with human-readable messages
**Rationale**:
- **Client Handling**: Enables proper error handling in frontend
- **User Experience**: Clear error messages for users
- **Debugging**: Specific codes help identify issues
- **Monitoring**: Enables error tracking and alerting

---

## 🔐 **Track A Implementation Decisions**

### **Instagram-like Privacy Model**
**Decision**: Implement comprehensive privacy controls matching Instagram's behavior
**Rationale**:
- **User Trust**: Users need control over their social interactions
- **Familiar UX**: Instagram's privacy model is well-understood by users
- **Graduated Privacy**: Different levels of privacy for different content types
- **Social Safety**: Protects users from unwanted followers and content access

**Implementation**:
```
User Privacy Settings:
- is_private: boolean (account-level privacy)
- Follow system: pending/accepted states
- Content visibility: controlled by follow relationships
- List access: privacy-aware with authentication requirements
```

**Privacy Logic**:
- **Public accounts**: Anyone can follow instantly, view content, see follower lists
- **Private accounts**: Follow requests required, only approved followers see content
- **Error handling**: Specific error codes (`PRIVATE_ACCOUNT_AUTH_REQUIRED`, `PRIVATE_ACCOUNT_FOLLOW_REQUIRED`)
- **Pagination**: Privacy-aware with follow status included for authenticated users

### **Test-Driven Development (TDD) Methodology**
**Decision**: Implement strict TDD with Red-Green-Refactor cycles
**Rationale**:
- **Quality Assurance**: Comprehensive test coverage ensures reliability
- **Regression Prevention**: Changes can't break existing functionality
- **Documentation**: Tests serve as living documentation of behavior
- **Confidence**: Refactoring and feature additions with confidence

**Implementation**:
```
Red Phase: Write failing tests for new functionality
Green Phase: Implement minimal code to pass tests
Refactor Phase: Optimize and clean up code
Integration: Ensure all tests pass before moving forward
```

**Quality Metrics**:
- **40 API Tests**: Comprehensive coverage of all social endpoints
- **100% Pass Rate**: All tests must pass before deployment
- **Mock Strategy**: Fast, isolated tests with proper database mocking
- **Realistic Scenarios**: Tests cover success, error, and edge cases

### **Service Layer Architecture**
**Decision**: Implement Repository and Service patterns for business logic
**Rationale**:
- **Separation of Concerns**: Business logic separated from API controllers
- **Testability**: Easy to test business logic independently
- **Maintainability**: Clear boundaries between layers
- **Extensibility**: Easy to add new features and modify existing ones

**Implementation**:
```
Controllers → Services → Repositories → Database
     ↓           ↓           ↓
  API Logic  Business    Data Access
              Logic
```

**Benefits**:
- **Clean Architecture**: Clear separation of responsibilities
- **Easy Testing**: Mock services and repositories independently
- **Code Reuse**: Business logic can be reused across different endpoints
- **Scalability**: Easy to add new services as platform grows

---

## 📋 Future Expansion Considerations

### **Designed for Growth**
- **Multi-user Conversations**: Schema supports multiple participants
- **Advanced AI Features**: Pluggable AI agent system
- **Content Moderation**: Status fields support moderation workflows
- **Analytics**: Comprehensive tracking for insights
- **Privacy Controls**: Extensible permission system

### **Deferred Features**
- **Content Editing**: Intentionally omitted for MVP
- **Advanced Search**: Semantic search and recommendations
- **Media Support**: Text-only for MVP simplicity
- **Notification System**: Not critical for core value prop

---

## 🎯 Success Metrics & Validation

### **MVP Success Indicators**
1. **Conversation Quality**: Length and depth of AI interactions
2. **Content Creation**: Posts generated from conversations
3. **Engagement**: Expand/repost usage indicating exploration
4. **User Retention**: Return visits for continued conversations
5. **Social Growth**: Follow relationships and content sharing

### **Technical Validation**
- **API Performance**: Response times under 200ms for most endpoints
- **SSE Streaming**: Reliable real-time conversation experience
- **Database Efficiency**: Query performance with proper indexing
- **Error Rates**: Low error rates across all endpoints

---

## 📝 Decision Log Summary

| Decision | Rationale | Impact |
|----------|-----------|---------|
| Conversation-centric model | Supports AI-assisted content creation | Core platform differentiator |
| Forked_from for reposts | Elegant, normalized design | Reduces API complexity |
| Empty conversations for custom posts | Efficient, atomic operations | Maintains data consistency |
| Instagram-like privacy model | User trust and familiar UX | Production-ready social features |
| Test-Driven Development | Quality assurance and confidence | 40 passing tests, zero regressions |
| Service layer architecture | Clean architecture and testability | Maintainable and scalable codebase |
| Content editing deferred for MVP | MVP scope decision | Simplifies initial API complexity |
| SSE for AI chat | Real-time user experience | Essential for AI conversations |
| Google OAuth only | MVP simplicity | Reduces authentication complexity |
| UUID primary keys | Scalability and security | Future-proof architecture |
| Generous rate limits | MVP testing and feedback | Enables thorough validation |
| Public read access | Discovery and growth | Lowers adoption barriers |
| Soft deletion | Data integrity and audit | Supports future features |

---

This document serves as the definitive reference for understanding the architectural decisions behind [APP_NAME]'s MVP API design. Each decision supports the platform's unique value proposition while maintaining simplicity and extensibility for future growth.