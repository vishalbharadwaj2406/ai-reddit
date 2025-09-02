/**
 * Hook for hydration-safe date formatting
 * 
 * Prevents hydration mismatches by ensuring date formatting
 * only happens on the client side after hydration is complete.
 */

import { useState, useEffect } from 'react';

export function useHydrationSafeDate() {
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    setIsHydrated(true);
  }, []);

  const formatRelativeTime = (dateString: string): string => {
    if (!isHydrated) {
      return 'Recently';
    }

    try {
      const now = new Date();
      const date = new Date(dateString);
      const diffInMs = now.getTime() - date.getTime();
      const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
      const diffInDays = Math.floor(diffInHours / 24);

      if (diffInHours < 1) return 'Just now';
      if (diffInHours < 24) return `${diffInHours} hours ago`;
      if (diffInDays === 1) return '1 day ago';
      if (diffInDays < 7) return `${diffInDays} days ago`;
      return '1 week ago';
    } catch {
      return 'Recently';
    }
  };

  const formatTime = (dateString: string): string => {
    if (!isHydrated) {
      return 'Recently';
    }

    try {
      const date = new Date(dateString);
      return isNaN(date.getTime()) 
        ? 'Just now' 
        : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return 'Just now';
    }
  };

  const formatDateTime = (dateString: string): string => {
    if (!isHydrated) {
      return 'recently';
    }

    try {
      const date = new Date(dateString);
      return isNaN(date.getTime()) 
        ? 'recently' 
        : date.toLocaleString();
    } catch {
      return 'recently';
    }
  };

  return {
    isHydrated,
    formatRelativeTime,
    formatTime,
    formatDateTime
  };
}
