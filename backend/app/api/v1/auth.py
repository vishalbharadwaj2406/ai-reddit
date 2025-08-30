"""
Production-Grade Authentication API Routes

Enterprise-level OAuth authentication with HTTP-only cookies.
Implements security patterns used by Google, GitHub, and Slack.

Security Features:
- OAuth redirect-based authentication
- HTTP-only session cookies
- CSRF protection with state parameter
- Session fingerprinting
- Comprehensive audit logging
- Secure cookie settings
- Return URL preservation with open redirect protection
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone
from urllib.parse import urlencode, urlparse
import logging
import re

# Import our components
from app.core.database import get_db
from app.core.config import settings
from app.core.jwt import create_session_token_with_fingerprint
from app.services.oauth_service import OAuthService, OAuthStateManager, OAuthError, OAuthSecurityError
from app.dependencies.auth import (
    get_current_user_from_cookie, 
    get_current_user_from_cookie_optional,
    get_client_ip
)
from app.models.user import User
from app.schemas.auth import UserInfo

logger = logging.getLogger(__name__)

# Create router for authentication endpoints
router = APIRouter(tags=["authentication"])


def _is_safe_return_url(return_url: str) -> bool:
    """
    Validate return URL to prevent open redirect attacks.
    
    Args:
        return_url: URL to validate
        
    Returns:
        True if URL is safe, False otherwise
    """
    if not return_url:
        return False
    
    # Allow relative URLs that start with /
    if return_url.startswith('/') and not return_url.startswith('//'):
        # Check for valid path characters and prevent dangerous patterns
        if re.match(r'^/[a-zA-Z0-9/_\-\?&=]*$', return_url):
            return True
    
    # Parse absolute URLs
    try:
        parsed = urlparse(return_url)
        # Only allow localhost and the configured frontend URL
        allowed_hosts = ['localhost', '127.0.0.1']
        if settings.FRONTEND_URL:
            frontend_parsed = urlparse(settings.FRONTEND_URL)
            if frontend_parsed.hostname:
                allowed_hosts.append(frontend_parsed.hostname)
        
        return parsed.hostname in allowed_hosts
    except Exception:
        return False


@router.get("/google/login")
async def initiate_google_oauth(request: Request):
    """
    Initiate Google OAuth authentication flow with return URL support.
    
    This endpoint starts the OAuth process by redirecting users to Google's
    authorization server with proper security parameters and return URL preservation.
    
    Query Parameters:
        return_url: Optional URL to redirect after successful authentication
    
    Security Features:
    - CSRF protection with state parameter
    - Secure redirect URI validation
    - Session fingerprint generation
    - Return URL preservation through OAuth flow
    
    Returns:
        RedirectResponse: Redirect to Google OAuth authorization URL
    """
    try:
        # Extract and validate return URL
        return_url = request.query_params.get("return_url", "/conversations")
        
        # Validate return URL for security (prevent open redirect attacks)
        if not _is_safe_return_url(return_url):
            logger.warning(f"Invalid return URL rejected: {return_url}")
            return_url = "/conversations"  # Safe default
        
        # Generate secure state parameter for CSRF protection
        state = OAuthService.generate_state_parameter()
        
        # Get redirect URI from settings
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        
        # Validate redirect URI security
        if not OAuthService.validate_redirect_uri(redirect_uri):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "INVALID_REDIRECT_URI",
                    "message": "Invalid OAuth redirect configuration"
                }
            )
        
        # Store state with session data for later validation (INCLUDING return_url)
        client_ip = get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        OAuthStateManager.store_state(state, {
            "redirect_uri": redirect_uri,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "return_url": return_url,  # CRITICAL: Store return URL
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Generate OAuth authorization URL
        oauth_url = OAuthService.generate_oauth_url(state, redirect_uri)
        
        logger.info(f"OAuth flow initiated for IP: {client_ip}, return_url: {return_url}")
        
        # Redirect user to Google OAuth
        return RedirectResponse(url=oauth_url, status_code=302)
        
    except Exception as e:
        logger.error(f"OAuth initiation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "OAUTH_INIT_FAILED",
                "message": "Failed to start authentication"
            }
        )


@router.get("/google/callback")
async def handle_google_oauth_callback(
    request: Request,
    response: Response,
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback and create user session.
    
    This endpoint processes the OAuth callback, validates the authorization code,
    creates or updates the user, and establishes a secure session.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object
        code: Authorization code from Google
        state: State parameter for CSRF protection
        error: Error parameter if OAuth failed
        db: Database session
        
    Returns:
        RedirectResponse: Redirect to frontend with success/error status
    """
    try:
        logger.info("OAuth callback function entry point reached")
        
        # Handle OAuth errors
        if error:
            logger.warning(f"OAuth error from Google: {error}")
            error_url = f"{settings.FRONTEND_URL}/?auth_error={error}"
            return RedirectResponse(url=error_url, status_code=302)
        
        # Validate required parameters
        if not code or not state:
            logger.warning("Missing code or state parameter in OAuth callback")
            error_url = f"{settings.FRONTEND_URL}/?auth_error=missing_parameters"
            return RedirectResponse(url=error_url, status_code=302)
        
        logger.info(f"OAuth callback received: state={state[:8]}..., code present={bool(code)}")
        
        # Retrieve and validate state data (don't delete yet)
        state_data = OAuthStateManager.get_state(state)
        if not state_data:
            logger.warning(f"Invalid or expired state parameter: {state[:8]}...")
            error_url = f"{settings.FRONTEND_URL}/?auth_error=invalid_state"
            return RedirectResponse(url=error_url, status_code=302)
        
        logger.info(f"State data retrieved successfully: {list(state_data.keys())}")
        
        # Store return URL
        return_url = state_data.get("return_url", "/conversations")
        
        # Complete OAuth flow with security validation
        # Note: For CSRF protection, we compare the state from URL with the stored state key
        # Since the state parameter IS the key, we pass the same value for both
        try:
            logger.info("Starting OAuth token exchange...")
            user_data = await OAuthService.complete_oauth_flow(
                code=code,
                state=state,
                redirect_uri=state_data["redirect_uri"],
                stored_state=state  # This should be the same as the key we used to store
            )
            logger.info(f"OAuth flow completed successfully for user: {user_data.get('google_id')}")
        except OAuthSecurityError as e:
            logger.error(f"OAuth security violation: {str(e)}")
            OAuthStateManager.delete_state(state)  # Clean up on security error
            error_url = f"{settings.FRONTEND_URL}/?auth_error=security_violation"
            return RedirectResponse(url=error_url, status_code=302)
        except OAuthError as e:
            logger.error(f"OAuth flow failed: {str(e)}")
            OAuthStateManager.delete_state(state)  # Clean up on OAuth error
            error_url = f"{settings.FRONTEND_URL}/?auth_error=oauth_failed"
            return RedirectResponse(url=error_url, status_code=302)
        
        # Delete the state after successful OAuth validation
        OAuthStateManager.delete_state(state)
        
        # Create or update user in database
        user = await create_or_update_user(db, user_data)
        
        # Generate session token with fingerprint
        client_ip = get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        session_token = create_session_token_with_fingerprint(
            user_id=str(user.user_id),
            user_agent=user_agent,
            ip_address=client_ip,
            additional_data={
                "login_method": "google_oauth",
                "user_name": user.user_name
            }
        )
        
        # Set secure HTTP-only cookie with enhanced security
        set_session_cookie(response, session_token)
        
        # Update user login timestamp
        user.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        # Validate return URL again for security
        if not _is_safe_return_url(return_url):
            logger.warning(f"Invalid return URL in callback, using default: {return_url}")
            return_url = "/conversations"
        
        # Construct success URL with proper return path
        if return_url.startswith('/'):
            success_url = f"{settings.FRONTEND_URL}{return_url}"
        else:
            success_url = f"{settings.FRONTEND_URL}/conversations"
        
        logger.info(f"User authenticated successfully: {user.google_id}")
        
        # Production OAuth callback: Direct HTTP redirect with secure cookie
        # This ensures cookie is set in the same request context as the redirect
        redirect_url = return_url if return_url and _is_safe_return_url(return_url) else "/conversations"
        if not redirect_url.startswith('/'):
            redirect_url = "/conversations"
        
        # Construct final redirect URL (same origin for BFF pattern)
        final_redirect_url = f"{settings.FRONTEND_URL}{redirect_url}"
        
        # Add success parameter to URL for frontend to detect successful authentication
        separator = "&" if "?" in final_redirect_url else "?"
        final_redirect_url += f"{separator}auth_success=true&auth_timestamp={int(datetime.now().timestamp())}"
        
        # Return direct HTTP 302 redirect with cookie set in same response
        redirect_response = RedirectResponse(url=final_redirect_url, status_code=302)
        
        # Set the session cookie in the redirect response
        set_session_cookie(redirect_response, session_token)
        
        return redirect_response
        
    except Exception as e:
        logger.error(f"OAuth callback failed with exception: {type(e).__name__}: {str(e)}")
        logger.error(f"Exception details: {repr(e)}")
        if hasattr(e, '__traceback__'):
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        db.rollback()
        OAuthStateManager.delete_state(state) if 'state' in locals() else None
        error_url = f"{settings.FRONTEND_URL}/?auth_error=server_error"
        return RedirectResponse(url=error_url, status_code=302)


@router.post("/logout")
async def logout_user(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user_from_cookie_optional)
):
    """
    Log out user and clear session.
    
    Clears the session cookie and optionally logs the logout event.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object
        current_user: Current authenticated user (optional)
        
    Returns:
        Success message
    """
    try:
        # Clear session cookie
        clear_session_cookie(response)
        
        # Log logout event if user was authenticated
        if current_user:
            client_ip = get_client_ip(request)
            logger.info(f"User logged out: {current_user.google_id} from IP: {client_ip}")
        
        return {
            "success": True,
            "message": "Successfully logged out"
        }
        
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        # Still clear cookie even if logging fails
        clear_session_cookie(response)
        return {
            "success": True,
            "message": "Logged out"
        }


@router.get("/session")
async def get_session_status(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie_optional)
):
    """
    Get current session status and user information.
    
    Args:
        request: FastAPI request object for session validation
        current_user: Current authenticated user (optional)
        
    Returns:
        Session status and user information if authenticated
    """
    if not current_user:
        return {
            "authenticated": False,
            "user": None
        }
    
    return {
        "authenticated": True,
        "user": UserInfo(
            user_id=str(current_user.user_id),
            user_name=current_user.user_name,
            email=current_user.email or "",
            profile_picture=current_user.profile_picture,
            is_private=current_user.is_private,
            created_at=current_user.created_at
        )
    }


@router.get("/health")
async def auth_health_check():
    """
    Health check endpoint for authentication system.
    
    Returns:
        System health status
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.now().isoformat(),
        "oauth_configured": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        "cookie_settings": {
            "secure": settings.COOKIE_SECURE,
            "samesite": settings.COOKIE_SAMESITE,
            "httponly": settings.COOKIE_HTTPONLY,
            "domain": settings.COOKIE_DOMAIN or "none_for_localhost"
        }
    }


@router.post("/test-cookie")
async def test_cookie_setting(request: Request, response: Response):
    """
    Development-only endpoint for cookie functionality testing.
    """
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    
    test_cookie_name = "bff_test_cookie"
    test_cookie_value = f"test_{int(datetime.now().timestamp())}"
    
    response.set_cookie(
        key=test_cookie_name,
        value=test_cookie_value,
        max_age=300,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
        domain=settings.COOKIE_DOMAIN if settings.COOKIE_DOMAIN and settings.COOKIE_DOMAIN.strip() else None
    )
    
    return {
        "test_cookie_set": test_cookie_name,
        "test_cookie_value": test_cookie_value,
        "existing_cookies": list(request.cookies.keys()),
        "instructions": "Make another request to GET /test-cookie to check persistence"
    }


@router.get("/test-cookie")
async def check_test_cookie(request: Request):
    """
    Development-only endpoint to check test cookie persistence.
    """
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    
    test_cookie_name = "bff_test_cookie"
    test_cookie_value = request.cookies.get(test_cookie_name)
    
    return {
        "test_cookie_found": test_cookie_value is not None,
        "test_cookie_value": test_cookie_value,
        "session_cookie_present": settings.SESSION_COOKIE_NAME in request.cookies,
        "total_cookies": len(request.cookies)
    }


# Helper Functions

async def create_or_update_user(db: Session, user_data: dict) -> User:
    """
    Create new user or update existing user with OAuth data.
    
    Args:
        db: Database session
        user_data: Normalized user data from OAuth
        
    Returns:
        User object
    """
    # Check if user exists
    stmt = select(User).where(User.google_id == user_data['google_id'])
    existing_user = db.execute(stmt).scalar_one_or_none()
    
    if existing_user:
        # Update existing user
        existing_user.updated_at = datetime.now(timezone.utc)
        if user_data.get('email'):
            existing_user.email = user_data['email']
        if user_data.get('profile_picture'):
            existing_user.profile_picture = user_data['profile_picture']
        if user_data.get('user_name'):
            existing_user.user_name = user_data['user_name']
        
        user = existing_user
    else:
        # Create new user
        user = User(
            google_id=user_data['google_id'],
            email=user_data.get('email'),
            user_name=user_data['user_name'],
            profile_picture=user_data.get('profile_picture'),
            status='active'
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    return user


def set_session_cookie(response: Response, session_token: str):
    """
    Set secure session cookie with production-grade security settings.
    
    Args:
        response: FastAPI response object
        session_token: JWT session token
    """
    if not session_token or len(session_token) < 10:
        raise ValueError("Invalid session token")
    
    cookie_settings = {
        "key": settings.SESSION_COOKIE_NAME,
        "value": session_token,
        "max_age": settings.SESSION_TOKEN_EXPIRE_HOURS * 3600,
        "httponly": settings.COOKIE_HTTPONLY,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
        "path": "/"
    }
    
    # Only add domain if specified (important for localhost)
    if settings.COOKIE_DOMAIN and settings.COOKIE_DOMAIN.strip():
        cookie_settings["domain"] = settings.COOKIE_DOMAIN
    
    # Development mode logging
    if settings.DEBUG:
        logger.info(f"Setting session cookie: {settings.SESSION_COOKIE_NAME}")
        logger.info(f"Cookie settings: secure={settings.COOKIE_SECURE}, "
                   f"samesite={settings.COOKIE_SAMESITE}, httponly={settings.COOKIE_HTTPONLY}, "
                   f"domain={settings.COOKIE_DOMAIN or 'None'}")
    
    response.set_cookie(**cookie_settings)


def clear_session_cookie(response: Response):
    """
    Clear session cookie by setting it to expire immediately.
    
    Args:
        response: FastAPI response object
    """
    cookie_settings = {
        "key": settings.SESSION_COOKIE_NAME,
        "value": "",
        "max_age": 0,
        "httponly": True,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
        "path": "/"
    }
    
    # Add domain if specified
    if settings.COOKIE_DOMAIN and settings.COOKIE_DOMAIN.strip():
        cookie_settings["domain"] = settings.COOKIE_DOMAIN
    
    response.set_cookie(**cookie_settings)
    
    if settings.DEBUG:
        logger.info("Session cookie cleared")
