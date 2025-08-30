/**
 * Production-Grade Profile Picture Manager Hook
 * 
 * Features:
 * - Automatic URL optimization
 * - Intelligent fallback strategies  
 * - Performance optimization
 * - Error handling and retry logic
 * - Caching and prefetching
 * - Security validation
 */

'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';

// Profile picture configuration
interface ProfilePictureConfig {
  /** Use backend proxy for additional security and caching */
  useProxy?: boolean;
  /** Preferred image size */
  preferredSize?: number;
  /** Custom fallback image URL */
  fallbackUrl?: string;
  /** Enable aggressive caching */
  enableCaching?: boolean;
}

interface ProfilePictureResult {
  /** Optimized image URL ready for display */
  src: string | null;
  /** Whether the image is loading */
  isLoading: boolean;
  /** Error message if image failed to load */
  error: string | null;
  /** Retry function for failed images */
  retry: () => void;
  /** Whether using fallback image */
  isFallback: boolean;
}

// Validated Google CDN domains
const GOOGLE_CDN_DOMAINS = [
  'lh3.googleusercontent.com',
  'lh4.googleusercontent.com', 
  'lh5.googleusercontent.com',
  'lh6.googleusercontent.com',
  'googleusercontent.com',
];

/**
 * Check if URL is from Google CDN
 */
function isGoogleCDNUrl(url: string): boolean {
  try {
    const urlObj = new URL(url);
    return GOOGLE_CDN_DOMAINS.some(domain => 
      urlObj.hostname === domain || urlObj.hostname.endsWith(`.${domain}`)
    );
  } catch {
    return false;
  }
}

/**
 * Optimize Google profile picture URL
 */
function optimizeGoogleUrl(url: string, size: number): string {
  if (!isGoogleCDNUrl(url)) return url;
  
  try {
    const urlObj = new URL(url);
    
    // Add Google-specific optimization parameters
    urlObj.searchParams.set('s', size.toString()); // Size
    urlObj.searchParams.set('c', 'c'); // Crop to square
    urlObj.searchParams.set('rw', size.toString()); // Resize width
    urlObj.searchParams.set('rh', size.toString()); // Resize height
    
    return urlObj.toString();
  } catch {
    return url;
  }
}

/**
 * Generate proxy URL for additional security and caching
 */
function generateProxyUrl(originalUrl: string, size?: number): string {
  const params = new URLSearchParams();
  params.set('url', originalUrl);
  if (size) {
    params.set('size', size.toString());
  }
  
  return `/api/v1/images/proxy?${params.toString()}`;
}

/**
 * Validate image URL for security
 */
function isValidImageUrl(url: string): boolean {
  try {
    const urlObj = new URL(url);
    
    // Only allow HTTPS URLs
    if (urlObj.protocol !== 'https:') return false;
    
    // Check against allowed domains
    const allowedDomains = [
      ...GOOGLE_CDN_DOMAINS,
      'localhost', // For development
    ];
    
    return allowedDomains.some(domain => 
      urlObj.hostname === domain || urlObj.hostname.endsWith(`.${domain}`)
    );
  } catch {
    return false;
  }
}

// Cache for optimized URLs
const urlCache = new Map<string, string>();

/**
 * Production-grade profile picture manager hook
 */
export function useProfilePicture(
  originalUrl: string | null | undefined,
  config: ProfilePictureConfig = {}
): ProfilePictureResult {
  const {
    useProxy = true,
    preferredSize = 64,
    fallbackUrl = '/images/blue_lotus_logo.png',
    enableCaching = true,
  } = config;

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFallback, setIsFallback] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  // Generate cache key
  const cacheKey = useMemo(() => {
    if (!originalUrl) return null;
    return `${originalUrl}:${preferredSize}:${useProxy}`;
  }, [originalUrl, preferredSize, useProxy]);

  // Process and optimize the image URL
  const processedUrl = useMemo(() => {
    if (!originalUrl) return null;

    // Check cache first
    if (enableCaching && cacheKey && urlCache.has(cacheKey)) {
      return urlCache.get(cacheKey)!;
    }

    // Validate URL security
    if (!isValidImageUrl(originalUrl)) {
      console.warn('Invalid or insecure profile picture URL:', originalUrl);
      return null;
    }

    let optimizedUrl = originalUrl;

    // Optimize Google CDN URLs
    if (isGoogleCDNUrl(originalUrl)) {
      optimizedUrl = optimizeGoogleUrl(originalUrl, preferredSize * 2); // 2x for retina
    }

    // Use proxy if enabled
    if (useProxy && isGoogleCDNUrl(originalUrl)) {
      optimizedUrl = generateProxyUrl(originalUrl, preferredSize * 2);
    }

    // Cache the result
    if (enableCaching && cacheKey) {
      urlCache.set(cacheKey, optimizedUrl);
    }

    return optimizedUrl;
  }, [originalUrl, preferredSize, useProxy, enableCaching, cacheKey]);

  // Reset state when URL changes
  useEffect(() => {
    setIsLoading(!!processedUrl);
    setError(null);
    setIsFallback(false);
    setRetryCount(0);
  }, [processedUrl]);

  // Preload image to detect loading state and errors
  useEffect(() => {
    if (!processedUrl) {
      setIsLoading(false);
      return;
    }

    const img = new Image();
    let mounted = true;

    const handleLoad = () => {
      if (!mounted) return;
      setIsLoading(false);
      setError(null);
      setIsFallback(false);
    };

    const handleError = () => {
      if (!mounted) return;
      setIsLoading(false);
      
      // If this is the original URL and we have a fallback
      if (!isFallback && fallbackUrl) {
        setIsFallback(true);
        setError(null);
      } else {
        setError('Failed to load profile picture');
      }
    };

    img.onload = handleLoad;
    img.onerror = handleError;
    
    // Set src to start loading
    img.src = isFallback ? fallbackUrl : processedUrl;

    return () => {
      mounted = false;
      img.onload = null;
      img.onerror = null;
    };
  }, [processedUrl, isFallback, fallbackUrl]);

  // Retry function
  const retry = useCallback(() => {
    if (retryCount < 2) { // Max 2 retries
      setRetryCount(prev => prev + 1);
      setError(null);
      setIsLoading(true);
      setIsFallback(false);
      
      // Clear cache for this URL
      if (cacheKey) {
        urlCache.delete(cacheKey);
      }
    }
  }, [retryCount, cacheKey]);

  // Determine final source URL
  const src = useMemo(() => {
    if (error && !isFallback) return null;
    if (isFallback) return fallbackUrl;
    return processedUrl;
  }, [processedUrl, isFallback, fallbackUrl, error]);

  return {
    src,
    isLoading,
    error,
    retry,
    isFallback: isFallback || (!processedUrl && !!fallbackUrl),
  };
}

export default useProfilePicture;
