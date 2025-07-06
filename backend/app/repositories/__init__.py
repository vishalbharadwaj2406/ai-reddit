"""
Repositories Package

This package contains data access layer (repository pattern).
Repositories handle all database operations and queries.

Repository Pattern Benefits:
- Abstracts database operations
- Makes testing easier (can mock repositories)
- Centralizes database logic
- Provides consistent interface for data access
- Easier to switch databases if needed

Each repository typically handles one main entity (User, Post, etc.)
but can include related operations.
"""

# Import all repositories so they're available when this package is imported
# from app.repositories.user_repository import UserRepository
# from app.repositories.conversation_repository import ConversationRepository
# from app.repositories.post_repository import PostRepository
# from app.repositories.message_repository import MessageRepository

# List all repositories for easy reference
# __all__ = [
#     "UserRepository",
#     "ConversationRepository",
#     "PostRepository",
#     "MessageRepository"
# ]