"""
Blog Generation Prompts

Specialized prompts for transforming conversations into blog posts.
Handles different blog styles, formats, and target audiences.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .system_prompts import system_prompts


class BlogGenerationPrompts(BaseModel):
    """Blog generation specific prompt templates"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @property
    def base_blog_prompt(self) -> str:
        """Base prompt for blog generation"""
        return system_prompts.get_system_prompt({"conversation_type": "blog_generation"}) + """

You are an expert content creator specializing in transforming conversations into engaging blog posts. Your task is to take a conversation and create a well-structured, informative, and engaging blog post that captures the key insights while making them accessible to a broader audience.

Key Requirements:
1. Create compelling titles and headings
2. Structure content logically with clear flow
3. Maintain the conversational insights while improving readability
4. Add context and explanations for broader audience understanding
5. Include actionable takeaways when appropriate
6. Ensure proper blog formatting and style"""

    def format_blog_generation_prompt(
        self,
        conversation_content: str,
        blog_style: str = "informative",
        target_audience: str = "general",
        additional_context: Optional[str] = None
    ) -> str:
        """
        Format comprehensive blog generation prompt.
        
        Args:
            conversation_content: The conversation to transform
            blog_style: Style of blog (informative, narrative, how-to, opinion)
            target_audience: Target audience (general, technical, beginner, expert)
            additional_context: Additional instructions
            
        Returns:
            Formatted blog generation prompt
        """
        
        style_instructions = {
            "informative": "Write an informative, educational blog post that explains concepts clearly and provides valuable insights.",
            "narrative": "Write a narrative-style blog post that tells a story while incorporating the key insights from the conversation.",
            "how-to": "Write a practical how-to guide that provides step-by-step instructions or actionable advice.",
            "opinion": "Write an opinion piece that presents thoughtful perspectives while acknowledging different viewpoints.",
            "listicle": "Write a list-style article that organizes information into digestible, numbered points."
        }
        
        audience_instructions = {
            "general": "Write for a general audience with clear explanations of technical terms and concepts.",
            "technical": "Write for a technical audience familiar with industry terminology and advanced concepts.",
            "beginner": "Write for beginners, providing basic explanations and avoiding jargon.",
            "expert": "Write for experts who understand the field and appreciate nuanced discussion.",
            "business": "Write for business professionals focusing on practical applications and impact."
        }
        
        style_instruction = style_instructions.get(blog_style, style_instructions["informative"])
        audience_instruction = audience_instructions.get(target_audience, audience_instructions["general"])
        
        prompt = f"""{self.base_blog_prompt}

CONVERSATION TO TRANSFORM:
{conversation_content}

BLOG STYLE: {style_instruction}

TARGET AUDIENCE: {audience_instruction}

BLOG STRUCTURE REQUIREMENTS:
1. **Compelling Title**: Create a title that captures the essence of the discussion
2. **Engaging Introduction**: Hook the reader and preview what they'll learn
3. **Main Content Sections**: Organize key points into logical sections with clear headings
4. **Supporting Details**: Add context, examples, or explanations as needed
5. **Conclusion**: Summarize key takeaways and provide a call-to-action or thought-provoking ending

FORMATTING GUIDELINES:
- Use markdown formatting for headings, lists, and emphasis
- Include subheadings to break up long sections
- Use bullet points or numbered lists where appropriate
- Keep paragraphs concise and readable
- Add smooth transitions between sections

{f"ADDITIONAL INSTRUCTIONS: {additional_context}" if additional_context else ""}

Please generate a complete, well-formatted blog post based on this conversation."""

        return prompt
    
    def format_blog_title_prompt(self, conversation_summary: str, style: str = "engaging") -> str:
        """
        Generate compelling blog titles.
        
        Args:
            conversation_summary: Brief summary of conversation content
            style: Title style (engaging, professional, creative, seo)
            
        Returns:
            Formatted title generation prompt
        """
        
        style_instructions = {
            "engaging": "Create engaging, attention-grabbing titles that make readers want to click and read more.",
            "professional": "Create professional, clear titles that accurately describe the content.",
            "creative": "Create creative, unique titles that stand out while remaining relevant.",
            "seo": "Create SEO-friendly titles that include relevant keywords and are optimized for search.",
            "question": "Create question-based titles that spark curiosity and engagement."
        }
        
        instruction = style_instructions.get(style, style_instructions["engaging"])
        
        return f"""Based on this conversation summary, generate 5-7 compelling blog post titles:

Conversation Summary: {conversation_summary}

Title Style: {instruction}

Requirements:
- Titles should be 6-12 words long
- Capture the main value or insight from the conversation
- Be specific enough to set clear expectations
- Appeal to the target audience
- Avoid clickbait while remaining engaging

Please provide a numbered list of title options."""

    def format_blog_outline_prompt(self, conversation_content: str) -> str:
        """
        Generate blog post outline before full content creation.
        
        Args:
            conversation_content: The conversation to outline
            
        Returns:
            Formatted outline generation prompt
        """
        return f"""Create a detailed outline for a blog post based on this conversation:

Conversation Content:
{conversation_content}

Please create an outline that includes:

1. **Proposed Title**: A compelling title for the blog post
2. **Introduction Hook**: How you'll grab the reader's attention
3. **Main Sections**: 3-5 main sections with:
   - Section heading
   - Key points to cover
   - Supporting details or examples
4. **Conclusion Strategy**: How you'll wrap up and what call-to-action you'll include
5. **Estimated Word Count**: For each section

Format your outline clearly with headings and bullet points. This outline should serve as a roadmap for creating the full blog post."""

    def get_blog_style_options(self) -> Dict[str, str]:
        """Get available blog style options with descriptions"""
        return {
            "informative": "Educational content that explains concepts and provides insights",
            "narrative": "Story-driven content that engages through personal experience or case studies",
            "how-to": "Step-by-step guides and practical instructions", 
            "opinion": "Thoughtful perspectives and analysis on topics",
            "listicle": "List-format content that's easy to scan and digest",
            "interview": "Q&A format that preserves conversational elements",
            "case-study": "Deep-dive analysis of specific examples or situations"
        }
    
    def get_audience_options(self) -> Dict[str, str]:
        """Get available target audience options with descriptions"""
        return {
            "general": "General audience seeking accessible explanations",
            "technical": "Technical professionals familiar with industry terminology",
            "beginner": "Newcomers who need basic concepts explained clearly",
            "expert": "Experts who appreciate nuanced, advanced discussion",
            "business": "Business professionals focused on practical applications",
            "academic": "Academic audience interested in research and theory",
            "creative": "Creative professionals in design, arts, or media"
        }


# Global instance for easy access
blog_generation_prompts = BlogGenerationPrompts()
