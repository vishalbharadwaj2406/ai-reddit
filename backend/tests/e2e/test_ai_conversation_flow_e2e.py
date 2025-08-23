"""
AI Conversation Flow E2E Tests

End-to-end tests for complete AI conversation workflows.
Tests the full stack from API endpoints to AI service integration.

Following TDD methodology:
1. Test complete conversation workflows
2. Test SSE streaming endpoints  
3. Test message persistence and retrieval
4. Test error scenarios in production context
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from uuid import UUID

from app.main import app
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User


class TestAIConversationFlowE2E:
    """End-to-end tests for AI conversation workflows"""

    @pytest.fixture
    def client(self, db_session):
        """FastAPI test client with database override"""
        def override_get_db():
            yield db_session
        
        app.dependency_overrides[get_db] = override_get_db
        
        with TestClient(app) as test_client:
            yield test_client
        
        app.dependency_overrides.clear()

    @pytest.fixture
    def test_user(self, db_session):
        """Create a real test user in the database"""
        user = User(
            user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            user_name="e2e_test_user",
            email="e2e@example.com"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def auth_override(self, test_user):
        """Override authentication for testing"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        yield
        app.dependency_overrides.clear()

    def test_complete_conversation_workflow(self, client, auth_override):
        """Test complete conversation creation and messaging workflow"""
        # Step 1: Create a conversation
        conversation_response = client.post(
            "/api/v1/conversations/",
            json={"title": "AI Integration Test Conversation"}
        )
        
        assert conversation_response.status_code == 201
        conversation_data = conversation_response.json()
        assert conversation_data["success"] is True
        
        conversation_id = conversation_data["data"]["conversation"]["conversation_id"]

        # Step 2: Send a message to the conversation
        message_response = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={"content": "Hello AI! Tell me about renewable energy."}
        )
        
        assert message_response.status_code == 201
        message_data = message_response.json()
        assert message_data["success"] is True
        assert "message_id" in message_data["data"]

        # Step 3: Verify conversation contains the message
        get_conversation_response = client.get(f"/api/v1/conversations/{conversation_id}")
        
        assert get_conversation_response.status_code == 200
        conv_data = get_conversation_response.json()
        assert conv_data["success"] is True
        
        messages = conv_data["data"]["messages"]
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        assert len(user_messages) >= 1
        assert "renewable energy" in user_messages[0]["content"]

    def test_sse_streaming_endpoint_format(self, client, auth_override):
        """Test SSE streaming endpoint returns proper format"""
        # Create conversation and message first
        conversation_response = client.post(
            "/api/v1/conversations/",
            json={"title": "Streaming Test"}
        )
        conversation_id = conversation_response.json()["data"]["conversation"]["conversation_id"]
        
        message_response = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={"content": "Test streaming response"}
        )
        message_id = message_response.json()["data"]["message_id"]

        # Test SSE endpoint (note: TestClient doesn't fully support SSE, so we test the route exists)
        sse_response = client.get(
            f"/api/v1/conversations/{conversation_id}/stream",
            params={"message_id": message_id}
        )
        
        # Should not return 404 (route exists)
        assert sse_response.status_code != 404

    def test_conversation_not_found_error(self, client, auth_override):
        """Test proper error handling for non-existent conversation"""
        fake_conversation_id = "00000000-0000-0000-0000-000000000000"
        
        response = client.get(f"/api/v1/conversations/{fake_conversation_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "error" in error_data["detail"]
        assert error_data["detail"]["error"] == "NOT_FOUND"

    def test_message_to_nonexistent_conversation(self, client, auth_override):
        """Test sending message to non-existent conversation"""
        fake_conversation_id = "00000000-0000-0000-0000-000000000000"
        
        response = client.post(
            f"/api/v1/conversations/{fake_conversation_id}/messages",
            json={"content": "This should fail"}
        )
        
        assert response.status_code == 404
        error_data = response.json()
        assert "error" in error_data["detail"]

    def test_unauthorized_conversation_access(self, client):
        """Test that unauthorized users cannot access conversations"""
        # Don't use auth_override fixture for this test
        response = client.get("/api/v1/conversations/")
        
        assert response.status_code == 401

    def test_conversation_ownership_enforcement(self, client, db_session, test_user, auth_override):
        """Test that users can only access their own conversations"""
        # Create conversation with one user
        conversation_response = client.post(
            "/api/v1/conversations/",
            json={"title": "Private Conversation"}
        )
        conversation_id = conversation_response.json()["data"]["conversation"]["conversation_id"]

        # Create a different user
        different_user = User(
            user_name="different_user",
            email="different@example.com"
        )
        db_session.add(different_user)
        db_session.commit()
        db_session.refresh(different_user)

        # Override with different user
        app.dependency_overrides[get_current_user] = lambda: different_user

        # Try to access conversation with different user
        response = client.get(f"/api/v1/conversations/{conversation_id}")
        
        assert response.status_code == 403

    def test_archived_conversation_restrictions(self, client, auth_override):
        """Test that archived conversations cannot receive new messages"""
        # Create and archive conversation
        conversation_response = client.post(
            "/api/v1/conversations/",
            json={"title": "To Be Archived"}
        )
        conversation_id = conversation_response.json()["data"]["conversation"]["conversation_id"]

        # Archive the conversation 
        archive_response = client.delete(f"/api/v1/conversations/{conversation_id}")
        assert archive_response.status_code == 200

        # Try to send message to archived conversation
        message_response = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={"content": "This should be rejected"}
        )
        
        assert message_response.status_code == 400
        error_data = message_response.json()
        assert "archived" in error_data["detail"]["message"].lower()

    def test_conversation_list_pagination(self, client, auth_override):
        """Test conversation listing with pagination"""
        # Create multiple conversations
        for i in range(5):
            client.post(
                "/api/v1/conversations/",
                json={"title": f"Test Conversation {i}"}
            )

        # Test pagination
        response = client.get("/api/v1/conversations/?limit=3&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) <= 3

    def test_invalid_uuid_format_handling(self, client, auth_override):
        """Test proper error handling for invalid UUID formats"""
        invalid_id = "not-a-valid-uuid"
        
        response = client.get(f"/api/v1/conversations/{invalid_id}")
        
        assert response.status_code == 422
        error_data = response.json()
        assert "invalid" in error_data["detail"]["message"].lower()

    @pytest.mark.asyncio
    async def test_ai_service_integration_in_context(self):
        """Test that AI service integrates properly in application context"""
        from app.services.ai_service import ai_service
        
        # Test that global AI service instance is properly configured
        assert ai_service is not None
        
        # Test health check
        health = await ai_service.health_check()
        assert "status" in health
        assert health["status"] in ["healthy", "unhealthy", "degraded"]
        
        # Test basic response generation
        responses = []
        async for response in ai_service.generate_ai_response("Test message"):
            responses.append(response)
            
        assert len(responses) > 0
        assert responses[-1]["is_complete"] is True
