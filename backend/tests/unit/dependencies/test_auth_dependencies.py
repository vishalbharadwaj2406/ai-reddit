"""
Test Authentication Dependencies

Tests for JWT authentication middleware and user extraction.
Validates token parsing, user validation, and error handling.
"""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.dependencies.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.core.config import settings
from app.core.jwt import JWTManager

# Import from our new test infrastructure
from tests.fixtures.auth_fixtures import sample_user, valid_token, mock_db_session
from tests.utils.test_helpers import mock_dependency_override


def create_mock_request(token=None):
    """Create mock request object with optional token"""
    mock_request = Mock()
    if token:
        mock_request.headers = {"authorization": f"Bearer {token}"}
    else:
        mock_request.headers = {}
    return mock_request


class TestAuthenticationDependencies:
    """Test suite for authentication dependencies"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_user(self):
        """Sample user for testing"""
        user = Mock(spec=User)
        user.user_id = "550e8400-e29b-41d4-a716-446655440000"
        user.user_name = "testuser"
        user.email = "test@example.com"
        user.status = "active"
        user.created_at = datetime.now(timezone.utc)
        return user
    
    @pytest.fixture
    def valid_token(self, sample_user):
        """Generate valid JWT token for testing"""
        return JWTManager.create_access_token(str(sample_user.user_id))
    
    @pytest.fixture
    def expired_token(self, sample_user):
        """Generate expired JWT token for testing"""
        # Create token that expired 1 hour ago
        expire = datetime.now(timezone.utc) - timedelta(hours=1)
        claims = {
            "sub": str(sample_user.user_id),
            "exp": expire,
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "type": "access"
        }
        return jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, mock_db, sample_user, valid_token):
        """Test successful user authentication"""
        # Mock database query
        mock_stmt = Mock()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result
        
        # Mock credentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=valid_token
        )
        
        # Test authentication
        result = await get_current_user(credentials, mock_db)
        
        # Assertions
        assert result == sample_user
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self, mock_db):
        """Test authentication failure when no credentials provided"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(None, mock_db)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error"] == "AUTH_REQUIRED"
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, mock_db):
        """Test authentication failure with invalid token"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid_token"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_db)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error"] == "INVALID_TOKEN"
    
    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self, mock_db, expired_token):
        """Test authentication failure with expired token"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=expired_token
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_db)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error"] == "INVALID_TOKEN"
    
    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self, mock_db, valid_token):
        """Test authentication failure when user not found in database"""
        # Mock database query returning None
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=valid_token
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_db)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error"] == "INVALID_TOKEN"
    
    @pytest.mark.asyncio
    async def test_get_current_user_inactive_user(self, mock_db, sample_user, valid_token):
        """Test authentication failure when user is inactive"""
        # Set user as inactive
        sample_user.status = "archived"
        
        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None  # Query filters out inactive users
        mock_db.execute.return_value = mock_result
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=valid_token
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_db)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error"] == "INVALID_TOKEN"
    
    @pytest.mark.asyncio
    async def test_get_current_user_refresh_token_rejected(self, mock_db, sample_user):
        """Test authentication failure when refresh token is used for access"""
        # Create refresh token
        refresh_token = JWTManager.create_refresh_token(str(sample_user.user_id))
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=refresh_token
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_db)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error"] == "INVALID_TOKEN"
    
    @pytest.mark.asyncio
    async def test_get_current_user_optional_success(self, mock_db, sample_user, valid_token):
        """Test optional authentication with valid token"""
        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=valid_token
        )
        
        result = await get_current_user_optional(credentials, mock_db)
        
        assert result == sample_user
    
    @pytest.mark.asyncio
    async def test_get_current_user_optional_no_credentials(self, mock_db):
        """Test optional authentication with no credentials"""
        result = await get_current_user_optional(None, mock_db)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_current_user_optional_invalid_token(self, mock_db):
        """Test optional authentication with invalid token returns None"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid_token"
        )
        
        result = await get_current_user_optional(credentials, mock_db)
        
        assert result is None


class TestRefreshTokens:
    """Test refresh token functionality"""
    
    def test_create_refresh_token(self, sample_user):
        """Test refresh token creation"""
        refresh_token = JWTManager.create_refresh_token(str(sample_user.user_id))
        
        # Decode to verify structure
        payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        assert payload["sub"] == str(sample_user.user_id)
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload
        assert "fingerprint" in payload
    
    def test_create_refresh_token_with_fingerprint(self, sample_user):
        """Test refresh token creation with custom fingerprint"""
        fingerprint = "test-device-fingerprint"
        refresh_token = JWTManager.create_refresh_token(str(sample_user.user_id), fingerprint)
        
        payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        assert payload["fingerprint"] == fingerprint
    
    def test_refresh_access_token_success(self, sample_user):
        """Test successful token refresh"""
        refresh_token = JWTManager.create_refresh_token(str(sample_user.user_id))
        
        tokens = JWTManager.refresh_access_token(refresh_token)
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        
        # Verify the new tokens are valid
        access_payload = jwt.decode(tokens["access_token"], settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        refresh_payload = jwt.decode(tokens["refresh_token"], settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        assert access_payload["sub"] == str(sample_user.user_id)
        assert access_payload["type"] == "access"
        assert refresh_payload["sub"] == str(sample_user.user_id)
        assert refresh_payload["type"] == "refresh"
    
    def test_refresh_token_invalid_type(self):
        """Test refresh with invalid token type"""
        # Create access token instead of refresh token
        access_token = JWTManager.create_access_token("test-user-id")
        
        with pytest.raises(HTTPException) as exc_info:
            JWTManager.refresh_access_token(access_token)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token type" in str(exc_info.value.detail)
    
    def test_refresh_token_expired(self, expired_refresh_token):
        """Test refresh with expired token"""
        with pytest.raises(HTTPException) as exc_info:
            JWTManager.refresh_access_token(expired_refresh_token)
        
        assert exc_info.value.status_code == 401
    
    def test_refresh_token_invalid_format(self):
        """Test refresh with malformed token"""
        with pytest.raises(HTTPException) as exc_info:
            JWTManager.refresh_access_token("invalid.token.format")
        
        assert exc_info.value.status_code == 401
