"""
Conversation Prompts

Prompt templates for AI conversation interactions.
Handles regular chat, follow-up questions, and context management.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .system_prompts import system_prompts

# Predefined tags that the LLM can choose from for blog generation
PREDEFINED_BLOG_TAGS = [
    "technology", "science", "ai", "machine-learning", "programming", "web-development",
    "mobile-development", "data-science", "cybersecurity", "cloud-computing", "blockchain",
    "environment", "climate-change", "sustainability", "renewable-energy", "conservation",
    "health", "fitness", "nutrition", "mental-health", "medicine", "wellness",
    "business", "entrepreneurship", "finance", "investing", "marketing", "productivity",
    "education", "learning", "career", "leadership", "management", "skills",
    "lifestyle", "travel", "food", "culture", "entertainment", "sports",
    "philosophy", "psychology", "society", "politics", "economics", "history",
    "art", "design", "creativity", "music", "literature", "photography",
    "gaming", "automotive", "space", "innovation", "research", "tutorial"
]


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
        tags_list = ", ".join(PREDEFINED_BLOG_TAGS)
        
        base_prompt = """Transform the following conversation into a well-structured, engaging blog post.

CRITICAL: You MUST respond with ONLY valid JSON in the following exact format:
{{
    "title": "Your engaging blog title here",
    "content": "Your complete blog content with proper markdown formatting",
    "tags": ["tag1", "tag2", "tag3"]
}}

TAGS REQUIREMENT:
- You MUST select 2-5 tags ONLY from this predefined list: {predefined_tags}
- DO NOT create any tags that are not in this list
- Choose tags that best represent the main topics discussed in the conversation

Conversation Content:
{conversation_content}

Blog Post Requirements:
1. Create an engaging title (keep it concise and descriptive)
2. Organize content into logical sections with clear headings
3. Maintain the key insights and information from the conversation
4. Write in a clear, accessible style suitable for a general audience
5. Include a conclusion that summarizes key takeaways
6. Use proper markdown formatting for headers, lists, etc.
7. Select 2-5 relevant tags from the predefined list only
8. IMPORTANT: Do NOT repeat the title as a header in the content - the title will be displayed separately
9. CRITICAL QUOTE PREVENTION: Do NOT use any quotation marks (single quotes ' or double quotes ") anywhere in the title or content text. When referencing movie quotes, book lines, or spoken dialogue, use alternative phrasing instead of direct quotes. For example:
   - Instead of: The famous line "There is no spoon" from The Matrix
   - Write: The famous line about there being no spoon from The Matrix
   - Instead of: Einstein said "Imagination is more important than knowledge"
   - Write: Einstein believed that imagination is more important than knowledge
   You can use regular apostrophes for contractions (like "don't", "it's") but avoid quotation marks entirely. Never wrap referenced text, dialogue, or phrases in quotation marks.

{additional_instructions}

IMPORTANT: Return ONLY the raw JSON object. Do NOT wrap it in markdown code blocks. Do NOT use ```json or ``` markers. Start your response directly with the opening brace {{ and end with the closing brace }}. No other text, explanations, or formatting."""

        additional_instructions = ""
        if additional_context:
            additional_instructions = f"Additional Instructions: {additional_context}"
            
        return base_prompt.format(
            conversation_content=conversation_content,
            additional_instructions=additional_instructions,
            predefined_tags=tags_list
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
