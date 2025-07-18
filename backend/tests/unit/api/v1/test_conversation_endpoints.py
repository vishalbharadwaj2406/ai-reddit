"""
Test Conversation API Endpoints

Tests for conversation management endpoints including creation, listing,
retrieval, and archiving.

This file tests the API layer specifically - ensuring endpoints
return correct responses and handle errors properly.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import Mock
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
    db.refresh = mock_refresh
    db.rollback.return_value = None
    return db


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def api_client(client):
    """Enhanced API test client"""
    return APITestClient(client)


class TestConversationEndpoints:
    """Test suite for conversation API endpoints"""

    def test_create_conversation_success_basic(self, client, mock_user, mock_db):
        """Test successful conversation creation with minimal data"""
        # Create mock conversation with proper attributes
        mock_conversation = Mock()
        mock_conversation.conversation_id = uuid4()
        mock_conversation.user_id = mock_user.user_id
        mock_conversation.title = "New Chat"
        mock_conversation.forked_from = None
        mock_conversation.status = "active"
        mock_conversation.created_at = datetime.now(timezone.utc)
        mock_conversation.updated_at = datetime.now(timezone.utc)

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            # Make the request
            response = client.post("/api/v1/conversations")

            # Verify response
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert_api_response_format(data, success=True)
            assert data["message"] == "Conversation created successfully"

            conversation_data = data["data"]["conversation"]
            assert conversation_data["title"] == "New Chat"
            assert conversation_data["user_id"] == str(mock_user.user_id)
            assert conversation_data["status"] == "active"
            assert conversation_data["forked_from"] is None
            assert "conversation_id" in conversation_data
            assert "created_at" in conversation_data

        finally:
            # Clean up dependency overrides
            app.dependency_overrides.clear()

    def test_create_conversation_with_title(self, client, mock_user, mock_db):
        """Test successful conversation creation with custom title"""
        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            # Make request with custom title
            response = client.post("/api/v1/conversations", json={"title": "My Custom Chat"})

            # Verify response
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert_api_response_format(data, success=True)

            conversation_data = data["data"]["conversation"]
            assert conversation_data["title"] == "My Custom Chat"

        finally:
            # Clean up dependency overrides
            app.dependency_overrides.clear()

    def test_create_conversation_unauthorized(self, client):
        """Test conversation creation without authentication"""
        response = client.post("/api/v1/conversations", json={"title": "Test Conversation"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "AUTH_REQUIRED"
        assert data["detail"]["message"] == "Authentication required"

    def test_create_conversation_invalid_token(self, client):
        """Test conversation creation with invalid token"""
        response = client.post(
            "/api/v1/conversations",
            json={"title": "Test Conversation"},
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "INVALID_TOKEN"
        assert data["detail"]["message"] == "Invalid or expired token"

    def test_create_conversation_invalid_forked_from(self, client, mock_user, mock_db):
        """Test conversation creation with invalid forked_from UUID"""
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.post("/api/v1/conversations", json={"forked_from": "invalid-uuid"})

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            data = response.json()
            assert "detail" in data
            # FastAPI validation error for invalid UUID format

        finally:
            app.dependency_overrides.clear()

    def test_create_conversation_empty_title_uses_default(self, client, mock_user, mock_db):
        """Test conversation creation with empty title uses default"""
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.post("/api/v1/conversations", json={"title": "   "})

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            conversation_data = data["data"]["conversation"]
            assert conversation_data["title"] == "New Chat"

        finally:
            app.dependency_overrides.clear()

    # GET /conversations endpoint tests
    def test_get_conversations_success_empty_list(self, client, mock_user, mock_db):
        """Test successful retrieval of conversations when user has no conversations"""
        # Mock query result - empty list
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        mock_db.query.return_value = mock_query

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.get("/api/v1/conversations")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert_api_response_format(data, success=True)
            assert data["message"] == "Conversations retrieved successfully"
            assert data["data"] == []

        finally:
            app.dependency_overrides.clear()

    def test_get_conversations_success_with_data(self, client, mock_user, mock_db):
        """Test successful retrieval of conversations with data"""
        # Create mock conversations
        mock_conv1 = Mock()
        mock_conv1.conversation_id = uuid4()
        mock_conv1.title = "Chat about AI"
        mock_conv1.forked_from = None
        mock_conv1.created_at = datetime.now(timezone.utc)
        mock_conv1.updated_at = datetime.now(timezone.utc)

        mock_conv2 = Mock()
        mock_conv2.conversation_id = uuid4()
        mock_conv2.title = "Python Discussion"
        mock_conv2.forked_from = uuid4()  # Forked conversation
        mock_conv2.created_at = datetime.now(timezone.utc)
        mock_conv2.updated_at = datetime.now(timezone.utc)

        # Mock query result
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_conv1, mock_conv2]

        mock_db.query.return_value = mock_query

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.get("/api/v1/conversations")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert_api_response_format(data, success=True)
            assert data["message"] == "Conversations retrieved successfully"

            conversations = data["data"]
            assert len(conversations) == 2

            # Check first conversation
            assert conversations[0]["title"] == "Chat about AI"
            assert conversations[0]["forked_from"] is None
            assert "conversation_id" in conversations[0]
            assert "created_at" in conversations[0]
            assert "updated_at" in conversations[0]

            # Check second conversation (forked)
            assert conversations[1]["title"] == "Python Discussion"
            assert conversations[1]["forked_from"] is not None

        finally:
            app.dependency_overrides.clear()

    def test_get_conversations_with_pagination(self, client, mock_user, mock_db):
        """Test conversations retrieval with pagination parameters"""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        mock_db.query.return_value = mock_query

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.get("/api/v1/conversations?limit=10&offset=5")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert_api_response_format(data, success=True)

            # Verify that pagination was applied to the query
            mock_query.limit.assert_called_with(10)
            mock_query.offset.assert_called_with(5)

        finally:
            app.dependency_overrides.clear()

    def test_get_conversations_pagination_limits(self, client, mock_user, mock_db):
        """Test conversations retrieval respects pagination limits"""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        mock_db.query.return_value = mock_query

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            # Test maximum limit enforcement
            response = client.get("/api/v1/conversations?limit=200")

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            # FastAPI validation should reject limit > 100

        finally:
            app.dependency_overrides.clear()

    def test_get_conversations_unauthorized(self, client):
        """Test conversations retrieval without authentication"""
        response = client.get("/api/v1/conversations")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "AUTH_REQUIRED"

    def test_get_conversations_invalid_token(self, client):
        """Test conversations retrieval with invalid token"""
        response = client.get(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "INVALID_TOKEN"

    def test_get_conversations_database_error(self, client, mock_user, mock_db):
        """Test conversations retrieval handles database errors gracefully"""
        # Mock database error
        mock_db.query.side_effect = Exception("Database connection failed")

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.get("/api/v1/conversations")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data

        finally:
            app.dependency_overrides.clear()

    # GET /conversations/{conversation_id} endpoint tests
    def test_get_conversation_by_id_success_with_messages(self, client, mock_user, mock_db):
        """Test successful retrieval of conversation with messages"""
        conversation_id = str(uuid4())

        # Create mock conversation
        mock_conversation = Mock()
        mock_conversation.conversation_id = uuid4()
        mock_conversation.user_id = mock_user.user_id
        mock_conversation.title = "AI Discussion"
        mock_conversation.forked_from = None
        mock_conversation.created_at = datetime.now(timezone.utc)
        mock_conversation.updated_at = datetime.now(timezone.utc)

        # Create mock messages
        mock_msg1 = Mock()
        mock_msg1.message_id = uuid4()
        mock_msg1.role = "user"
        mock_msg1.content = "Hello AI"
        mock_msg1.is_blog = False
        mock_msg1.created_at = datetime.now(timezone.utc)

        mock_msg2 = Mock()
        mock_msg2.message_id = uuid4()
        mock_msg2.role = "assistant"
        mock_msg2.content = "Hello! How can I help you today?"
        mock_msg2.is_blog = False
        mock_msg2.created_at = datetime.now(timezone.utc)

        # Mock database queries
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_conversation
        mock_db.query.return_value = mock_query

        # Mock messages relationship
        mock_conversation.messages = [mock_msg1, mock_msg2]

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.get(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert_api_response_format(data, success=True)
            assert data["message"] == "Conversation retrieved successfully"

            conversation_data = data["data"]
            assert conversation_data["conversationId"] == str(mock_conversation.conversation_id)
            assert conversation_data["title"] == "AI Discussion"
            assert conversation_data["forkedFrom"] is None
            assert "createdAt" in conversation_data

            # Check messages
            messages = conversation_data["messages"]
            assert len(messages) == 2

            # Check first message (user)
            assert messages[0]["role"] == "user"
            assert messages[0]["content"] == "Hello AI"
            assert messages[0]["isBlog"] is False
            assert "messageId" in messages[0]
            assert "createdAt" in messages[0]

            # Check second message (assistant)
            assert messages[1]["role"] == "assistant"
            assert messages[1]["content"] == "Hello! How can I help you today?"
            assert messages[1]["isBlog"] is False

        finally:
            app.dependency_overrides.clear()

    def test_get_conversation_by_id_success_empty_messages(self, client, mock_user, mock_db):
        """Test successful retrieval of conversation with no messages"""
        conversation_id = str(uuid4())

        # Create mock conversation with no messages
        mock_conversation = Mock()
        mock_conversation.conversation_id = uuid4()
        mock_conversation.user_id = mock_user.user_id
        mock_conversation.title = "New Conversation"
        mock_conversation.forked_from = None
        mock_conversation.created_at = datetime.now(timezone.utc)
        mock_conversation.updated_at = datetime.now(timezone.utc)
        mock_conversation.messages = []

        # Mock database queries
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_conversation
        mock_db.query.return_value = mock_query

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.get(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert_api_response_format(data, success=True)

            conversation_data = data["data"]
            assert conversation_data["title"] == "New Conversation"
            assert conversation_data["messages"] == []

        finally:
            app.dependency_overrides.clear()

    def test_get_conversation_by_id_forked_conversation(self, client, mock_user, mock_db):
        """Test successful retrieval of conversation that was forked from a post"""
        conversation_id = str(uuid4())
        post_id = uuid4()

        # Create mock forked conversation
        mock_conversation = Mock()
        mock_conversation.conversation_id = uuid4()
        mock_conversation.user_id = mock_user.user_id
        mock_conversation.title = "Expanding on AI Ethics"
        mock_conversation.forked_from = post_id
        mock_conversation.created_at = datetime.now(timezone.utc)
        mock_conversation.updated_at = datetime.now(timezone.utc)
        mock_conversation.messages = []

        # Mock database queries
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_conversation
        mock_db.query.return_value = mock_query

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.get(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            conversation_data = data["data"]
            assert conversation_data["title"] == "Expanding on AI Ethics"
            assert conversation_data["forkedFrom"] == str(post_id)

        finally:
            app.dependency_overrides.clear()

    def test_get_conversation_by_id_not_found(self, client, mock_user, mock_db):
        """Test conversation retrieval when conversation doesn't exist"""
        conversation_id = str(uuid4())

        # Mock database query returning None
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.get(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert "detail" in data
            assert data["detail"]["error"] == "NOT_FOUND"
            assert data["detail"]["message"] == "Conversation not found"

        finally:
            app.dependency_overrides.clear()

    def test_get_conversation_by_id_forbidden_other_user(self, client, mock_user, mock_db):
        """Test conversation retrieval when user doesn't own the conversation"""
        conversation_id = str(uuid4())
        other_user_id = uuid4()

        # Create mock conversation owned by different user
        mock_conversation = Mock()
        mock_conversation.conversation_id = uuid4()
        mock_conversation.user_id = other_user_id  # Different user
        mock_conversation.title = "Someone else's conversation"
        mock_conversation.messages = []

        # Mock database queries
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_conversation
        mock_db.query.return_value = mock_query

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.get(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == status.HTTP_403_FORBIDDEN
            data = response.json()
            assert "detail" in data
            assert data["detail"]["error"] == "FORBIDDEN"
            assert data["detail"]["message"] == "Access denied to conversation"

        finally:
            app.dependency_overrides.clear()

    def test_get_conversation_by_id_unauthorized(self, client):
        """Test conversation retrieval without authentication"""
        conversation_id = str(uuid4())

        response = client.get(f"/api/v1/conversations/{conversation_id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "AUTH_REQUIRED"

    def test_get_conversation_by_id_invalid_token(self, client):
        """Test conversation retrieval with invalid token"""
        conversation_id = str(uuid4())

        response = client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "INVALID_TOKEN"

    def test_get_conversation_by_id_invalid_uuid(self, client, mock_user, mock_db):
        """Test conversation retrieval with invalid UUID format"""
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.get("/api/v1/conversations/invalid-uuid")

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            # FastAPI validation error for invalid UUID format

        finally:
            app.dependency_overrides.clear()

    def test_get_conversation_by_id_database_error(self, client, mock_user, mock_db):
        """Test conversation retrieval handles database errors gracefully"""
        conversation_id = str(uuid4())

        # Mock database error
        mock_db.query.side_effect = Exception("Database connection failed")

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.get(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data

        finally:
            app.dependency_overrides.clear()

    # ===== DELETE CONVERSATION TESTS =====

    def test_archive_conversation_success(self, client, mock_user, mock_db):
        """Test successful conversation archiving"""
        conversation_id = str(uuid4())

        # Create mock conversation
        mock_conversation = Mock()
        mock_conversation.conversation_id = uuid4()
        mock_conversation.user_id = mock_user.user_id
        mock_conversation.title = "Test Conversation"
        mock_conversation.status = "active"
        mock_conversation.created_at = datetime.now(timezone.utc)
        mock_conversation.updated_at = datetime.now(timezone.utc)

        # Mock database queries
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_conversation
        mock_db.query.return_value = mock_query

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.delete(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert_api_response_format(data, success=True)
            assert data["message"] == "Conversation archived successfully"

            # Verify the conversation status was updated to archived
            assert mock_conversation.status == "archived"
            # Verify database operations were called
            mock_db.commit.assert_called_once()

        finally:
            app.dependency_overrides.clear()

    def test_archive_conversation_not_found(self, client, mock_user, mock_db):
        """Test archiving non-existent conversation returns 404"""
        conversation_id = str(uuid4())

        # Mock database query returning None
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.delete(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert "detail" in data
            assert data["detail"]["error"] == "NOT_FOUND"

        finally:
            app.dependency_overrides.clear()

    def test_archive_conversation_forbidden_other_user(self, client, mock_user, mock_db):
        """Test archiving conversation from another user returns 403"""
        conversation_id = str(uuid4())
        other_user_id = uuid4()

        # Create mock conversation owned by different user
        mock_conversation = Mock()
        mock_conversation.conversation_id = uuid4()
        mock_conversation.user_id = other_user_id  # Different user
        mock_conversation.title = "Other User's Conversation"
        mock_conversation.status = "active"

        # Mock database queries
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_conversation
        mock_db.query.return_value = mock_query

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.delete(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == status.HTTP_403_FORBIDDEN
            data = response.json()
            assert "detail" in data
            assert data["detail"]["error"] == "FORBIDDEN"

        finally:
            app.dependency_overrides.clear()

    def test_archive_conversation_unauthorized(self, client, mock_db):
        """Test archiving conversation without authentication returns 401"""
        conversation_id = str(uuid4())

        # Don't override the get_current_user dependency
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.delete(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        finally:
            app.dependency_overrides.clear()

    def test_archive_conversation_invalid_uuid(self, client, mock_user, mock_db):
        """Test archiving conversation with invalid UUID format"""
        invalid_conversation_id = "not-a-valid-uuid"

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.delete(f"/api/v1/conversations/{invalid_conversation_id}")

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            data = response.json()
            assert "detail" in data

        finally:
            app.dependency_overrides.clear()

    def test_archive_conversation_already_archived(self, client, mock_user, mock_db):
        """Test archiving an already archived conversation"""
        conversation_id = str(uuid4())

        # Create mock conversation that's already archived
        mock_conversation = Mock()
        mock_conversation.conversation_id = uuid4()
        mock_conversation.user_id = mock_user.user_id
        mock_conversation.title = "Already Archived Conversation"
        mock_conversation.status = "archived"
        mock_conversation.created_at = datetime.now(timezone.utc)
        mock_conversation.updated_at = datetime.now(timezone.utc)

        # Mock database queries
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_conversation
        mock_db.query.return_value = mock_query

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.delete(f"/api/v1/conversations/{conversation_id}")

            # Should still return 200 OK but indicate it was already archived
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert_api_response_format(data, success=True)
            assert "already archived" in data["message"].lower()

        finally:
            app.dependency_overrides.clear()

    def test_archive_conversation_database_error(self, client, mock_user, mock_db):
        """Test archiving conversation handles database errors gracefully"""
        conversation_id = str(uuid4())

        # Mock database error
        mock_db.query.side_effect = Exception("Database connection failed")

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        try:
            response = client.delete(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data

        finally:
            app.dependency_overrides.clear()