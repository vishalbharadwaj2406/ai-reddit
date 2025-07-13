"""
Authentication Schemas

Pydantic models for authentication requests and responses.
These define the structure of data flowing in/out of auth endpoints.

Frontend Integration:
- All schemas designed for easy frontend consumption
- Clear error messages and validation
- Consistent response structure
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class GoogleAuthRequest(BaseModel):
    """
    Request schema for Google OAuth authentication.
    
    Frontend sends this after user completes Google OAuth on client side.
    """
    google_token: str = Field(
        ...,
        description="Google ID token from frontend OAuth flow",
        min_length=100  # Google tokens are long
    )


class TokenResponse(BaseModel):
    """
    Response schema for successful authentication.
    
    Returns JWT tokens that frontend can use for API calls.
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiry in seconds")
    user: 'UserInfo' = Field(..., description="Basic user information")


class UserInfo(BaseModel):
    """
    Basic user information returned after authentication.
    
    Includes essential profile data for frontend display.
    """
    user_id: str = Field(..., description="User's unique ID")
    user_name: str = Field(..., description="User's display name")
    email: str = Field(..., description="User's email address")
    profile_picture: Optional[str] = Field(None, description="Profile picture URL")
    is_private: bool = Field(..., description="Whether user profile is private")
    created_at: datetime = Field(..., description="Account creation timestamp")


class RefreshTokenRequest(BaseModel):
    """
    Request schema for refreshing access tokens.
    
    Frontend sends this when access token expires.
    """
    refresh_token: str = Field(
        ...,
        description="Valid refresh token",
        min_length=10
    )


class RefreshTokenResponse(BaseModel):
    """
    Response schema for token refresh.
    
    Returns new access token (and optionally new refresh token).
    """
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiry in seconds")
    refresh_token: Optional[str] = Field(None, description="New refresh token (if rotated)")


class AuthError(BaseModel):
    """
    Error response schema for authentication failures.
    
    Provides clear error messages for frontend handling.
    """
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional error details")


class LogoutRequest(BaseModel):
    """
    Request schema for user logout.
    
    Optional - can include refresh token to blacklist it.
    """
    refresh_token: Optional[str] = Field(None, description="Refresh token to invalidate")


class LogoutResponse(BaseModel):
    """
    Response schema for successful logout.
    """
    message: str = Field(default="Successfully logged out", description="Confirmation message")


# Update forward references
TokenResponse.model_rebuild()


# Example usage for frontend developers:
"""
// Login with Google (frontend JavaScript example)
const response = await fetch('/auth/google', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        google_token: googleIdToken  // from Google OAuth
    })
});

const data = await response.json();
// data.access_token - use for API calls
// data.user - display user info
"""
