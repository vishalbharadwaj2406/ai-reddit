# AIkya MVP Database Schema (Markdown)

This schema is designed for a minimal, production-ready MVP of the AIkya platform. It follows best practices for normalization, extensibility, and efficient querying. All fields are explicitly described. (Engine: PostgreSQL recommended)

---

## Users
| Field            | Type           | Constraints / Notes                                  |
|------------------|---------------|------------------------------------------------------|
| user_id          | UUID (PK)      | Unmodifiable, primary key                            |
| user_name        | VARCHAR UNIQUE | Modifiable, unique display name                      |
| email            | VARCHAR UNIQUE | Optional, for login/notifications                    |
| phone            | VARCHAR UNIQUE | Optional                                             |
| profile_picture  | VARCHAR        | Optional, URL                                        |
| gender           | VARCHAR        | Optional                                             |
| created_at       | TIMESTAMP      |                                                      |
| updated_at       | TIMESTAMP      | Last modification time                               |
| google_id        | VARCHAR UNIQUE | For Google sign-in                                   |
| is_private       | BOOLEAN        | Default FALSE. TRUE = followers-only content         |
| status           | VARCHAR        | Record status: 'active', 'archived', etc.            |

---

## Follows
| Field         | Type      | Constraints / Notes                                         |
|---------------|-----------|-----------------------------------------------------------|
| follower_id   | UUID (FK) | References users(user_id)                                  |
| following_id  | UUID (FK) | References users(user_id)                                  |
| created_at    | TIMESTAMP |                                                           |
| updated_at    | TIMESTAMP | Last modification time                                    |
| status        | VARCHAR   | 'pending', 'accepted', 'rejected', 'archived', etc.       |
| PRIMARY KEY   | (follower_id, following_id)                                            |
| Constraint    | follower_id != following_id                                            |

---

## Conversations
| Field           | Type      | Constraints / Notes                                 |
|-----------------|-----------|-----------------------------------------------------|
| conversation_id | UUID (PK) | Primary key                                         |
| user_id         | UUID (FK) | Creator, references users(user_id)                  |
| title           | VARCHAR   |                                                     |
| created_at      | TIMESTAMP |                                                     |
| updated_at      | TIMESTAMP | Last modification time                              |
| forked_from     | UUID (FK) | Nullable, references posts(post_id)                 |
| status          | VARCHAR   | Record status: 'active', 'archived', etc.           |

---

## Messages
| Field         | Type      | Constraints / Notes                                 |
|---------------|-----------|-----------------------------------------------------|
| message_id    | UUID (PK) | Primary key                                         |
| conversation_id| UUID (FK)| References conversations(conversation_id)           |
| user_id       | UUID (FK) | Author, references users(user_id), nullable for AI  |
| role          | VARCHAR   | 'user', 'assistant', 'system'                       |
| content       | TEXT      |                                                     |
| is_blog       | BOOLEAN   | Default false, can be true for blog candidate       |
| created_at    | TIMESTAMP |                                                     |
| updated_at    | TIMESTAMP | Last modification time                              |
| status        | VARCHAR   | Record status: 'active', 'archived', etc.           |

---

## Posts
| Field           | Type      | Constraints / Notes                                 |
|-----------------|-----------|-----------------------------------------------------|
| post_id         | UUID (PK) | Primary key                                         |
| user_id         | UUID (FK) | Creator, references users(user_id)                  |
| conversation_id | UUID (FK) | References conversations(conversation_id)           |
| title           | VARCHAR   |                                                     |
| content         | TEXT      |                                                     |
| is_conversation_visible | BOOLEAN   | If TRUE, the conversation linked to this post is viewable by others (subject to user/conversation privacy). If FALSE, only the post content is visible. |
| created_at      | TIMESTAMP |                                                     |
| updated_at      | TIMESTAMP | Last modification time                              |
| edited          | BOOLEAN   | True if post has been edited                        |
| status          | VARCHAR   | Record status: 'active', 'archived', etc.           |

---

## Post Reactions
| Field         | Type      | Constraints / Notes                                 |
|---------------|-----------|-----------------------------------------------------|
| user_id       | UUID (FK) | References users(user_id)                           |
| post_id       | UUID (FK) | References posts(post_id)                           |
| reaction      | VARCHAR   | e.g. 'like', 'dislike', 'love', 'laugh', 'sad', etc. Only one reaction per user per post is allowed. |
| created_at    | TIMESTAMP |                                                     |
| updated_at    | TIMESTAMP | Last modification time                              |
| status        | VARCHAR   | Record status: 'active', 'archived', etc.           |
| PRIMARY KEY   | (user_id, post_id)                                               |

---

## Post Views
| Field         | Type      | Constraints / Notes                                 |
|---------------|-----------|-----------------------------------------------------|
| user_id       | UUID (FK) | References users(user_id)                           |
| post_id       | UUID (FK) | References posts(post_id)                           |
| viewed_at     | TIMESTAMP |                                                     |
| updated_at    | TIMESTAMP | Last modification time                              |
| status        | VARCHAR   | Record status: 'active', 'archived', etc.           |
| PRIMARY KEY   | (user_id, post_id, viewed_at)                                   |

---

## Post Shares
| Field         | Type      | Constraints / Notes                                 |
|---------------|-----------|-----------------------------------------------------|
| user_id       | UUID (FK) | References users(user_id)                           |
| post_id       | UUID (FK) | References posts(post_id)                           |
| shared_at     | TIMESTAMP |                                                     |
| updated_at    | TIMESTAMP | Last modification time                              |
| status        | VARCHAR   | Record status: 'active', 'archived', etc.           |
| PRIMARY KEY   | (user_id, post_id, shared_at)                                   |

---

## Comments
| Field           | Type      | Constraints / Notes                                 |
|-----------------|-----------|-----------------------------------------------------|
| comment_id      | UUID (PK) | Primary key                                         |
| post_id         | UUID (FK) | References posts(post_id)                           |
| user_id         | UUID (FK) | Author, references users(user_id)                   |
| parent_comment_id| UUID (FK)| Nullable, for replies                               |
| content         | TEXT      |                                                     |
| created_at      | TIMESTAMP |                                                     |
| updated_at      | TIMESTAMP | Last modification time                              |
| like_count      | INT       |                                                     |
| dislike_count   | INT       |                                                     |
| status          | VARCHAR   | Record status: 'active', 'archived', etc.           |

---

## Comment Reactions
| Field         | Type      | Constraints / Notes                                 |
|---------------|-----------|-----------------------------------------------------|
| user_id       | UUID (FK) | References users(user_id)                           |
| comment_id    | UUID (FK) | References comments(comment_id)                     |
| reaction      | VARCHAR   | e.g. 'like', 'dislike', 'love', 'laugh', 'sad', etc. Only one reaction per user per comment is allowed. |
| created_at    | TIMESTAMP |                                                     |
| updated_at    | TIMESTAMP | Last modification time                              |
| status        | VARCHAR   | Record status: 'active', 'archived', etc.           |
| PRIMARY KEY   | (user_id, comment_id)                                            |

---

## Tags
| Field    | Type      | Constraints / Notes         |
|----------|-----------|----------------------------|
| tag_id   | UUID (PK) | Primary key                |
| name     | VARCHAR   | Unique, tag text           |

---

## Post Tags
| Field    | Type      | Constraints / Notes         |
|----------|-----------|----------------------------|
| post_id  | UUID (FK) | References posts(post_id)   |
| tag_id   | UUID (FK) | References tags(tag_id)     |
| PRIMARY KEY | (post_id, tag_id)                   |

---

## Indexes
- CREATE INDEX idx_posts_user_id ON posts(user_id);
- CREATE INDEX idx_posts_conversation_id ON posts(conversation_id);
- CREATE INDEX idx_post_tags_post_id ON post_tags(post_id);
- CREATE INDEX idx_post_tags_tag_id ON post_tags(tag_id);
- CREATE INDEX idx_comments_post_id ON comments(post_id);
- CREATE INDEX idx_comments_user_id ON comments(user_id);
- CREATE INDEX idx_tags_name ON tags(name);

---

## Design Justifications

- **Normalization & Extensibility:**
  - All entities (users, posts, comments, tags, etc.) are in separate tables, following 3NF. This avoids data duplication and supports future features (e.g., advanced search, analytics) without major refactoring.
  - Many-to-many relationships (e.g., post_tags, follows, likes) use join tables, which is best practice for flexibility and efficient querying.

- **Indexes:**
  - Indexes are added on foreign keys and frequently queried fields (e.g., user_id, post_id, tag_id, conversation_id, tag name) to ensure fast lookups, filtering, and joins, especially as data grows.

- **UUIDs:**
  - UUIDs are used as primary keys for scalability and to support distributed systems. This is future-proof for sharding and horizontal scaling.

- **Timestamps & Status:**
  - Timestamps and status fields enable soft-deletion, auditing, and efficient filtering for both MVP and future moderation or workflow features.

- **Tagging:**
  - Tags and post_tags tables allow efficient many-to-many tagging, supporting both MVP (filtering/discovery) and future advanced topic discovery (semantic search, recommendations).

- **No ON DELETE CASCADE:**
  - Deletions are handled at the application level to prevent accidental data loss and to support soft-deletion and archiving.

- **MVP & Future Scale:**
  - The schema is minimal for MVP but designed for easy extension (e.g., adding AI feedback, multi-user conversations, advanced analytics) without breaking existing data or requiring major migrations.

This schema is designed for extensibility and efficient querying for all major MVP features. All content is public, and only text is supported for posts/comments. No ON DELETE CASCADE is used. All timestamps are in UTC.
