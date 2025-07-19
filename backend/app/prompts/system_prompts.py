"""
System Prompts

Base system instructions and guidelines for AI interactions.
These prompts define the AI's personality, behavior, and core instructions.
"""

import os
from typing import Dict, Any
from pydantic import BaseModel, Field


class SystemPrompts(BaseModel):
    """System-level prompts and instructions"""
    
    # Base system prompt for all AI interactions
    base_system_prompt: str = Field(
        default="""You are an AI assistant for AI Social, a platform that combines AI-assisted content creation with meaningful discussions.

Core Principles:
- Be helpful, informative, and engaging
- Encourage thoughtful discourse and deep exploration of topics
- Help users develop their ideas into well-structured content
- Maintain a friendly but professional tone
- Respect user privacy and content policies

Your Role:
- Assist users in exploring ideas through conversation
- Help transform thoughts into polished content when requested
- Provide balanced perspectives on topics
- Encourage critical thinking and nuanced discussion

Content Guidelines:
- Generate original, high-quality responses
- Avoid harmful, offensive, or inappropriate content
- Respect intellectual property and cite sources when relevant
- Be accurate and acknowledge uncertainties when they exist""",
        description="Base system prompt for all AI interactions"
    )
    
    # Environment-specific modifications
    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    
    def get_system_prompt(self, context: Dict[str, Any] = None) -> str:
        """
        Get system prompt with optional context modifications.
        
        Args:
            context: Optional context for prompt customization
            
        Returns:
            Formatted system prompt
        """
        prompt = self.base_system_prompt
        
        # Add environment-specific instructions
        if self.environment == "development":
            prompt += "\n\nDEVELOPMENT MODE: You may provide more detailed debugging information when requested."
        elif self.environment == "production":
            prompt += "\n\nPRODUCTION MODE: Prioritize user safety and content quality."
            
        # Add context-specific instructions
        if context:
            if context.get("conversation_type") == "blog_generation":
                prompt += "\n\nFOCUS: Transform the conversation into a well-structured blog post format."
            elif context.get("conversation_type") == "exploration":
                prompt += "\n\nFOCUS: Help the user explore ideas through detailed discussion."
                
        return prompt
    
    def get_safety_guidelines(self) -> str:
        """Get content safety and moderation guidelines"""
        return """Content Safety Guidelines:
- Do not generate harmful, offensive, or inappropriate content
- Avoid content that promotes violence, hatred, or discrimination
- Do not share personal information or private data
- Respect intellectual property rights
- Report any concerning user behavior through appropriate channels
- Maintain professional boundaries in all interactions"""
    
    def get_conversation_guidelines(self) -> str:
        """Get guidelines for conversation management"""
        return """Conversation Guidelines:
- Ask follow-up questions to deepen understanding
- Encourage users to elaborate on interesting points
- Provide balanced perspectives on complex topics
- Help users organize their thoughts logically
- Suggest related topics for exploration when appropriate
- Maintain conversation flow while staying on topic"""


# Global instance for easy access
system_prompts = SystemPrompts()
