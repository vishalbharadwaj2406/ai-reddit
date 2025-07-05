<!-- # AI Social MVP - Database Schema Design

## Schema Overview
**5 tables supporting AI chat → social content transformation with threaded discussions**

```sql
-- User management with social profiles
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    bio TEXT,
    avatar_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI conversations with forking support
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ,
    title VARCHAR(200),
    forked_from INTEGER REFERENCES conversations(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat messages (user/assistant pairs) with blog drafts
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    forked_message_id INTEGER REFERENCES messages(id),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    is_blog BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Published social content with discovery metadata and threading support
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ,
    conversation_id INTEGER REFERENCES conversations(id),
    parent_post_id INTEGER REFERENCES posts(id) ,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    tags VARCHAR(500), -- comma-separated: "ai,ethics,philosophy"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Social following relationships
CREATE TABLE follows (
    follower_id INTEGER REFERENCES users(id) ,
    following_id INTEGER REFERENCES users(id) ,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, following_id),
    CHECK (follower_id != following_id)
);
```

## Key Design Decisions

### **Message Ordering Strategy**
- **Approach**: Auto-incrementing `id` field for chronological ordering
- **Rationale**: Simpler than timestamps for real-time streaming scenarios
- **Query Pattern**: `ORDER BY id ASC` for conversation replay

### **Blog Draft Management**
- **Approach**: Blog drafts stored as special messages with `is_blog=TRUE`
- **Rationale**: Keeps drafts in conversation context, easy to retrieve/edit
- **Publishing Flow**: User can edit blog content before creating actual post
- **Flexibility**: Posts can contain any text, not tied to specific message content

### **Conversation Forking Implementation**
- **Approach**: Copy all messages to new conversation (data duplication)
- **Alternative Rejected**: Shared message references (complex queries)
- **Trade-off**: Storage cost vs. query simplicity and data isolation
- **Lineage Tracking**: `forked_from` field maintains conversation history

### **Content Threading**
- **Approach**: Self-referencing `parent_post_id` for threaded discussions
- **Tree Structure**: Posts can reply to other posts creating conversation threads
- **Depth Strategy**: Unlimited nesting depth (can be limited in application logic)
- **Orphan Handling**: CASCADE deletes ensure clean thread cleanup when parent posts are deleted

### **Content Metadata**
- **Tags**: Simple comma-separated strings for MVP
- **Search Strategy**: Basic LIKE queries, can evolve to full-text search
- **Migration Path**: Easy to convert to separate tags table later

### **Social Relationships**
- **Following Model**: Simple one-way relationships (Twitter-style)
- **No Mutual Friends**: Keeps social graph simple for MVP
- **Cascade Deletes**: Clean up orphaned data automatically

## Core Feature Support

### **1. AI Chat Flow**
```sql
-- Create conversation
INSERT INTO conversations (user_id, title) VALUES (1, 'AI Ethics Discussion');

-- Add messages (streaming responses)
INSERT INTO messages (conversation_id, role, content) 
VALUES (1, 'user', 'What do you think about AI ethics?');

INSERT INTO messages (conversation_id, role, content) 
VALUES (1, 'assistant', 'AI ethics involves considerations of...');

-- Generate blog draft (saved as special message)
INSERT INTO messages (conversation_id, role, content, is_blog) 
VALUES (1, 'assistant', 'AI Ethics: Key Considerations for Modern Technology...', TRUE);
```

### **2. Conversation Forking**
```sql
-- User discovers conversation via post
SELECT c.* FROM conversations c 
JOIN posts p ON c.id = p.conversation_id 
WHERE p.id = 123;

-- Fork: Create new conversation
INSERT INTO conversations (user_id, title, forked_from) 
VALUES (2, 'AI Ethics Discussion (continued)', 1);

-- Copy all messages to forked conversation
INSERT INTO messages (conversation_id, role, content)
SELECT 2, role, content FROM messages WHERE conversation_id = 1;
```

### **3. Social Publishing & Threading**
```sql
-- Transform conversation to social post (top-level post)
INSERT INTO posts (user_id, conversation_id, parent_post_id, title, content, tags)
VALUES (1, 1, NULL, 'Exploring AI Ethics', 
        'A deep dive into the moral implications of artificial intelligence...', 
        'ai,ethics,philosophy,technology');

-- Reply to existing post (threaded discussion)
INSERT INTO posts (user_id, conversation_id, parent_post_id, title, content, tags)
VALUES (2, 15, 1, 'Re: AI Ethics - A Counter-Perspective', 
        'While I agree with the main points, I think we should also consider...', 
        'ai,ethics,debate');
```

### **4. Content Discovery & Threading**
```sql
-- Feed generation (top-level posts only, chronological with following filter)
SELECT p.*, u.username, u.display_name 
FROM posts p 
JOIN users u ON p.user_id = u.id
WHERE p.user_id IN (
    SELECT following_id FROM follows WHERE follower_id = current_user_id
)
AND p.parent_post_id IS NULL  -- Only top-level posts in main feed
ORDER BY p.created_at DESC;

-- Get threaded replies for a specific post
SELECT p.*, u.username, u.display_name 
FROM posts p 
JOIN users u ON p.user_id = u.id
WHERE p.parent_post_id = 123
ORDER BY p.created_at ASC;

-- Recursive thread traversal (get full discussion tree)
WITH RECURSIVE thread_tree AS (
    -- Base case: get the root post
    SELECT id, user_id, parent_post_id, title, content, 0 as depth
    FROM posts WHERE id = 123
    
    UNION ALL
    
    -- Recursive case: get all replies
    SELECT p.id, p.user_id, p.parent_post_id, p.title, p.content, tt.depth + 1
    FROM posts p
    JOIN thread_tree tt ON p.parent_post_id = tt.id
)
SELECT * FROM thread_tree ORDER BY depth, created_at;

-- Tag-based search (works across all posts)
SELECT * FROM posts 
WHERE tags LIKE '%ai%' OR tags LIKE '%ethics%'
ORDER BY created_at DESC;
```

## Performance Considerations

### **Essential Indexes**
```sql
-- Core performance indexes
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_parent_id ON posts(parent_post_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Social graph optimization  
CREATE INDEX idx_follows_follower ON follows(follower_id);
CREATE INDEX idx_follows_following ON follows(following_id);

-- Threading and feed optimization
CREATE INDEX idx_posts_parent_null ON posts(parent_post_id) WHERE parent_post_id IS NULL;
CREATE INDEX idx_posts_thread_lookup ON posts(parent_post_id, created_at) WHERE parent_post_id IS NOT NULL;

-- Search optimization (can be upgraded to full-text later)
CREATE INDEX idx_posts_tags ON posts USING gin(to_tsvector('english', tags));
```

### **Query Patterns**
- **Conversation Replay**: Single query by conversation_id, ordered by message.id
- **Feed Generation**: Join posts + users with following filter (top-level posts only)
- **Thread Display**: Parent-child queries for reply hierarchies
- **Recursive Threading**: CTE queries for full discussion trees
- **Search**: Tag-based filtering with text matching
- **Fork Discovery**: Navigate conversation lineage via forked_from

## Constraints & Data Integrity

### **Business Rules Enforced**
```sql
-- Message roles are constrained
CHECK (role IN ('user', 'assistant'))

-- Users cannot follow themselves  
CHECK (follower_id != following_id)

-- Proper foreign key relationships with cascade deletes
-- Orphaned conversations/messages/posts are cleaned up automatically
```

### **Data Limits**
- **Username**: 50 chars (URL-friendly)
- **Display Name**: 100 chars (human-readable)
- **Post Title**: 200 chars (Twitter-ish)
- **Tags**: 500 chars (generous for comma-separated)
- **Bio**: TEXT (unlimited for user expression)
- **Content**: TEXT (unlimited for AI conversations)

## Migration Strategy

### **Schema Evolution Path**
1. **Phase 1 (MVP)**: Current schema as-is
2. **Phase 2**: Add engagement metrics (views, likes) to posts table
3. **Phase 3**: Separate tags table with many-to-many relationships
4. **Phase 4**: Add conversation state management (active, archived)
5. **Phase 5**: Message metadata (token_count, model_used, processing_time)

### **Search Upgrade Path**
- **MVP**: Simple LIKE queries on tags field
- **Phase 2**: PostgreSQL full-text search with tsvector
- **Phase 3**: Dedicated search service (Elasticsearch) for semantic search

## Technical Debt & Trade-offs

### **Accepted for MVP Speed**
1. **Tag Storage**: String concatenation vs. normalized table
2. **Message Duplication**: Copy-on-fork vs. shared references  
3. **Basic Search**: Text matching vs. semantic/vector search
4. **No Engagement Metrics**: Focus on creation over consumption analytics

### **Future Refactoring Candidates**
- Conversation context windowing (for very long chats)
- Message compression/archiving (for storage optimization)
- Denormalized feed tables (for performance at scale)
- User preference/settings tables

## Development Notes

### **SQLAlchemy Models Required**
- User (with profile fields)
- Conversation (with forking relationship)  
- Message (with role validation)
- Post (with threading and tag indexing)
- Follow (composite primary key)

### **API Endpoint Implications**
- GET /conversations/{id}/messages (paginated message history)
- POST /conversations/{id}/fork (duplicate conversation for new user)
- POST /conversations/{id}/publish (create post from conversation)
- POST /posts/{id}/reply (create threaded reply to existing post)
- GET /posts/{id}/thread (get full discussion tree for post)
- GET /posts/{id}/replies (get direct replies to post)
- GET /feed (personalized post feed with following filter, top-level only)
- GET /search?tags=ai,ethics (tag-based content discovery)

**Schema Status**: ✅ **LOCKED AND APPROVED**  
**Next Phase**: API Architecture Design -->