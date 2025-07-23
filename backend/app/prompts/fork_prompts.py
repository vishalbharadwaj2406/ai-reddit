"""
Post Fork Prompts

Prompt templates for post forking functionality.
Handles context integration when forking posts into new conversations.
"""

from typing import Optional


class ForkPrompts:
    """Fork-specific prompt templates"""
    
    def get_fork_context_prompt(
        self, 
        post_title: str, 
        post_content: str, 
        original_conversation: Optional[str] = None,
        include_original_conversation: bool = False
    ) -> str:
        """
        Generate the context prompt for a forked conversation.
        
        This prompt sets up the AI with proper context about the original post
        and optionally includes the full original conversation.
        
        Args:
            post_title: Title of the original post being forked
            post_content: Content of the original post being forked
            original_conversation: Full conversation context if available
            include_original_conversation: Whether to include full conversation
            
        Returns:
            Formatted context prompt for the fork
        """
        base_prompt = f"""This conversation is a fork from an original post titled: "{post_title}"

Original Post Content:
{post_content}

---

You are starting a new conversation based on this post. The user has forked this post to explore it further, ask questions, or discuss related topics. 

Please:
1. Acknowledge that this is a fork from the original post
2. Be ready to discuss the content in depth
3. Encourage the user to explore aspects they find interesting
4. Ask thoughtful follow-up questions to deepen the discussion
5. Build upon the ideas presented in the original post"""

        if include_original_conversation and original_conversation:
            context_prompt = f"""{base_prompt}

Original Conversation Context:
{original_conversation}

Note: The above conversation context from the original post is provided for reference. You can refer to it to provide more informed responses, but focus primarily on the new direction this forked conversation takes."""
        else:
            context_prompt = base_prompt + "\n\nYou're starting fresh with this post as the foundation for a new discussion."
        
        return context_prompt
    
    def get_fork_welcome_message(
        self, 
        post_title: str,
        include_original_conversation: bool = False
    ) -> str:
        """
        Generate a welcome message for the forked conversation.
        
        Args:
            post_title: Title of the original post
            include_original_conversation: Whether original conversation was included
            
        Returns:
            Welcome message for the user
        """
        if include_original_conversation:
            return f"""I can see you've forked the post "{post_title}" and included the original conversation context. 

I'm ready to continue exploring this topic with you! What aspect would you like to dive deeper into? Feel free to ask questions, share your thoughts, or take the discussion in a new direction."""
        else:
            return f"""Welcome to your fork of "{post_title}"! 

I'm here to help you explore this topic further. What questions do you have about the post? What aspects interest you most? Let's dive deeper into this subject together."""
    
    def get_fork_system_prompt(self) -> str:
        """
        Get the system prompt for forked conversations.
        
        Returns:
            System prompt for AI behavior in forked conversations
        """
        return """You are an AI assistant in a forked conversation. The user has taken an interesting post and created a new conversation to explore it further.

Your role is to:
- Be knowledgeable about the original post content
- Help the user explore the topic in depth
- Ask thought-provoking questions
- Encourage critical thinking and new perspectives
- Build upon the foundation of the original post
- Make connections to related concepts and ideas

Be engaging, informative, and help the user get the most value from their forked discussion."""


# Global instance for easy access
fork_prompts = ForkPrompts()
