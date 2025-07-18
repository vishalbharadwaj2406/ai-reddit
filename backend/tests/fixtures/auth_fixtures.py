"""
Authentication Test Fixtures

Provides reusable fixtures for authentication-related tests.
Centralized location for auth test data and mocks.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime, timezone
from jose import jwt

from app.models.user import User
from app.core.jwt import JWTManager
from app.core.config import settings


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    user = Mock(spec=User)
    user.user_id = "550e8400-e29b-41d4-a716-446655440000"
    user.user_name = "testuser"
    user.email = "test@example.com"
    user.profile_picture = "https://example.com/photo.jpg"
    user.created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    user.is_private = False
    user.status = "active"
    return user


@pytest.fixture
def sample_private_user():
    """Create a sample private user for testing."""
    user = Mock(spec=User)
    user.user_id = "550e8400-e29b-41d4-a716-446655440001"
    user.user_name = "privateuser"
    user.email = "private@example.com"
    user.profile_picture = "https://example.com/private.jpg"
    user.created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    user.is_private = True
    user.status = "active"
    return user


@pytest.fixture
def valid_token(sample_user):
    """Generate a valid JWT token for testing."""
    return JWTManager.create_access_token(str(sample_user.user_id))


@pytest.fixture
def valid_refresh_token(sample_user):
    """Generate a valid refresh token for testing."""
    return JWTManager.create_refresh_token(str(sample_user.user_id))


@pytest.fixture
def expired_token(sample_user):
    """Generate an expired JWT token for testing."""
    from datetime import timedelta
    # Create token that expired 1 hour ago
    expire = datetime.now(timezone.utc) - timedelta(hours=1)
    claims = {
        "sub": str(sample_user.user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        "type": "access"
    }
    return jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def invalid_token():
    """Generate an invalid JWT token for testing."""
    return "invalid.jwt.token"


@pytest.fixture
def mock_google_user_data():
    """Mock Google OAuth user data."""
    return {
        "google_id": "google_123456789",
        "email": "test@example.com",
        "user_name": "Test User",
        "profile_picture": "https://example.com/photo.jpg"
    }


@pytest.fixture
def mock_db_session():
    """Mock database session for testing."""
    from unittest.mock import Mock
    from sqlalchemy.orm import Session
    
    mock_db = Mock(spec=Session)
    # Mock common database operations
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    mock_db.execute.return_value.scalar.return_value = 0
    mock_db.commit.return_value = None
    mock_db.rollback.return_value = None
    mock_db.refresh.return_value = None
    
    return mock_db
