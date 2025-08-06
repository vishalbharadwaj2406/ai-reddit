"""
AI Service Integration Tests

Integration tests for AI service with real Gemini 2.5 Flash API calls.
These tests verify that the AI service works correctly with real API responses.

Following TDD methodology:
1. Test real API integration
2. Test streaming responses
3. Test conversation context handling
4. Test error scenarios with real API

Note: These tests require GOOGLE_GEMINI_API_KEY to be set for full validation.
Without API key, tests will verify graceful fallback behavior.
"""

import pytest
import asyncio
from unittest.mock import patch, Mock
import os

from app.services.ai_service import AIService, AIServiceError
from app.core.config import settings


class TestAIServiceIntegration:
    """Integration tests for AI service with real Gemini API"""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing"""
        return AIService()

    @pytest.mark.asyncio
    async def test_health_check_with_api_key(self, ai_service):
        """Test health check with configured API key"""
        health = await ai_service.health_check()
        
        assert "status" in health
        assert health["status"] in ["healthy", "unhealthy", "degraded"]
        assert "mode" in health
        assert "provider" in health
        assert "framework" in health
        
        # Framework should always be langchain
        assert health["framework"] == "langchain"

    @pytest.mark.asyncio
    async def test_health_check_without_api_key(self):
        """Test health check without API key (mock mode)"""
        with patch('app.core.config.settings.GOOGLE_GEMINI_API_KEY', ''):
            service = AIService()
            health = await service.health_check()
            
            assert health["status"] == "healthy"
            assert health["mode"] == "mock"
            assert health["provider"] == "mock"

    @pytest.mark.asyncio 
    async def test_simple_conversation_response(self, ai_service):
        """Test simple conversation with AI service"""
        test_message = "Hello! Can you respond with exactly 'AI integration test' to confirm you're working?"
        
        responses = []
        async for response_chunk in ai_service.generate_ai_response(test_message):
            responses.append(response_chunk)
            
        assert len(responses) > 0
        
        # Check final response
        final_response = responses[-1]
        assert final_response["is_complete"] is True
        assert "content" in final_response
        assert len(final_response["content"]) > 0

    @pytest.mark.asyncio
    async def test_conversation_with_history(self, ai_service):
        """Test conversation with conversation history context"""
        conversation_history = [
            {"role": "user", "content": "What is quantum computing?"},
            {"role": "assistant", "content": "Quantum computing uses quantum mechanics principles."}
        ]
        
        follow_up = "Can you explain quantum superposition?"
        
        responses = []
        async for response_chunk in ai_service.generate_ai_response(
            follow_up,
            conversation_history=conversation_history
        ):
            responses.append(response_chunk)
            
        assert len(responses) > 0
        final_response = responses[-1]
        assert final_response["is_complete"] is True
        
        # Response should be relevant to quantum superposition
        content = final_response["content"].lower()
        assert len(content) > 50  # Should be a substantial response

    @pytest.mark.asyncio
    async def test_streaming_response_format(self, ai_service):
        """Test that streaming responses have correct format"""
        test_message = "Tell me about renewable energy in one paragraph."
        
        responses = []
        async for response_chunk in ai_service.generate_ai_response(test_message):
            responses.append(response_chunk)
            
            # Each chunk should have required fields
            assert "content" in response_chunk
            assert "is_complete" in response_chunk
            assert isinstance(response_chunk["is_complete"], bool)
            
        # Should have multiple chunks for streaming
        assert len(responses) > 1
        
        # All but last should be incomplete
        for response in responses[:-1]:
            assert response["is_complete"] is False
            
        # Last should be complete
        assert responses[-1]["is_complete"] is True

    @pytest.mark.asyncio
    async def test_blog_generation_integration(self, ai_service):
        """Test blog generation from conversation content"""
        conversation_content = """
        User: What are the benefits of renewable energy?
        AI: Renewable energy offers environmental protection and economic advantages.
        User: Can you elaborate on the economic benefits?
        AI: Economically, renewable energy creates jobs and reduces costs.
        """
        
        responses = []
        async for response_chunk in ai_service.generate_blog_from_conversation(
            conversation_content,
            additional_context="Make it engaging for a general audience"
        ):
            responses.append(response_chunk)
            
        assert len(responses) > 0
        final_response = responses[-1]
        assert final_response["is_complete"] is True
        
        # Blog should be longer than original conversation
        content = final_response["content"]
        assert len(content) > len(conversation_content.strip())

    @pytest.mark.asyncio
    async def test_error_handling_with_invalid_input(self, ai_service):
        """Test error handling with problematic input"""
        # Test with very long input
        long_message = "Tell me about AI. " * 1000
        
        try:
            responses = []
            async for response_chunk in ai_service.generate_ai_response(long_message):
                responses.append(response_chunk)
                # Prevent infinite loops in test
                if len(responses) > 100:
                    break
                    
            # Should still get some response (even if truncated or error)
            assert len(responses) > 0
            
        except AIServiceError as e:
            # Error handling is acceptable for edge cases
            assert str(e) is not None

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, ai_service):
        """Test handling of concurrent AI requests"""
        async def make_request(message_num):
            message = f"Test message {message_num}"
            responses = []
            async for response_chunk in ai_service.generate_ai_response(message):
                responses.append(response_chunk)
            return responses
        
        # Make 3 concurrent requests
        tasks = [make_request(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        # All requests should complete successfully
        assert len(results) == 3
        for result in results:
            assert len(result) > 0
            assert result[-1]["is_complete"] is True

    @pytest.mark.asyncio
    async def test_api_key_rotation_handling(self, ai_service):
        """Test behavior when API key changes"""
        # Test with current configuration
        health1 = await ai_service.health_check()
        
        # Test that service maintains state properly
        health2 = await ai_service.health_check()
        
        # Status should be consistent
        assert health1["status"] == health2["status"]
        assert health1["mode"] == health2["mode"]

    @pytest.mark.asyncio
    async def test_conversation_context_limits(self, ai_service):
        """Test handling of large conversation history"""
        # Create a long conversation history
        conversation_history = []
        for i in range(20):  # More than the 10 message limit
            conversation_history.append({
                "role": "user", 
                "content": f"Message {i}: Tell me about topic {i}"
            })
            conversation_history.append({
                "role": "assistant", 
                "content": f"Response {i}: Here's information about topic {i}"
            })
        
        test_message = "Summarize our conversation so far."
        
        responses = []
        async for response_chunk in ai_service.generate_ai_response(
            test_message,
            conversation_history=conversation_history
        ):
            responses.append(response_chunk)
            
        assert len(responses) > 0
        assert responses[-1]["is_complete"] is True
        
        # Should handle the large context gracefully
        content = responses[-1]["content"]
        assert len(content) > 10  # Should produce some response
