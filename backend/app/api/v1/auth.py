"""
Authentication API Routes

This module handles all authentication-related endpoints:
- Google OAuth login
- JWT token refresh
- Logout

The auth system uses:
1. Google OAuth for user verification
2. JWT tokens for session management
3. Refresh tokens for extended sessions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

# Import our components
from app.core.database import get_db
from app.schemas.auth import (
    GoogleAuthRequest, TokenResponse, UserInfo,
    RefreshTokenRequest, RefreshTokenResponse,
    LogoutRequest, LogoutResponse
)
from app.services.google_auth import GoogleOAuthService, GoogleOAuthError
from app.core.jwt import JWTManager, create_token_pair, get_token_expiry_seconds
from app.models.user import User

# Create router for authentication endpoints
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/google", response_model=TokenResponse)
async def google_login(
    auth_request: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Google OAuth token.

    Frontend Integration:
    1. User completes Google OAuth on frontend
    2. Frontend sends Google ID token to this endpoint
    3. Backend verifies token with Google
    4. Returns JWT tokens for API authentication

    Args:
        auth_request: Contains Google ID token from frontend
        db: Database session (injected by FastAPI)

    Returns:
        TokenResponse: User info and JWT tokens for frontend

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Step 1: Verify Google token and get user info
        google_user_data = await GoogleOAuthService.get_user_info_from_token(
            auth_request.google_token
        )
        
        # Step 2: Check if user exists in our database
        stmt = select(User).where(User.google_id == google_user_data['google_id'])
        existing_user = db.execute(stmt).scalar_one_or_none()
        
        if existing_user:
            # Step 3a: User exists - update last login and any profile changes
            existing_user.updated_at = datetime.utcnow()
            if google_user_data.get('email'):
                existing_user.email = google_user_data['email']
            if google_user_data.get('profile_picture'):
                existing_user.profile_picture = google_user_data['profile_picture']
            
            user = existing_user
        else:
            # Step 3b: New user - create account
            user = User(
                google_id=google_user_data['google_id'],
                email=google_user_data.get('email'),
                user_name=google_user_data['user_name'],
                profile_picture=google_user_data.get('profile_picture'),
                status='active'
            )
            db.add(user)
        
        # Step 4: Save changes to database
        db.commit()
        db.refresh(user)
        
        # Step 5: Generate JWT tokens
        tokens = create_token_pair(str(user.user_id))
        
        # Step 6: Return response with tokens and user info
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            expires_in=get_token_expiry_seconds(),
            user=UserInfo(
                user_id=str(user.user_id),
                user_name=user.user_name,
                email=user.email or "",
                profile_picture=user.profile_picture,
                is_private=user.is_private,
                created_at=user.created_at
            )
        )
        
    except GoogleOAuthError as e:
        # Google token verification failed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_google_token",
                "message": "Google authentication failed",
                "details": str(e)
            }
        )
    except Exception as e:
        # Database or other errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "authentication_failed",
                "message": "Authentication process failed",
                "details": str(e)
            }
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh an expired access token using a valid refresh token.

    Frontend Integration:
    1. When access token expires, frontend calls this endpoint
    2. Sends valid refresh token
    3. Receives new access token
    4. Can continue making API calls

    Args:
        refresh_request: Contains refresh token
        db: Database session

    Returns:
        RefreshTokenResponse: New access token

    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        # Step 1: Verify refresh token is valid and correct type
        if not JWTManager.verify_token_type(refresh_request.refresh_token, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "invalid_token_type", "message": "Invalid refresh token"}
            )
        
        # Step 2: Extract user ID from refresh token
        user_id = JWTManager.get_user_id_from_token(refresh_request.refresh_token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "invalid_token", "message": "Invalid refresh token"}
            )
        
        # Step 3: Verify user still exists and is active
        stmt = select(User).where(User.user_id == user_id, User.status == 'active')
        user = db.execute(stmt).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "user_not_found", "message": "User not found or inactive"}
            )
        
        # Step 4: Generate new access token
        new_access_token = JWTManager.create_access_token(user_id)
        
        return RefreshTokenResponse(
            access_token=new_access_token,
            expires_in=get_token_expiry_seconds()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "token_refresh_failed",
                "message": "Token refresh failed",
                "details": str(e)
            }
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(logout_request: LogoutRequest = None):
    """
    Log out user and optionally invalidate refresh token.

    Frontend Integration:
    1. Frontend calls this endpoint when user logs out
    2. Clears tokens from frontend storage
    3. Optional: sends refresh token to blacklist it

    Note: In this simple implementation, we don't maintain a token blacklist.
    Frontend should remove tokens from storage.

    Args:
        logout_request: Optional request with refresh token

    Returns:
        LogoutResponse: Confirmation message
    """
    # In a production system, you might want to:
    # 1. Add refresh token to a blacklist in Redis/database
    # 2. Log the logout event
    # 3. Invalidate all user sessions
    
    return LogoutResponse(message="Successfully logged out")


# Health check endpoint for auth system
@router.get("/health")
async def auth_health():
    """
    Check if authentication system is working.
    
    Useful for monitoring and debugging.
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "google_oauth": "configured",
        "jwt": "configured"
    }
