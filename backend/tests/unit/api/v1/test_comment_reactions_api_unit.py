"""
Unit Tests for Comment Reactions API Endpoints

Tests the POST /comments/{comment_id}/reaction endpoint for adding/updating reactions to comments.
Follows TDD methodology with comprehensive coverage of success scenarios, validation,
authorization, and error handling.

Test Categories:
1. Success Scenarios - Valid reactions with different types
2. Validation Scenarios - Invalid reaction types, comment IDs
3. Authorization Scenarios - Authentication requirements
4. Business Logic - Reaction updates, removal, user restrictions
5. Error Scenarios - Invalid comment IDs, server errors, etc.
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4, UUID
from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.comment import Comment
from app.models.comment_reaction import CommentReaction


class TestCommentReactionsEndpoints:
    """Test class for POST /comments/{comment_id}/reaction endpoint"""

    # === SUCCESS SCENARIOS ===
    
    def test_add_new_reaction_success(self, client, mock_user, mock_comment, mock_db):
        """Test adding a new reaction to a comment"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service to return new reaction
        mock_reaction = Mock(spec=CommentReaction)
        mock_reaction.comment_id = mock_comment.comment_id
        mock_reaction.user_id = mock_user.user_id
        mock_reaction.reaction = "upvote"
        mock_reaction.created_at = datetime.now()
        
        with patch('app.services.comment_reaction_service.CommentReactionService.add_or_update_reaction') as mock_add:
            mock_add.return_value = (mock_reaction, "created")
            
            response = client.post(
                f"/api/v1/comments/{mock_comment.comment_id}/reaction",
                json={"reactionType": "upvote"}
            )
        
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["data"]["reactionType"] == "upvote"
        assert response_data["data"]["commentId"] == str(mock_comment.comment_id)
        assert "message" in response_data
        
        app.dependency_overrides.clear()

    def test_update_existing_reaction_success(self, client, mock_user, mock_comment, mock_db):
        """Test updating an existing reaction to a different type"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service to return updated reaction
        mock_reaction = Mock(spec=CommentReaction)
        mock_reaction.comment_id = mock_comment.comment_id
        mock_reaction.user_id = mock_user.user_id
        mock_reaction.reaction = "heart"
        mock_reaction.created_at = datetime.now()
        
        with patch('app.services.comment_reaction_service.CommentReactionService.add_or_update_reaction') as mock_update:
            mock_update.return_value = (mock_reaction, "updated")
            
            response = client.post(
                f"/api/v1/comments/{mock_comment.comment_id}/reaction",
                json={"reactionType": "heart"}
            )
        
        assert response.status_code == 200  # 200 for update, 201 for create
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["data"]["reactionType"] == "heart"
        assert "updated" in response_data["message"].lower()
        
        app.dependency_overrides.clear()

    def test_remove_reaction_success(self, client, mock_user, mock_comment, mock_db):
        """Test removing a reaction by setting it to the same type"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service to return None (indicating removal)
        with patch('app.services.comment_reaction_service.CommentReactionService.add_or_update_reaction') as mock_remove:
            mock_remove.return_value = (None, "removed")
            
            response = client.post(
                f"/api/v1/comments/{mock_comment.comment_id}/reaction",
                json={"reactionType": "upvote"}
            )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["data"] is None
        assert "removed" in response_data["message"].lower()
        
        app.dependency_overrides.clear()

    def test_all_valid_reaction_types_success(self, client, mock_user, mock_comment, mock_db):
        """Test that all valid reaction types are accepted"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        valid_reactions = ["upvote", "downvote", "heart", "insightful", "accurate"]
        
        for reaction_type in valid_reactions:
            mock_reaction = Mock(spec=CommentReaction)
            mock_reaction.comment_id = mock_comment.comment_id
            mock_reaction.user_id = mock_user.user_id
            mock_reaction.reaction = reaction_type
            mock_reaction.created_at = datetime.now()
            
            with patch('app.services.comment_reaction_service.CommentReactionService.add_or_update_reaction') as mock_add:
                mock_add.return_value = (mock_reaction, "created")
                
                response = client.post(
                    f"/api/v1/comments/{mock_comment.comment_id}/reaction",
                    json={"reactionType": reaction_type}
                )
            
            assert response.status_code in [200, 201]
            response_data = response.json()
            assert response_data["success"] is True
            assert response_data["data"]["reactionType"] == reaction_type
        
        app.dependency_overrides.clear()

    # === VALIDATION SCENARIOS ===
    
    def test_invalid_reaction_type_error(self, client, mock_user, mock_comment, mock_db):
        """Test that invalid reaction types return validation error"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        response = client.post(
            f"/api/v1/comments/{mock_comment.comment_id}/reaction",
            json={"reactionType": "invalid_reaction"}
        )
        
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
        assert isinstance(response_data["detail"], list)
        
        app.dependency_overrides.clear()

    def test_missing_reaction_type_error(self, client, mock_user, mock_comment, mock_db):
        """Test that missing reactionType field returns validation error"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        response = client.post(
            f"/api/v1/comments/{mock_comment.comment_id}/reaction",
            json={}  # Missing reactionType field
        )
        
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
        assert isinstance(response_data["detail"], list)
        # Check that reactionType field is mentioned in the error
        error_details = str(response_data["detail"]).lower()
        assert "reactiontype" in error_details and "required" in error_details
        
        app.dependency_overrides.clear()

    def test_malformed_comment_uuid_error(self, client, mock_user, mock_db):
        """Test that malformed comment UUID returns validation error"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        response = client.post(
            "/api/v1/comments/invalid-uuid/reaction",
            json={"reactionType": "upvote"}
        )
        
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
        assert isinstance(response_data["detail"], list)
        
        app.dependency_overrides.clear()

    def test_empty_request_body_error(self, client, mock_user, mock_comment, mock_db):
        """Test that empty request body returns validation error"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        response = client.post(
            f"/api/v1/comments/{mock_comment.comment_id}/reaction"
            # No json body
        )
        
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
        
        app.dependency_overrides.clear()

    # === AUTHORIZATION SCENARIOS ===
    
    def test_unauthenticated_request_error(self, client, mock_comment):
        """Test that unauthenticated request returns 401 error"""
        
        # Clear any existing dependency overrides to test real authentication
        app.dependency_overrides.clear()
        
        response = client.post(
            f"/api/v1/comments/{mock_comment.comment_id}/reaction",
            json={"reactionType": "upvote"}
        )
        
        assert response.status_code == 401
        response_data = response.json()
        assert "detail" in response_data

    # === BUSINESS LOGIC SCENARIOS ===
    
    def test_cannot_react_to_own_comment_error(self, client, mock_user, mock_db):
        """Test that users cannot react to their own comments"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Create a comment owned by the same user
        mock_own_comment = Mock(spec=Comment)
        mock_own_comment.comment_id = uuid4()
        mock_own_comment.user_id = mock_user.user_id  # Same user
        
        # Mock service to raise exception for own comment
        with patch('app.services.comment_reaction_service.CommentReactionService.add_or_update_reaction') as mock_react:
            from fastapi import HTTPException
            mock_react.side_effect = HTTPException(
                status_code=400,
                detail="Cannot react to your own comment"
            )
            
            response = client.post(
                f"/api/v1/comments/{mock_own_comment.comment_id}/reaction",
                json={"reactionType": "upvote"}
            )
        
        assert response.status_code == 400
        response_data = response.json()
        assert "detail" in response_data
        assert "own comment" in response_data["detail"]
        
        app.dependency_overrides.clear()

    # === ERROR SCENARIOS ===
    
    def test_nonexistent_comment_error(self, client, mock_user, mock_db):
        """Test that reacting to non-existent comment returns 404"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service to raise exception for non-existent comment
        with patch('app.services.comment_reaction_service.CommentReactionService.add_or_update_reaction') as mock_react:
            from fastapi import HTTPException
            mock_react.side_effect = HTTPException(status_code=404, detail="Comment not found")
            
            fake_comment_id = uuid4()
            response = client.post(
                f"/api/v1/comments/{fake_comment_id}/reaction",
                json={"reactionType": "upvote"}
            )
        
        assert response.status_code == 404
        response_data = response.json()
        assert "detail" in response_data
        assert "Comment not found" in response_data["detail"]
        
        app.dependency_overrides.clear()

    def test_deleted_comment_error(self, client, mock_user, mock_db):
        """Test that reacting to deleted comment returns 410 error"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service to raise exception for deleted comment
        with patch('app.services.comment_reaction_service.CommentReactionService.add_or_update_reaction') as mock_react:
            from fastapi import HTTPException
            mock_react.side_effect = HTTPException(
                status_code=410,
                detail="Comment has been deleted"
            )
            
            deleted_comment_id = uuid4()
            response = client.post(
                f"/api/v1/comments/{deleted_comment_id}/reaction",
                json={"reactionType": "upvote"}
            )
        
        assert response.status_code == 410
        response_data = response.json()
        assert "detail" in response_data
        assert "deleted" in response_data["detail"].lower()
        
        app.dependency_overrides.clear()

    def test_database_error_handling(self, client, mock_user, mock_comment, mock_db):
        """Test that database errors are handled gracefully"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock service to raise database exception
        with patch('app.services.comment_reaction_service.CommentReactionService.add_or_update_reaction') as mock_react:
            from fastapi import HTTPException
            mock_react.side_effect = HTTPException(status_code=500, detail="Database connection error")
            
            response = client.post(
                f"/api/v1/comments/{mock_comment.comment_id}/reaction",
                json={"reactionType": "upvote"}
            )
        
        assert response.status_code == 500
        response_data = response.json()
        assert "detail" in response_data
        
        app.dependency_overrides.clear()

    # === EDGE CASES ===
    
    def test_rapid_reaction_changes_handling(self, client, mock_user, mock_comment, mock_db):
        """Test that rapid reaction changes are handled correctly"""
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        reaction_sequence = ["upvote", "downvote", "heart", "upvote"]
        
        for i, reaction_type in enumerate(reaction_sequence):
            mock_reaction = Mock(spec=CommentReaction)
            mock_reaction.comment_id = mock_comment.comment_id
            mock_reaction.user_id = mock_user.user_id
            mock_reaction.reaction = reaction_type
            mock_reaction.created_at = datetime.now()
            
            with patch('app.services.comment_reaction_service.CommentReactionService.add_or_update_reaction') as mock_react:
                action = "created" if i == 0 else "updated"
                mock_react.return_value = (mock_reaction, action)
                
                response = client.post(
                    f"/api/v1/comments/{mock_comment.comment_id}/reaction",
                    json={"reactionType": reaction_type}
                )
            
            assert response.status_code in [200, 201]
            response_data = response.json()
            assert response_data["success"] is True
            assert response_data["data"]["reactionType"] == reaction_type
        
        app.dependency_overrides.clear()

    # === FIXTURES ===
    
    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user fixture"""
        user = Mock(spec=User)
        user.user_id = uuid4()
        user.username = "testuser"
        user.email = "test@example.com"
        user.display_name = "Test User"
        return user

    @pytest.fixture
    def mock_comment(self):
        """Mock comment fixture"""
        comment = Mock(spec=Comment)
        comment.comment_id = uuid4()
        comment.content = "Test comment"
        comment.user_id = uuid4()  # Different from test user
        comment.post_id = uuid4()
        comment.status = "active"
        return comment

    @pytest.fixture
    def mock_db(self):
        """Mock database session fixture"""
        return Mock()
