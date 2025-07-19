"""
Services Package

This package contains business logic services.
Services handle the core application logic and orchestrate
between different layers (repositories, external APIs, etc.).

Service Layer Responsibilities:
- Business logic implementation
- Orchestration between repositories
- External API integrations (Google OAuth, AI services)
- Complex data transformations
- Transaction management
- Error handling and logging

Why use a service layer?
- Separation of concerns
- Reusable business logic
- Easier testing
- Better organization
- Centralized error handling
"""

# Import all services so they're available when this package is imported
# from app.services.auth_service import AuthService
# from app.services.user_service import UserService
# from app.services.conversation_service import ConversationService
# from app.services.post_service import PostService
from app.services.ai_service import AIService

# List all services for easy reference
__all__ = [
    # "AuthService",
    # "UserService", 
    # "ConversationService",
    # "PostService",
    "AIService"
]