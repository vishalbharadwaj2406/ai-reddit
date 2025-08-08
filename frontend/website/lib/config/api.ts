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
  // Authentication
  auth: {
    googleLogin: '/auth/google',
    refreshToken: '/auth/refresh',
    logout: '/auth/logout',
  },
  
  // Conversations
  conversations: {
    list: '/conversations/',
    create: '/conversations/',
    getById: (id: string) => `/conversations/${id}`,
    sendMessage: (id: string) => `/conversations/${id}/messages`,
    streamAI: (id: string) => `/conversations/${id}/stream`,
    generateBlog: (id: string) => `/conversations/${id}/generate-blog`,
    archive: (id: string) => `/conversations/${id}`,
  },
  
  // Posts
  posts: {
    list: '/posts/',
    create: '/posts/',
    getById: (id: string) => `/posts/${id}`,
    fork: (id: string) => `/posts/${id}/fork`,
  },
  
  // Users
  users: {
    profile: '/users/me',
    updateProfile: '/users/me',
    getById: (id: string) => `/users/${id}`,
  },
  
  // Health (these don't use /api/v1 prefix)
  health: {
    system: '/health',
    database: '/health/database',
  },
};

// Circuit breaker configuration for production resilience
interface CircuitBreakerConfig {
  failureThreshold: number;
  recoveryTimeout: number;
  monitoringPeriod: number;
}

enum CircuitState {
  CLOSED = 'CLOSED',
  OPEN = 'OPEN', 
  HALF_OPEN = 'HALF_OPEN'
}

class CircuitBreaker {
  private failures = 0;
  private lastFailureTime = 0;
  private state = CircuitState.CLOSED;
  
  constructor(private config: CircuitBreakerConfig) {}
  
  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === CircuitState.OPEN) {
      if (Date.now() - this.lastFailureTime > this.config.recoveryTimeout) {
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

// Enhanced HTTP client integrated with NextAuth
export class ApiClient {
  private baseURL: string;
  private timeout: number;
  private defaultHeaders: Record<string, string>;
  private circuitBreaker: CircuitBreaker;

  constructor() {
    this.baseURL = apiConfig.baseURL;
    this.timeout = apiConfig.timeout;
    this.defaultHeaders = apiConfig.headers;
    this.circuitBreaker = new CircuitBreaker({
      failureThreshold: 5,
      recoveryTimeout: 30000,
      monitoringPeriod: 60000,
    });
  }

  getBaseURL(): string { return this.baseURL; }

  /**
   * Get authentication token - now integrated with backend auth
   */
  /**
   * Enhanced token management with automatic refresh
   */
  private async getAuthToken(): Promise<string | null> {
    if (typeof window === 'undefined') return null;
    
    // Check if we have a cached backend JWT token from our manual auth
    const cachedJWT = localStorage.getItem('ai_social_backend_jwt');
    const cachedExpiry = localStorage.getItem('ai_social_backend_jwt_expiry');
    
    if (cachedJWT && cachedExpiry) {
      const expiryTime = parseInt(cachedExpiry, 10);
      // Check if token expires in more than 5 minutes
      if (expiryTime > Date.now() + (5 * 60 * 1000)) {
        return cachedJWT;
      } else {
        // Token is about to expire, try to refresh it
        const refreshed = await this.refreshBackendToken();
        if (refreshed) {
          return localStorage.getItem('ai_social_backend_jwt');
        }
      }
    }
    
    // No valid cached token available
    return null;
  }

  /**
   * Attempt to refresh backend token using current session
   */
  private async refreshBackendToken(): Promise<boolean> {
    try {
      // Get current session
      const sessionResponse = await fetch('/api/auth/session');
      if (!sessionResponse.ok) return false;
      
      const session = await sessionResponse.json();
      const googleIdToken = session?.idToken;
      
      if (!googleIdToken) return false;

      // Check if Google token is still valid
      const tokenPayload = JSON.parse(atob(googleIdToken.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      
      if (tokenPayload.exp <= currentTime) {
        console.warn('Google token is expired, cannot refresh backend token automatically');
        return false;
      }

      // Refresh backend token
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ google_token: googleIdToken }),
      });

      if (response.ok) {
        const authData = await response.json();
        
        if (authData.access_token && authData.expires_in) {
          const expiryTime = Date.now() + (authData.expires_in * 1000);
          localStorage.setItem('ai_social_backend_jwt', authData.access_token);
          localStorage.setItem('ai_social_backend_jwt_expiry', expiryTime.toString());
          return true;
        }
      }
      
      return false;
    } catch (error) {
      console.error('Failed to refresh backend token:', error);
      return false;
    }
  }

  /**
   * Build headers with correlation ID (no auto-authentication)
   */
  private async getHeaders(customHeaders?: Record<string, string>): Promise<Record<string, string>> {
    const headers = { ...this.defaultHeaders, ...customHeaders };
    
    // Add correlation ID for request tracing
    headers['X-Correlation-ID'] = this.generateCorrelationId();
    
    // Simple approach - only add auth header if explicitly provided
    const token = await this.getAuthToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    
    return headers;
  }

  /**
   * Generate correlation ID for request tracing
   */
  private generateCorrelationId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Enhanced request method with automatic token refresh on 401 errors
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
        const headers = await this.getHeaders(options.headers as Record<string, string> | undefined);
        const config: RequestInit = { ...options, headers };
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        try {
          const response = await fetch(url, { ...config, signal: controller.signal });
          clearTimeout(timeoutId);
          if (response.status === 401 && !isRetry) {
            const refreshed = await this.refreshBackendToken();
            if (refreshed) return makeRequest(true);
            throw new Error('Authentication expired. Please sign out and sign back in to refresh your session.');
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
      if (errorData.detail) {
        if (typeof errorData.detail === 'object' && errorData.detail.message) {
          return { message: errorData.detail.message, code: errorData.detail.error || 'API_ERROR' };
        }
        if (typeof errorData.detail === 'string') {
          return { message: errorData.detail, code: 'API_ERROR' };
        }
      }
      if (errorData.message) {
        return { message: errorData.message, code: errorData.code || 'API_ERROR' };
      }
      return { message: `HTTP ${response.status}: ${response.statusText}`, code: 'HTTP_ERROR' };
    } catch {
      return { message: `HTTP ${response.status}: ${response.statusText}`, code: 'PARSE_ERROR' };
    }
  }

  async get<T>(endpoint: string, params?: Record<string, string>): Promise<ApiResponse<T>> {
    const url = params ? `${endpoint}?${new URLSearchParams(params).toString()}` : endpoint;
    return this.request<T>(url, { method: 'GET' });
  }

  async post<TResponse, TBody = unknown>(endpoint: string, data?: TBody): Promise<ApiResponse<TResponse>> {
    return this.request<TResponse>(endpoint, {
      method: 'POST',
      body: data !== undefined ? JSON.stringify(data) : undefined,
    });
  }

  async put<TResponse, TBody = unknown>(endpoint: string, data?: TBody): Promise<ApiResponse<TResponse>> {
    return this.request<TResponse>(endpoint, {
      method: 'PUT',
      body: data !== undefined ? JSON.stringify(data) : undefined,
    });
  }

  async delete<TResponse>(endpoint: string): Promise<ApiResponse<TResponse>> {
    return this.request<TResponse>(endpoint, { method: 'DELETE' });
  }

  /**
   * Create EventSource for Server-Sent Events
   */
  async createEventSource(endpoint: string, params?: URLSearchParams): Promise<EventSource> {
    const baseUrl = endpoint.startsWith('/health') 
      ? API_BASE_URL.replace('/api/v1', '')  
      : this.baseURL;
      
    const url = new URL(`${baseUrl}${endpoint}`);
    
    // Add existing params
    if (params) {
      params.forEach((value, key) => url.searchParams.set(key, value));
    }
    
    // Add JWT token as URL parameter for SSE authentication
    const token = await this.getAuthToken();
    if (token) {
      url.searchParams.set('token', token);
    }
    
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
