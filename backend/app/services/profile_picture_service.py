"""
Production-Grade Profile Picture Service

Handles profile picture URL validation, optimization, and processing
for the AI Social platform with enhanced security and performance.

Features:
- Google OAuth profile picture processing
- URL validation and security checks  
- Image optimization and resizing
- Fallback handling for broken URLs
- Caching strategies for better performance
"""

from typing import Optional, Dict, Any
import re
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import httpx
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

class ProfilePictureService:
    """Service for handling profile picture operations."""
    
    # Allowed profile picture domains for security
    ALLOWED_DOMAINS = {
        'lh3.googleusercontent.com',
        'lh4.googleusercontent.com',
        'lh5.googleusercontent.com', 
        'lh6.googleusercontent.com',
        'googleusercontent.com',
    }
    
    # Default profile picture sizes
    DEFAULT_SIZES = {
        'thumbnail': 32,
        'small': 48,
        'medium': 64,
        'large': 128,
        'extra_large': 256
    }
    
    @classmethod
    def is_valid_profile_picture_url(cls, url: str) -> bool:
        """
        Validate if profile picture URL is secure and allowed.
        
        Args:
            url: Profile picture URL to validate
            
        Returns:
            True if URL is valid and secure
        """
        if not url or not isinstance(url, str):
            return False
            
        try:
            parsed = urlparse(url)
            
            # Must be HTTPS
            if parsed.scheme != 'https':
                return False
                
            # Must be from allowed domains
            if not any(
                parsed.hostname and 
                (parsed.hostname == domain or parsed.hostname.endswith(f'.{domain}'))
                for domain in cls.ALLOWED_DOMAINS
            ):
                return False
                
            return True
            
        except Exception as e:
            logger.warning(f"Error validating profile picture URL {url}: {e}")
            return False
    
    @classmethod
    def optimize_google_profile_picture_url(
        cls, 
        url: str, 
        size: int = 64,
        ensure_square: bool = True
    ) -> str:
        """
        Optimize Google profile picture URL for better performance.
        
        Args:
            url: Original Google profile picture URL
            size: Desired image size in pixels
            ensure_square: Whether to crop image to square
            
        Returns:
            Optimized URL with size parameters
        """
        if not cls.is_valid_profile_picture_url(url):
            return url
            
        if 'googleusercontent.com' not in url:
            return url
            
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # Add Google-specific optimization parameters
            query_params['s'] = [str(size)]  # Size parameter
            if ensure_square:
                query_params['c'] = ['c']  # Crop to square
            
            # Additional optimization parameters
            query_params['rw'] = [str(size)]  # Resize width
            query_params['rh'] = [str(size)]  # Resize height
            query_params['mo'] = ['k']  # Maintain original quality when possible
            
            # Rebuild URL with optimized parameters
            new_query = urlencode(query_params, doseq=True)
            optimized_url = urlunparse(parsed._replace(query=new_query))
            
            logger.debug(f"Optimized profile picture URL from {url} to {optimized_url}")
            return optimized_url
            
        except Exception as e:
            logger.warning(f"Error optimizing Google profile picture URL {url}: {e}")
            return url
    
    @classmethod
    def get_profile_picture_variants(cls, url: str) -> Dict[str, str]:
        """
        Generate multiple size variants of a profile picture.
        
        Args:
            url: Original profile picture URL
            
        Returns:
            Dictionary of size variants
        """
        if not cls.is_valid_profile_picture_url(url):
            return {}
            
        variants = {}
        for size_name, size_px in cls.DEFAULT_SIZES.items():
            variants[size_name] = cls.optimize_google_profile_picture_url(
                url, size_px, ensure_square=True
            )
            
        return variants
    
    @classmethod
    async def validate_profile_picture_accessibility(cls, url: str) -> bool:
        """
        Check if profile picture URL is accessible via HTTP request.
        
        Args:
            url: Profile picture URL to check
            
        Returns:
            True if URL is accessible
        """
        if not cls.is_valid_profile_picture_url(url):
            return False
            
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(connect=2.0, read=5.0)
            ) as client:
                response = await client.head(
                    url,
                    headers={
                        'User-Agent': 'AI-Social/1.0 Profile-Validator'
                    }
                )
                
                # Check if response is successful and content is an image
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    return content_type.startswith('image/')
                    
                return False
                
        except Exception as e:
            logger.warning(f"Error checking profile picture accessibility {url}: {e}")
            return False
    
    @classmethod
    def sanitize_profile_picture_data(cls, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize and optimize profile picture data from OAuth providers.
        
        Args:
            profile_data: Raw profile data from OAuth provider
            
        Returns:
            Sanitized profile data with optimized picture URLs
        """
        if not isinstance(profile_data, dict):
            return profile_data
            
        # Create a copy to avoid modifying original
        sanitized_data = profile_data.copy()
        
        # Process profile picture URL
        picture_url = profile_data.get('profile_picture') or profile_data.get('picture')
        
        if picture_url and cls.is_valid_profile_picture_url(picture_url):
            # Optimize the URL for medium size (good for most UI contexts)
            optimized_url = cls.optimize_google_profile_picture_url(
                picture_url, 
                size=cls.DEFAULT_SIZES['medium'],
                ensure_square=True
            )
            sanitized_data['profile_picture'] = optimized_url
            
            # Generate variants for different use cases
            sanitized_data['profile_picture_variants'] = cls.get_profile_picture_variants(picture_url)
            
        else:
            # Remove invalid URLs
            sanitized_data['profile_picture'] = None
            sanitized_data.pop('picture', None)
            
        logger.info(f"Sanitized profile picture data: {bool(sanitized_data.get('profile_picture'))}")
        return sanitized_data
    
    @classmethod
    def get_fallback_profile_picture_url(cls) -> str:
        """
        Get fallback profile picture URL for users without pictures.
        
        Returns:
            URL to default profile picture
        """
        # Use the app logo as fallback
        base_url = settings.FRONTEND_URL or 'http://localhost:8000'
        return f"{base_url}/images/blue_lotus_logo.png"
    
    @classmethod
    def generate_profile_picture_proxy_url(
        cls, 
        original_url: str, 
        size: Optional[int] = None
    ) -> str:
        """
        Generate proxy URL for profile picture with optional size optimization.
        
        Args:
            original_url: Original profile picture URL
            size: Optional desired size
            
        Returns:
            Proxy URL for serving the profile picture
        """
        if not cls.is_valid_profile_picture_url(original_url):
            return cls.get_fallback_profile_picture_url()
            
        base_url = settings.FRONTEND_URL or 'http://localhost:8000'
        params = {'url': original_url}
        
        if size:
            params['size'] = str(size)
            
        query_string = urlencode(params)
        return f"{base_url}/api/v1/images/proxy?{query_string}"
