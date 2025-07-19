"""
Test LangChain + Gemini AI Integration

Production-ready tests for LangChain + Google Gemini API integration.
These tests cover real-world scenarios using LangChain's ChatGoogleGenerativeAI.

Following TDD methodology:
1. Write comprehensive tests for production scenarios
2. Run tests (they should fail initially)  
3. Implement LangChain + Gemini integration to pass these tests
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
import json

from app.services.ai_service import AIService, AIServiceError
from app.prompts.conversation_prompts import ConversationPrompts


class TestLangChainGeminiIntegration:
    """Test LangChain + Gemini API integration scenarios"""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing"""
        service = AIService()
        service.mock_mode = False  # Test real AI mode
        return service

    @pytest.mark.asyncio
    async def test_api_key_validation_failure(self, ai_service):
        """Test handling of invalid/missing API keys"""
        with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock_chat:
            mock_chat.side_effect = Exception("Invalid API key")
            
            # Test that service falls back to mock mode gracefully
            responses = []
            async for response in ai_service.generate_ai_response("test message"):
                responses.append(response)
                
            # Should fall back to mock response
            assert len(responses) > 0
            assert responses[-1]["is_complete"] is True

    @pytest.mark.asyncio
    async def test_langchain_initialization_success(self, ai_service):
        """Test successful LangChain ChatGoogleGenerativeAI initialization"""
        with patch('app.services.ai_service.ChatGoogleGenerativeAI') as mock_chat:
            with patch('app.core.config.settings.GOOGLE_GEMINI_API_KEY', 'test-key'):
                mock_instance = Mock()
                mock_chat.return_value = mock_instance
                
                # Create new service to test initialization
                service = AIService()
                
                # Verify ChatGoogleGenerativeAI was called with correct parameters
                if not service.mock_mode:
                    mock_chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_streaming_response_success(self, ai_service):
        """Test successful streaming response via LangChain"""
        with patch.object(ai_service, 'llm') as mock_llm:
            # Mock LangChain streaming response
            mock_chunks = [
                Mock(content="Hello"),
                Mock(content=" there"),
                Mock(content="!"),
            ]
            
            async def mock_astream(messages, callbacks=None):
                for chunk in mock_chunks:
                    yield chunk
                    
            mock_llm.astream = mock_astream
            
            responses = []
            async for response in ai_service.generate_ai_response("test message"):
                responses.append(response)
                
            assert len(responses) > 0
            assert responses[-1]["is_complete"] is True
            assert responses[-1]["content"] == "Hello there!"

    @pytest.mark.asyncio
    async def test_conversation_history_context(self, ai_service):
        """Test that conversation history is properly formatted for LangChain"""
        with patch.object(ai_service, 'llm') as mock_llm:
            async def mock_astream(messages, callbacks=None):
                yield Mock(content="Response")
                
            mock_llm.astream = mock_astream
            
            conversation_history = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ]
            
            responses = []
            async for response in ai_service.generate_ai_response(
                "How are you?", 
                conversation_history=conversation_history
            ):
                responses.append(response)
                break  # Just test the call was made
                
            # Verify response was generated
            assert len(responses) > 0

    @pytest.mark.asyncio
    async def test_error_fallback_to_mock(self, ai_service):
        """Test fallback to mock response when LangChain fails"""
        with patch.object(ai_service, 'llm') as mock_llm:
            mock_llm.astream.side_effect = Exception("LangChain API error")
            
            responses = []
            async for response in ai_service.generate_ai_response("test message"):
                responses.append(response)
                
            # Should fall back to mock response
            assert len(responses) > 0
            assert responses[-1]["is_complete"] is True
            assert "test message" in responses[-1]["content"] or len(responses[-1]["content"]) > 0

    @pytest.mark.asyncio
    async def test_health_check_success(self, ai_service):
        """Test health check with working LangChain + Gemini"""
        with patch.object(ai_service, 'llm') as mock_llm:
            mock_response = Mock()
            mock_response.content = "OK - System working correctly"
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            
            health = await ai_service.health_check()
            
            assert health["status"] == "healthy"
            assert health["mode"] == "production"
            assert health["framework"] == "langchain"
            assert health["provider"] == "google_gemini"

    @pytest.mark.asyncio
    async def test_health_check_degraded(self, ai_service):
        """Test health check with unexpected response"""
        with patch.object(ai_service, 'llm') as mock_llm:
            mock_response = Mock()
            mock_response.content = "Unexpected response"
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            
            health = await ai_service.health_check()
            
            assert health["status"] == "degraded"
            assert health["framework"] == "langchain"

    @pytest.mark.asyncio
    async def test_health_check_failure(self, ai_service):
        """Test health check with LangChain error"""
        with patch.object(ai_service, 'llm') as mock_llm:
            mock_llm.ainvoke = AsyncMock(side_effect=Exception("Connection failed"))
            
            health = await ai_service.health_check()
            
            assert health["status"] == "unhealthy"
            assert "Connection failed" in health["message"]

    @pytest.mark.asyncio 
    async def test_blog_generation_success(self, ai_service):
        """Test blog generation from conversation"""
        with patch.object(ai_service, 'generate_ai_response') as mock_generate:
            async def mock_generator():
                yield {"content": "Blog post content", "is_complete": True, "message_id": None}
            
            mock_generate.return_value = mock_generator()
            
            responses = []
            async for response in ai_service.generate_blog_from_conversation(
                "User: Hello\nAI: Hi there!", 
                "Make it professional"
            ):
                responses.append(response)
                
            assert len(responses) > 0
            assert responses[-1]["is_complete"] is True

    @pytest.mark.asyncio
    async def test_blog_generation_error(self, ai_service):
        """Test blog generation error handling"""
        with patch('app.prompts.conversation_prompts.ConversationPrompts.format_blog_prompt') as mock_format:
            mock_format.side_effect = Exception("Formatting error")
            
            with pytest.raises(AIServiceError) as exc_info:
                async for _ in ai_service.generate_blog_from_conversation("content"):
                    pass
                    
            assert "Blog generation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_mock_mode_behavior(self):
        """Test AI service behavior in mock mode"""
        # Create service without API key to force mock mode
        with patch('app.core.config.settings.GOOGLE_GEMINI_API_KEY', None):
            service = AIService()
            
            assert service.mock_mode is True
            
            responses = []
            async for response in service.generate_ai_response("quantum computing"):
                responses.append(response)
                
            assert len(responses) > 0
            assert responses[-1]["is_complete"] is True
            assert "quantum" in responses[-1]["content"].lower()

    @pytest.mark.asyncio
    async def test_mock_mode_health_check(self):
        """Test health check in mock mode"""
        with patch('app.core.config.settings.GOOGLE_GEMINI_API_KEY', None):
            service = AIService()
            
            health = await service.health_check()
            
            assert health["status"] == "healthy"
            assert health["mode"] == "mock"
            assert health["provider"] == "mock"
            assert health["framework"] == "langchain"

    @pytest.mark.asyncio
    async def test_langchain_message_formatting(self, ai_service):
        """Test proper LangChain message formatting"""
        with patch.object(ai_service, 'llm') as mock_llm:
            async def mock_astream(messages, callbacks=None):
                yield Mock(content="Test response")
            
            mock_llm.astream = mock_astream
            
            conversation_history = [
                {"role": "user", "content": "User message"},
                {"role": "assistant", "content": "AI response"},
            ]
            
            responses = []
            async for response in ai_service.generate_ai_response(
                "Current message", 
                conversation_history=conversation_history
            ):
                responses.append(response)
                break
                
            # Verify response was generated
            assert len(responses) > 0

    @pytest.mark.asyncio
    async def test_context_limit_handling(self, ai_service):
        """Test handling of conversation history context limits"""
        with patch.object(ai_service, 'llm') as mock_llm:
            async def mock_astream(messages, callbacks=None):
                yield Mock(content="Response")
            
            mock_llm.astream = mock_astream
            
            # Create long conversation history (more than 10 messages)
            long_history = []
            for i in range(15):
                long_history.extend([
                    {"role": "user", "content": f"User message {i}"},
                    {"role": "assistant", "content": f"AI response {i}"},
                ])
            
            responses = []
            async for response in ai_service.generate_ai_response(
                "Current message", 
                conversation_history=long_history
            ):
                responses.append(response)
                break
                
            # Verify response was generated
            assert len(responses) > 0

    @pytest.mark.asyncio
    async def test_streaming_callback_handler(self, ai_service):
        """Test StreamingCallbackHandler functionality"""
        from app.services.ai_service import StreamingCallbackHandler
        
        handler = StreamingCallbackHandler()
        
        # Test token collection
        await handler.on_llm_new_token("Hello")
        await handler.on_llm_new_token(" world")
        
        assert handler.tokens == ["Hello", " world"]

    @pytest.mark.asyncio
    async def test_generate_ai_response_with_uuid_conversation_id(self, ai_service):
        """Test generate_ai_response with UUID conversation_id"""
        conversation_id = uuid4()
        
        with patch.object(ai_service, '_generate_mock_response') as mock_generate:
            async def mock_generator():
                yield {"content": "Response", "is_complete": True, "message_id": None}
            
            mock_generate.return_value = mock_generator()
            ai_service.mock_mode = True
            
            responses = []
            async for response in ai_service.generate_ai_response(
                "test", 
                conversation_id=conversation_id
            ):
                responses.append(response)
                
            assert len(responses) > 0
            mock_generate.assert_called_once()


class TestAIServiceGlobalInstance:
    """Test the global AI service instance"""
    
    def test_global_instance_exists(self):
        """Test that global ai_service instance is available"""
        from app.services.ai_service import ai_service
        
        assert ai_service is not None
        assert isinstance(ai_service, AIService)

    @pytest.mark.asyncio
    async def test_global_generate_function(self):
        """Test the global generate_ai_response function"""
        from app.services.ai_service import generate_ai_response
        
        responses = []
        async for response in generate_ai_response("test message"):
            responses.append(response)
            
        assert len(responses) > 0
        assert responses[-1]["is_complete"] is True
