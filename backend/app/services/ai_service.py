"""
AI Service for AI Social Platform

This service handles AI interactions including:
- Generating AI responses to user messages
- Streaming responses token by token
- Managing AI conversation context
- Error handling for AI service failures

Uses Google Gemini API for production AI responses.
Future versions may support multiple AI providers.
"""

import asyncio
import logging
import os
from typing import AsyncGenerator, Dict, Any, Optional, List
from uuid import UUID
import json

import google.generativeai as genai
from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold

from app.prompts import conversation_prompts, system_prompts
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass


class AIService:
    """
    AI Service for handling conversation responses using Google Gemini.
    
    This service is responsible for:
    1. Generating AI responses based on user messages using Gemini API
    2. Streaming responses in real-time
    3. Maintaining conversation context
    4. Handling AI service failures gracefully
    5. Managing content safety and moderation
    """
    
    def __init__(self):
        """Initialize AI service with Gemini configuration"""
        # Initialize Gemini API
        api_key = settings.GOOGLE_GEMINI_API_KEY
        if not api_key:
            logger.warning("GOOGLE_GEMINI_API_KEY not found. Running in mock mode.")
            self.mock_mode = True
            self.model = None
        else:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(
                    model_name=settings.AI_MODEL_NAME,
                    generation_config=GenerationConfig(
                        temperature=settings.AI_TEMPERATURE,
                        top_p=settings.AI_TOP_P,
                        top_k=settings.AI_TOP_K,
                        max_output_tokens=settings.AI_MAX_TOKENS,
                        candidate_count=1,
                    ),
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    }
                )
                self.mock_mode = False
                logger.info(f"Gemini AI service initialized successfully with {settings.AI_MODEL_NAME}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini API: {str(e)}")
                self.mock_mode = True
                self.model = None
        
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
        
        if self.mock_mode:
            # Mock AI response for testing/development
            async for chunk in self._generate_mock_response(user_message):
                yield chunk
        else:
            # Real Gemini AI implementation
            async for chunk in self._generate_gemini_response(
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
            else:
                current_content += f" {word}"
            
            # Simulate streaming delay
            await asyncio.sleep(0.05)  # 50ms delay between tokens
            
            # Yield current state
            yield {
                "content": current_content,
                "is_complete": i == len(words) - 1,
                "message_id": None  # Will be set by the endpoint
            }
    
    async def _generate_gemini_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        conversation_id: Optional[UUID] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate real AI response using Google Gemini API.
        
        Constructs the conversation context and streams the response.
        """
        
        try:
            # Build the conversation context using our prompt templates
            system_prompts_instance = system_prompts.SystemPrompts()
            conversation_prompts_instance = conversation_prompts.ConversationPrompts()
            
            system_message = system_prompts_instance.get_system_prompt()
            conversation_starter = conversation_prompts_instance.get_conversation_starter()
            
            # Build conversation history for Gemini
            messages = []
            
            # Add system context
            messages.append({
                "role": "user", 
                "parts": [system_message]
            })
            messages.append({
                "role": "model", 
                "parts": [conversation_starter]
            })
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg["role"] == "user" else "model"
                    messages.append({
                        "role": role,
                        "parts": [msg["content"]]
                    })
            
            # Add current user message
            messages.append({
                "role": "user",
                "parts": [user_message]
            })
            
            # Start chat session with history
            chat = self.model.start_chat(history=messages[:-1])
            
            # Generate streaming response
            response = await asyncio.to_thread(
                chat.send_message,
                user_message,
                stream=True
            )
            
            current_content = ""
            
            # Stream the response chunks
            for chunk in response:
                if chunk.text:
                    current_content += chunk.text
                    
                    yield {
                        "content": current_content,
                        "is_complete": False,
                        "message_id": None  # Will be set by the endpoint
                    }
                    
                    # Add small delay to simulate more natural streaming
                    await asyncio.sleep(0.01)
            
            # Send final complete message
            yield {
                "content": current_content,
                "is_complete": True,
                "message_id": None
            }
            
        except Exception as e:
            logger.error(f"Gemini AI service error: {str(e)}")
            
            # Fallback to mock response if Gemini fails
            logger.warning("Falling back to mock response due to Gemini error")
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
                "provider": "mock"
            }
        else:
            try:
                # Test Gemini API connectivity with a simple request
                test_response = await asyncio.to_thread(
                    self.model.generate_content,
                    "Hello, please respond with 'OK' to confirm you're working."
                )
                
                if test_response.text and "OK" in test_response.text.upper():
                    return {
                        "status": "healthy",
                        "mode": "production",
                        "message": "Gemini AI service connected and responsive",
                        "provider": "google_gemini"
                    }
                else:
                    return {
                        "status": "degraded",
                        "mode": "production", 
                        "message": "Gemini responded but with unexpected content",
                        "provider": "google_gemini"
                    }
                    
            except Exception as e:
                logger.error(f"Gemini health check failed: {str(e)}")
                return {
                    "status": "unhealthy",
                    "mode": "production",
                    "message": f"Gemini API error: {str(e)}",
                    "provider": "google_gemini"
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
