"""
Test Post Creation API Endpoints

TDD tests for POST /posts endpoint with comprehensive coverage:
- Happy path scenarios
- Message validation and ownership
- Content validation
- Tag handling (auto-creation)
- Error scenarios with proper response wrapper format
- Edge cases and security validations

Following TDD methodology:
1. Write failing tests first
2. Implement minimal API to pass tests  
3. Refactor and improve
"""

import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime

from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.post import Post
from app.models.tag import Tag
from app.dependencies.auth import get_current_user
from app.core.database import get_db


class TestPostCreationEndpoints:
    """Test cases for POST /posts endpoint"""

    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)

    @pytest.fixture
    def mock_user(self):
        """Mock user fixture"""
        user = Mock(spec=User)
        user.user_id = uuid4()
        user.user_name = "testuser"
        user.email = "test@example.com"
        return user

    @pytest.fixture
    def mock_db(self):
        """Mock database session fixture"""
        return Mock()

    @pytest.fixture
    def mock_message(self):
        """Mock message fixture"""
        message = Mock(spec=Message)
        message.message_id = uuid4()
        message.content = "This is a test message"
        return message

    @pytest.fixture
    def valid_post_request(self):
        """Valid post creation request fixture"""
        return {
            "messageId": str(uuid4()),
            "title": "My Amazing Post",
            "content": "This is edited content for the post",
            "tags": ["ai", "machine-learning", "technology"],
            "isConversationVisible": True
        }

    def test_create_post_success(self, client, mock_user, mock_db, mock_message, valid_post_request):
        """Test successful post creation with proper response wrapper"""
        
        # Set up user ID for proper access control
        mock_user.user_id = uuid4()
        
        # Mock conversation and message relationship
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.user_id = mock_user.user_id  # Ensure user owns the conversation
        mock_conversation.conversation_id = uuid4()
        mock_conversation.status = "active"  # Ensure conversation is not archived
        mock_message.conversation = mock_conversation
        mock_message.conversation_id = mock_conversation.conversation_id
        
        # Mock database queries with proper chaining for SQLAlchemy
        mock_query = Mock()
        mock_join = Mock()
        mock_filter = Mock()
        
        mock_db.query.return_value = mock_query
        mock_query.join.return_value = mock_join
        mock_join.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_message
        
        # Mock tag creation/retrieval
        mock_existing_tag = Mock(spec=Tag)
        mock_existing_tag.name = "ai"
        
        # We need to set up separate query chains for different queries
        # For tags query: db.query(Tag).filter(Tag.name.in_(tag_names)).all()
        mock_tag_query = Mock()
        mock_tag_filter = Mock()
        mock_tag_filter.all.return_value = [mock_existing_tag]
        mock_tag_query.filter.return_value = mock_tag_filter
        
        # Configure the mock to return different query chains based on the model
        def mock_query_side_effect(model):
            if model == Message:
                return mock_query
            elif model == Tag:
                return mock_tag_query
            else:
                # For other queries (like checking existing posts), return a basic mock
                basic_mock = Mock()
                basic_mock.filter.return_value.first.return_value = None
                return basic_mock
                
        mock_db.query.side_effect = mock_query_side_effect
        
        # Mock post creation
        mock_post = Mock(spec=Post)
        mock_post.post_id = uuid4()
        mock_post.title = valid_post_request["title"]
        mock_post.content = valid_post_request["content"]
        mock_post.created_at = datetime.now()  # Use actual datetime instead of string
        
        # Mock database operations
        mock_db.add.return_value = None
        mock_db.flush.return_value = None
        mock_db.commit.return_value = None
        
        # The refresh operation should set the created_at timestamp
        def mock_refresh(obj):
            # When refresh is called on any Post object, set its created_at
            if hasattr(obj, 'post_id'):
                obj.created_at = datetime.now()
        mock_db.refresh.side_effect = mock_refresh
        
        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.post("/api/v1/posts", json=valid_post_request)

            assert response.status_code == 201
            data = response.json()
            
            # Verify success response wrapper
            assert data["success"] is True
            assert data["data"] is not None
            assert data["message"] == "Post created successfully"
            assert data["errorCode"] is None
            
            # Verify post data
            post_data = data["data"]
            assert "postId" in post_data
            assert post_data["title"] == valid_post_request["title"]
            assert post_data["content"] == valid_post_request["content"]
            assert "createdAt" in post_data
        finally:
            # Clean up dependency overrides
            app.dependency_overrides.clear()

    def test_create_post_message_not_found(self, client, mock_user, mock_db):
        """Test creating post with non-existent message ID"""
        
        # Set up user ID for proper access control
        mock_user.user_id = uuid4()
        
        # Mock database queries with proper chaining for SQLAlchemy
        # First query: db.query(Message).join(Conversation).filter(...).first() returns None
        mock_join_query = Mock()
        mock_join = Mock()
        mock_filter_chain = Mock()
        mock_join_query.join.return_value = mock_join
        mock_join.filter.return_value = mock_filter_chain
        mock_filter_chain.filter.return_value = mock_filter_chain
        mock_filter_chain.first.return_value = None  # Message not found in user's conversations
        
        # Second query: db.query(Message).filter(Message.message_id == message_id).first() returns None
        mock_simple_query = Mock()
        mock_simple_filter = Mock()
        mock_simple_query.filter.return_value = mock_simple_filter
        mock_simple_filter.first.return_value = None  # Message doesn't exist at all
        
        # Configure side effect to return different mocks for different calls
        query_call_count = 0
        def mock_query_side_effect(model):
            nonlocal query_call_count
            query_call_count += 1
            if model == Message:
                if query_call_count == 1:
                    return mock_join_query  # First call with join
                else:
                    return mock_simple_query  # Second call checking existence
            else:
                # For other models (like Tag), return a basic mock
                basic_mock = Mock()
                basic_mock.filter.return_value.first.return_value = None
                return basic_mock
                
        mock_db.query.side_effect = mock_query_side_effect
        
        request_data = {
            "messageId": str(uuid4()),
            "title": "Test Post",
            "content": "Test content",
            "tags": [],
            "isConversationVisible": True
        }

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.post("/api/v1/posts", json=request_data)
            
            assert response.status_code == 404
            data = response.json()
            
            # Verify error response wrapper (nested under "detail")
            assert data["detail"]["success"] is False
            assert data["detail"]["data"] is None
            assert "not found" in data["detail"]["message"].lower()
            assert data["detail"]["errorCode"] == "MESSAGE_NOT_FOUND"
        finally:
            # Clean up dependency overrides
            app.dependency_overrides.clear()

    def test_create_post_unauthorized_message(self, client, mock_user, mock_db, mock_message):
        """Test creating post from message owned by different user"""
        
        # Set up user ID for proper access control
        mock_user.user_id = uuid4()
        
        # Mock conversation and message relationship with different user
        different_user_id = uuid4()
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.user_id = different_user_id  # Different user owns the conversation
        mock_conversation.conversation_id = uuid4()
        mock_conversation.status = "active"
        mock_message.conversation = mock_conversation
        mock_message.conversation_id = mock_conversation.conversation_id
        
        # Mock database queries with proper chaining for SQLAlchemy
        # First query: db.query(Message).join(Conversation).filter(...).first() returns None (no access)
        mock_join_query = Mock()
        mock_join = Mock()
        mock_filter_chain = Mock()
        mock_join_query.join.return_value = mock_join
        mock_join.filter.return_value = mock_filter_chain
        mock_filter_chain.filter.return_value = mock_filter_chain
        mock_filter_chain.first.return_value = None  # No access to message
        
        # Second query: db.query(Message).filter(Message.message_id == message_id).first() returns message (exists)
        mock_simple_query = Mock()
        mock_simple_filter = Mock()
        mock_simple_query.filter.return_value = mock_simple_filter
        mock_simple_filter.first.return_value = mock_message  # Message exists but belongs to different user
        
        # Configure side effect to return different mocks for different calls
        query_call_count = 0
        def mock_query_side_effect(model):
            nonlocal query_call_count
            query_call_count += 1
            if model == Message:
                if query_call_count == 1:
                    return mock_join_query  # First call with join
                else:
                    return mock_simple_query  # Second call checking existence
            else:
                # For other models (like Tag), return a basic mock
                basic_mock = Mock()
                basic_mock.filter.return_value.first.return_value = None
                return basic_mock
                
        mock_db.query.side_effect = mock_query_side_effect
        
        request_data = {
            "messageId": str(mock_message.message_id),
            "title": "Test Post", 
            "content": "Test content",
            "tags": [],
            "isConversationVisible": True
        }

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.post("/api/v1/posts", json=request_data)
            
            assert response.status_code == 403
            data = response.json()
            
            # Verify error response wrapper (nested under "detail")
            assert data["detail"]["success"] is False
            assert data["detail"]["data"] is None
            assert "access denied" in data["detail"]["message"].lower()
            assert data["detail"]["errorCode"] == "FORBIDDEN"
        finally:
            # Clean up dependency overrides
            app.dependency_overrides.clear()

    def test_create_post_missing_title(self, client, mock_user, mock_db):
        """Test creating post without title - should get validation error"""
        
        # Set up user ID for proper access control
        mock_user.user_id = uuid4()
        
        request_data = {
            "messageId": str(uuid4()),
            # Missing title field
            "content": "Test content",
            "tags": [],
            "isConversationVisible": True
        }

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.post("/api/v1/posts", json=request_data)
            
            assert response.status_code == 422  # Validation error
            data = response.json()
            
            # Verify validation error format (FastAPI format)
            assert "detail" in data
            assert isinstance(data["detail"], list)
            assert any("title" in str(error).lower() for error in data["detail"])
        finally:
            # Clean up dependency overrides
            app.dependency_overrides.clear()

    def test_create_standalone_post_success(self, client, mock_user, mock_db):
        """Test creating standalone post without messageId"""
        
        # Set up user ID for proper access control
        mock_user.user_id = uuid4()
        
        # Mock tag handling (existing tag)
        mock_existing_tag = Mock(spec=Tag)
        mock_existing_tag.name = "thoughts"
        
        # Set up separate query chains for different queries
        mock_tag_query = Mock()
        mock_tag_filter = Mock()
        mock_tag_filter.all.return_value = [mock_existing_tag]
        mock_tag_query.filter.return_value = mock_tag_filter
        
        # Configure the mock to return different query chains based on the model
        def mock_query_side_effect(model):
            if model == Tag:
                return mock_tag_query
            else:
                # For other queries (like checking existing posts), return a basic mock
                basic_mock = Mock()
                basic_mock.filter.return_value.first.return_value = None
                return basic_mock
                
        mock_db.query.side_effect = mock_query_side_effect
        
        # Mock post creation
        mock_post = Mock(spec=Post)
        mock_post.post_id = uuid4()
        mock_post.title = "My Thoughts on AI"
        mock_post.content = "Today I want to share my thoughts..."
        mock_post.created_at = datetime.now()
        
        # Mock database operations
        mock_db.add.return_value = None
        mock_db.flush.return_value = None
        mock_db.commit.return_value = None
        
        # The refresh operation should set the created_at timestamp
        def mock_refresh(obj):
            if hasattr(obj, 'post_id'):
                obj.created_at = datetime.now()
        mock_db.refresh.side_effect = mock_refresh
        
        request_data = {
            # No messageId - standalone post
            "title": "My Thoughts on AI",
            "content": "Today I want to share my thoughts on AI development and its implications...",
            "tags": ["ai", "thoughts"],
            "isConversationVisible": False  # Should be ignored for standalone posts
        }

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.post("/api/v1/posts", json=request_data)
            
            assert response.status_code == 201
            data = response.json()
            
            # Verify response wrapper format (success case uses direct format)
            assert data["success"] is True
            assert data["data"] is not None
            assert "successfully" in data["message"].lower()
            
            # Verify post data structure
            post_data = data["data"]
            assert "postId" in post_data
            assert post_data["title"] == request_data["title"]
            assert post_data["content"] == request_data["content"]
            assert "createdAt" in post_data
        finally:
            # Clean up dependency overrides
            app.dependency_overrides.clear()

    def test_create_post_empty_content(self, client, mock_user, mock_db):
        """Test creating post with empty content - should get validation error"""
        
        mock_user.user_id = uuid4()
        
        request_data = {
            "messageId": str(uuid4()),
            "title": "Valid Title",
            "content": "",  # Empty content
            "tags": [],
            "isConversationVisible": True
        }

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.post("/api/v1/posts", json=request_data)
            
            assert response.status_code == 422  # Validation error
            data = response.json()
            
            # Verify validation error format (FastAPI format)
            assert "detail" in data
            assert isinstance(data["detail"], list)
            assert any("content" in str(error).lower() for error in data["detail"])
        finally:
            # Clean up dependency overrides
            app.dependency_overrides.clear()

    def test_create_post_invalid_tags(self, client, mock_user, mock_db):
        """Test creating post with invalid/empty tags"""
        
        mock_user.user_id = uuid4()
        
        # Mock database for no existing tags
        mock_tag_query = Mock()
        mock_tag_filter = Mock()
        mock_tag_filter.all.return_value = []  # No existing tags
        mock_tag_query.filter.return_value = mock_tag_filter
        
        def mock_query_side_effect(model):
            if model == Tag:
                return mock_tag_query
            else:
                basic_mock = Mock()
                basic_mock.filter.return_value.first.return_value = None
                return basic_mock
                
        mock_db.query.side_effect = mock_query_side_effect
        
        # Mock post creation
        mock_post = Mock(spec=Post)
        mock_post.post_id = uuid4()
        mock_post.title = "Test Post"
        mock_post.content = "Valid content"
        mock_post.created_at = datetime.now()
        
        mock_db.add.return_value = None
        mock_db.flush.return_value = None
        mock_db.commit.return_value = None
        
        def mock_refresh(obj):
            if hasattr(obj, 'post_id'):
                obj.created_at = datetime.now()
        mock_db.refresh.side_effect = mock_refresh
        
        request_data = {
            "title": "Test Post",
            "content": "Valid content here",
            "tags": ["", "  ", "valid-tag", "", "another-tag"],  # Mix of empty and valid tags
            "isConversationVisible": False
        }

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.post("/api/v1/posts", json=request_data)
            
            # Should still succeed, empty tags filtered out by validation
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
        finally:
            # Clean up dependency overrides
            app.dependency_overrides.clear()

    def test_create_post_archived_conversation(self, client, mock_user, mock_db, mock_message):
        """Test creating post from archived conversation - should fail"""
        
        mock_user.user_id = uuid4()
        
        # Mock conversation as archived
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.user_id = mock_user.user_id
        mock_conversation.conversation_id = uuid4()
        mock_conversation.status = "archived"  # Archived conversation
        mock_message.conversation = mock_conversation
        mock_message.conversation_id = mock_conversation.conversation_id
        
        # Mock database queries - user has access but conversation is archived
        # First query: db.query(Message).join(Conversation).filter(...).first() returns message
        mock_join_query = Mock()
        mock_join = Mock()
        mock_filter_chain = Mock()
        mock_join_query.join.return_value = mock_join
        mock_join.filter.return_value = mock_filter_chain
        mock_filter_chain.filter.return_value = mock_filter_chain
        mock_filter_chain.first.return_value = mock_message  # User has access but conversation is archived
        
        # Configure side effect for single query (no second query needed for archived check)
        def mock_query_side_effect(model):
            if model == Message:
                return mock_join_query
            else:
                # For other models (like Tag), return a basic mock
                basic_mock = Mock()
                basic_mock.filter.return_value.first.return_value = None
                return basic_mock
                
        mock_db.query.side_effect = mock_query_side_effect
        
        request_data = {
            "messageId": str(mock_message.message_id),
            "title": "Test Post",
            "content": "Test content",
            "tags": [],
            "isConversationVisible": True
        }

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.post("/api/v1/posts", json=request_data)
            
            assert response.status_code == 400
            data = response.json()
            
            # Verify error response
            assert data["detail"]["success"] is False
            assert "archived" in data["detail"]["message"].lower()
        finally:
            # Clean up dependency overrides
            app.dependency_overrides.clear()

    def test_create_post_unauthenticated(self, client, mock_db):
        """Test creating post without authentication - should fail"""
        
        request_data = {
            "title": "Test Post",
            "content": "Test content",
            "tags": [],
            "isConversationVisible": True
        }

        # Override only database, no authentication
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = client.post("/api/v1/posts", json=request_data)
            
            assert response.status_code == 401  # Unauthorized
        finally:
            # Clean up dependency overrides
            app.dependency_overrides.clear()
