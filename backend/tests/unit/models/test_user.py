"""
User Model Tests

Comprehensive test suite for the User model.
Tests cover:
- Model creation and validation
- Database constraints
- Helper methods
- String representations
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User


class TestUserModel:
    """Comprehensive tests for User model."""
    
    def test_user_creation_basic(self, db_session):
        """Test basic user creation with minimal fields."""
        user = User(
            user_name="test_user",
            email="test@example.com"
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Verify user was created
        assert user.user_id is not None
        assert user.user_name == "test_user"
        assert user.email == "test@example.com"
        assert user.is_private is False  # Default value
        assert user.status == "active"  # Default value
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_creation_complete(self, db_session):
        """Test user creation with all fields."""
        user = User(
            user_name="complete_user",
            email="complete@example.com",
            phone="+1234567890",
            profile_picture="https://example.com/pic.jpg",
            gender="prefer_not_to_say",
            google_id="google_123",
            is_private=True
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Verify all fields
        assert user.user_name == "complete_user"
        assert user.email == "complete@example.com"
        assert user.phone == "+1234567890"
        assert user.profile_picture == "https://example.com/pic.jpg"
        assert user.gender == "prefer_not_to_say"
        assert user.google_id == "google_123"
        assert user.is_private is True
    
    def test_user_unique_constraints(self, db_session):
        """Test that unique constraints work properly."""
        # Create first user
        user1 = User(user_name="unique_test", email="unique@test.com")
        db_session.add(user1)
        db_session.commit()
        
        # Try to create user with same username
        user2 = User(user_name="unique_test", email="different@test.com")
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Try to create user with same email
        user3 = User(user_name="different_name", email="unique@test.com")
        db_session.add(user3)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_helper_methods(self, db_session):
        """Test user helper methods."""
        user = User(
            user_name="helper_test",
            profile_picture="https://example.com/pic.jpg"
        )
        db_session.add(user)
        db_session.commit()
        
        # Test helper methods
        assert user.is_active is True
        assert user.get_display_name() == "helper_test"
        assert user.has_profile_picture() is True
        
        # Test with no profile picture
        user.profile_picture = None
        assert user.has_profile_picture() is False
        
        # Test with empty profile picture
        user.profile_picture = "   "
        assert user.has_profile_picture() is False
    
    def test_user_status_inactive(self, db_session):
        """Test user with inactive status."""
        user = User(
            user_name="inactive_user",
            status="archived"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.is_active is False
    
    def test_user_string_representations(self, db_session):
        """Test __str__ and __repr__ methods."""
        user = User(user_name="string_test")
        db_session.add(user)
        db_session.commit()
        
        # Test string representations
        assert str(user) == "string_test"
        assert repr(user) == f"<User(id={user.user_id}, username=string_test)>"
