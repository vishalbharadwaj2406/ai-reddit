/**
 * Production-Grade API Client - Cookie-Based Authentication
 * 
 * Features:
 * - HTTP-only cookie-based authentication
 * - Automatic cookie handling for all requests
 * - Circuit breaker pattern for resilience
 * - Comprehensive error handling with session integration
 * - Production-grade logging and monitoring
 * - Request/response interceptors
 * - Retry mechanism with exponential backoff
 */

const API_BASE_URL = (() => {
  const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    new URL(url); // Validate URL format
    return url.replace(/\/$/, ''); // Remove trailing slash
  } catch {
    console.error('Invalid API_BASE_URL, falling back to localhost');
    return 'http://localhost:8000';
  }
})();

// API endpoints configuration
export const endpoints = {
  // Authentication (Backend Session)
  auth: {
    session: '/api/v1/auth/session',
    googleLogin: '/api/v1/auth/google/login',
    logout: '/api/v1/auth/logout',
    refresh: '/api/v1/auth/refresh',
    health: '/api/v1/auth/health',
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
  
  // Health
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

// Enhanced API error types
export enum ApiErrorType {
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT = 'TIMEOUT',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  CIRCUIT_BREAKER_OPEN = 'CIRCUIT_BREAKER_OPEN',
  UNKNOWN = 'UNKNOWN'
}

export class ApiError extends Error {
  constructor(
    public type: ApiErrorType,
    message: string,
    public statusCode?: number,
    public response?: Response,
    public data?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Request/Response interceptor types
export interface RequestInterceptor {
  (config: RequestInit): RequestInit | Promise<RequestInit>;
}

export interface ResponseInterceptor {
  (response: Response): Response | Promise<Response>;
}

// Standard API response wrapper with enhanced typing
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
  errorCode?: string;
  timestamp?: string;
  requestId?: string;
}

// Enhanced HTTP client with automatic cookie authentication and session integration
export class ApiClient {
  private baseURL: string;
  private timeout: number;
  private defaultHeaders: Record<string, string>;
  private circuitBreaker: CircuitBreaker;
  private requestInterceptors: RequestInterceptor[] = [];
  private responseInterceptors: ResponseInterceptor[] = [];
  private isRefreshing = false;
  private refreshPromise: Promise<void> | null = null;
  private retryConfig = {
    maxRetries: 3,
    baseDelay: 1000, // 1 second
    maxDelay: 10000, // 10 seconds
    retryCondition: (error: ApiError) => {
      // Retry on network errors, timeouts, and 5xx errors
      return [
        ApiErrorType.NETWORK_ERROR,
        ApiErrorType.TIMEOUT,
        ApiErrorType.SERVER_ERROR
      ].includes(error.type);
    }
  };

  constructor() {
    this.baseURL = API_BASE_URL;
    this.timeout = 15000; // Increased to 15 seconds for production
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      // Add request ID for tracking
      'X-Request-ID': this.generateRequestId(),
    };

    // Initialize circuit breaker with enhanced config
    this.circuitBreaker = new CircuitBreaker({
      failureThreshold: 5,
      recoveryTimeout: 30000, // 30 seconds
      monitoringPeriod: 60000, // 1 minute
    });
  }

  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Add request interceptor
  addRequestInterceptor(interceptor: RequestInterceptor): void {
    this.requestInterceptors.push(interceptor);
  }

  // Add response interceptor
  addResponseInterceptor(interceptor: ResponseInterceptor): void {
    this.responseInterceptors.push(interceptor);
  }

  // Sleep utility for retry delays
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Calculate exponential backoff delay
  private calculateRetryDelay(attempt: number): number {
    const delay = this.retryConfig.baseDelay * Math.pow(2, attempt);
    return Math.min(delay, this.retryConfig.maxDelay);
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    // Apply request interceptors
    let requestConfig = { ...options };
    for (const interceptor of this.requestInterceptors) {
      requestConfig = await interceptor(requestConfig);
    }

    return this.circuitBreaker.execute(async () => {
      let response = await this.makeRequest<T>(endpoint, requestConfig);
      
      // If 401 and we haven't tried refreshing, attempt refresh
      if (response instanceof ApiError && response.type === ApiErrorType.UNAUTHORIZED && !this.isRefreshing) {
        await this.handleTokenRefresh();
        // Retry the original request
        response = await this.makeRequest<T>(endpoint, requestConfig);
      }
      
      if (response instanceof ApiError) {
        throw response;
      }
      
      return response;
    });
  }

  private async makeRequest<T>(endpoint: string, options: RequestInit): Promise<T | ApiError> {
    return this.requestWithRetry<T>(endpoint, options);
  }

  private async handleTokenRefresh(): Promise<void> {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.isRefreshing = true;
    this.refreshPromise = this.performRefresh();

    try {
      await this.refreshPromise;
    } finally {
      this.isRefreshing = false;
      this.refreshPromise = null;
    }
  }

  private async performRefresh(): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        // Refresh failed, redirect to login
        if (typeof window !== 'undefined') {
          const { clearSessionCache } = await import('../auth/session');
          clearSessionCache();
          window.location.href = '/login';
        }
        throw new Error('Token refresh failed');
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      throw error;
    }
  }

  private async requestWithRetry<T>(endpoint: string, options: RequestInit, attempt = 0): Promise<T | ApiError> {
    const url = `${this.baseURL}${endpoint}`;
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      // Generate unique request ID for this specific request
      const requestId = this.generateRequestId();
      const headers = {
        ...this.defaultHeaders,
        ...options.headers,
        'X-Request-ID': requestId,
      };

      let response = await fetch(url, {
        ...options,
        signal: controller.signal,
        credentials: 'include', // Include HTTP-only cookies automatically
        headers,
      });

      clearTimeout(timeoutId);

      // Apply response interceptors
      for (const interceptor of this.responseInterceptors) {
        response = await interceptor(response);
      }

      if (!response.ok) {
        const apiError = await this.createApiError(response);
        
        // Don't retry on 401s - let the main request method handle token refresh
        if (apiError.type === ApiErrorType.UNAUTHORIZED) {
          return apiError;
        }
        
        // Check if we should retry
        if (attempt < this.retryConfig.maxRetries && this.retryConfig.retryCondition(apiError)) {
          const delay = this.calculateRetryDelay(attempt);
          console.warn(`Request failed, retrying in ${delay}ms (attempt ${attempt + 1}/${this.retryConfig.maxRetries})`);
          await this.sleep(delay);
          return this.requestWithRetry<T>(endpoint, options, attempt + 1);
        }

        return apiError;
      }

      // Handle empty responses (like from DELETE requests)
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        return {} as T;
      }

      const data = await response.json();
      
      // Log successful requests in development
      if (process.env.NODE_ENV === 'development') {
        console.debug(`API Success: ${options.method || 'GET'} ${endpoint}`, {
          requestId,
          status: response.status,
          data
        });
      }

      return data;

    } catch (error) {
      if (error instanceof ApiError) {
        return error; // Return API errors instead of throwing
      }

      // Handle network errors and timeouts
      if (error instanceof Error && error.name === 'AbortError') {
        const timeoutError = new ApiError(
          ApiErrorType.TIMEOUT,
          'Request timeout',
          408
        );
        
        // Retry on timeout if configured
        if (attempt < this.retryConfig.maxRetries && this.retryConfig.retryCondition(timeoutError)) {
          const delay = this.calculateRetryDelay(attempt);
          await this.sleep(delay);
          return this.requestWithRetry<T>(endpoint, options, attempt + 1);
        }
        
        return timeoutError;
      }

      // Handle other network errors
      const networkError = new ApiError(
        ApiErrorType.NETWORK_ERROR,
        error instanceof Error ? error.message : 'Network error',
        0
      );

      if (attempt < this.retryConfig.maxRetries && this.retryConfig.retryCondition(networkError)) {
        const delay = this.calculateRetryDelay(attempt);
        await this.sleep(delay);
        return this.requestWithRetry<T>(endpoint, options, attempt + 1);
      }

      return networkError;
    }
  }

  private async createApiError(response: Response): Promise<ApiError> {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    let errorData: unknown = null;

    try {
      errorData = await response.json();
      
      // Extract error message with comprehensive FastAPI support
      if (errorData && typeof errorData === 'object') {
        const data = errorData as Record<string, any>;
        
        // Handle FastAPI HTTPException format: {"detail": {"message": "...", "errorCode": "..."}}
        if (data.detail && typeof data.detail === 'object') {
          const detail = data.detail as Record<string, any>;
          errorMessage = detail.message || detail.detail || errorMessage;
        }
        // Handle FastAPI direct string detail: {"detail": "Error message"}
        else if (data.detail && typeof data.detail === 'string') {
          errorMessage = data.detail;
        }
        // Handle standard formats: {"message": "..."} or {"error": "..."}
        else if (data.message) {
          errorMessage = data.message;
        }
        else if (data.error) {
          errorMessage = data.error;
        }
        // Handle validation errors: {"detail": [{"msg": "...", "loc": [...]}]}
        else if (Array.isArray(data.detail) && data.detail.length > 0) {
          const firstError = data.detail[0];
          if (firstError && typeof firstError === 'object' && firstError.msg) {
            const location = firstError.loc ? ` (${firstError.loc.join(' -> ')})` : '';
            errorMessage = `${firstError.msg}${location}`;
          }
        }
      }
    } catch (parseError) {
      // Unable to parse error response as JSON - keep default message
      console.warn('Failed to parse error response:', parseError);
    }

    // Determine error type based on status code
    let errorType: ApiErrorType;
    switch (response.status) {
      case 401:
        errorType = ApiErrorType.UNAUTHORIZED;
        // Don't immediately redirect - let the request method handle token refresh
        if (typeof window !== 'undefined') {
          // Import session utilities dynamically to avoid circular dependency
          const { clearSessionCache } = await import('../auth/session');
          
          // Only clear cache if this isn't a refresh request
          if (!response.url.includes('/auth/refresh')) {
            clearSessionCache();
          }
        }
        break;
      case 403:
        errorType = ApiErrorType.FORBIDDEN;
        break;
      case 404:
        errorType = ApiErrorType.NOT_FOUND;
        break;
      case 422:
        errorType = ApiErrorType.VALIDATION_ERROR;
        break;
      case 408:
        errorType = ApiErrorType.TIMEOUT;
        break;
      default:
        if (response.status >= 500) {
          errorType = ApiErrorType.SERVER_ERROR;
          console.error('Server error:', errorMessage, errorData);
        } else if (response.status >= 400) {
          errorType = ApiErrorType.VALIDATION_ERROR;
        } else {
          errorType = ApiErrorType.UNKNOWN;
        }
    }

    return new ApiError(errorType, errorMessage, response.status, response, errorData);
  }

  // Convenience methods for standard HTTP operations
  async get<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    const url = new URL(endpoint, this.baseURL);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
      return this.request<T>(url.pathname + url.search);
    }
    return this.request<T>(endpoint);
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }

  // File upload with multipart form data
  async uploadFile<T>(endpoint: string, file: File, additionalData?: Record<string, string>): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    return this.request<T>(endpoint, {
      method: 'POST',
      body: formData,
      headers: {
        // Don't set Content-Type for FormData - let browser set it with boundary
      },
    });
  }

  // Streaming endpoints with enhanced error handling
  async getStream(endpoint: string): Promise<ReadableStream<Uint8Array> | null> {
    const url = `${this.baseURL}${endpoint}`;
    
    const response = await fetch(url, {
      credentials: 'include',
      headers: this.defaultHeaders,
    });

    if (!response.ok) {
      const apiError = await this.createApiError(response);
      throw apiError;
    }

    return response.body;
  }

  // Get circuit breaker status for monitoring
  getCircuitBreakerStatus() {
    return {
      state: this.circuitBreaker.getState(),
      healthy: this.circuitBreaker.getState() === CircuitState.CLOSED,
    };
  }

  // Health check utility
  async healthCheck(): Promise<boolean> {
    try {
      await this.get('/health');
      return true;
    } catch {
      return false;
    }
  }

  // Set timeout for requests
  setTimeout(timeout: number): void {
    this.timeout = timeout;
  }

  // Get current configuration
  getConfig() {
    return {
      baseURL: this.baseURL,
      timeout: this.timeout,
      circuitBreaker: this.getCircuitBreakerStatus(),
      retryConfig: this.retryConfig,
    };
  }
}

// Create singleton instance with production configuration
export const apiClient = new ApiClient();

// Add default request interceptor for development logging
if (process.env.NODE_ENV === 'development') {
  apiClient.addRequestInterceptor((config) => {
    console.debug('API Request:', {
      method: config.method || 'GET',
      headers: config.headers,
      body: config.body,
    });
    return config;
  });
}

// Add response interceptor for monitoring
apiClient.addResponseInterceptor((response) => {
  if (process.env.NODE_ENV === 'development') {
    console.debug('API Response:', {
      status: response.status,
      statusText: response.statusText,
      headers: Object.fromEntries(response.headers.entries()),
    });
  }
  return response;
});

// Export circuit breaker state enum (ApiErrorType already exported above)
export { CircuitState };

// Convenience functions using the singleton
export const api = {
  get: <T>(endpoint: string, params?: Record<string, string>) => apiClient.get<T>(endpoint, params),
  post: <T>(endpoint: string, data?: unknown) => apiClient.post<T>(endpoint, data),
  put: <T>(endpoint: string, data?: unknown) => apiClient.put<T>(endpoint, data),
  patch: <T>(endpoint: string, data?: unknown) => apiClient.patch<T>(endpoint, data),
  delete: <T>(endpoint: string) => apiClient.delete<T>(endpoint),
  uploadFile: <T>(endpoint: string, file: File, additionalData?: Record<string, string>) => 
    apiClient.uploadFile<T>(endpoint, file, additionalData),
  getStream: (endpoint: string) => apiClient.getStream(endpoint),
  healthCheck: () => apiClient.healthCheck(),
};
