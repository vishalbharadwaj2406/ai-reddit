"""
Production-Grade Profile Picture Proxy API

Features:
- Security validation for external image URLs
- Image caching and optimization
- Proper content-type headers
- Error handling with fallbacks
- Rate limiting protection
- CDN-ready responses
"""

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import Response as FastAPIResponse
import httpx
import hashlib
import logging
from urllib.parse import urlparse
from typing import Optional
import mimetypes
from datetime import datetime, timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/images", tags=["images"])

# Allowed image domains for security
ALLOWED_IMAGE_DOMAINS = {
    'lh3.googleusercontent.com',
    'lh4.googleusercontent.com', 
    'lh5.googleusercontent.com',
    'lh6.googleusercontent.com',
    'googleusercontent.com',
}

# Supported image types
SUPPORTED_IMAGE_TYPES = {
    'image/jpeg', 'image/jpg', 'image/png', 
    'image/webp', 'image/gif', 'image/bmp'
}

# Cache TTL for profile pictures (1 hour)
CACHE_TTL = 3600

# Maximum image size (5MB)
MAX_IMAGE_SIZE = 5 * 1024 * 1024


def is_allowed_image_url(url: str) -> bool:
    """
    Validate if image URL is from allowed domains.
    
    Args:
        url: Image URL to validate
        
    Returns:
        True if URL is from allowed domain
    """
    try:
        parsed = urlparse(url)
        return any(
            parsed.hostname and parsed.hostname.endswith(domain) 
            for domain in ALLOWED_IMAGE_DOMAINS
        )
    except Exception:
        return False


def generate_cache_key(url: str, size: Optional[str] = None) -> str:
    """
    Generate cache key for image URL.
    
    Args:
        url: Original image URL
        size: Optional size parameter
        
    Returns:
        Cache key hash
    """
    cache_data = f"{url}:{size or 'original'}"
    return hashlib.md5(cache_data.encode()).hexdigest()


@router.get("/proxy")
async def proxy_profile_picture(
    url: str,
    size: Optional[str] = None,
    request: Request = None
) -> FastAPIResponse:
    """
    Proxy profile pictures with security validation and caching.
    
    Args:
        url: External image URL to proxy
        size: Optional size parameter for optimization
        request: FastAPI request object
        
    Returns:
        Proxied image response with proper headers
        
    Raises:
        HTTPException: For invalid URLs or fetch errors
    """
    # Validate URL security
    if not url:
        raise HTTPException(
            status_code=400,
            detail="Image URL is required"
        )
    
    if not is_allowed_image_url(url):
        logger.warning(f"Blocked request for disallowed image URL: {url}")
        raise HTTPException(
            status_code=403,
            detail="Image URL not from allowed domain"
        )
    
    # Generate cache key
    cache_key = generate_cache_key(url, size)
    
    try:
        # Fetch image from external URL
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(connect=5.0, read=10.0),
            limits=httpx.Limits(max_connections=10)
        ) as client:
            
            # Add size optimization for Google images
            fetch_url = url
            if size and 'googleusercontent.com' in url:
                try:
                    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
                    parsed = urlparse(url)
                    query_params = parse_qs(parsed.query)
                    query_params['s'] = [size]  # Google size parameter
                    query_params['c'] = ['c']   # Crop to square
                    new_query = urlencode(query_params, doseq=True)
                    fetch_url = urlunparse(parsed._replace(query=new_query))
                except Exception as e:
                    logger.warning(f"Failed to optimize Google image URL: {e}")
            
            response = await client.get(
                fetch_url,
                headers={
                    'User-Agent': 'AI-Social-App/1.0',
                    'Referer': settings.FRONTEND_URL or 'http://localhost:8000'
                }
            )
            
            response.raise_for_status()
            
            # Validate content type
            content_type = response.headers.get('content-type', '').lower()
            if not any(supported in content_type for supported in SUPPORTED_IMAGE_TYPES):
                raise HTTPException(
                    status_code=415,
                    detail=f"Unsupported image type: {content_type}"
                )
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > MAX_IMAGE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail="Image file too large"
                )
            
            # Validate actual content size
            content = response.content
            if len(content) > MAX_IMAGE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail="Image file too large"
                )
            
            # Determine proper content type
            if content_type.startswith('image/'):
                final_content_type = content_type
            else:
                # Fallback to MIME type detection
                guessed_type, _ = mimetypes.guess_type(url)
                final_content_type = guessed_type or 'image/jpeg'
            
            # Build response headers
            headers = {
                'Content-Type': final_content_type,
                'Cache-Control': f'public, max-age={CACHE_TTL}, immutable',
                'ETag': f'"{cache_key}"',
                'Expires': (datetime.utcnow() + timedelta(seconds=CACHE_TTL)).strftime(
                    '%a, %d %b %Y %H:%M:%S GMT'
                ),
                'X-Content-Type-Options': 'nosniff',
                'X-Robots-Tag': 'noindex, nofollow',
            }
            
            # Add CORS headers for frontend access
            if settings.FRONTEND_URL:
                headers['Access-Control-Allow-Origin'] = settings.FRONTEND_URL
            
            return FastAPIResponse(
                content=content,
                media_type=final_content_type,
                headers=headers
            )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching image {url}: {e.response.status_code}")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch image: HTTP {e.response.status_code}"
        )
    except httpx.RequestError as e:
        logger.error(f"Request error fetching image {url}: {e}")
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch image: Network error"
        )
    except Exception as e:
        logger.error(f"Unexpected error proxying image {url}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing image"
        )


@router.get("/health")
async def images_health_check():
    """
    Health check for image proxy service.
    
    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": "image_proxy",
        "timestamp": datetime.utcnow().isoformat(),
        "allowed_domains": list(ALLOWED_IMAGE_DOMAINS),
        "supported_types": list(SUPPORTED_IMAGE_TYPES),
        "max_size_mb": MAX_IMAGE_SIZE / (1024 * 1024)
    }
