"""
Authentication Dependencies

Provides FastAPI dependencies for JWT token validation and user authentication.
Used across all protected endpoints to extract and validate current user.

Security Features:
- JWT token validation
- User extraction from database
- Proper error handling for invalid/expired tokens
- Optional authentication support
"""

from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from jose import JWTError

from app.core.database import get_db
from app.core.jwt import JWTManager
from app.models.user import User


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
