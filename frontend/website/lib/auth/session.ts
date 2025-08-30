/**
 * Production-grade authentication utility functions for session management
 * Uses HTTP-only cookies for secure authentication with comprehensive error handling
 */

// Enhanced session user interface
export interface SessionUser {
  user_id: string;
  user_name: string;
  email: string;
  profile_picture?: string;
}

// Enhanced session state interface
export interface SessionStatus {
  isAuthenticated: boolean;
  user: SessionUser | null;
  loading: boolean;
  error?: string;
}

// Authentication error types
export enum AuthErrorType {
  NETWORK_ERROR = 'NETWORK_ERROR',
  UNAUTHORIZED = 'UNAUTHORIZED',
  SESSION_EXPIRED = 'SESSION_EXPIRED',
  SERVER_ERROR = 'SERVER_ERROR',
  INVALID_RESPONSE = 'INVALID_RESPONSE',
  TIMEOUT = 'TIMEOUT'
}

export class AuthError extends Error {
  constructor(
    public type: AuthErrorType,
    message: string,
    public statusCode?: number
  ) {
    super(message);
    this.name = 'AuthError';
  }
}

// Get API base URL from environment with validation - BFF PATTERN
const API_BASE_URL = (() => {
  // BFF Pattern: API and frontend served from same origin
  const url = process.env.NEXT_PUBLIC_API_URL || '';
  try {
    if (url) {
      new URL(url); // Validate URL format
      return url.replace(/\/$/, ''); // Remove trailing slash
    }
    // BFF: Use relative URLs for same-origin setup
    return '';
  } catch {
    console.error('Invalid API_BASE_URL, using relative URLs for BFF pattern');
    return '';
  }
})();

// Session cache with TTL for performance optimization
interface SessionCache {
  data: SessionStatus | null;
  timestamp: number;
  ttl: number; // Time to live in milliseconds
}

const sessionCache: SessionCache = {
  data: null,
  timestamp: 0,
  ttl: 30000 // 30 seconds cache for production performance
};

// Request timeout configuration
const REQUEST_TIMEOUT = 10000; // 10 seconds

/**
 * Create fetch request with timeout
 */
function fetchWithTimeout(url: string, options: RequestInit, timeout = REQUEST_TIMEOUT): Promise<Response> {
  return Promise.race([
    fetch(url, options),
    new Promise<never>((_, reject) =>
      setTimeout(() => reject(new AuthError(AuthErrorType.TIMEOUT, 'Request timeout')), timeout)
    )
  ]);
}

/**
 * Get current session status from backend with caching and comprehensive error handling
 */
export async function getSessionStatus(forceRefresh = false): Promise<SessionStatus> {
  // Check cache first (unless force refresh)
  if (!forceRefresh && sessionCache.data && Date.now() - sessionCache.timestamp < sessionCache.ttl) {
    return sessionCache.data;
  }

  // Clear cache and set loading state
  sessionCache.data = {
    isAuthenticated: false,
    user: null,
    loading: true
  };

  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/auth/session`, {
      method: 'GET',
      credentials: 'include', // Include HTTP-only cookies
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      // Security headers for production
      cache: 'no-store'
    });

    if (!response.ok) {
      if (response.status === 401) {
        const result: SessionStatus = {
          isAuthenticated: false,
          user: null,
          loading: false,
        };
        
        // Cache unauthenticated state
        sessionCache.data = result;
        sessionCache.timestamp = Date.now();
        return result;
      }
      throw new AuthError(
        AuthErrorType.SERVER_ERROR,
        `Session check failed: ${response.status} ${response.statusText}`,
        response.status
      );
    }

    const data = await response.json();
    
    // Handle both response formats for maximum compatibility
    // Backend currently returns: { "authenticated": true, "user": {...} }
    // Legacy systems might use: { "is_authenticated": true, "user": {...} }
    const isAuthenticated = data.authenticated ?? data.is_authenticated ?? false;
    
    // Validate response structure
    if (typeof isAuthenticated !== 'boolean') {
      throw new AuthError(
        AuthErrorType.INVALID_RESPONSE,
        'Invalid session response format: missing authentication status'
      );
    }

    const result: SessionStatus = {
      isAuthenticated,
      user: (isAuthenticated && data.user) ? {
        user_id: data.user.user_id,
        user_name: data.user.user_name,
        email: data.user.email,
        profile_picture: data.user.profile_picture,
      } : null,
      loading: false,
    };

    // Cache successful result
    sessionCache.data = result;
    sessionCache.timestamp = Date.now();
    
    return result;

  } catch (error) {
    const errorResult: SessionStatus = {
      isAuthenticated: false,
      user: null,
      loading: false,
      error: error instanceof AuthError ? error.message : 
             (error instanceof Error ? error.message : 'Failed to check session status')
    };

    // Cache error state with shorter TTL
    sessionCache.data = errorResult;
    sessionCache.timestamp = Date.now();
    sessionCache.ttl = 5000; // 5 seconds for errors

    // Log error for debugging in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Session status error:', error);
    }

    return errorResult;
  }
}

/**
 * Redirect to Google OAuth login with optional return URL
 */
export function redirectToLogin(returnUrl?: string): void {
  const loginUrl = new URL(`${API_BASE_URL}/api/v1/auth/google/login`);
  
  if (returnUrl) {
    loginUrl.searchParams.set('return_url', returnUrl);
  }
  
  // Add timestamp to prevent caching issues
  loginUrl.searchParams.set('t', Date.now().toString());
  
  console.log('🔐 Redirecting to OAuth login:', loginUrl.toString());
  window.location.href = loginUrl.toString();
}

/**
 * Logout user and clear session with comprehensive cleanup
 */
export async function logout(redirectPath = '/'): Promise<void> {
  try {
    // Clear cache immediately
    sessionCache.data = null;
    sessionCache.timestamp = 0;

    const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/auth/logout`, {
      method: 'POST',
      credentials: 'include', // Include HTTP-only cookies
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      console.warn('Logout request failed:', response.statusText);
      // Continue with client-side cleanup even if server logout fails
    }
  } catch (error) {
    console.error('Logout error:', error);
    // Continue with client-side cleanup even if network fails
  } finally {
    // Always redirect after logout attempt
    if (typeof window !== 'undefined') {
      window.location.href = redirectPath;
    }
  }
}

/**
 * Check if user is authenticated (simple boolean check with caching)
 */
export async function isAuthenticated(useCache = true): Promise<boolean> {
  const session = await getSessionStatus(!useCache);
  return session.isAuthenticated;
}

/**
 * Get current user information if authenticated
 */
export async function getCurrentUser(): Promise<SessionUser | null> {
  const session = await getSessionStatus();
  return session.user;
}

/**
 * Clear session cache (useful for forcing fresh data)
 */
export function clearSessionCache(): void {
  sessionCache.data = null;
  sessionCache.timestamp = 0;
  sessionCache.ttl = 30000; // Reset TTL
}

/**
 * Check if session is loading
 */
export function isSessionLoading(): boolean {
  return sessionCache.data?.loading ?? false;
}

/**
 * Get session error if any
 */
export function getSessionError(): string | undefined {
  return sessionCache.data?.error;
}

/**
 * Production-grade authentication state hook data
 */
export interface AuthState {
  isAuthenticated: boolean;
  user: SessionUser | null;
  loading: boolean;
  error?: string;
  login: (returnUrl?: string) => void;
  logout: (redirectPath?: string) => Promise<void>;
  refresh: () => Promise<SessionStatus>;
  clearError: () => void;
}

/**
 * Get complete authentication state for React components
 */
export async function getAuthState(): Promise<AuthState> {
  const session = await getSessionStatus();
  
  return {
    isAuthenticated: session.isAuthenticated,
    user: session.user,
    loading: session.loading,
    error: session.error,
    login: redirectToLogin,
    logout,
    refresh: () => getSessionStatus(true),
    clearError: clearSessionCache
  };
}
