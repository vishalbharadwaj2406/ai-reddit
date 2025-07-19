"""
Test Gemini AI Integration

Production-ready tests for Google Gemini API integration.
These tests cover real-world scenarios that will occur when using Gemini API.

Following TDD methodology:
1. Write comprehensive tests for production scenarios
2. Run tests (they should fail initially)
3. Implement Gemini integration to pass these tests
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
import json

from app.services.ai_service import AIService, AIServiceError
from app.prompts.conversation_prompts import ConversationPrompts


class TestGeminiAPIIntegration:
    """Test real Gemini API integration scenarios"""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing"""
        service = AIService()
        service.mock_mode = False  # Test real AI mode
        return service

    @pytest.mark.asyncio
    async def test_api_key_validation_failure(self, ai_service):
        """Test handling of invalid/missing API keys"""
        with patch('google.generativeai.configure') as mock_configure:
            mock_configure.side_effect = Exception("Invalid API key")
            
            with pytest.raises(AIServiceError) as exc_info:
                async for _ in ai_service.generate_ai_response("test message"):
                    pass
                    
            assert "API key" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_network_timeout_retry(self, ai_service):
        """Test retry mechanism for network timeouts"""
        with patch('google.generativeai.GenerativeModel') as mock_model:
            # Simulate timeout then success
            mock_instance = mock_model.return_value
            mock_instance.generate_content_async.side_effect = [
                asyncio.TimeoutError("Request timeout"),
                AsyncMock(text="Response after retry", parts=[Mock(text="Response after retry")])
            ]
            
            responses = []
            async for response in ai_service.generate_ai_response("test message"):
                responses.append(response)
                
            assert len(responses) > 0
            assert responses[-1]["is_complete"] is True
            assert "retry" in responses[-1]["content"].lower() or responses[-1]["content"]

    @pytest.mark.asyncio 
    async def test_rate_limiting_backoff(self, ai_service):
        """Test exponential backoff for rate limits (429 errors)"""
        import google.api_core.exceptions as gcp_exceptions
        
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_instance = mock_model.return_value
            
            # Simulate rate limit then success
            rate_limit_error = gcp_exceptions.ResourceExhausted("Rate limit exceeded")
            rate_limit_error.code = 429
            
            mock_instance.generate_content_async.side_effect = [
                rate_limit_error,
                AsyncMock(text="Success after backoff", parts=[Mock(text="Success after backoff")])
            ]
            
            responses = []
            async for response in ai_service.generate_ai_response("test message"):
                responses.append(response)
                
            assert len(responses) > 0
            assert responses[-1]["is_complete"] is True

    @pytest.mark.asyncio
    async def test_quota_exceeded_error(self, ai_service):
        """Test handling of quota exceeded errors"""
        import google.api_core.exceptions as gcp_exceptions
        
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_instance = mock_model.return_value
            
            quota_error = gcp_exceptions.ResourceExhausted("Quota exceeded")
            quota_error.code = 403
            mock_instance.generate_content_async.side_effect = quota_error
            
            with pytest.raises(AIServiceError) as exc_info:
                async for _ in ai_service.generate_ai_response("test message"):
                    pass
                    
            assert "quota" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_malformed_response_handling(self, ai_service):
        """Test handling of malformed API responses"""
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_instance = mock_model.return_value
            
            # Mock response with missing expected fields
            mock_response = Mock()
            mock_response.text = None
            mock_response.parts = []
            mock_instance.generate_content_async.return_value = mock_response
            
            with pytest.raises(AIServiceError) as exc_info:
                async for _ in ai_service.generate_ai_response("test message"):
                    pass
                    
            assert "malformed" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_streaming_interruption_recovery(self, ai_service):
        """Test recovery from interrupted streams"""
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_instance = mock_model.return_value
            
            # Create a generator that fails mid-stream
            async def failing_generator():
                yield Mock(text="First part", parts=[Mock(text="First part")])
                yield Mock(text=" second part", parts=[Mock(text=" second part")])
                raise ConnectionError("Network interrupted")
                
            mock_instance.generate_content_async.return_value = failing_generator()
            
            responses = []
            with pytest.raises(AIServiceError):
                async for response in ai_service.generate_ai_response("test message"):
                    responses.append(response)
                    
            # Should have received partial responses before failure
            assert len(responses) >= 1
            assert not responses[-1]["is_complete"]

    @pytest.mark.asyncio
    async def test_long_response_handling(self, ai_service):
        """Test handling of very long AI responses (>8K tokens)"""
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_instance = mock_model.return_value
            
            # Simulate a very long response
            long_text = "This is a very long response. " * 1000  # ~6K chars
            mock_response = Mock()
            mock_response.text = long_text
            mock_response.parts = [Mock(text=long_text)]
            mock_instance.generate_content_async.return_value = mock_response
            
            responses = []
            async for response in ai_service.generate_ai_response("test message"):
                responses.append(response)
                
            # Should break into reasonable chunks
            assert len(responses) > 10  # Should be chunked
            assert responses[-1]["is_complete"] is True
            
            # Reconstruct full response
            full_response = "".join(r["content"] for r in responses if not r["content"].startswith("This is a very long"))
            # Note: This test verifies chunking behavior

    @pytest.mark.asyncio
    async def test_content_safety_filtering(self, ai_service):
        """Test integration with Gemini's built-in content safety"""
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_instance = mock_model.return_value
            
            # Simulate content safety block
            safety_error = Exception("Content blocked by safety filters")
            mock_instance.generate_content_async.side_effect = safety_error
            
            with pytest.raises(AIServiceError) as exc_info:
                async for _ in ai_service.generate_ai_response("inappropriate content"):
                    pass
                    
            assert "safety" in str(exc_info.value).lower() or "blocked" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_concurrent_request_limits(self, ai_service):
        """Test handling of concurrent request limits"""
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_instance = mock_model.return_value
            mock_instance.generate_content_async.return_value = AsyncMock(
                text="Response", parts=[Mock(text="Response")]
            )
            
            # Simulate multiple concurrent requests
            tasks = []
            for i in range(5):
                task = ai_service.generate_ai_response(f"message {i}")
                tasks.append([chunk async for chunk in task])
                
            # All should complete without interference
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that all completed successfully
            for result in results:
                assert not isinstance(result, Exception)
                assert len(result) > 0

    @pytest.mark.asyncio
    async def test_environment_variable_validation(self, ai_service):
        """Test proper environment variable validation"""
        with patch.dict('os.environ', {}, clear=True):
            # Remove GOOGLE_API_KEY from environment
            with pytest.raises(AIServiceError) as exc_info:
                async for _ in ai_service.generate_ai_response("test"):
                    pass
                    
            assert "api key" in str(exc_info.value).lower() or "environment" in str(exc_info.value).lower()


class TestPromptTemplateSystem:
    """Test the prompt template management system"""

    def test_conversation_prompt_loading(self):
        """Test loading conversation prompts"""
        prompts = ConversationPrompts()
        
        # Should have required prompt types
        assert hasattr(prompts, 'system_prompt')
        assert hasattr(prompts, 'conversation_prompt')
        assert hasattr(prompts, 'blog_generation_prompt')
        
        # System prompt should be non-empty
        assert len(prompts.system_prompt) > 0
        assert isinstance(prompts.system_prompt, str)

    def test_prompt_template_variables(self):
        """Test prompt template variable substitution"""
        prompts = ConversationPrompts()
        
        # Test conversation prompt with variables
        formatted = prompts.format_conversation_prompt(
            user_message="What is quantum computing?",
            conversation_history=[
                {"role": "user", "content": "Hello"}, 
                {"role": "assistant", "content": "Hi there!"}
            ]
        )
        
        assert "What is quantum computing?" in formatted
        assert "Hello" in formatted or "Hi there!" in formatted

    def test_blog_generation_prompt(self):
        """Test blog generation specific prompts"""
        prompts = ConversationPrompts()
        
        formatted = prompts.format_blog_prompt(
            conversation_content="Discussion about AI",
            additional_context="Focus on practical applications"
        )
        
        assert "blog" in formatted.lower()
        assert "Discussion about AI" in formatted
        assert "practical applications" in formatted

    def test_prompt_validation(self):
        """Test prompt template validation"""
        prompts = ConversationPrompts()
        
        # Should validate required variables
        with pytest.raises(ValueError):
            prompts.format_conversation_prompt(user_message="", conversation_history=[])
            
        # Should handle None values gracefully
        formatted = prompts.format_conversation_prompt(
            user_message="test",
            conversation_history=None
        )
        assert "test" in formatted


class TestAIServiceConfiguration:
    """Test AI service configuration and health checks"""

    def test_health_check_with_real_config(self):
        """Test health check with real Gemini configuration"""
        service = AIService()
        service.mock_mode = False
        
        # This will test actual configuration loading
        # Will fail until we implement real Gemini integration
        health = asyncio.run(service.health_check())
        
        assert "status" in health
        # Initially should be unhealthy until we implement Gemini
        assert health["status"] in ["healthy", "unhealthy"]

    def test_configuration_loading(self):
        """Test that AI service loads configuration properly"""
        service = AIService()
        
        # Should have configuration attributes after real implementation
        assert hasattr(service, 'mock_mode')
        
        # After implementation, should have:
        # assert hasattr(service, 'api_key')
        # assert hasattr(service, 'model_name')
        # assert hasattr(service, 'generation_config')

    def test_error_message_formatting(self):
        """Test that error messages are user-friendly"""
        service = AIService()
        
        # Test error creation
        error = AIServiceError("API key not configured")
        assert "API key" in str(error)
        
        # Error messages should be clear and actionable
        assert len(str(error)) > 10  # Not just a code


# Integration tests that will initially fail
class TestRealGeminiFlow:
    """Integration tests for complete Gemini flow"""

    @pytest.mark.asyncio
    async def test_complete_conversation_flow(self):
        """Test complete conversation flow with real prompts"""
        service = AIService()
        service.mock_mode = False
        
        conversation_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help you today?"}
        ]
        
        responses = []
        async for response in service.generate_ai_response(
            user_message="Explain quantum computing briefly",
            conversation_history=conversation_history
        ):
            responses.append(response)
            
        # Verify response structure
        assert len(responses) > 0
        assert responses[-1]["is_complete"] is True
        
        # Verify content quality (basic checks)
        full_content = "".join(r["content"] for r in responses)
        assert len(full_content) > 50  # Reasonable response length
        assert "quantum" in full_content.lower()

    @pytest.mark.asyncio 
    async def test_blog_generation_flow(self):
        """Test blog generation with real prompts"""
        service = AIService()
        service.mock_mode = False
        
        # This will test the blog generation prompt template
        responses = []
        async for response in service.generate_blog_from_conversation(
            conversation_content="User discussed quantum computing basics",
            additional_context="Make it beginner-friendly"
        ):
            responses.append(response)
            
        assert len(responses) > 0
        assert responses[-1]["is_complete"] is True
        
        full_content = "".join(r["content"] for r in responses)
        assert len(full_content) > 100  # Blog should be substantial
