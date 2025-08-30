"""
Production-Grade OAuth Service

Enterprise-level OAuth implementation with redirect-based authentication flow.
Follows security best practices used by Google, GitHub, and Slack.

Security Features:
- CSRF protection with state parameter
- Secure redirect handling
- Comprehensive error handling
- Session fingerprinting
- Audit logging
"""

import secrets
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from urllib.parse import urlencode, urlparse, parse_qs
from google.auth.transport import requests
from google.oauth2 import id_token
import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class OAuthError(Exception):
    """Base exception for OAuth operations."""
    pass


class OAuthSecurityError(OAuthError):
    """Exception for OAuth security violations."""
    pass


class OAuthService:
    """
    Production-grade OAuth service with redirect-based authentication flow.
    
    Implements enterprise security patterns:
    - State parameter for CSRF protection
    - Secure redirect validation
    - Session fingerprinting
    - Comprehensive audit logging
    """
    
    GOOGLE_OAUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    @staticmethod
    def generate_state_parameter() -> str:
        """
        Generate cryptographically secure state parameter for CSRF protection.
        
        Returns:
            Secure random state string
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_oauth_url(state: str, redirect_uri: str) -> str:
        """
        Generate Google OAuth authorization URL with security parameters.
        
        Args:
            state: CSRF protection state parameter
            redirect_uri: Callback URL after OAuth completion
            
        Returns:
            Complete OAuth authorization URL
        """
        params = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'state': state,
            'access_type': 'online',  # We don't need offline access
            'prompt': 'select_account',  # Always show account selection
            'include_granted_scopes': 'true'
        }
        
        oauth_url = f"{OAuthService.GOOGLE_OAUTH_URL}?{urlencode(params)}"
        
        logger.info(f"Generated OAuth URL for state: {state[:8]}...")
        return oauth_url
    
    @staticmethod
    def validate_redirect_uri(redirect_uri: str) -> bool:
        """
        Validate redirect URI against security requirements.
        
        Args:
            redirect_uri: URI to validate
            
        Returns:
            True if URI is valid and secure
        """
        try:
            parsed = urlparse(redirect_uri)
            
            # Must be HTTPS in production
            if settings.ENVIRONMENT == "production" and parsed.scheme != "https":
                return False
            
            # Must be HTTP/HTTPS
            if parsed.scheme not in ["http", "https"]:
                return False
            
            # Must have valid hostname
            if not parsed.netloc:
                return False
            
            # Validate against allowed domains
            allowed_domains = settings.ALLOWED_OAUTH_DOMAINS
            if allowed_domains and parsed.netloc not in allowed_domains:
                return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    async def exchange_code_for_tokens(
        code: str, 
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Exchange OAuth authorization code for access tokens.
        
        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Original redirect URI (must match)
            
        Returns:
            Dictionary containing tokens and user info
            
        Raises:
            OAuthError: If token exchange fails
        """
        try:
            # Prepare token exchange request
            token_data = {
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri
            }
            
            # Exchange code for tokens
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    OAuthService.GOOGLE_TOKEN_URL,
                    data=token_data,
                    headers={'Accept': 'application/json'}
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    logger.error(f"Token exchange failed: {response.status_code} - {error_data}")
                    raise OAuthError(f"Token exchange failed: {error_data.get('error', 'Unknown error')}")
                
                tokens = response.json()
                
                # Validate required tokens
                if 'access_token' not in tokens:
                    raise OAuthError("No access token received")
                
                logger.info("Successfully exchanged OAuth code for tokens")
                return tokens
                
        except httpx.RequestError as e:
            logger.error(f"Network error during token exchange: {e}")
            raise OAuthError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during token exchange: {e}")
            raise OAuthError(f"Token exchange failed: {str(e)}")
    
    @staticmethod
    async def get_user_info_from_access_token(access_token: str) -> Dict[str, Any]:
        """
        Retrieve user information using Google access token.
        
        Args:
            access_token: Google access token
            
        Returns:
            User profile information from Google
            
        Raises:
            OAuthError: If user info retrieval fails
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    OAuthService.GOOGLE_USERINFO_URL,
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Accept': 'application/json'
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"User info request failed: {response.status_code}")
                    raise OAuthError("Failed to retrieve user information")
                
                user_info = response.json()
                
                # Validate required fields
                if 'id' not in user_info:
                    raise OAuthError("Invalid user information received")
                
                logger.info(f"Retrieved user info for Google ID: {user_info['id']}")
                return user_info
                
        except httpx.RequestError as e:
            logger.error(f"Network error retrieving user info: {e}")
            raise OAuthError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Error retrieving user info: {e}")
            raise OAuthError(f"User info retrieval failed: {str(e)}")
    
    @staticmethod
    def normalize_user_data(google_user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Google user data for database storage.
        
        Args:
            google_user_info: Raw user info from Google
            
        Returns:
            Normalized user data with optimized profile picture
        """
        from app.services.profile_picture_service import ProfilePictureService
        
        # Basic user data
        user_data = {
            'google_id': google_user_info['id'],
            'email': google_user_info.get('email'),
            'user_name': google_user_info.get('name', google_user_info.get('given_name', 'User')),
            'profile_picture': google_user_info.get('picture'),
            'email_verified': google_user_info.get('verified_email', False),
            'given_name': google_user_info.get('given_name'),
            'family_name': google_user_info.get('family_name'),
            'locale': google_user_info.get('locale')
        }
        
        # Sanitize and optimize profile picture
        sanitized_data = ProfilePictureService.sanitize_profile_picture_data(user_data)
        
        logger.info(f"Normalized user data for {user_data.get('email')}: profile_picture_valid={bool(sanitized_data.get('profile_picture'))}")
        return sanitized_data
    
    @staticmethod
    def generate_session_fingerprint(user_agent: str, ip_address: str) -> str:
        """
        Generate session fingerprint for additional security.
        
        Args:
            user_agent: Browser user agent string
            ip_address: User's IP address
            
        Returns:
            Session fingerprint hash
        """
        fingerprint_data = f"{user_agent}:{ip_address}:{settings.JWT_SECRET_KEY}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
    
    @staticmethod
    async def complete_oauth_flow(
        code: str,
        state: str,
        redirect_uri: str,
        stored_state: str
    ) -> Dict[str, Any]:
        """
        Complete OAuth flow: validate state, exchange code, get user info.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
            redirect_uri: Original redirect URI
            stored_state: State parameter stored in session
            
        Returns:
            Complete user information
            
        Raises:
            OAuthSecurityError: If security validation fails
            OAuthError: If OAuth flow fails
        """
        # Validate state parameter (CSRF protection)
        if not secrets.compare_digest(state, stored_state):
            logger.warning(f"State parameter mismatch: {state[:8]}... vs {stored_state[:8]}...")
            raise OAuthSecurityError("Invalid state parameter - possible CSRF attack")
        
        # Exchange code for tokens
        tokens = await OAuthService.exchange_code_for_tokens(code, redirect_uri)
        
        # Get user information
        user_info = await OAuthService.get_user_info_from_access_token(tokens['access_token'])
        
        # Normalize and return user data
        normalized_data = OAuthService.normalize_user_data(user_info)
        
        logger.info(f"OAuth flow completed successfully for user: {normalized_data['google_id']}")
        return normalized_data


class OAuthStateManager:
    """
    Manages OAuth state parameters for CSRF protection.
    
    In production, this should use Redis or a similar store.
    For now, we'll use in-memory storage with cleanup.
    """
    
    _states: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def store_state(cls, state: str, data: Dict[str, Any]) -> None:
        """Store state with associated data."""
        cls._states[state] = {
            'created_at': datetime.now(timezone.utc),
            'data': data
        }
        
        # Cleanup old states (older than 10 minutes)
        cls._cleanup_expired_states()
    
    @classmethod
    def get_state_data(cls, state: str) -> Optional[Dict[str, Any]]:
        """Retrieve and remove state data."""
        state_info = cls._states.pop(state, None)
        if state_info:
            return state_info['data']
        return None
    
    @classmethod
    def get_state(cls, state: str) -> Optional[Dict[str, Any]]:
        """Get state data without removing it."""
        state_info = cls._states.get(state)
        if state_info:
            return state_info['data']
        return None
    
    @classmethod
    def delete_state(cls, state: str) -> None:
        """Delete state data."""
        cls._states.pop(state, None)
    
    @classmethod
    def _cleanup_expired_states(cls) -> None:
        """Remove expired states."""
        from datetime import datetime, timezone, timedelta
        
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
        expired_states = [
            state for state, info in cls._states.items()
            if info['created_at'] < cutoff
        ]
        
        for state in expired_states:
            cls._states.pop(state, None)
