/**
 * Production-Grade Profile Picture Component
 * 
 * Features:
 * - Google CDN image optimization
 * - Multiple fallback strategies
 * - Loading states with skeleton
 * - Error handling with retry
 * - Accessibility compliance
 * - Performance optimization
 * - Security validation
 */

'use client';

import React, { useState, useCallback, useRef } from 'react';
import Image from 'next/image';
import { User } from 'lucide-react';
import styles from './ProfilePicture.module.css';

// Profile picture size variants
export type ProfilePictureSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

interface ProfilePictureProps {
  /** Profile picture URL (typically from Google OAuth) */
  src?: string | null;
  /** User's display name for alt text */
  alt?: string;
  /** Size variant */
  size?: ProfilePictureSize;
  /** Custom CSS classes */
  className?: string;
  /** Whether to show loading skeleton */
  showSkeleton?: boolean;
  /** Click handler */
  onClick?: () => void;
  /** Whether the image should be clickable */
  clickable?: boolean;
  /** Custom fallback image URL */
  fallbackSrc?: string;
}

// Size configuration mapping
const sizeConfig: Record<ProfilePictureSize, { width: number; height: number; iconSize: number }> = {
  xs: { width: 20, height: 20, iconSize: 12 },
  sm: { width: 24, height: 24, iconSize: 14 },
  md: { width: 32, height: 32, iconSize: 18 },
  lg: { width: 48, height: 48, iconSize: 24 },
  xl: { width: 64, height: 64, iconSize: 32 },
};

/**
 * Validates if URL is from allowed Google CDN domains
 */
function isValidGoogleImageUrl(url: string): boolean {
  try {
    const urlObj = new URL(url);
    const allowedDomains = [
      'lh3.googleusercontent.com',
      'lh4.googleusercontent.com',
      'lh5.googleusercontent.com',
      'lh6.googleusercontent.com',
      'googleusercontent.com',
    ];
    return allowedDomains.some(domain => urlObj.hostname.endsWith(domain));
  } catch {
    return false;
  }
}

/**
 * Optimizes Google profile picture URL for better performance
 */
function optimizeGoogleImageUrl(url: string, size: number): string {
  if (!isValidGoogleImageUrl(url)) return url;
  
  try {
    const urlObj = new URL(url);
    // Google allows size optimization via URL parameters
    urlObj.searchParams.set('s', size.toString()); // Size parameter
    urlObj.searchParams.set('c', 'c'); // Crop to square
    return urlObj.toString();
  } catch {
    return url;
  }
}

export function ProfilePicture({
  src,
  alt = 'Profile',
  size = 'md',
  className = '',
  showSkeleton = true,
  onClick,
  clickable = false,
  fallbackSrc = '/images/blue_lotus_logo.png'
}: ProfilePictureProps) {
  const [imageState, setImageState] = useState<'loading' | 'loaded' | 'error' | 'fallback'>('loading');
  const [retryCount, setRetryCount] = useState(0);
  const imageRef = useRef<HTMLImageElement>(null);
  
  const config = sizeConfig[size];
  const maxRetries = 2;

  // Optimize image URL if it's from Google
  const optimizedSrc = src && isValidGoogleImageUrl(src) 
    ? optimizeGoogleImageUrl(src, config.width * 2) // 2x for retina displays
    : src;

  const handleImageLoad = useCallback(() => {
    setImageState('loaded');
  }, []);

  const handleImageError = useCallback(() => {
    if (retryCount < maxRetries && src) {
      // Retry with original URL
      setRetryCount(prev => prev + 1);
      if (imageRef.current) {
        imageRef.current.src = src;
      }
    } else if (fallbackSrc && src !== fallbackSrc) {
      // Fall back to default image
      setImageState('fallback');
    } else {
      // Final fallback to icon
      setImageState('error');
    }
  }, [retryCount, src, fallbackSrc, maxRetries]);

  const handleRetry = useCallback(() => {
    if (src) {
      setImageState('loading');
      setRetryCount(0);
    }
  }, [src]);

  // Determine what to render
  const shouldShowImage = optimizedSrc && imageState !== 'error';
  const shouldShowFallbackImage = imageState === 'fallback' && fallbackSrc;
  const shouldShowIcon = !shouldShowImage && !shouldShowFallbackImage;
  const shouldShowSkeleton = showSkeleton && imageState === 'loading';

  const containerClasses = [
    styles.profilePicture,
    styles[size],
    clickable || onClick ? styles.clickable : '',
    shouldShowSkeleton ? styles.loading : '',
    className
  ].filter(Boolean).join(' ');

  const handleClick = useCallback(() => {
    if (onClick) onClick();
  }, [onClick]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if ((e.key === 'Enter' || e.key === ' ') && onClick) {
      e.preventDefault();
      onClick();
    }
  }, [onClick]);

  return (
    <div 
      className={containerClasses}
      style={{ 
        width: config.width, 
        height: config.height,
        cursor: (clickable || onClick) ? 'pointer' : 'default'
      }}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={(clickable || onClick) ? 0 : undefined}
      role={(clickable || onClick) ? 'button' : undefined}
      aria-label={(clickable || onClick) ? `${alt} profile picture` : undefined}
    >
      {/* Loading Skeleton */}
      {shouldShowSkeleton && (
        <div className={styles.skeleton} aria-label="Loading profile picture" />
      )}

      {/* Main Profile Image */}
      {shouldShowImage && (
        <Image
          ref={imageRef}
          src={optimizedSrc}
          alt={alt}
          width={config.width}
          height={config.height}
          className={styles.image}
          onLoad={handleImageLoad}
          onError={handleImageError}
          priority={size === 'lg' || size === 'xl'} // Prioritize larger images
          quality={85}
          placeholder="blur"
          blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkqGx0f/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R+Rw="
        />
      )}

      {/* Fallback Image */}
      {shouldShowFallbackImage && (
        <Image
          src={fallbackSrc}
          alt={alt}
          width={config.width}
          height={config.height}
          className={styles.image}
          onLoad={handleImageLoad}
          onError={() => setImageState('error')}
        />
      )}

      {/* Icon Fallback */}
      {shouldShowIcon && (
        <div className={styles.iconFallback}>
          <User size={config.iconSize} />
        </div>
      )}

      {/* Retry Button for Failed Images */}
      {imageState === 'error' && retryCount >= maxRetries && (
        <button
          className={styles.retryButton}
          onClick={handleRetry}
          aria-label="Retry loading profile picture"
          type="button"
        >
          ↻
        </button>
      )}
    </div>
  );
}

export default ProfilePicture;
