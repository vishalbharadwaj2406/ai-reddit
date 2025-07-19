"""
Test AI Streaming API Endpoints

Tests for AI conversation streaming endpoints including:
- POST /conversations/{conversation_id}/messages - Send message to AI
- GET /conversations/{conversation_id}/stream - Stream AI response via SSE

This file tests the API layer specifically - ensuring endpoints
return correct responses and handle SSE streaming properly.

Following TDD methodology:
1. Write comprehensive tests covering edge cases
2. Run tests (they should fail initially)
3. Implement the actual endpoints to pass these tests
"""

import pytest
import json
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
from uuid import uuid4

from app.main import app
from app.dependencies.auth import get_current_user
from app.core.database import get_db

# Import from test infrastructure
from tests.utils.test_helpers import APITestClient, assert_api_response_format


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    user = Mock()
    user.user_id = uuid4()
    user.user_name = "testuser"
    user.email = "test@example.com"
    user.status = "active"
    return user


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    db = Mock()
    
    def mock_refresh(obj):
        """Mock refresh that sets timestamps if they're None"""
        if hasattr(obj, 'created_at') and obj.created_at is None:
            obj.created_at = datetime.now(timezone.utc)
        if hasattr(obj, 'updated_at') and obj.updated_at is None:
            obj.updated_at = datetime.now(timezone.utc)
            
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.side_effect = mock_refresh
    
    return db


@pytest.fixture
def client(mock_user, mock_db):
    """Create test client with mocked dependencies"""
    
    def override_get_current_user():
        return mock_user
    
    def override_get_db():
        return mock_db
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def mock_conversation():
    """Create a mock conversation object"""
    conversation = Mock()
    conversation.conversation_id = uuid4()
    conversation.user_id = uuid4()
    conversation.title = "Test Conversation"
    conversation.status = "active"
    conversation.created_at = datetime.now(timezone.utc)
    conversation.updated_at = datetime.now(timezone.utc)
    return conversation


@pytest.fixture
def mock_message():
    """Create a mock message object"""
    message = Mock()
    message.message_id = uuid4()
    message.conversation_id = uuid4()
    message.user_id = uuid4()
    message.role = "user"
    message.content = "Test message"
    message.is_blog = False
    message.created_at = datetime.now(timezone.utc)
    message.updated_at = datetime.now(timezone.utc)
    return message


class TestSendMessage:
    """Test POST /conversations/{conversation_id}/messages endpoint"""
    
    def test_send_message_success(self, client, mock_user, mock_db, mock_conversation, mock_message):
        """Test successful message sending"""
        conversation_id = str(mock_conversation.conversation_id)
        mock_conversation.user_id = mock_user.user_id
        mock_conversation.status = "active"
        
        # Mock database queries using ORM pattern
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_conversation
        mock_db.query.return_value = mock_query
        
        # Mock message creation
        with patch('app.models.message.Message') as mock_message_class:
            mock_message_class.return_value = mock_message
            
            response = client.post(
                f"/api/v1/conversations/{conversation_id}/messages",
                json={"content": "Hello AI, explain quantum computing"}
            )
            
        assert response.status_code == status.HTTP_201_CREATED
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        data = response.json()
        
        # Verify response format
        assert data["success"] is True
        assert "data" in data
        assert "message" in data
        
        # Verify message data
        message_data = data["data"]
        assert "message_id" in message_data
        assert message_data["content"] == "Hello AI, explain quantum computing"
        assert message_data["role"] == "user"
        assert "created_at" in message_data
        
    def test_send_message_conversation_not_found(self, client, mock_user, mock_db):
        """Test sending message to non-existent conversation"""
        conversation_id = str(uuid4())
        
        # Mock conversation not found
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        response = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={"content": "Hello AI"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "NOT_FOUND"
        assert "not found" in data["detail"]["message"].lower()
        
    def test_send_message_unauthorized_conversation(self, client, mock_user, mock_db, mock_conversation):
        """Test sending message to conversation owned by another user"""
        conversation_id = str(mock_conversation.conversation_id)
        mock_conversation.user_id = uuid4()  # Different user
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_conversation
        mock_db.query.return_value = mock_query
        
        response = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={"content": "Hello AI"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "FORBIDDEN"
        assert "access" in data["detail"]["message"].lower()
        
    def test_send_message_empty_content(self, client, mock_user, mock_db, mock_conversation):
        """Test sending message with empty content"""
        conversation_id = str(mock_conversation.conversation_id)
        
        response = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={"content": ""}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
    def test_send_message_missing_content(self, client, mock_user, mock_db, mock_conversation):
        """Test sending message without content field"""
        conversation_id = str(mock_conversation.conversation_id)
        
        response = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
    def test_send_message_invalid_conversation_id(self, client, mock_user, mock_db):
        """Test sending message with invalid conversation ID format"""
        response = client.post(
            "/api/v1/conversations/invalid-uuid/messages",
            json={"content": "Hello AI"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
    def test_send_message_unauthenticated(self, mock_db):
        """Test sending message without authentication"""
        
        def override_get_db():
            return mock_db
            
        app.dependency_overrides[get_db] = override_get_db
        
        client = TestClient(app)
        conversation_id = str(uuid4())
        
        response = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={"content": "Hello AI"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Clean up
        app.dependency_overrides.clear()
        
    def test_send_message_archived_conversation(self, client, mock_user, mock_db, mock_conversation):
        """Test sending message to archived conversation"""
        conversation_id = str(mock_conversation.conversation_id)
        mock_conversation.status = "archived"
        mock_conversation.user_id = mock_user.user_id
        
        # Mock ORM query pattern used by send_message endpoint
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_conversation
        mock_db.query.return_value = mock_query
        
        response = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={"content": "Hello AI"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "CONVERSATION_ARCHIVED"
        assert "archived" in data["detail"]["message"].lower()


class TestStreamAIResponse:
    """Test GET /conversations/{conversation_id}/stream endpoint"""
    
    @pytest.mark.asyncio
    async def test_stream_ai_response_success(self, client, mock_user, mock_db, mock_conversation, mock_message):
        """Test successful AI response streaming"""
        conversation_id = str(mock_conversation.conversation_id)
        message_id = str(mock_message.message_id)
        mock_conversation.user_id = mock_user.user_id
        
        # Mock ORM queries for streaming endpoint
        mock_conversation_query = Mock()
        mock_conversation_query.filter.return_value = mock_conversation_query
        mock_conversation_query.first.return_value = mock_conversation
        
        mock_message_query = Mock()
        mock_message_query.filter.return_value = mock_message_query
        mock_message_query.first.return_value = mock_message
        
        # Set up query returns in order they're called
        mock_db.query.side_effect = [mock_conversation_query, mock_message_query]
        
        # Mock AI service
        with patch('app.services.ai_service.generate_ai_response') as mock_ai_service:
            # Mock streaming response
            async def mock_stream():
                yield {"content": "Quantum computing is", "is_complete": False}
                yield {"content": " a revolutionary technology", "is_complete": False}
                yield {"content": " that uses quantum mechanics.", "is_complete": True}
                
            mock_ai_service.return_value = mock_stream()
            
            response = client.get(
                f"/api/v1/conversations/{conversation_id}/stream",
                params={"message_id": message_id},
                headers={"Accept": "text/event-stream"}
            )
            
        assert response.status_code == status.HTTP_200_OK
        assert "text/event-stream" in response.headers["content-type"]
        
        # Parse SSE events
        events = []
        for line in response.text.split('\n'):
            if line.startswith('data: '):
                events.append(json.loads(line[6:]))
                
        # Verify SSE events contain proper API wrapper format
        assert len(events) >= 3
        for event in events:
            assert "success" in event
            assert "data" in event
            assert "message" in event
            assert event["success"] is True
            
    def test_stream_conversation_not_found(self, client, mock_user, mock_db):
        """Test streaming for non-existent conversation"""
        conversation_id = str(uuid4())
        message_id = str(uuid4())
        
        # Mock conversation not found using ORM pattern
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        response = client.get(
            f"/api/v1/conversations/{conversation_id}/stream",
            params={"message_id": message_id},
            headers={"Accept": "text/event-stream"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_stream_message_not_found(self, client, mock_user, mock_db, mock_conversation):
        """Test streaming for non-existent message"""
        conversation_id = str(mock_conversation.conversation_id)
        message_id = str(uuid4())
        mock_conversation.user_id = mock_user.user_id
        
        # Mock conversation found, message not found using ORM pattern
        mock_conversation_query = Mock()
        mock_conversation_query.filter.return_value = mock_conversation_query
        mock_conversation_query.first.return_value = mock_conversation
        
        mock_message_query = Mock()
        mock_message_query.filter.return_value = mock_message_query
        mock_message_query.first.return_value = None  # Message not found
        
        mock_db.query.side_effect = [mock_conversation_query, mock_message_query]
        
        response = client.get(
            f"/api/v1/conversations/{conversation_id}/stream",
            params={"message_id": message_id},
            headers={"Accept": "text/event-stream"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_stream_unauthorized_conversation(self, client, mock_user, mock_db, mock_conversation):
        """Test streaming for conversation owned by another user"""
        conversation_id = str(mock_conversation.conversation_id)
        message_id = str(uuid4())
        mock_conversation.user_id = uuid4()  # Different user
        
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_conversation
        
        response = client.get(
            f"/api/v1/conversations/{conversation_id}/stream",
            params={"message_id": message_id},
            headers={"Accept": "text/event-stream"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    def test_stream_missing_message_id(self, client, mock_user, mock_db, mock_conversation):
        """Test streaming without message_id parameter"""
        conversation_id = str(mock_conversation.conversation_id)
        
        response = client.get(
            f"/api/v1/conversations/{conversation_id}/stream",
            headers={"Accept": "text/event-stream"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
    def test_stream_invalid_message_id(self, client, mock_user, mock_db, mock_conversation):
        """Test streaming with invalid message_id format"""
        conversation_id = str(mock_conversation.conversation_id)
        
        response = client.get(
            f"/api/v1/conversations/{conversation_id}/stream",
            params={"message_id": "invalid-uuid"},
            headers={"Accept": "text/event-stream"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
    @pytest.mark.asyncio
    async def test_stream_ai_service_error(self, client, mock_user, mock_db, mock_conversation, mock_message):
        """Test streaming when AI service fails"""
        conversation_id = str(mock_conversation.conversation_id)
        message_id = str(mock_message.message_id)
        mock_conversation.user_id = mock_user.user_id
        
        # Mock ORM queries for both conversation and message
        mock_conversation_query = Mock()
        mock_conversation_query.filter.return_value = mock_conversation_query
        mock_conversation_query.first.return_value = mock_conversation
        
        mock_message_query = Mock()
        mock_message_query.filter.return_value = mock_message_query
        mock_message_query.first.return_value = mock_message
        
        mock_db.query.side_effect = [mock_conversation_query, mock_message_query]
        
        # Mock AI service failure
        with patch('app.api.v1.conversations.generate_ai_response') as mock_ai_service:
            mock_ai_service.side_effect = Exception("AI service unavailable")
            
            response = client.get(
                f"/api/v1/conversations/{conversation_id}/stream",
                params={"message_id": message_id},
                headers={"Accept": "text/event-stream"}
            )
            
        assert response.status_code == status.HTTP_200_OK
        assert "text/event-stream" in response.headers["content-type"]
        
        # Should contain error event
        error_found = False
        for line in response.text.split('\n'):
            if line.startswith('data: '):
                event = json.loads(line[6:])
                if not event.get("success", True):
                    error_found = True
                    assert "errorCode" in event
                    break
                    
        assert error_found, "Expected error event in SSE stream"
        
    def test_stream_archived_conversation(self, client, mock_user, mock_db, mock_conversation):
        """Test streaming for archived conversation"""
        conversation_id = str(mock_conversation.conversation_id)
        message_id = str(uuid4())
        mock_conversation.status = "archived"
        mock_conversation.user_id = mock_user.user_id
        
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_conversation
        
        response = client.get(
            f"/api/v1/conversations/{conversation_id}/stream",
            params={"message_id": message_id},
            headers={"Accept": "text/event-stream"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    def test_stream_unauthenticated(self, mock_db):
        """Test streaming without authentication"""
        
        def override_get_db():
            return mock_db
            
        app.dependency_overrides[get_db] = override_get_db
        
        client = TestClient(app)
        conversation_id = str(uuid4())
        message_id = str(uuid4())
        
        response = client.get(
            f"/api/v1/conversations/{conversation_id}/stream",
            params={"message_id": message_id},
            headers={"Accept": "text/event-stream"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Clean up
        app.dependency_overrides.clear()


class TestIntegrationFlow:
    """Test the complete flow of sending message and streaming response"""
    
    @pytest.mark.asyncio
    async def test_complete_ai_conversation_flow(self, client, mock_user, mock_db, mock_conversation):
        """Test the complete flow: send message -> stream response"""
        conversation_id = str(mock_conversation.conversation_id)
        mock_conversation.user_id = mock_user.user_id
        
        # Step 1: Send message
        mock_message = Mock()
        mock_message.message_id = uuid4()
        mock_message.content = "Explain quantum computing"
        mock_message.role = "user"
        mock_message.created_at = datetime.now(timezone.utc)
        
        # Mock ORM query for send message endpoint
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_conversation
        mock_db.query.return_value = mock_query
        
        with patch('app.models.message.Message') as mock_message_class:
            mock_message_class.return_value = mock_message
            
            # Send message
            send_response = client.post(
                f"/api/v1/conversations/{conversation_id}/messages",
                json={"content": "Explain quantum computing"}
            )
            
        assert send_response.status_code == status.HTTP_201_CREATED
        send_data = send_response.json()
        message_id = send_data["data"]["message_id"]
        
        # Step 2: Stream AI response
        # Reset mock_db for streaming endpoint
        mock_conversation_query = Mock()
        mock_conversation_query.filter.return_value = mock_conversation_query
        mock_conversation_query.first.return_value = mock_conversation
        
        mock_message_query = Mock()
        mock_message_query.filter.return_value = mock_message_query
        mock_message_query.first.return_value = mock_message
        
        mock_db.query.side_effect = [mock_conversation_query, mock_message_query]
        
        with patch('app.api.v1.conversations.generate_ai_response') as mock_ai_service:
            async def mock_stream():
                yield {"content": "Quantum computing utilizes", "is_complete": False}
                yield {"content": " quantum mechanical phenomena", "is_complete": False}
                yield {"content": " to process information.", "is_complete": True}
                
            mock_ai_service.return_value = mock_stream()
            
            stream_response = client.get(
                f"/api/v1/conversations/{conversation_id}/stream",
                params={"message_id": message_id},
                headers={"Accept": "text/event-stream"}
            )
            
        assert stream_response.status_code == status.HTTP_200_OK
        assert "text/event-stream" in stream_response.headers["content-type"]
        
        # Verify the complete flow worked
        events = []
        for line in stream_response.text.split('\n'):
            if line.startswith('data: '):
                events.append(json.loads(line[6:]))
                
        assert len(events) >= 3  # Should have multiple streaming events
        
        # Verify all events have proper format
        for event in events:
            assert "success" in event
            assert "data" in event
            assert "message" in event
            if event["success"]:
                assert "content" in event["data"]
                assert "is_complete" in event["data"]
