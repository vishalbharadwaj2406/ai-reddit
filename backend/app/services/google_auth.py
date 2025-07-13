"""
Google OAuth Service

Handles Google OAuth token verification and user data extraction.
Integrates with Google's token verification API.

Security Features:
- Verifies Google ID tokens
- Validates token audience (client ID)
- Extracts user profile information
- Handles token expiration and errors
"""

from typing import Dict, Any
from google.auth.transport import requests
from google.oauth2 import id_token
from app.core.config import settings


class GoogleOAuthError(Exception):
    """Custom exception for Google OAuth errors."""
    pass


class GoogleOAuthService:
    """
    Service for handling Google OAuth operations.
    
    Provides methods to verify Google ID tokens and extract user information.
    """
    
    @staticmethod
    async def verify_google_token(token: str) -> Dict[str, Any]:
        """
        Verify a Google ID token and extract user information.
        
        Args:
            token: Google ID token from frontend
            
        Returns:
            Dictionary containing user information from Google
            
        Raises:
            GoogleOAuthError: If token verification fails
        """
        try:
            # Verify the token with Google using the modern approach
            id_info = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            # Verify the token is for our application
            if id_info['aud'] != settings.GOOGLE_CLIENT_ID:
                raise GoogleOAuthError("Token audience mismatch")
            
            # Verify the token issuer (both formats accepted by Google)
            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise GoogleOAuthError("Invalid token issuer")
            
            # Verify token hasn't expired (additional safety check)
            import time
            if 'exp' in id_info and id_info['exp'] < time.time():
                raise GoogleOAuthError("Token has expired")
            
            return {
                'google_id': id_info['sub'],
                'email': id_info.get('email'),
                'name': id_info.get('name'),
                'picture': id_info.get('picture'),
                'email_verified': id_info.get('email_verified', False),
                'given_name': id_info.get('given_name'),
                'family_name': id_info.get('family_name')
            }
            
        except ValueError as e:
            # Token verification failed
            raise GoogleOAuthError(f"Invalid Google token: {str(e)}")
        except Exception as e:
            # Other errors
            raise GoogleOAuthError(f"Token verification failed: {str(e)}")
    
    @staticmethod
    def extract_user_data(google_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and normalize user data from Google response.
        
        Args:
            google_info: User information from Google token verification
            
        Returns:
            Normalized user data for database storage
        """
        return {
            'google_id': google_info['google_id'],
            'email': google_info.get('email'),
            'user_name': google_info.get('name') or google_info.get('given_name', 'User'),
            'profile_picture': google_info.get('picture'),
            'email_verified': google_info.get('email_verified', False)
        }
    
    @staticmethod
    async def get_user_info_from_token(token: str) -> Dict[str, Any]:
        """
        Complete flow: verify token and extract user data.
        
        Convenience method that combines token verification and data extraction.
        
        Args:
            token: Google ID token
            
        Returns:
            Normalized user data ready for database operations
            
        Raises:
            GoogleOAuthError: If any step fails
        """
        google_info = await GoogleOAuthService.verify_google_token(token)
        return GoogleOAuthService.extract_user_data(google_info)


class GoogleUserProfile:
    """
    Data class for Google user profile information.
    
    Provides a structured way to handle user data from Google.
    """
    
    def __init__(self, google_info: Dict[str, Any]):
        self.google_id = google_info['google_id']
        self.email = google_info.get('email')
        self.name = google_info.get('name', 'User')
        self.picture = google_info.get('picture')
        self.email_verified = google_info.get('email_verified', False)
        self.given_name = google_info.get('given_name')
        self.family_name = google_info.get('family_name')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'google_id': self.google_id,
            'email': self.email,
            'user_name': self.name,
            'profile_picture': self.picture,
            'email_verified': self.email_verified
        }
    
    def get_display_name(self) -> str:
        """Get appropriate display name for user."""
        if self.given_name:
            return self.given_name
        elif self.name:
            return self.name
        else:
            return "User"


# Example usage:
"""
# In your auth endpoint:
try:
    user_data = await GoogleOAuthService.get_user_info_from_token(google_token)
    # user_data now contains verified user information
    # Ready to create or update user in database
except GoogleOAuthError as e:
    # Handle authentication error
    return {"error": str(e)}
"""
