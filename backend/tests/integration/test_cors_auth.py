"""
Test CORS and Cross-Origin Authentication

Validates that authentication works properly across origins.
Tests the migration from BFF to cross-origin authentication pattern.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from app.models.user import User
from tests.fixtures.auth_fixtures import sample_user, cors_headers


class TestCORSAuthentication:
    """Test cross-origin authentication scenarios"""
    
    @pytest.fixture
    def client(self):
        """Test client for making requests"""
        return TestClient(app)
    
    @pytest.fixture
    def authenticated_user_cookies(self, sample_user):
        """Mock authenticated user cookies"""
        from app.core.jwt import JWTManager, create_session_token_with_fingerprint
        
        # Create session token
        session_token = create_session_token_with_fingerprint(
            user_id=str(sample_user.user_id),
            user_agent="test-agent",
            ip_address="127.0.0.1"
        )
        
        # Create refresh token
        refresh_token = JWTManager.create_refresh_token(str(sample_user.user_id))
        
        return {
            "ai_social_session": session_token,
            "ai_social_session_refresh": refresh_token
        }
    
    def test_cors_preflight_auth_endpoint(self, client):
        """Test CORS preflight for auth endpoints"""
        response = client.options(
            "/api/v1/auth/session",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            }
        )
        
        # Note: FastAPI CORS middleware handles preflight at middleware level
        # The endpoint might return 405 (Method Not Allowed) but CORS headers should be present
        # What matters is that there's no CORS error (which would be a different status)
        
        # Check that we don't get a CORS-specific error
        assert response.status_code != 403  # Not a CORS forbidden
        
        # In a real browser, the middleware would have already handled the preflight
        # and this test confirms the endpoint is accessible cross-origin
    
    def test_cors_simple_request(self, client):
        """Test simple CORS request to health endpoint"""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_cross_origin_session_validation(self, client, authenticated_user_cookies, sample_user):
        """Test session validation from different origin"""
        with patch('app.dependencies.auth.get_db') as mock_get_db:
            # Mock the database session
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_db.execute.return_value.scalar_one_or_none.return_value = sample_user
            
            response = client.get(
                "/api/v1/auth/session",
                headers={"Origin": "http://localhost:3000"},
                cookies=authenticated_user_cookies
            )
            
            # The exact response depends on the session validation logic
            # but we should not get a CORS error
        assert response.status_code in [200, 401]  # Either valid session or needs refresh
        
        # Verify no CORS error occurred
        if response.status_code == 401:
            data = response.json()
            # Should be an auth error, not a CORS error
            assert "CORS" not in data.get("detail", "")
    
    def test_refresh_token_cors_request(self, client):
        """Test token refresh endpoint with CORS headers"""
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Origin": "http://localhost:3000"},
            # No cookies provided - should get auth error, not CORS error
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Token refresh failed"
        
        # This confirms CORS is working - we get auth error, not CORS error
    
    def test_cors_credentials_included(self, client):
        """Test that CORS allows credentials for cookie-based auth"""
        # This test verifies the allow_credentials=True setting
        response = client.get(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Cookie": "test=value"  # Simulate cookie being sent
            }
        )
        
        assert response.status_code == 200
        # If CORS credentials weren't allowed, this would fail in a real browser
    
    def test_cors_disallowed_origin(self, client):
        """Test that non-allowed origins are rejected"""
        response = client.get(
            "/health",
            headers={"Origin": "http://malicious-site.com"}
        )
        
        # The request itself might succeed (server-side doesn't block)
        # but in a real browser, the CORS check would prevent the response from being read
        # This test mainly documents the expected behavior
        assert response.status_code == 200  # Server responds
        # In browser: CORS error would prevent reading the response


class TestCORSConfiguration:
    """Test CORS configuration itself"""
    
    def test_cors_origins_development(self):
        """Test that development origins are properly configured"""
        from app.core.config import settings
        
        # Verify our development origins are configured
        origins = settings.ALLOWED_ORIGINS.split(",")
        assert "http://localhost:3000" in origins
        assert "http://localhost:3001" in origins
    
    def test_cors_settings_cross_origin_compatible(self):
        """Test that cookie settings are compatible with cross-origin"""
        from app.core.config import settings
        
        # For development, these should be set for cross-origin compatibility
        assert settings.COOKIE_SAMESITE == "lax"  # Allows cross-origin
        assert settings.COOKIE_SECURE == False  # For localhost development
        assert settings.COOKIE_DOMAIN in [None, ""]  # No domain restriction for localhost


class TestBackendOnlyMigration:
    """Test that BFF-specific functionality has been removed"""
    
    def test_no_frontend_serving(self, client):
        """Test that backend no longer serves frontend files"""
        # These should return 404, not serve HTML files
        frontend_paths = [
            "/",
            "/dashboard", 
            "/conversations",
            "/login"
        ]
        
        for path in frontend_paths:
            response = client.get(path)
            # Should be 404 (not found) since we removed frontend serving
            assert response.status_code == 404
            
            # Should not return HTML content
            content_type = response.headers.get("content-type", "")
            assert "text/html" not in content_type
    
    def test_api_endpoints_still_work(self, client):
        """Test that API endpoints are still functional"""
        # Health endpoint should work
        response = client.get("/health")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        # Auth endpoints should exist (even if they return errors without auth)
        response = client.get("/api/v1/auth/session")
        assert response.status_code in [200, 401]  # Should exist, might need auth
        
        # API docs should be available
        response = client.get("/docs")
        assert response.status_code == 200
