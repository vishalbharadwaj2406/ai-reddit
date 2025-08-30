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
  TIMEOUT = 'TIMEOUT',
  POST_AUTH_SYNC_FAILED = 'POST_AUTH_SYNC_FAILED'
}

export class AuthError extends Error {
  constructor(
    public type: AuthErrorType,
    message: string,
    public statusCode?: number,
    public retryable: boolean = false
  ) {
    super(message);
    this.name = 'AuthError';
  }
}

// Production-grade authentication metrics tracking
interface AuthMetrics {
  sessionValidationTime: number;
  cacheHitRate: number;
  authLoopDetection: number;
  postAuthLatency: number;
}

/**
 * Track authentication metrics for production monitoring
 * Integrates with monitoring services (DataDog, New Relic, etc.)
 */
function trackAuthMetric(metric: keyof AuthMetrics, value: number, tags?: Record<string, string>): void {
  if (process.env.NODE_ENV === 'development') {
    console.log(`📊 Auth Metric [${metric}]: ${value}ms`, tags || '');
  }
  
  // TODO: Integrate with your monitoring service
  // Example: datadog.increment(`auth.${metric}`, value, tags);
}

/**
 * Production-grade circuit breaker for authentication reliability
 * Prevents cascading failures and auth loops
 */
class AuthCircuitBreaker {
  private failures = 0;
  private lastFailure = 0;
  private readonly maxFailures = 3;
  private readonly resetTimeout = 60000; // 1 minute
  
  isOpen(): boolean {
    if (this.failures >= this.maxFailures) {
      if (Date.now() - this.lastFailure > this.resetTimeout) {
        this.reset();
        return false;
      }
      return true;
    }
    return false;
  }
  
  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.isOpen()) {
      throw new AuthError(
        AuthErrorType.SERVER_ERROR,
        'Authentication circuit breaker is open - too many failures',
        503,
        true
      );
    }
    
    try {
      const result = await operation();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }
  
  private onSuccess(): void {
    this.failures = 0;
    this.lastFailure = 0;
  }
  
  private onFailure(): void {
    this.failures++;
    this.lastFailure = Date.now();
    
    if (process.env.NODE_ENV === 'development') {
      console.warn(`🔥 Auth circuit breaker: ${this.failures}/${this.maxFailures} failures`);
    }
  }
  
  private reset(): void {
    this.failures = 0;
    this.lastFailure = 0;
    
    if (process.env.NODE_ENV === 'development') {
      console.log('🔄 Auth circuit breaker: Reset after timeout');
    }
  }
}

// Global circuit breaker instance
const authCircuitBreaker = new AuthCircuitBreaker();

// Get API base URL from environment with validation - CROSS-ORIGIN PATTERN
const API_BASE_URL = (() => {
  // Cross-origin pattern: API and frontend on separate ports/domains
  const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    new URL(url); // Validate URL format
    return url.replace(/\/$/, ''); // Remove trailing slash
  } catch {
    console.error('Invalid API_BASE_URL, falling back to localhost:8000');
    return 'http://localhost:8000';
  }
})();

// Session cache with TTL for performance optimization
interface SessionCache {
  data: SessionStatus | null;
  timestamp: number;
  ttl: number; // Time to live in milliseconds
  state: 'stable' | 'post-auth' | 'error'; // Cache state for different TTL strategies
}

const sessionCache: SessionCache = {
  data: null,
  timestamp: 0,
  ttl: 30000, // 30 seconds default cache for production performance
  state: 'stable'
};

// Dynamic TTL based on authentication state (Production pattern)
const CACHE_TTL_STRATEGY = {
  stable: 30000,        // 30 seconds for stable authenticated state
  'post-auth': 5000,    // 5 seconds after authentication for quick synchronization
  error: 10000          // 10 seconds for error states
} as const;

/**
 * Clear session cache and reset to stable state
 * Used for post-authentication cache invalidation
 */
export function clearSessionCache(): void {
  sessionCache.data = null;
  sessionCache.timestamp = 0;
  sessionCache.state = 'stable';
  sessionCache.ttl = CACHE_TTL_STRATEGY.stable;
}

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
/**
 * Enhanced session status check with post-authentication detection
 * Production-grade implementation with dynamic cache TTL
 */
export async function getSessionStatus(forceRefresh = false): Promise<SessionStatus> {
  const startTime = Date.now();
  
  // Detect post-authentication state from URL parameters
  const isPostAuth = typeof window !== 'undefined' && 
    (window.location.search.includes('auth_success=true') || 
     window.location.search.includes('auth_timestamp='));

  // Use aggressive refresh for post-auth scenarios
  if (isPostAuth) {
    sessionCache.state = 'post-auth';
    sessionCache.ttl = CACHE_TTL_STRATEGY['post-auth'];
    forceRefresh = true; // Always force refresh after authentication
  }

  // Check cache first (unless force refresh)
  const cacheValid = !forceRefresh && 
    sessionCache.data && 
    Date.now() - sessionCache.timestamp < sessionCache.ttl;
    
  if (cacheValid && sessionCache.data) {
    // Track cache hit
    trackAuthMetric('cacheHitRate', Date.now() - startTime, { source: 'cache' });
    return sessionCache.data;
  }

  // Clear cache and set loading state
  sessionCache.data = {
    isAuthenticated: false,
    user: null,
    loading: true
  };

  try {
    const response = await authCircuitBreaker.execute(() => 
      fetchWithTimeout(`${API_BASE_URL}/api/v1/auth/session`, {
        method: 'GET',
        credentials: 'include', // Include HTTP-only cookies
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        // Security headers for production
        cache: 'no-store'
      })
    );

    if (!response.ok) {
      if (response.status === 401) {
        // Try token refresh before giving up
        const refreshResponse = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (refreshResponse.ok) {
          // Retry original request after successful refresh
          return getSessionStatus(true);
        }
        
        // Refresh failed, user is not authenticated
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

    // Production-grade cache strategy: Dynamic TTL based on state
    sessionCache.data = result;
    sessionCache.timestamp = Date.now();
    
    // Set appropriate cache state for next requests
    if (isPostAuth) {
      sessionCache.state = 'stable'; // Transition to stable after successful post-auth check
      sessionCache.ttl = CACHE_TTL_STRATEGY.stable;
      
      // Track post-auth performance
      trackAuthMetric('postAuthLatency', Date.now() - startTime, { 
        success: 'true',
        authenticated: String(isAuthenticated)
      });
    } else {
      // Track normal session validation
      trackAuthMetric('sessionValidationTime', Date.now() - startTime, {
        source: 'backend',
        authenticated: String(isAuthenticated)
      });
    }
    
    return result;

  } catch (error) {
    const errorResult: SessionStatus = {
      isAuthenticated: false,
      user: null,
      loading: false,
      error: error instanceof AuthError ? error.message : 
             (error instanceof Error ? error.message : 'Failed to check session status')
    };

    // Production-grade error caching with shorter TTL
    sessionCache.data = errorResult;
    sessionCache.timestamp = Date.now();
    sessionCache.state = 'error';
    sessionCache.ttl = CACHE_TTL_STRATEGY.error;

    // Log error for debugging in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Session status error:', error);
    }

    return errorResult;
  }
}

/**
 * Production-grade post-authentication synchronization
 * Handles cache invalidation and ensures all layers are synchronized
 */
export async function handlePostAuthSuccess(callbackUrl = '/feed'): Promise<void> {
  try {
    console.log('🎉 Starting post-auth synchronization');
    
    // Step 1: Clear all caches to force fresh validation
    clearSessionCache();
    
    // Step 2: Wait for cookie propagation (shorter delay for better UX)
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Step 3: Force fresh session validation
    const session = await getSessionStatus(true);
    
    if (!session.isAuthenticated) {
      console.log('🚀 Post-auth: Session not authenticated yet, waiting...');
      // Wait a bit more and try once more
      await new Promise(resolve => setTimeout(resolve, 200));
      const retrySession = await getSessionStatus(true);
      
      if (!retrySession.isAuthenticated) {
        console.warn('🚨 Post-auth: Session still not authenticated after retry');
        // Don't throw error, let client handle fallback
        return;
      }
    }
    
    // Step 4: Clean URL parameters
    if (typeof window !== 'undefined') {
      const url = new URL(window.location.href);
      url.searchParams.delete('auth_success');
      url.searchParams.delete('auth_timestamp');
      
      // Use replaceState to avoid adding to browser history
      window.history.replaceState({}, '', url.toString());
    }
    
    // Step 5: Navigate to intended destination after synchronization
    if (typeof window !== 'undefined') {
      console.log(`🎉 Post-auth complete: Navigating to ${callbackUrl}`);
      setTimeout(() => {
        window.location.href = callbackUrl;
      }, 50); // Minimal delay for final synchronization
    }
    
  } catch (error) {
    console.error('Post-auth synchronization failed:', error);
    // Fallback: Direct navigation without throwing
    if (typeof window !== 'undefined') {
      window.location.href = callbackUrl;
    }
  }
}

/**
 * Check if current URL indicates post-authentication state
 */
export function isPostAuthentication(): boolean {
  if (typeof window === 'undefined') return false;
  
  const params = new URLSearchParams(window.location.search);
  return params.has('auth_success') || params.has('auth_timestamp');
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
