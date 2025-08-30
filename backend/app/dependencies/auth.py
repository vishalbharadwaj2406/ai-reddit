"""
Authentication Dependencies

Provides FastAPI dependencies for JWT token validation and user authentication.
Supports both Bearer token and HTTP-only cookie authentication.

Security Features:
- JWT token validation (Bearer and Cookie)
- Session fingerprint validation
- User extraction from database
- Proper error handling for invalid/expired tokens
- Optional authentication support
"""

from fastapi import Depends, HTTPException, status, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from jose import JWTError
import logging

from app.core.database import get_db
from app.core.jwt import JWTManager
from app.core.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)


# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate current user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Check if token is provided
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "AUTH_REQUIRED",
                "message": "Authentication required"
            }
        )
    
    try:
        # Decode JWT token
        payload = JWTManager.decode_token(credentials.credentials)
        
        # Extract user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_TOKEN",
                    "message": "Token missing user ID"
                }
            )
        
        # Verify token type is access token
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_TOKEN",
                    "message": "Invalid token type"
                }
            )
        
        # Get user from database
        stmt = select(User).where(
            User.user_id == user_id,
            User.status == 'active'
        )
        user = db.execute(stmt).scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_TOKEN",
                    "message": "User not found or inactive"
                }
            )
        
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_TOKEN",
                "message": "Invalid or expired token"
            }
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like user not found)
        raise
    except Exception as e:
        # Log the error for debugging
        print(f"Auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "AUTH_ERROR",
                "message": "Authentication failed"
            }
        )


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Extract current user from JWT token if provided, otherwise return None.
    
    Used for endpoints that work with or without authentication.
    
    Args:
        credentials: HTTP Bearer token credentials (optional)
        db: Database session
        
    Returns:
        Current authenticated user or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        # If authentication fails, return None instead of raising
        return None


async def get_current_user_sse(
    token: Optional[str] = Query(None, description="JWT token for SSE authentication"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate current user for Server-Sent Events endpoints.
    
    SSE endpoints can't use Authorization headers, so we accept JWT tokens
    as URL parameters while maintaining compatibility with header auth.
    
    Args:
        token: JWT token from URL parameter (for SSE)
        credentials: HTTP Bearer token credentials (fallback)
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Try URL parameter first (for SSE), then Authorization header
    jwt_token = token or (credentials.credentials if credentials else None)
    
    if not jwt_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "AUTH_REQUIRED",
                "message": "Authentication required"
            }
        )
    
    try:
        # Decode JWT token
        payload = JWTManager.decode_token(jwt_token)
        
        # Extract user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_TOKEN",
                    "message": "Token missing user ID"
                }
            )
        
        # Verify token type is access token
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_TOKEN",
                    "message": "Invalid token type"
                }
            )
        
        # Get user from database
        stmt = select(User).where(
            User.user_id == user_id,
            User.status == 'active'
        )
        user = db.execute(stmt).scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_TOKEN",
                    "message": "User not found or inactive"
                }
            )
        
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_TOKEN",
                "message": "Invalid or expired token"
            }
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like user not found)
        raise
    except Exception as e:
        # Log the error for debugging
        print(f"SSE Auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "AUTH_ERROR",
                "message": "Authentication failed"
            }
        )


async def get_current_user_from_cookie(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate current user from HTTP-only session cookie.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If session is invalid or user not found
    """
    try:
        # Get session cookie
        session_token = request.cookies.get(settings.SESSION_COOKIE_NAME)
        if not session_token:
            logger.debug("No session cookie found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "NO_SESSION",
                    "message": "No session found - please log in"
                }
            )
        
        # Generate expected fingerprint
        from app.services.oauth_service import OAuthService
        user_agent = request.headers.get("user-agent", "")
        client_ip = get_client_ip(request)
        expected_fingerprint = OAuthService.generate_session_fingerprint(user_agent, client_ip)
        
        logger.debug(f"Session validation - IP: {client_ip}, UA: {user_agent[:50]}{'...' if len(user_agent) > 50 else ''}")
        
        # Decode session token with fingerprint validation
        payload = JWTManager.decode_session_token(session_token, expected_fingerprint)
        
        # Extract user ID
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Session token missing user ID")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_SESSION",
                    "message": "Invalid session data"
                }
            )
        
        # Get user from database
        stmt = select(User).where(
            User.user_id == user_id,
            User.status == 'active'
        )
        user = db.execute(stmt).scalar_one_or_none()
        
        if not user:
            logger.warning(f"User not found or inactive: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_SESSION",
                    "message": "User not found or inactive"
                }
            )
        
        logger.debug(f"Session validated successfully for user: {user.google_id}")
        return user
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_SESSION",
                "message": "Session expired or invalid - please log in again"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Cookie auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "AUTH_ERROR",
                "message": "Authentication failed"
            }
        )


async def get_current_user_from_cookie_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Extract current user from session cookie if valid, otherwise return None.
    
    Used for endpoints that work with or without authentication.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        Current authenticated user or None
    """
    try:
        return await get_current_user_from_cookie(request, db)
    except HTTPException:
        return None


async def get_session_from_cookie(request: Request) -> Optional[dict]:
    """
    Get session data from cookie without full user validation.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Session data dictionary or None
    """
    try:
        session_token = request.cookies.get(settings.SESSION_COOKIE_NAME)
        if not session_token:
            return None
        
        # Generate expected fingerprint
        from app.services.oauth_service import OAuthService
        user_agent = request.headers.get("user-agent", "")
        client_ip = get_client_ip(request)
        expected_fingerprint = OAuthService.generate_session_fingerprint(user_agent, client_ip)
        
        # Decode session token
        payload = JWTManager.decode_session_token(session_token, expected_fingerprint)
        return payload
        
    except (JWTError, Exception):
        return None


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request headers.
    
    Handles proxy headers like X-Forwarded-For for production load balancers
    and middleware-forwarded headers for development.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address
    """
    # Check for forwarded IP (from proxy/load balancer or Next.js middleware)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Take the first IP in the chain (original client)
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP header (from Next.js middleware or proxy)
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection IP
    if hasattr(request.client, 'host'):
        return request.client.host
    
    return "127.0.0.1"  # Development fallback


# Convenience alias for cookie-based auth (primary auth method)
get_current_user_primary = get_current_user_from_cookie
get_current_user_primary_optional = get_current_user_from_cookie_optional
