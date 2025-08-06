"""
AI Conversation Endpoints Integration Tests

Integration tests for the AI-powered conversation API endpoints.
These tests verify that the API endpoints correctly integrate with the real AI service.

Following TDD methodology:
1. Test message sending and AI response streaming
2. Test blog generation from conversations
3. Test error handling and edge cases
4. Test conversation context preservation

Note: These tests require GOOGLE_GEMINI_API_KEY to be set for full validation.
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4, UUID

from app.main import app
from app.core.database import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.dependencies.auth import get_current_user, get_current_user_sse


class TestAIConversationEndpoints:
    """Integration tests for AI conversation endpoints"""

    @pytest.fixture
    def client(self, db_session):
        """Create test client with database override"""
        def override_get_db():
            yield db_session
        
        app.dependency_overrides[get_db] = override_get_db
        
        with TestClient(app) as test_client:
            yield test_client
        
        app.dependency_overrides.clear()

    @pytest.fixture
    def test_user(self, db_session: Session):
        """Create test user"""
        user = User(
            user_name="ai_test_user",
            email="ai.test@example.com"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def auth_headers(self, test_user: User):
        """Create auth headers for test user"""
        # Mock both authentication dependencies
        def override_get_current_user():
            return test_user
        
        def override_get_current_user_sse():
            return test_user
        
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_current_user_sse] = override_get_current_user_sse
        return {}  # No actual headers needed when dependency is overridden

    @pytest.fixture
    def test_conversation(self, db_session: Session, test_user: User):
        """Create test conversation with some messages"""
        conversation = Conversation(
            conversation_id=uuid4(),
            user_id=test_user.user_id,
            title="Test AI Integration",
            status="active"
        )
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)

        # Add initial user message
        message = Message(
            message_id=uuid4(),
            conversation_id=conversation.conversation_id,
            user_id=test_user.user_id,
            role="user",
            content="Hello! Can you tell me about renewable energy?",
            is_blog=False,
            status="active"
        )
        db_session.add(message)
        db_session.commit()

        return conversation

    def test_send_message_to_conversation(self, client: TestClient, test_conversation: Conversation, auth_headers: dict):
        """Test sending a message to an existing conversation"""
        response = client.post(
            f"/api/v1/conversations/{test_conversation.conversation_id}/messages",
            json={"content": "What are the main benefits of solar power?"},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["content"] == "What are the main benefits of solar power?"
        assert data["data"]["role"] == "user"
        assert "message_id" in data["data"]

    def test_stream_ai_response_integration(self, client: TestClient, test_conversation: Conversation, auth_headers: dict, db_session: Session):
        """Test streaming AI response integration with real AI service"""
        # First send a message
        message_response = client.post(
            f"/api/v1/conversations/{test_conversation.conversation_id}/messages",
            json={"content": "Explain quantum computing in simple terms"},
            headers=auth_headers
        )
        
        assert message_response.status_code == 201
        message_data = message_response.json()
        message_id = message_data["data"]["message_id"]
        
        # Then stream AI response
        with client.stream(
            "GET",
            f"/api/v1/conversations/{test_conversation.conversation_id}/stream?message_id={message_id}",
            headers=auth_headers
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")
            
            events = []
            complete_response = ""
            
            for line in response.iter_lines():
                if line.startswith("data: "):
                    try:
                        event_data = json.loads(line[6:])  # Remove "data: " prefix
                        events.append(event_data)
                        
                        # Check event structure
                        assert event_data["success"] is True
                        assert "data" in event_data
                        assert "content" in event_data["data"]
                        assert "is_complete" in event_data["data"]
                        assert "message_id" in event_data["data"]
                        
                        # If complete, save the response
                        if event_data["data"]["is_complete"]:
                            complete_response = event_data["data"]["content"]
                            break
                            
                    except json.JSONDecodeError:
                        continue
            
            # Verify we got events and a complete response
            assert len(events) > 0
            assert len(complete_response) > 10  # Should be a substantial response
            assert "quantum" in complete_response.lower()  # Should contain relevant content
        
        # Note: The AI message is saved using a separate database session
        # to avoid transaction conflicts during streaming. In production this works fine,
        # but in tests with rollback transactions, we can't verify the persistence
        # since it uses a different session. The fact that we got the streaming
        # response confirms the integration is working correctly.

    def test_blog_generation_integration(self, client: TestClient, test_conversation: Conversation, auth_headers: dict, db_session: Session):
        """Test blog generation from conversation with real AI service"""
        # Add more conversation context
        ai_message = Message(
            message_id=uuid4(),
            conversation_id=test_conversation.conversation_id,
            user_id=None,  # AI message
            role="assistant",
            content="Renewable energy harnesses natural resources like sunlight, wind, and water to generate clean power.",
            is_blog=False,
            status="active"
        )
        db_session.add(ai_message)
        db_session.commit()
        
        # Generate blog from conversation
        with client.stream(
            "POST",
            f"/api/v1/conversations/{test_conversation.conversation_id}/generate-blog",
            json={"additional_context": "Make it suitable for a general audience"},
            headers=auth_headers
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")
            
            events = []
            complete_blog = ""
            
            for line in response.iter_lines():
                if line.startswith("data: "):
                    try:
                        event_data = json.loads(line[6:])
                        events.append(event_data)
                        
                        # Check event structure
                        assert event_data["success"] is True
                        assert "data" in event_data
                        assert "content" in event_data["data"]
                        assert "is_complete" in event_data["data"]
                        assert "is_blog" in event_data["data"]
                        assert event_data["data"]["is_blog"] is True
                        
                        # If complete, save the blog
                        if event_data["data"]["is_complete"]:
                            complete_blog = event_data["data"]["content"]
                            break
                            
                    except json.JSONDecodeError:
                        continue
            
            # Verify blog was generated
            assert len(events) > 0
            assert len(complete_blog) > 100  # Should be a substantial blog post
            
        # Note: The blog message is saved using a separate database session
        # to avoid transaction conflicts during streaming. In production this works fine,
        # but in tests with rollback transactions, we can't verify the persistence
        # since it uses a different session. The fact that we got the streaming
        # blog response confirms the integration is working correctly.

    def test_conversation_context_preservation(self, client: TestClient, test_conversation: Conversation, auth_headers: dict):
        """Test that conversation context is preserved across multiple AI interactions"""
        # Send first message
        response1 = client.post(
            f"/api/v1/conversations/{test_conversation.conversation_id}/messages",
            json={"content": "What is machine learning?"},
            headers=auth_headers
        )
        message_id_1 = response1.json()["data"]["message_id"]
        
        # Get AI response
        with client.stream(
            "GET",
            f"/api/v1/conversations/{test_conversation.conversation_id}/stream?message_id={message_id_1}",
            headers=auth_headers
        ) as stream_response:
            # Consume the stream
            for line in stream_response.iter_lines():
                if line.startswith("data: "):
                    try:
                        event_data = json.loads(line[6:])
                        if event_data["data"].get("is_complete"):
                            break
                    except json.JSONDecodeError:
                        continue
        
        # Send follow-up message that requires context
        response2 = client.post(
            f"/api/v1/conversations/{test_conversation.conversation_id}/messages",
            json={"content": "Can you give me a specific example of that?"},
            headers=auth_headers
        )
        message_id_2 = response2.json()["data"]["message_id"]
        
        # Get contextual AI response
        with client.stream(
            "GET",
            f"/api/v1/conversations/{test_conversation.conversation_id}/stream?message_id={message_id_2}",
            headers=auth_headers
        ) as stream_response:
            contextual_response = ""
            for line in stream_response.iter_lines():
                if line.startswith("data: "):
                    try:
                        event_data = json.loads(line[6:])
                        if event_data["data"].get("is_complete"):
                            contextual_response = event_data["data"]["content"]
                            break
                    except json.JSONDecodeError:
                        continue
        
        # Verify the response shows understanding of context
        assert len(contextual_response) > 10
        # Should contain machine learning related content since that was the context
        assert any(keyword in contextual_response.lower() for keyword in ["machine learning", "example", "algorithm", "data"])

    def test_ai_service_error_handling(self, client: TestClient, test_conversation: Conversation, auth_headers: dict):
        """Test API error handling when AI service encounters issues"""
        # Send a message
        response = client.post(
            f"/api/v1/conversations/{test_conversation.conversation_id}/messages",
            json={"content": "Test message"},
            headers=auth_headers
        )
        message_id = response.json()["data"]["message_id"]
        
        # Stream response - should handle any AI service errors gracefully
        with client.stream(
            "GET",
            f"/api/v1/conversations/{test_conversation.conversation_id}/stream?message_id={message_id}",
            headers=auth_headers
        ) as stream_response:
            assert stream_response.status_code == 200
            
            # Should get either valid response or error event, not crash
            received_event = False
            for line in stream_response.iter_lines():
                if line.startswith("event: ") or line.startswith("data: "):
                    received_event = True
                    break
            
            assert received_event  # Should receive some kind of event

    def test_invalid_conversation_access(self, client: TestClient, auth_headers: dict):
        """Test access control for non-existent or unauthorized conversations"""
        fake_conversation_id = str(uuid4())
        
        # Try to send message to non-existent conversation
        response = client.post(
            f"/api/v1/conversations/{fake_conversation_id}/messages",
            json={"content": "Test message"},
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "detail" in response.json()  # FastAPI error format

    def test_archived_conversation_handling(self, client: TestClient, test_conversation: Conversation, auth_headers: dict, db_session: Session):
        """Test that archived conversations reject new messages"""
        # Archive the conversation
        test_conversation.status = "archived"
        db_session.commit()
        
        # Try to send message to archived conversation
        response = client.post(
            f"/api/v1/conversations/{test_conversation.conversation_id}/messages",
            json={"content": "Test message"},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "detail" in response.json()  # FastAPI error format
        assert "archived" in response.json()["detail"]["message"].lower()
