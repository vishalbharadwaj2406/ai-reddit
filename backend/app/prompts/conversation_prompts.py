"""
Conversation Prompts

Prompt templates for AI conversation interactions.
Handles regular chat, follow-up questions, and context management.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .system_prompts import system_prompts


class ConversationPrompts(BaseModel):
    """Conversation-specific prompt templates"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    @property
    def system_prompt(self) -> str:
        """Get system prompt for conversations"""
        return system_prompts.get_system_prompt({"conversation_type": "exploration"})
    
    @property
    def conversation_prompt(self) -> str:
        """Base conversation prompt template"""
        return """Based on our conversation history and the user's latest message, provide a thoughtful, engaging response that:

1. Directly addresses the user's question or comment
2. Builds upon previous discussion points when relevant
3. Asks follow-up questions to deepen the conversation
4. Provides accurate, helpful information
5. Encourages further exploration of the topic

Conversation History:
{conversation_history}

User's Message: {user_message}

Please respond in a natural, conversational tone while being informative and engaging."""
    
    @property 
    def blog_generation_prompt(self) -> str:
        """Prompt for blog generation from conversations"""
        return system_prompts.get_system_prompt({"conversation_type": "blog_generation"})
    
    def format_conversation_prompt(
        self, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Format conversation prompt with user message and history.
        
        Args:
            user_message: Current user message
            conversation_history: Previous messages in conversation
            
        Returns:
            Formatted prompt string
            
        Raises:
            ValueError: If user_message is empty
        """
        if not user_message or not user_message.strip():
            raise ValueError("User message cannot be empty")
            
        # Format conversation history
        if conversation_history:
            history_text = ""
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                history_text += f"{role.title()}: {content}\n"
        else:
            history_text = "This is the beginning of the conversation."
            
        return self.conversation_prompt.format(
            conversation_history=history_text,
            user_message=user_message
        )
    
    def format_blog_prompt(
        self,
        conversation_content: str,
        additional_context: Optional[str] = None
    ) -> str:
        """
        Format prompt for blog generation from conversation.
        
        Args:
            conversation_content: The conversation to transform into a blog
            additional_context: Additional instructions or context
            
        Returns:
            Formatted blog generation prompt
        """
        base_prompt = """Transform the following conversation into a well-structured, engaging blog post:

Conversation Content:
{conversation_content}

Blog Post Requirements:
1. Create an engaging title and introduction
2. Organize content into logical sections with clear headings
3. Maintain the key insights and information from the conversation
4. Write in a clear, accessible style suitable for a general audience
5. Include a conclusion that summarizes key takeaways
6. Ensure the post is informative, engaging, and well-structured

{additional_instructions}

Please generate a complete blog post based on this conversation."""

        additional_instructions = ""
        if additional_context:
            additional_instructions = f"Additional Instructions: {additional_context}"
            
        return base_prompt.format(
            conversation_content=conversation_content,
            additional_instructions=additional_instructions
        )
    
    def format_follow_up_prompt(self, topic: str, depth_level: str = "medium") -> str:
        """
        Generate follow-up questions for deeper exploration.
        
        Args:
            topic: The topic to explore further
            depth_level: Level of depth (basic, medium, advanced)
            
        Returns:
            Formatted follow-up prompt
        """
        depth_instructions = {
            "basic": "Ask 2-3 simple, accessible questions that help beginners understand the topic better.",
            "medium": "Ask 3-4 questions that explore different aspects and implications of the topic.",
            "advanced": "Ask 4-5 detailed questions that dive deep into nuances, connections, and expert-level considerations."
        }
        
        instruction = depth_instructions.get(depth_level, depth_instructions["medium"])
        
        return f"""Based on our discussion about "{topic}", generate thoughtful follow-up questions that would help continue this conversation.

{instruction}

Topic: {topic}

Please provide follow-up questions that:
1. Build on what we've already discussed
2. Explore different angles or perspectives
3. Encourage deeper thinking about the topic
4. Are engaging and thought-provoking

Format your response as a numbered list of questions."""
    
    def get_conversation_starter_prompts(self) -> List[str]:
        """Get conversation starter prompts for new users"""
        return [
            "What topic would you like to explore today? I'm here to help you develop your thoughts and ideas.",
            "I'd love to help you dive deep into any subject that interests you. What's on your mind?",
            "What questions have you been pondering lately? Let's explore them together.",
            "Is there a topic you've been wanting to understand better? I'm here to help you work through it.",
            "What ideas have been sparking your curiosity? Let's have a meaningful conversation about them."
        ]
    
    def get_conversation_starter(self) -> str:
        """Get a single conversation starter message"""
        import random
        starters = self.get_conversation_starter_prompts()
        return random.choice(starters)


# Global instance for easy access
conversation_prompts = ConversationPrompts()
