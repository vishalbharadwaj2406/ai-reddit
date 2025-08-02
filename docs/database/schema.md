# Database Schema

PostgreSQL database schema with 13 tables supporting AI conversations, social interactions, and content management.

## Overview

Conversation-centric design where posts are derived from AI conversations, enabling post forking with full context preservation.

### Core Tables (13)

## User Management

### Users
| Field            | Type           | Notes                                  |
|------------------|---------------|----------------------------------------|
| user_id          | UUID (PK)      | Primary key                            |
| user_name        | VARCHAR UNIQUE | Display name                           |
| email            | VARCHAR UNIQUE | Optional, for login/notifications      |
| phone            | VARCHAR UNIQUE | Optional                               |
| profile_picture  | VARCHAR        | Optional, URL                          |
| gender           | VARCHAR        | Optional                               |
| google_id        | VARCHAR UNIQUE | For Google sign-in                     |
| is_private       | BOOLEAN        | Default FALSE, followers-only content  |
| created_at       | TIMESTAMP      |                                        |
| updated_at       | TIMESTAMP      |                                        |
| status           | VARCHAR        | 'active', 'archived', etc.             |

### Follows
| Field         | Type      | Notes                                    |
|---------------|-----------|------------------------------------------|
| follower_id   | UUID (FK) | References users(user_id)                |
| following_id  | UUID (FK) | References users(user_id)                |
| created_at    | TIMESTAMP |                                          |
| updated_at    | TIMESTAMP |                                          |
| status        | VARCHAR   | 'pending', 'accepted', 'rejected', etc.  |
| PRIMARY KEY   | (follower_id, following_id)              |

## Content Creation

### Conversations
| Field           | Type      | Notes                                 |
|-----------------|-----------|---------------------------------------|
| conversation_id | UUID (PK) | Primary key                           |
| user_id         | UUID (FK) | Creator, references users(user_id)    |
| title           | VARCHAR   |                                       |
| forked_from     | UUID (FK) | Nullable, references posts(post_id)   |
| created_at      | TIMESTAMP |                                       |
| updated_at      | TIMESTAMP |                                       |
| status          | VARCHAR   | 'active', 'archived', etc.            |

### Messages
| Field         | Type      | Notes                                 |
|---------------|-----------|---------------------------------------|
| message_id    | UUID (PK) | Primary key                           |
| conversation_id| UUID (FK)| References conversations(conversation_id) |
| user_id       | UUID (FK) | Author, nullable for AI messages      |
| role          | VARCHAR   | 'user', 'assistant', 'system'         |
| content       | TEXT      |                                       |
| is_blog       | BOOLEAN   | Default false, blog candidate         |
| created_at    | TIMESTAMP |                                       |
| updated_at    | TIMESTAMP |                                       |
| status        | VARCHAR   | 'active', 'archived', etc.            |

### Posts
| Field           | Type      | Notes                                 |
|-----------------|-----------|---------------------------------------|
| post_id         | UUID (PK) | Primary key                           |
| user_id         | UUID (FK) | Creator, references users(user_id)    |
| conversation_id | UUID (FK) | References conversations(conversation_id) |
| title           | VARCHAR   |                                       |
| content         | TEXT      |                                       |
| fork_count      | INTEGER   | Number of forks, default 0            |
| is_conversation_visible | BOOLEAN | Conversation viewability       |
| created_at      | TIMESTAMP |                                       |
| updated_at      | TIMESTAMP |                                       |
| edited          | BOOLEAN   | True if post has been edited          |
| status          | VARCHAR   | 'active', 'archived', etc.            |

## Social Interactions

### Post Forks
| Field           | Type      | Notes                                 |
|-----------------|-----------|---------------------------------------|
| user_id         | UUID (FK) | References users(user_id)              |
| post_id         | UUID (FK) | References posts(post_id)              |
| conversation_id | UUID (FK) | References new forked conversation     |
| forked_at       | TIMESTAMP | When the fork was created              |
| original_conversation_included | VARCHAR | Context inclusion flag       |
| status          | VARCHAR   | 'active', 'archived', etc.             |
| PRIMARY KEY     | (user_id, post_id, forked_at)          |

### Post Reactions
| Field         | Type      | Notes                                 |
|---------------|-----------|---------------------------------------|
| user_id       | UUID (FK) | References users(user_id)              |
| post_id       | UUID (FK) | References posts(post_id)              |
| reaction      | VARCHAR   | 'upvote', 'downvote', 'heart', 'insightful', 'accurate' |
| created_at    | TIMESTAMP |                                       |
| updated_at    | TIMESTAMP |                                       |
| status        | VARCHAR   | 'active', 'archived', etc.            |
| PRIMARY KEY   | (user_id, post_id)                    |

### Post Views
| Field         | Type      | Notes                                 |
|---------------|-----------|---------------------------------------|
| user_id       | UUID (FK) | References users(user_id)              |
| post_id       | UUID (FK) | References posts(post_id)              |
| viewed_at     | TIMESTAMP |                                       |
| updated_at    | TIMESTAMP |                                       |
| status        | VARCHAR   | 'active', 'archived', etc.            |
| PRIMARY KEY   | (user_id, post_id, viewed_at)         |

### Post Shares
| Field         | Type      | Notes                                 |
|---------------|-----------|---------------------------------------|
| user_id       | UUID (FK) | References users(user_id)              |
| post_id       | UUID (FK) | References posts(post_id)              |
| shared_at     | TIMESTAMP |                                       |
| updated_at    | TIMESTAMP |                                       |
| status        | VARCHAR   | 'active', 'archived', etc.            |
| PRIMARY KEY   | (user_id, post_id, shared_at)         |

## Discussion System

### Comments
| Field           | Type      | Notes                                 |
|-----------------|-----------|---------------------------------------|
| comment_id      | UUID (PK) | Primary key                           |
| post_id         | UUID (FK) | References posts(post_id)              |
| user_id         | UUID (FK) | Author, references users(user_id)     |
| parent_comment_id| UUID (FK)| Nullable, for threaded replies        |
| content         | TEXT      |                                       |
| created_at      | TIMESTAMP |                                       |
| updated_at      | TIMESTAMP |                                       |
| status          | VARCHAR   | 'active', 'archived', etc.            |

### Comment Reactions
| Field         | Type      | Notes                                 |
|---------------|-----------|---------------------------------------|
| user_id       | UUID (FK) | References users(user_id)              |
| comment_id    | UUID (FK) | References comments(comment_id)        |
| reaction      | VARCHAR   | 'upvote', 'downvote', 'heart', 'insightful', 'accurate' |
| created_at    | TIMESTAMP |                                       |
| updated_at    | TIMESTAMP |                                       |
| status        | VARCHAR   | 'active', 'archived', etc.            |
| PRIMARY KEY   | (user_id, comment_id)                 |

## Content Organization

### Tags
| Field    | Type      | Notes                     |
|----------|-----------|---------------------------|
| tag_id   | UUID (PK) | Primary key               |
| name     | VARCHAR   | Unique, tag text          |

### Post Tags
| Field    | Type      | Notes                     |
|----------|-----------|---------------------------|
| post_id  | UUID (FK) | References posts(post_id) |
| tag_id   | UUID (FK) | References tags(tag_id)   |
| PRIMARY KEY | (post_id, tag_id)        |

## Indexes

Essential indexes for query performance:

```sql
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_conversation_id ON posts(conversation_id);
CREATE INDEX idx_post_tags_post_id ON post_tags(post_id);
CREATE INDEX idx_post_tags_tag_id ON post_tags(tag_id);
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_tags_name ON tags(name);
```

## Design Principles

### Scalability
- **UUID Primary Keys**: Distributed system ready
- **Proper Indexing**: Optimized for common query patterns
- **Soft Deletion**: Status fields enable data preservation
- **Normalized Design**: Follows 3NF principles

### Extensibility
- **Many-to-Many Relationships**: Join tables for flexibility
- **Timestamp Tracking**: Full audit trail capability
- **Status Fields**: Support for workflow states
- **Foreign Key Constraints**: Data integrity enforcement

### Performance
- **Strategic Indexes**: On foreign keys and query fields
- **Efficient Joins**: Optimized relationship queries
- **No Cascade Deletes**: Application-level control
- **Caching Ready**: Structure supports future caching layers

This schema supports MVP features and provides foundation for platform expansion.
