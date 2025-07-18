"""
JWT Token Utilities

Handles JWT token creation, validation, and extraction.
Provides secure token management for authentication system.

Security Features:
- RS256 or HS256 algorithm support
- Token expiration handling
- Refresh token rotation
- Secure token validation
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.core.config import settings
import uuid


class JWTManager:
    """
    JWT token management utility class.
    
    Handles creation and validation of access and refresh tokens.
    """
    
    @staticmethod
    def create_access_token(user_id: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a JWT access token for a user.
        
        Args:
            user_id: User's unique identifier
            additional_claims: Optional additional claims to include
            
        Returns:
            Encoded JWT access token
        """
        # Calculate expiration time
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Base claims
        claims = {
            "sub": user_id,  # Subject (user ID)
            "exp": expire,   # Expiration time
            "iat": datetime.now(timezone.utc),  # Issued at
            "type": "access",  # Token type
            "jti": str(uuid.uuid4())  # JWT ID for tracking
        }
        
        # Add additional claims if provided
        if additional_claims:
            claims.update(additional_claims)
        
        # Encode and return token
        return jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """
        Create a JWT refresh token for a user.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Encoded JWT refresh token
        """
        # Calculate expiration time (longer than access token)
        expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        claims = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
            "jti": str(uuid.uuid4())
        }
        
        return jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token to decode
            
        Returns:
            Decoded token claims
            
        Raises:
            JWTError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            raise JWTError(f"Invalid token: {str(e)}")
    
    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[str]:
        """
        Extract user ID from a JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            User ID if token is valid, None otherwise
        """
        try:
            payload = JWTManager.decode_token(token)
            return payload.get("sub")
        except JWTError:
            return None
    
    @staticmethod
    def verify_token_type(token: str, expected_type: str) -> bool:
        """
        Verify that a token is of the expected type.
        
        Args:
            token: JWT token to verify
            expected_type: Expected token type ('access' or 'refresh')
            
        Returns:
            True if token type matches, False otherwise
        """
        try:
            payload = JWTManager.decode_token(token)
            return payload.get("type") == expected_type
        except JWTError:
            return False
    
    @staticmethod
    def is_token_expired(token: str) -> bool:
        """
        Check if a token is expired.
        
        Args:
            token: JWT token to check
            
        Returns:
            True if token is expired, False otherwise
        """
        try:
            payload = JWTManager.decode_token(token)
            exp = payload.get("exp")
            if exp:
                return datetime.utcnow() > datetime.fromtimestamp(exp)
            return True  # If no expiration, consider expired
        except JWTError:
            return True  # If can't decode, consider expired


def create_token_pair(user_id: str) -> Dict[str, str]:
    """
    Create both access and refresh tokens for a user.
    
    Convenience function for login endpoints.
    
    Args:
        user_id: User's unique identifier
        
    Returns:
        Dictionary with access_token and refresh_token
    """
    return {
        "access_token": JWTManager.create_access_token(user_id),
        "refresh_token": JWTManager.create_refresh_token(user_id)
    }


def get_token_expiry_seconds() -> int:
    """
    Get access token expiry time in seconds.
    
    Used for frontend token management.
    
    Returns:
        Token expiry time in seconds
    """
    return settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60


# Example usage:
"""
# Create tokens
tokens = create_token_pair("user-123")
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]

# Verify token
user_id = JWTManager.get_user_id_from_token(access_token)

# Check if token is valid access token
is_valid = JWTManager.verify_token_type(access_token, "access")
"""
