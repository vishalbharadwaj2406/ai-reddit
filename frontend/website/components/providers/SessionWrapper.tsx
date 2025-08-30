/**
 * Production-Grade Session Context Provider
 * 
 * Provides global authentication state management with caching, error handling,
 * and comprehensive session utilities for the entire application.
 */

'use client'

import { 
  createContext, 
  useContext, 
  useEffect, 
  useState, 
  useCallback,
  ReactNode 
} from 'react'
import { 
  getSessionStatus, 
  redirectToLogin, 
  logout,
  clearSessionCache,
  type SessionStatus,
  type AuthState
} from '../../lib/auth/session'

// Enhanced context type with all authentication utilities
interface SessionContextType extends AuthState {
  // System state for initialization tracking
  isInitialized: boolean;
  
  // Additional context-specific methods
  refreshSession: () => Promise<SessionStatus>;
  clearError: () => void;
}

// Create context with proper typing
const SessionContext = createContext<SessionContextType | undefined>(undefined);

interface SessionProviderProps {
  children: ReactNode;
  autoRefreshInterval?: number; // Optional auto-refresh interval in ms
}

export function SessionProvider({ 
  children, 
  autoRefreshInterval = 5 * 60 * 1000 // Default: 5 minutes
}: SessionProviderProps) {
  // Production-grade initial state - always start with loading for consistency
  const getInitialSessionState = (): SessionStatus => {
    if (typeof window === 'undefined') {
      return { isAuthenticated: false, user: null, loading: true };
    }
    
    // Always start with loading: true to prevent race conditions
    // Session validation will determine actual state
    return {
      isAuthenticated: false,
      user: null,
      loading: true,
    };
  };

  const [session, setSession] = useState<SessionStatus>(getInitialSessionState());
  const [isInitialized, setIsInitialized] = useState(false);

  const checkSession = useCallback(async (forceRefresh = false) => {
    try {
      // Only set loading if not initialized to prevent flash
      if (!isInitialized || forceRefresh) {
        setSession(prev => ({ ...prev, loading: true, error: undefined }));
      }
      
      const status = await getSessionStatus(forceRefresh);
      
      // Ensure we mark as initialized after first successful check
      setSession(status);
      if (!isInitialized) {
        setIsInitialized(true);
      }
      
      return status;
    } catch (error) {
      console.error('Session check failed:', error);
      
      // Production-grade error handling - be explicit about auth state
      const errorSession: SessionStatus = {
        isAuthenticated: false,
        user: null,
        loading: false,
        error: error instanceof Error ? error.message : 'Session validation failed',
      };
      
      setSession(errorSession);
      if (!isInitialized) {
        setIsInitialized(true);
      }
      
      return errorSession;
    }
  }, [isInitialized]);

  const refreshSession = useCallback(() => checkSession(true), [checkSession]);

  const handleLogin = useCallback((returnUrl?: string) => {
    redirectToLogin(returnUrl);
  }, []);

  const handleLogout = useCallback(async (redirectPath?: string) => {
    // Immediately update state to prevent UI flickering
    setSession({
      isAuthenticated: false,
      user: null,
      loading: false,
    });
    
    // Clear cache and perform logout
    clearSessionCache();
    await logout(redirectPath);
  }, []);

  const clearError = useCallback(() => {
    setSession(prev => ({ ...prev, error: undefined }));
    clearSessionCache();
  }, []);

  // Production-grade session initialization
  useEffect(() => {
    // Always perform session check on mount for consistency
    checkSession();
  }, [checkSession]);

  // Auto-refresh session periodically (if enabled)
  useEffect(() => {
    if (!autoRefreshInterval || autoRefreshInterval <= 0 || !isInitialized) return;

    const intervalId = setInterval(() => {
      // Only refresh if user is authenticated and system is stable
      if (session.isAuthenticated && !session.loading) {
        checkSession(true);
      }
    }, autoRefreshInterval);

    return () => clearInterval(intervalId);
  }, [autoRefreshInterval, session.isAuthenticated, session.loading, checkSession, isInitialized]);

  // Build context value with all authentication utilities
  const contextValue: SessionContextType = {
    // Session state
    isAuthenticated: session.isAuthenticated,
    user: session.user,
    loading: session.loading,
    error: session.error,
    
    // System state
    isInitialized,
    
    // Authentication actions
    login: handleLogin,
    logout: handleLogout,
    refresh: refreshSession,
    
    // Context-specific methods
    refreshSession,
    clearError,
  };

  return (
    <SessionContext.Provider value={contextValue}>
      {children}
    </SessionContext.Provider>
  );
}

/**
 * Enhanced hook to use session context with proper error handling
 */
export function useSessionContext() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSessionContext must be used within a SessionProvider');
  }
  return context;
}

/**
 * Convenience hook that provides just the authentication state
 */
export function useAuth() {
  const context = useSessionContext();
  return {
    isAuthenticated: context.isAuthenticated,
    user: context.user,
    loading: context.loading,
    error: context.error,
  };
}

/**
 * Convenience hook that provides just the authentication actions
 */
export function useAuthActions() {
  const context = useSessionContext();
  return {
    login: context.login,
    logout: context.logout,
    refresh: context.refresh,
    clearError: context.clearError,
  };
}

// Keep the old SessionWrapper name for backward compatibility
export default SessionProvider;
