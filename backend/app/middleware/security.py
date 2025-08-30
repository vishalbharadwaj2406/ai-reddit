"""
Security Middleware

Enterprise-grade security middleware for production deployment.
Implements OWASP security headers and best practices.

Security Features:
- Security headers for XSS, CSRF, and clickjacking protection
- CORS configuration
- Request rate limiting foundation
- Security event logging
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    
    Implements OWASP security guidelines for web applications.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add security headers
        self.add_security_headers(response)
        
        # Add performance header
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log security events
        self.log_security_events(request, response)
        
        return response
    
    def add_security_headers(self, response: Response):
        """Add comprehensive security headers."""
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS Protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (adjust based on your needs)
        if settings.ENVIRONMENT == "production":
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' https://accounts.google.com",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
                "font-src 'self' https://fonts.gstatic.com",
                "img-src 'self' data: https:",
                "connect-src 'self' https://api.example.com",
                "frame-src https://accounts.google.com"
            ]
            response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # HTTPS enforcement in production
        if settings.ENVIRONMENT == "production":
            # HTTP Strict Transport Security (1 year)
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Permissions Policy (formerly Feature Policy)
        permissions_policy = [
            "camera=()",
            "microphone=()",
            "geolocation=()",
            "gyroscope=()",
            "magnetometer=()",
            "payment=()",
            "usb=()"
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions_policy)
    
    def log_security_events(self, request: Request, response: Response):
        """Log security-relevant events."""
        
        # Log failed authentication attempts
        if response.status_code == 401:
            client_ip = self.get_client_ip(request)
            logger.warning(f"Authentication failed from IP: {client_ip} - Path: {request.url.path}")
        
        # Log suspicious requests
        if response.status_code == 403:
            client_ip = self.get_client_ip(request)
            logger.warning(f"Forbidden access attempt from IP: {client_ip} - Path: {request.url.path}")
        
        # Log server errors
        if response.status_code >= 500:
            client_ip = self.get_client_ip(request)
            logger.error(f"Server error for IP: {client_ip} - Path: {request.url.path} - Status: {response.status_code}")
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        if hasattr(request.client, 'host'):
            return request.client.host
        
        return "unknown"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all requests for monitoring and debugging.
    
    Provides structured logging for production monitoring.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request start
        client_ip = self.get_client_ip(request)
        logger.info(f"Request started: {request.method} {request.url.path} from {client_ip}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log request completion
        logger.info(
            f"Request completed: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        if hasattr(request.client, 'host'):
            return request.client.host
        
        return "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Basic rate limiting middleware.
    
    In production, use Redis-based rate limiting like slowapi or
    a dedicated service like Cloudflare or AWS API Gateway.
    """
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}  # In production, use Redis
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self.get_client_ip(request)
        current_time = int(time.time() / 60)  # Current minute
        
        # Clean old entries (keep only current minute)
        self.request_counts = {
            ip: {minute: count for minute, count in data.items() if minute >= current_time - 1}
            for ip, data in self.request_counts.items()
        }
        
        # Check rate limit
        if client_ip in self.request_counts:
            if current_time in self.request_counts[client_ip]:
                self.request_counts[client_ip][current_time] += 1
            else:
                self.request_counts[client_ip][current_time] = 1
        else:
            self.request_counts[client_ip] = {current_time: 1}
        
        # Check if rate limit exceeded
        if self.request_counts[client_ip][current_time] > self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": "60"}
            )
        
        return await call_next(request)
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        if hasattr(request.client, 'host'):
            return request.client.host
        
        return "unknown"
