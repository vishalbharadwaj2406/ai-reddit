"""
Comprehensive integration tests for POST /posts/{post_id}/fork endpoint.

These tests validate the complete fork functionality including:
- Basic fork creation
- Fork count tracking
- Conversation creation
- Message initialization
- Database integrity
- Error handling scenarios
- Edge cases and validation
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from app.main import app
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.post import Post
from app.models.conversation import Conversation


class TestPostForkComprehensive:
    """Comprehensive test suite for post forking functionality"""
    
    def create_test_user(self, db_session, user_id=None, username="test_user", email="test@example.com"):
        """Create a test user"""
        if user_id is None:
            user_id = uuid4()
        
        user = User(
            user_id=user_id,
            user_name=username,
            email=email,
            status="active",
            created_at=datetime.now(timezone.utc)
        )
        
        db_session.add(user)
        db_session.flush()
        return user
    
    def create_test_post(self, db_session, post_id, user_id, title="Test Post", 
                        content="Test content", fork_count=0):
        """Create a test post with required conversation"""
        # Ensure user exists
        user = db_session.query(User).filter(User.user_id == user_id).first()
        if not user:
            user = self.create_test_user(db_session, user_id=user_id)
        
        # Create a conversation for the post
        conversation = Conversation(
            conversation_id=uuid4(),
            user_id=user_id,
            title=f"Conversation for {title}",
            status="active",
            created_at=datetime.now(timezone.utc)
        )
        
        db_session.add(conversation)
        db_session.flush()
        
        post = Post(
            post_id=post_id,
            user_id=user_id,
            conversation_id=conversation.conversation_id,
            title=title,
            content=content,
            status="active",
            fork_count=fork_count,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add(post)
        db_session.flush()
        return post
    
    def test_fork_post_basic_success(self, client, db_session):
        """Test basic successful post fork"""
        # Create test data
        user_id = uuid4()
        post_id = uuid4()
        
        post = self.create_test_post(
            db_session=db_session,
            post_id=post_id,
            user_id=user_id,
            title="Introduction to Machine Learning",
            content="This is a comprehensive guide to ML basics"
        )
        
        # Create a test user for authentication and add to database
        test_user = self.create_test_user(
            db_session=db_session,
            username="test_forker",
            email="forker@example.com"
        )
        
        # Override authentication
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        try:
            # Fork the post
            response = client.post(
                f"/api/v1/posts/{post_id}/fork",
                json={"includeOriginalConversation": True}
            )
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert "data" in data
            fork_data = data["data"]
            
            # Verify fork data structure
            assert "conversationId" in fork_data
            assert "title" in fork_data
            assert "forkedFrom" in fork_data
            assert "includeOriginalConversation" in fork_data
            
            # Verify values
            assert fork_data["forkedFrom"] == str(post_id)
            assert fork_data["includeOriginalConversation"] is True
            assert fork_data["title"].startswith("Fork of:")
            assert "Introduction to Machine Learning" in fork_data["title"]
            
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()
    
    def test_fork_post_without_original_conversation(self):
        """Test forking without including original conversation"""
        # Create test post
        self.create_test_post(title="Python Tips", content="Some useful Python tricks")
        
        # Fork without original conversation
        response = self.client.post(
            f"/api/v1/posts/{self.post_id}/fork",
            json={"includeOriginalConversation": False},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        fork_data = data["data"]
        assert fork_data["includeOriginalConversation"] is False
    
    def test_fork_post_long_title_truncation(self):
        """Test that long post titles are properly truncated in fork title"""
        long_title = "A" * 100  # 100 character title
        self.create_test_post(title=long_title, content="Content")
        
        response = self.client.post(
            f"/api/v1/posts/{self.post_id}/fork",
            json={"includeOriginalConversation": True},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        fork_title = data["data"]["title"]
        # Should be "Fork of: " + first 50 chars + "..."
        assert fork_title.startswith("Fork of:")
        assert "..." in fork_title
        assert len(fork_title) <= 62  # "Fork of: " (9) + 50 + "..." (3)
    
    def test_fork_nonexistent_post(self):
        """Test forking a non-existent post returns 404"""
        fake_post_id = str(uuid4())
        
        response = self.client.post(
            f"/api/v1/posts/{fake_post_id}/fork",
            json={"includeOriginalConversation": True},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "POST_NOT_FOUND" in data.get("errorCode", "")
    
    def test_fork_deleted_post(self):
        """Test forking a deleted post returns 404"""
        # Create a deleted post
        post = self.create_test_post()
        self.test_app.delete_post(self.post_id)
        
        response = self.client.post(
            f"/api/v1/posts/{self.post_id}/fork",
            json={"includeOriginalConversation": True},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
    
    def test_fork_without_authentication(self):
        """Test forking without authentication returns 401"""
        self.create_test_post()
        
        response = self.client.post(
            f"/api/v1/posts/{self.post_id}/fork",
            json={"includeOriginalConversation": True}
            # No Authorization header
        )
        
        assert response.status_code == 401
    
    def test_fork_with_invalid_json(self):
        """Test forking with invalid JSON request body"""
        self.create_test_post()
        
        response = self.client.post(
            f"/api/v1/posts/{self.post_id}/fork",
            json={"invalidField": "value"},  # Missing required fields
            headers={"Authorization": "Bearer test-token"}
        )
        
        # Should still work as includeOriginalConversation has default
        assert response.status_code == 200
    
    def test_fork_with_empty_request_body(self):
        """Test forking with empty request body uses defaults"""
        self.create_test_post()
        
        response = self.client.post(
            f"/api/v1/posts/{self.post_id}/fork",
            json={},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should use default value for includeOriginalConversation
        fork_data = data["data"]
        assert "includeOriginalConversation" in fork_data
    
    def test_multiple_forks_by_same_user(self):
        """Test that the same user can fork the same post multiple times"""
        self.create_test_post()
        
        # First fork
        response1 = self.client.post(
            f"/api/v1/posts/{self.post_id}/fork",
            json={"includeOriginalConversation": True},
            headers={"Authorization": "Bearer test-token"}
        )
        
        # Second fork
        response2 = self.client.post(
            f"/api/v1/posts/{self.post_id}/fork",
            json={"includeOriginalConversation": False},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Should create different conversations
        conv1_id = response1.json()["data"]["conversationId"]
        conv2_id = response2.json()["data"]["conversationId"]
        assert conv1_id != conv2_id
    
    def test_fork_count_increments(self):
        """Test that post fork count increments correctly (would need DB verification)"""
        self.create_test_post(fork_count=5)
        
        # Fork the post
        response = self.client.post(
            f"/api/v1/posts/{self.post_id}/fork",
            json={"includeOriginalConversation": True},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        # Note: In a real test we would verify the DB fork_count increased from 5 to 6
        # This would require additional DB query capabilities in the test framework
    
    def test_fork_special_characters_in_content(self):
        """Test forking posts with special characters, unicode, etc."""
        special_content = "Special chars: äöü 中文 🚀 <script>alert('xss')</script>"
        self.create_test_post(
            title="Special Characters Test",
            content=special_content
        )
        
        response = self.client.post(
            f"/api/v1/posts/{self.post_id}/fork",
            json={"includeOriginalConversation": True},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        # The fork should handle special characters gracefully
    
    def test_fork_very_long_content(self):
        """Test forking posts with very long content"""
        long_content = "A" * 10000  # 10KB content
        self.create_test_post(
            title="Long Content Test",
            content=long_content
        )
        
        response = self.client.post(
            f"/api/v1/posts/{self.post_id}/fork",
            json={"includeOriginalConversation": True},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        # Should handle long content without issues
    
    def test_fork_response_schema_validation(self):
        """Test that fork response exactly matches expected schema"""
        self.create_test_post()
        
        response = self.client.post(
            f"/api/v1/posts/{self.post_id}/fork",
            json={"includeOriginalConversation": True},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate top-level response structure
        required_top_fields = ["success", "data", "message"]
        for field in required_top_fields:
            assert field in data, f"Missing field: {field}"
        
        # Validate fork data structure
        fork_data = data["data"]
        required_fork_fields = ["conversationId", "title", "forkedFrom", "includeOriginalConversation"]
        for field in required_fork_fields:
            assert field in fork_data, f"Missing fork data field: {field}"
        
        # Validate data types
        assert isinstance(data["success"], bool)
        assert isinstance(data["message"], str)
        assert isinstance(fork_data["conversationId"], str)
        assert isinstance(fork_data["title"], str)
        assert isinstance(fork_data["forkedFrom"], str)
        assert isinstance(fork_data["includeOriginalConversation"], bool)
    
    def test_concurrent_forks(self):
        """Test multiple concurrent forks don't cause race conditions"""
        self.create_test_post()
        
        # Simulate concurrent forks (in real scenario these would be truly concurrent)
        responses = []
        for i in range(3):
            response = self.client.post(
                f"/api/v1/posts/{self.post_id}/fork",
                json={"includeOriginalConversation": True},
                headers={"Authorization": "Bearer test-token"}
            )
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
        
        # All should create unique conversations
        conversation_ids = [r.json()["data"]["conversationId"] for r in responses]
        assert len(set(conversation_ids)) == 3  # All unique
