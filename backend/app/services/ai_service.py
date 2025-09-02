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
from app.core.config import settings

logger = logging.getLogger(__name__)


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
        if "quantum" in user_message.lower():
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

        # Split response into tokens and stream them
        words = mock_response.split()
        current_content = ""

        for i, word in enumerate(words):
            # Add word to current content
            if i == 0:
                current_content = word
                new_chunk = word
            else:
                new_chunk = f" {word}"
                current_content += new_chunk

            # Simulate streaming delay
            await asyncio.sleep(0.05)  # 50ms delay between tokens

            # Yield current state
            yield {
                "content": new_chunk,  # Send only the new chunk
                "accumulated_content": current_content,  # Send accumulated content
                "is_complete": i == len(words) - 1,
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

            # Use streaming with callback handler
            callback_handler = StreamingCallbackHandler()

            async for chunk in self.llm.astream(messages, callbacks=[callback_handler]):
                if chunk.content:
                    # Break down large chunks into smaller pieces for better streaming effect
                    new_content = chunk.content
                    
                    # Split the new content into words for smoother streaming
                    words = new_content.split()
                    
                    for word in words:
                        # Add word to current content
                        if current_content:
                            word_with_space = f" {word}"
                        else:
                            word_with_space = word
                        
                        current_content += word_with_space

                        yield {
                            "content": word_with_space,  # Send only the new word
                            "accumulated_content": current_content,  # Send accumulated for reference
                            "is_complete": False,
                            "message_id": None  # Will be set by the endpoint
                        }

                        # Add delay between words for visible streaming effect
                        await asyncio.sleep(0.05)  # 50ms delay between words

            # Send final complete message
            yield {
                "content": "",  # No new chunk in final message
                "accumulated_content": current_content,
                "is_complete": True,
                "message_id": None
            }

        except Exception as e:
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

    async def generate_blog_from_conversation(
        self,
        conversation_content: str,
        additional_context: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate blog post from conversation content.

        Args:
            conversation_content: The conversation to transform into a blog
            additional_context: Additional instructions or context

        Yields:
            Dict containing response tokens for blog generation
        """

        try:
            # Use conversation prompts to format the blog generation request
            conversation_prompts_instance = conversation_prompts.ConversationPrompts()
            blog_prompt = conversation_prompts_instance.format_blog_prompt(
                conversation_content, additional_context
            )

            # Generate blog using the same response mechanism
            async for chunk in self.generate_ai_response(blog_prompt):
                yield chunk

        except Exception as e:
            logger.error(f"Blog generation error: {str(e)}")
            raise AIServiceError(f"Blog generation failed: {str(e)}")


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
