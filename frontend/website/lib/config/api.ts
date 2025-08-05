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
      recoveryTimeout: 30000, // 30 seconds
      monitoringPeriod: 60000, // 1 minute
    });
  }

  /**
   * Get authentication token - now integrated with backend auth
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
      }
    }
    
    // No valid cached token available
    return null;
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
   * Simple request method
   */
  async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    return this.circuitBreaker.execute(async () => {
      // Simple URL construction
      const baseUrl = endpoint.startsWith('/health') 
        ? API_BASE_URL.replace('/api/v1', '')  
        : this.baseURL;
        
      const url = `${baseUrl}${endpoint}`;
      const headers = await this.getHeaders(options.headers as Record<string, string>);
      
      const config: RequestInit = {
        ...options,
        headers,
      };

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);
      
      try {
        const response = await fetch(url, {
          ...config,
          signal: controller.signal,
        });
        
        clearTimeout(timeoutId);
        
        // Simple error handling
        if (!response.ok) {
          const errorData = await this.parseErrorResponse(response);
          throw new Error(errorData.message);
        }
        
        const result = await response.json();
        
        // Simple response wrapping
        if (typeof result === 'object' && result !== null && 'success' in result) {
          return result as ApiResponse<T>;
        }
        
        return {
          success: true,
          data: result as T,
          message: 'Request successful',
        };
        
      } catch (error) {
        clearTimeout(timeoutId);
        throw error;
      }
    });
  }

  /**
   * Simple error response parsing
   */
  private async parseErrorResponse(response: Response): Promise<{ message: string; code?: string }> {
    try {
      const errorData = await response.json();
      
      // Handle FastAPI format: {"detail": {"error": "CODE", "message": "text"}}
      if (errorData.detail) {
        if (typeof errorData.detail === 'object' && errorData.detail.message) {
          return {
            message: errorData.detail.message,
            code: errorData.detail.error || 'API_ERROR'
          };
        }
        if (typeof errorData.detail === 'string') {
          return {
            message: errorData.detail,
            code: 'API_ERROR'
          };
        }
      }
      
      // Handle direct message format
      if (errorData.message) {
        return {
          message: errorData.message,
          code: errorData.code || 'API_ERROR'
        };
      }
      
      // Fallback
      return {
        message: `HTTP ${response.status}: ${response.statusText}`,
        code: 'HTTP_ERROR'
      };
      
    } catch (parseError) {
      return {
        message: `HTTP ${response.status}: ${response.statusText}`,
        code: 'PARSE_ERROR'
      };
    }
  }

  // Convenience methods
  async get<T>(endpoint: string, params?: Record<string, string>): Promise<ApiResponse<T>> {
    const url = params ? `${endpoint}?${new URLSearchParams(params).toString()}` : endpoint;
    return this.request<T>(url, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
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
