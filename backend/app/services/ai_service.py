"""
AI Service for AI Social Platform

This service handles AI interactions including:
- Generating AI responses to user messages via LangChain abstraction
- Streaming responses token by token with real-time delivery
- Managing AI conversation context and memory
- Error handling for AI service failures with graceful fallbacks

Uses LangChain framework with Google Gemini 2.5 Flash for production AI responses.
LangChain abstraction ensures future-proofing for multiple AI providers (OpenAI, Anthropic, etc).
Provider switching is achieved by changing the LLM class while maintaining the same interface.
Architecture supports seamless migration between AI providers without code changes.
"""

import asyncio
import logging
import os
from typing import AsyncGenerator, Dict, Any, Optional, List
from uuid import UUID
import json

# LangChain imports for future-proof AI integration
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult

from app.prompts import conversation_prompts, system_prompts
from app.prompts.conversation_prompts import PREDEFINED_BLOG_TAGS
from app.core.config import settings

logger = logging.getLogger(__name__)


def extract_json_from_markdown(content: str) -> str:
    """
    Extract JSON from markdown code blocks or return the content as-is if it's already valid JSON.
    
    Args:
        content: Raw content that may contain JSON wrapped in markdown code blocks
        
    Returns:
        Clean JSON string
        
    Raises:
        json.JSONDecodeError: If no valid JSON is found
    """
    import re
    
    # First, try parsing the content directly as JSON
    try:
        json.loads(content.strip())
        return content.strip()
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    # Look for ```json...``` or ```...``` patterns (more flexible)
    patterns = [
        r'```json\s*\n(.*?)\n```',  # ```json ... ```
        r'```\s*\n(.*?)\n```',      # ``` ... ```
        r'```json\s*(.*?)```',      # ```json...``` (without newlines)
        r'```\s*(.*?)```',          # ```...``` (without newlines)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
        if match:
            extracted = match.group(1).strip()
            try:
                json.loads(extracted)  # Validate it's valid JSON
                return extracted
            except json.JSONDecodeError:
                continue
    
    # If no code blocks found, try to find JSON-like content
    # Look for content between { and } that might be JSON (more robust)
    json_pattern = r'\{.*?\}'
    matches = re.findall(json_pattern, content, re.DOTALL)
    
    # Try each potential JSON match
    for match in matches:
        try:
            json.loads(match.strip())  # Validate it's valid JSON
            return match.strip()
        except json.JSONDecodeError:
            continue
    
    # If all else fails, raise an error with more details
    raise json.JSONDecodeError(f"No valid JSON found in content. Content preview: {content[:200]}...", content, 0)


class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass


class StreamingCallbackHandler(AsyncCallbackHandler):
    """Custom callback handler for streaming responses"""

    def __init__(self):
        self.tokens = []

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when a new token is generated"""
        self.tokens.append(token)


class AIService:
    """
    AI Service for handling conversation responses using LangChain + Google Gemini.

    This service is responsible for:
    1. Generating AI responses based on user messages using LangChain abstraction
    2. Streaming responses in real-time
    3. Maintaining conversation context
    4. Handling AI service failures gracefully
    5. Future-proofing for multiple AI providers through LangChain
    """

    def __init__(self):
        """Initialize AI service with LangChain + Gemini configuration"""
        # Initialize Gemini through LangChain
        api_key = settings.GOOGLE_GEMINI_API_KEY
        if not api_key:
            logger.warning("GOOGLE_GEMINI_API_KEY not found. Running in mock mode.")
            self.mock_mode = True
            self.llm = None
        else:
            try:
                # Initialize LangChain Gemini LLM
                self.llm = ChatGoogleGenerativeAI(
                    model=settings.AI_MODEL_NAME,
                    google_api_key=api_key,
                    temperature=settings.AI_TEMPERATURE,
                    top_p=settings.AI_TOP_P,
                    top_k=settings.AI_TOP_K,
                    max_output_tokens=settings.AI_MAX_TOKENS,
                    timeout=settings.AI_REQUEST_TIMEOUT,  # Add timeout configuration
                )
                self.mock_mode = False
                logger.info(f"LangChain AI service initialized successfully with {settings.AI_MODEL_NAME}")
            except Exception as e:
                logger.error(f"Failed to initialize LangChain Gemini: {str(e)}")
                self.mock_mode = True
                self.llm = None

    async def generate_ai_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        conversation_id: Optional[UUID] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate AI response and stream it token by token.

        Args:
            user_message: The user's message to respond to
            conversation_history: Previous messages in the conversation
                Format: [{"role": "user"|"assistant", "content": "message"}]
            conversation_id: ID of the conversation for context

        Yields:
            Dict containing response tokens with format:
            {
                "content": "partial response...",
                "is_complete": False,
                "message_id": "uuid"
            }

        Raises:
            AIServiceError: If AI service fails
        """

        logger.info(f"🤖 AI Service running in {'mock' if self.mock_mode else 'production'} mode")
        
        if self.mock_mode:
            # Mock AI response for testing/development
            logger.info("🎭 Using mock AI response")
            async for chunk in self._generate_mock_response(user_message):
                yield chunk
        else:
            # Real LangChain + Gemini implementation
            logger.info("🚀 Using real LangChain + Gemini AI response")
            async for chunk in self._generate_langchain_response(
                user_message, conversation_history, conversation_id
            ):
                yield chunk

    async def _generate_mock_response(self, user_message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate mock AI response for testing.

        This simulates streaming AI responses by yielding tokens
        with realistic delays.
        """

        # Generate mock response based on user message
        if "TITLE:" in user_message and "CONTENT:" in user_message:
            # This is a blog generation request
            mock_response = (
                "TITLE: Understanding AI and Technology\n"
                "CONTENT: This blog post explores the fascinating world of artificial intelligence "
                "and its applications in modern technology. We'll examine how AI systems work, "
                "their benefits and challenges, and what the future holds for this revolutionary field.\n\n"
                "## Introduction\n\n"
                "Artificial Intelligence has become an integral part of our daily lives, "
                "transforming how we work, communicate, and solve complex problems.\n\n"
                "## Key Benefits\n\n"
                "AI technology offers numerous advantages including automation, "
                "improved decision-making, and enhanced problem-solving capabilities.\n\n"
                "## Conclusion\n\n"
                "As we continue to advance in AI technology, it's important to consider "
                "both the opportunities and responsibilities that come with these powerful tools."
            )
        elif "quantum" in user_message.lower():
            mock_response = (
                "Quantum computing is a revolutionary technology that "
                "harnesses the principles of quantum mechanics to process "
                "information in fundamentally different ways than classical computers. "
                "Unlike classical bits that exist in either 0 or 1 states, "
                "quantum bits (qubits) can exist in superposition, allowing them "
                "to be in multiple states simultaneously."
            )
        elif "hello" in user_message.lower():
            mock_response = (
                "Hello! I'm an AI assistant ready to help you explore ideas "
                "and create meaningful content. What would you like to discuss today?"
            )
        else:
            mock_response = (
                f"Thank you for your message: '{user_message}'. "
                "I'm here to help you develop your thoughts into structured content. "
                "Could you tell me more about what you'd like to explore?"
            )

        # Split response into larger chunks for better performance
        words = mock_response.split()
        current_content = ""
        
        # Process words in groups of 3-5 for more natural streaming
        chunk_size = 4
        word_chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]

        for i, word_chunk in enumerate(word_chunks):
            # Join words in this chunk
            chunk_text = " ".join(word_chunk)
            
            if i == 0:
                current_content = chunk_text
                new_chunk = chunk_text
            else:
                new_chunk = f" {chunk_text}"
                current_content += new_chunk

            # Simulate streaming delay - less frequent updates
            await asyncio.sleep(0.1)  # 100ms delay between chunks

            # Yield current state
            yield {
                "content": new_chunk,  # Send the chunk
                "accumulated_content": current_content,  # Send accumulated content
                "is_complete": i == len(word_chunks) - 1,
                "message_id": None  # Will be set by the endpoint
            }

    async def _generate_langchain_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        conversation_id: Optional[UUID] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate real AI response using LangChain + Google Gemini.

        This method uses LangChain's abstraction for future-proofing and
        provider flexibility.
        """

        try:
            # Build the conversation context using our prompt templates
            system_prompts_instance = system_prompts.SystemPrompts()
            conversation_prompts_instance = conversation_prompts.ConversationPrompts()

            system_message_content = system_prompts_instance.get_system_prompt()

            # Build LangChain message list
            messages = []

            # Add system message
            messages.append(SystemMessage(content=system_message_content))

            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages for context
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))

            # Add current user message
            messages.append(HumanMessage(content=user_message))

            # Generate streaming response using LangChain
            current_content = ""

            # Use streaming with callback handler and timeout
            callback_handler = StreamingCallbackHandler()

            # Stream with proper timeout handling
            async for chunk in self.llm.astream(messages, callbacks=[callback_handler]):
                if chunk.content:
                    # Use larger chunks for better performance and less frequent updates
                    new_content = chunk.content
                    current_content += new_content

                    yield {
                        "content": new_content,  # Send the chunk as received from LangChain
                        "accumulated_content": current_content,  # Send accumulated content
                        "is_complete": False,
                        "message_id": None  # Will be set by the endpoint
                    }

                    # Smaller delay for better responsiveness without overwhelming the frontend
                    await asyncio.sleep(0.01)  # 10ms delay between chunks

            # Send final complete message
            yield {
                "content": "",  # No new chunk in final message
                "accumulated_content": current_content,
                "is_complete": True,
                "message_id": None
            }

        except asyncio.TimeoutError:
            print(f"🚨 [AI] Request timeout after {settings.AI_REQUEST_TIMEOUT} seconds")
            logger.error(f"LangChain AI service timeout after {settings.AI_REQUEST_TIMEOUT} seconds")
            
            # Fallback to mock response on timeout
            logger.warning("Falling back to mock response due to timeout")
            async for chunk in self._generate_mock_response(user_message):
                yield chunk
        except Exception as e:
            print(f"🚨 [AI] LangChain error: {str(e)}")
            logger.error(f"LangChain AI service error: {str(e)}")

            # Fallback to mock response if LangChain fails
            logger.warning("Falling back to mock response due to LangChain error")
            async for chunk in self._generate_mock_response(user_message):
                yield chunk

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if AI service is healthy and responsive.

        Returns:
            Dict with health status information
        """

        if self.mock_mode:
            return {
                "status": "healthy",
                "mode": "mock",
                "message": "AI service running in mock mode",
                "provider": "mock",
                "framework": "langchain"
            }
        else:
            try:
                # Test LangChain + Gemini connectivity with a simple request
                test_messages = [
                    HumanMessage(content="Hello, please respond with 'OK' to confirm you're working.")
                ]

                response = await self.llm.ainvoke(test_messages)

                if response.content and "OK" in response.content.upper():
                    return {
                        "status": "healthy",
                        "mode": "production",
                        "message": "LangChain + Gemini AI service connected and responsive",
                        "provider": "google_gemini",
                        "framework": "langchain",
                        "model": settings.AI_MODEL_NAME
                    }
                else:
                    return {
                        "status": "degraded",
                        "mode": "production",
                        "message": "LangChain + Gemini responded but with unexpected content",
                        "provider": "google_gemini",
                        "framework": "langchain",
                        "model": settings.AI_MODEL_NAME
                    }

            except Exception as e:
                logger.error(f"LangChain health check failed: {str(e)}")
                return {
                    "status": "unhealthy",
                    "mode": "production",
                    "message": f"LangChain + Gemini API error: {str(e)}",
                    "provider": "google_gemini",
                    "framework": "langchain",
                    "model": settings.AI_MODEL_NAME
                }

    async def generate_content_only(
        self,
        conversation_content: str,
        additional_context: Optional[str] = None
    ) -> str:
        """
        Generate blog content only (without title) for fallback strategy.
        
        Args:
            conversation_content: The conversation to transform into a blog
            additional_context: Additional instructions or context
            
        Returns:
            Clean blog content as string
        """
        content_prompt = f"""Transform the following conversation into well-structured blog content.

DO NOT include a title - just provide the content body.

Conversation Content:
{conversation_content}

Requirements:
1. Organize content into logical sections with clear headings (use ### for sections)
2. Maintain the key insights and information from the conversation
3. Write in a clear, accessible style suitable for a general audience
4. Include a conclusion that summarizes key takeaways
5. Use proper markdown formatting for headers, lists, etc.

{f"Additional Instructions: {additional_context}" if additional_context else ""}

Return only the blog content without any title or wrapper formatting."""

        # Collect the complete response
        complete_response = ""
        async for chunk in self.generate_ai_response(content_prompt):
            if isinstance(chunk, dict) and "content" in chunk:
                complete_response += chunk["content"]
            elif isinstance(chunk, str):
                complete_response += chunk
                
        return complete_response.strip()

    async def generate_title_from_content(self, content: str) -> str:
        """
        Generate a title based on existing blog content for fallback strategy.
        
        Args:
            content: Blog content to generate title for
            
        Returns:
            Clean title as string
        """
        title_prompt = f"""Generate a concise, engaging title for the following blog content.

Blog Content:
{content[:1000]}...

Requirements:
1. Keep it concise and descriptive (under 80 characters)
2. Make it engaging and clickable
3. Capture the main theme of the content
4. Use proper title case

Return only the title text, nothing else."""

        # Collect the complete response
        complete_response = ""
        async for chunk in self.generate_ai_response(title_prompt):
            if isinstance(chunk, dict) and "content" in chunk:
                complete_response += chunk["content"]
            elif isinstance(chunk, str):
                complete_response += chunk
                
        return complete_response.strip().strip('"').strip("'")

    async def generate_emergency_fallback(
        self,
        conversation_content: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a simple fallback blog when all AI methods fail.
        
        Args:
            conversation_content: The conversation to transform
            additional_context: Additional context if available
            
        Returns:
            Simple blog structure with empty tags
        """
        try:
            # Simple template-based approach
            if isinstance(conversation_content, list):
                # Extract text from conversation messages
                text_content = []
                for msg in conversation_content:
                    if isinstance(msg, dict) and "content" in msg:
                        text_content.append(msg["content"])
                content_text = " ".join(text_content)
            else:
                content_text = str(conversation_content)
            
            # Create a simple summary
            words = content_text.split()
            if len(words) > 100:
                summary = " ".join(words[:100]) + "..."
            else:
                summary = content_text
                
            fallback_blog = {
                "title": "Conversation Summary",
                "content": f"## Summary\n\n{summary}\n\n*This is a simplified summary due to processing limitations.*",
                "tags": []  # Empty tags as requested for fallback
            }
            
            return fallback_blog
            
        except Exception as e:
            logger.error(f"Emergency fallback generation failed: {str(e)}")
            # Absolute last resort
            return {
                "title": "Conversation Summary",
                "content": "## Summary\n\nA conversation summary was requested but could not be generated at this time.",
                "tags": []
            }

    async def _generate_blog_single_call(
        self,
        conversation_content: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Primary strategy: Generate blog using single LLM call with full JSON structure.
        
        Args:
            conversation_content: The conversation to transform into a blog
            additional_context: Additional instructions or context
            
        Returns:
            Dict containing blog data with title, content, and tags
            
        Raises:
            ValidationError: If output doesn't meet format requirements
        """
        # Use conversation prompts to format the blog generation request
        conversation_prompts_instance = conversation_prompts.ConversationPrompts()
        blog_prompt = conversation_prompts_instance.format_blog_prompt(
            conversation_content, additional_context
        )

        # Collect the complete response first
        complete_response = ""
        async for chunk in self.generate_ai_response(blog_prompt):
            if isinstance(chunk, dict) and "content" in chunk:
                complete_response += chunk["content"]
            elif isinstance(chunk, str):
                complete_response += chunk

        # Extract clean JSON from the response
        clean_json = extract_json_from_markdown(complete_response)
        
        # Validate that it's proper JSON with required fields
        blog_data = json.loads(clean_json)
        
        # Verify required fields exist
        required_fields = ["title", "content", "tags"]
        for field in required_fields:
            if field not in blog_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Verify field types
        if not isinstance(blog_data["title"], str):
            raise ValueError("Title must be a string")
        if not isinstance(blog_data["content"], str):
            raise ValueError("Content must be a string")
        if not isinstance(blog_data["tags"], list):
            raise ValueError("Tags must be a list")
        
        # Verify non-empty values
        if not blog_data["title"].strip():
            raise ValueError("Title cannot be empty")
        if not blog_data["content"].strip():
            raise ValueError("Content cannot be empty")
        if not blog_data["tags"]:
            raise ValueError("Tags list cannot be empty")
        
        # Verify all tags are strings
        for tag in blog_data["tags"]:
            if not isinstance(tag, str):
                raise ValueError(f"All tags must be strings, got {type(tag)}: {tag}")
        
        # Verify all tags are from the predefined list
        for tag in blog_data["tags"]:
            if tag not in PREDEFINED_BLOG_TAGS:
                raise ValueError(f"Tag '{tag}' is not in the predefined list. Must be one of: {', '.join(PREDEFINED_BLOG_TAGS)}")
        
        # Verify tag count is within range (2-5 tags)
        if len(blog_data["tags"]) < 2:
            raise ValueError("Must have at least 2 tags")
        if len(blog_data["tags"]) > 5:
            raise ValueError("Must have no more than 5 tags")
            
        return blog_data

    async def _generate_blog_two_calls(
        self,
        conversation_content: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fallback strategy: Generate blog using separate calls for content and title.
        
        Args:
            conversation_content: The conversation to transform into a blog
            additional_context: Additional instructions or context
            
        Returns:
            Dict containing blog data with title, content, and empty tags
        """
        # Step 1: Generate content only
        content = await self.generate_content_only(conversation_content, additional_context)
        
        # Step 2: Generate title from content
        title = await self.generate_title_from_content(content)
        
        # Return with empty tags as requested for fallback
        return {
            "title": title,
            "content": content,
            "tags": []  # Empty tags for fallback strategy
        }

    async def generate_blog_from_conversation(
        self,
        conversation_content: str,
        additional_context: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate blog post from conversation content with layered fallback strategy.

        Strategy:
        1. Primary: Single-call full JSON generation (fast, efficient)
        2. Fallback: Two-call strategy (content + title, empty tags)
        3. Emergency: Template-based simple summary

        Args:
            conversation_content: The conversation to transform into a blog
            additional_context: Additional instructions or context

        Yields:
            Dict containing response tokens for blog generation with clean JSON
        """

        try:
            # Primary Strategy: Single-call approach
            logger.info("Attempting blog generation with single-call strategy")
            blog_data = await self._generate_blog_single_call(conversation_content, additional_context)
            
            # Success! Yield the result
            yield {
                "content": json.dumps(blog_data),
                "is_complete": True,
                "message_id": None
            }
            
        except Exception as primary_error:
            logger.warning(f"Single-call strategy failed: {str(primary_error)}")
            
            try:
                # Fallback Strategy: Two-call approach
                logger.info("Attempting blog generation with two-call fallback strategy")
                blog_data = await self._generate_blog_two_calls(conversation_content, additional_context)
                
                # Success! Yield the result
                yield {
                    "content": json.dumps(blog_data),
                    "is_complete": True,
                    "message_id": None
                }
                
            except Exception as fallback_error:
                logger.error(f"Two-call strategy also failed: {str(fallback_error)}")
                
                try:
                    # Emergency Strategy: Template-based fallback
                    logger.info("Using emergency fallback strategy")
                    blog_data = await self.generate_emergency_fallback(conversation_content, additional_context)
                    
                    # Always succeeds (has internal error handling)
                    yield {
                        "content": json.dumps(blog_data),
                        "is_complete": True,
                        "message_id": None
                    }
                    
                except Exception as emergency_error:
                    # This should never happen, but just in case
                    logger.error(f"Even emergency fallback failed: {str(emergency_error)}")
                    raise AIServiceError(f"All blog generation strategies failed. Primary: {str(primary_error)}, Fallback: {str(fallback_error)}, Emergency: {str(emergency_error)}")


# Global AI service instance
ai_service = AIService()


async def generate_ai_response(
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    conversation_id: Optional[UUID] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Convenience function for generating AI responses.

    This is the main entry point for AI response generation.
    """
    async for response_chunk in ai_service.generate_ai_response(
        user_message, conversation_history, conversation_id
    ):
        yield response_chunk
