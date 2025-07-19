"""
Prompt Templates Module

This module contains all AI prompt templates used throughout the application.
Uses Python files for type safety, IDE support, and version control.

Industry best practices:
- Environment-aware prompts
- Template variables for dynamic content
- Modular design for different AI functions
- Type validation with Pydantic
"""

from .conversation_prompts import ConversationPrompts
from .blog_generation_prompts import BlogGenerationPrompts
from .system_prompts import SystemPrompts

__all__ = [
    "ConversationPrompts",
    "BlogGenerationPrompts", 
    "SystemPrompts"
]
