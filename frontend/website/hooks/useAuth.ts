/**
 * Production-Grade Authentication Hooks
 * 
 * Provides type-safe, cached authentication state management with
 * comprehensive error handling and performance optimizations.
 */

'use client'

import { useCallback, useEffect, useState } from 'react';
import { useSessionContext } from '../components/providers/SessionWrapper';
import type { SessionUser } from '../lib/auth/session';

export interface UseAuthReturn {
  // Core authentication state
  isAuthenticated: boolean;
  user: SessionUser | null;
  loading: boolean;
  error: string | null;
  isInitialized: boolean;
  
  // Authentication actions
  login: (returnUrl?: string) => void;
  logout: (redirectPath?: string) => Promise<void>;
  refresh: () => Promise<void>;
  clearError: () => void;
  
  // Convenience helpers
  isLoggedIn: boolean;
  hasError: boolean;
  isReady: boolean; // Initialized and not loading
}

/**
 * Main authentication hook - provides complete auth state and actions
 */
export function useAuth(): UseAuthReturn {
  const sessionContext = useSessionContext();
  
  const handleRefresh = useCallback(async () => {
    try {
      await sessionContext.refresh();
    } catch (error) {
      console.error('Failed to refresh session:', error);
    }
  }, [sessionContext]);

  return {
    // Core state
    isAuthenticated: sessionContext.isAuthenticated,
    user: sessionContext.user,
    loading: sessionContext.loading,
    error: sessionContext.error || null,
    isInitialized: sessionContext.isInitialized,
    
    // Actions
    login: sessionContext.login,
    logout: sessionContext.logout,
    refresh: handleRefresh,
    clearError: sessionContext.clearError,
    
    // Convenience
    isLoggedIn: sessionContext.isAuthenticated && !!sessionContext.user,
    hasError: !!sessionContext.error,
    isReady: sessionContext.isInitialized && !sessionContext.loading,
  };
}

/**
 * Hook for components that need to know authentication status but don't need user data
 */
export function useAuthStatus() {
  const { isAuthenticated, loading, isInitialized } = useSessionContext();
  
  return {
    isAuthenticated,
    loading,
    isInitialized,
    isReady: isInitialized && !loading,
  };
}

/**
 * Hook for components that need user data (only returns when authenticated)
 */
export function useAuthUser(): {
  user: SessionUser | null;
  loading: boolean;
  error: string | null;
  isReady: boolean;
} {
  const { user, loading, error, isInitialized, isAuthenticated } = useSessionContext();
  
  return {
    user: isAuthenticated ? user : null,
    loading,
    error: error || null,
    isReady: isInitialized && !loading && isAuthenticated,
  };
}

/**
 * Hook for implementing authentication-dependent effects
 */
export function useAuthEffect(
  effect: (user: SessionUser) => void | (() => void),
  deps: React.DependencyList = []
) {
  const { user, isReady } = useAuth();
  
  useEffect(() => {
    if (isReady && user) {
      return effect(user);
    }
  }, [isReady, user, ...deps]);
}

/**
 * Hook for components that need to redirect based on auth state
 */
export function useAuthRedirect(options: {
  requireAuth?: boolean;
  redirectTo?: string;
  redirectWhen?: 'authenticated' | 'unauthenticated';
}) {
  const { isAuthenticated, isReady } = useAuth();
  const [hasRedirected, setHasRedirected] = useState(false);
  
  useEffect(() => {
    if (!isReady || hasRedirected) return;
    
    const shouldRedirect = 
      (options.redirectWhen === 'authenticated' && isAuthenticated) ||
      (options.redirectWhen === 'unauthenticated' && !isAuthenticated) ||
      (options.requireAuth && !isAuthenticated);
    
    if (shouldRedirect && options.redirectTo) {
      setHasRedirected(true);
      window.location.href = options.redirectTo;
    }
  }, [isReady, isAuthenticated, hasRedirected, options]);
  
  return { hasRedirected };
}

/**
 * Hook for managing loading states during authentication operations
 */
export function useAuthOperation<T = void>(
  operation: () => Promise<T>
): {
  execute: () => Promise<T | null>;
  loading: boolean;
  error: string | null;
  data: T | null;
  reset: () => void;
} {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<T | null>(null);
  
  const execute = useCallback(async (): Promise<T | null> => {
    try {
      setLoading(true);
      setError(null);
      const result = await operation();
      setData(result);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Operation failed';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, [operation]);
  
  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setData(null);
  }, []);
  
  return { execute, loading, error, data, reset };
}

export default useAuth;
