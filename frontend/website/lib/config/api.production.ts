/**
 * Production-Grade API Client - NextAuth Only
 * 
 * Features:
 * - Pure NextAuth session-based authentication
 * - Automatic token injection from session
 * - Circuit breaker pattern for resilience
 * - Comprehensive error handling
 * - Production-grade logging and monitoring
 */

import { getSession } from 'next-auth/react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiConfig = {
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
};

// API endpoints (relative to base URL which already includes /api/v1)
export const endpoints = {
  // Authentication (NextAuth + Legacy API)
  auth: {
    // NextAuth endpoints
    session: '/auth/session', // NextAuth session endpoint
    signIn: '/auth/signin',   // NextAuth sign-in page
    signOut: '/auth/signout', // NextAuth sign-out endpoint
    
    // Legacy API endpoints (deprecated)
    googleLogin: '/api/v1/auth/google',
    refreshToken: '/api/v1/auth/refresh',
    logout: '/api/v1/auth/logout',
  },

  // Conversations
  conversations: {
    list: '/api/v1/conversations/',
    create: '/api/v1/conversations/',
    getById: (id: string) => `/api/v1/conversations/${id}`,
    sendMessage: (id: string) => `/api/v1/conversations/${id}/messages`,
    streamAI: (id: string) => `/api/v1/conversations/${id}/stream`,
    generateBlog: (id: string) => `/api/v1/conversations/${id}/generate-blog`,
    archive: (id: string) => `/api/v1/conversations/${id}`,
  },
  
  // Posts
  posts: {
    list: '/api/v1/posts/',
    create: '/api/v1/posts/',
    getById: (id: string) => `/api/v1/posts/${id}`,
    fork: (id: string) => `/api/v1/posts/${id}/fork`,
  },
  
  // Users
  users: {
    profile: '/api/v1/users/me',
    updateProfile: '/api/v1/users/me',
    getById: (id: string) => `/api/v1/users/${id}`,
  },
  
  // Health (these don't use /api/v1 prefix)
  health: {
    system: '/health',
    database: '/health/database',
  },
};

// Circuit breaker pattern for resilient API calls
enum CircuitState {
  CLOSED = 'CLOSED',
  OPEN = 'OPEN',
  HALF_OPEN = 'HALF_OPEN'
}

interface CircuitBreakerConfig {
  failureThreshold: number;
  recoveryTimeout: number;
  monitoringPeriod: number;
}

class CircuitBreaker {
  private state = CircuitState.CLOSED;
  private failures = 0;
  private lastFailureTime = 0;
  private config: CircuitBreakerConfig;

  constructor(config: CircuitBreakerConfig) {
    this.config = config;
  }

  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === CircuitState.OPEN) {
      if (Date.now() - this.lastFailureTime >= this.config.recoveryTimeout) {
        this.state = CircuitState.HALF_OPEN;
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
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
    this.state = CircuitState.CLOSED;
  }
  
  private onFailure(): void {
    this.failures++;
    this.lastFailureTime = Date.now();
    
    if (this.failures >= this.config.failureThreshold) {
      this.state = CircuitState.OPEN;
    }
  }
  
  getState(): CircuitState {
    return this.state;
  }
}

// Standard API response wrapper
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
  errorCode?: string;
}

// Enhanced HTTP client with automatic authentication
export class ApiClient {
  private baseURL: string;
  private timeout: number;
  private defaultHeaders: Record<string, string>;
  private circuitBreaker: CircuitBreaker;
  private requestInterceptors: Array<(config: RequestInit & { url: string }) => RequestInit & { url: string }> = [];
  private responseInterceptors: Array<(response: Response) => Response | Promise<Response>> = [];

  constructor() {
    this.baseURL = apiConfig.baseURL;
    this.timeout = apiConfig.timeout;
    this.defaultHeaders = apiConfig.headers;
    this.circuitBreaker = new CircuitBreaker({
      failureThreshold: 5,
      recoveryTimeout: 30000,
      monitoringPeriod: 60000,
    });

    // Setup default interceptors
    this.setupDefaultInterceptors();
  }

  getBaseURL(): string { return this.baseURL; }

  /**
   * Setup default request/response interceptors
   */
  private setupDefaultInterceptors() {
    // Request interceptor: Automatic token injection from NextAuth
    this.requestInterceptors.push((config) => {
      // Skip auth for health endpoints and auth endpoints
      const isHealthEndpoint = config.url.includes('/health');
      const isAuthEndpoint = config.url.includes('/auth/google') || config.url.includes('/auth/refresh');
      
      if (!isHealthEndpoint && !isAuthEndpoint) {
        // Note: Session token injection will be handled in the actual request method
        // since interceptors need to be synchronous
      }

      // Include credentials for httpOnly cookies
      config.credentials = 'include';
      
      return config;
    });

    // Response interceptor: Handle basic HTTP errors
    this.responseInterceptors.push(async (response) => {
      // For 401 Unauthorized, let the conversation service handle it
      // NextAuth will manage session expiry
      return response;
    });
  }

  /**
   * Enhanced headers with automatic NextAuth session token injection
   */
  private async getHeaders(customHeaders?: Record<string, string>): Promise<Record<string, string>> {
    const headers = { ...this.defaultHeaders, ...customHeaders };
    
    // Inject NextAuth session token for backend authentication
    try {
      const session = await getSession();
      
      if (session && (session as any)?.idToken) {
        headers['Authorization'] = `Bearer ${(session as any).idToken}`;
        
        // Add user context for backend logging
        if (session.user?.email) {
          headers['X-User-Email'] = session.user.email;
        }
        
        console.log('🔑 API Request with auth token for user:', session.user?.email);
      } else {
        console.warn('⚠️ No session or idToken available for API request');
        // For production: Don't proceed with authenticated requests without token
        // This prevents the 401 error from happening
      }
    } catch (error) {
      console.error('⚠️ Failed to get NextAuth session for API request:', error);
      // Continue without auth header - let backend handle 401
    }
    
    // Production monitoring headers
    headers['X-Client-Version'] = process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0';
    headers['X-Request-Timestamp'] = new Date().toISOString();
    
    // Development headers
    if (process.env.NODE_ENV === 'development') {
      headers['X-Development-Mode'] = 'true';
    }

    // Add correlation ID for request tracing
    headers['X-Correlation-ID'] = this.generateCorrelationId();
    
    return headers;
  }

  /**
   * Generate correlation ID for request tracing
   */
  private generateCorrelationId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Execute request with interceptors
   */
  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    return this.circuitBreaker.execute(async () => {
      const makeRequest = async (isRetry = false): Promise<ApiResponse<T>> => {
        const baseUrl = endpoint.startsWith('/health')
          ? API_BASE_URL.replace('/api/v1', '')
          : this.baseURL;
        const url = `${baseUrl}${endpoint}`;
        
        // Apply request interceptors
        let config: RequestInit & { url: string } = { ...options, url };
        for (const interceptor of this.requestInterceptors) {
          config = interceptor(config);
        }
        
        const headers = await this.getHeaders(config.headers as Record<string, string> | undefined);
        const finalConfig: RequestInit = { ...config, headers };
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        
        try {
          let response = await fetch(config.url, { ...finalConfig, signal: controller.signal });
          clearTimeout(timeoutId);
          
          // Apply response interceptors
          for (const interceptor of this.responseInterceptors) {
            response = await interceptor(response);
          }
          
          if (response.status === 401 && !isRetry) {
            // For NextAuth system, 401 means session expired or invalid
            console.warn('🔐 Authentication failed - session may be expired');
            throw new Error('Authentication expired. Please sign in again.');
          }
          
          if (response.status === 403) {
            throw new Error('Access denied. You do not have permission to perform this action.');
          }
          
          if (response.status >= 500) {
            throw new Error('Server error. Please try again later.');
          }
          
          if (!response.ok) {
            const errorData = await this.parseErrorResponse(response);
            throw new Error(errorData.message);
          }
          
          const result: unknown = await response.json();
          if (typeof result === 'object' && result !== null && 'success' in result) {
            return result as ApiResponse<T>;
          }
          return { success: true, data: result as T, message: 'Request successful' };
        } catch (error) {
          clearTimeout(timeoutId);
          throw error;
        }
      };

      return makeRequest();
    });
  }

  private async parseErrorResponse(response: Response): Promise<{ message: string; code?: string }> {
    try {
      const errorData = await response.json();
      return {
        message: errorData.message || errorData.detail?.message || `HTTP ${response.status}`,
        code: errorData.errorCode || errorData.detail?.error
      };
    } catch {
      return {
        message: `HTTP ${response.status}: ${response.statusText}`,
        code: response.status.toString()
      };
    }
  }

  // HTTP method implementations
  async get<T>(endpoint: string, params?: Record<string, string>): Promise<ApiResponse<T>> {
    const url = new URL(endpoint, this.baseURL);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.set(key, value);
      });
    }
    return this.request<T>(url.pathname + url.search, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(endpoint: string, data?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  /**
   * Create server-sent events connection with authentication
   * TODO: Add proper NextAuth token injection for SSE
   */
  createEventSource(endpoint: string, params?: URLSearchParams): EventSource {
    const url = new URL(endpoint, this.baseURL);
    
    if (params) {
      params.forEach((value, key) => url.searchParams.set(key, value));
    }
    
    // Note: SSE auth token injection would need to be handled differently
    // since this method needs to be synchronous
    
    return new EventSource(url.toString());
  }

  /**
   * Get circuit breaker status
   */
  getCircuitBreakerState(): CircuitState {
    return this.circuitBreaker.getState();
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
