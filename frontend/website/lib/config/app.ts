/**
 * Production-Grade Application Configuration
 * 
 * Centralized configuration management with type safety, validation,
 * and environment-specific optimizations.
 */

// Environment types for type safety
export type Environment = 'development' | 'staging' | 'production';

// Application configuration interface
export interface AppConfig {
  // Environment
  env: Environment;
  isDevelopment: boolean;
  isProduction: boolean;
  
  // API Configuration
  api: {
    baseUrl: string;
    timeout: number;
    retryAttempts: number;
    retryDelay: number;
  };
  
  // Authentication Configuration
  auth: {
    sessionCookieName: string;
    sessionCheckInterval: number;
    tokenRefreshThreshold: number;
    maxLoginAttempts: number;
    lockoutDuration: number;
  };
  
  // Performance Configuration
  performance: {
    cacheTimeout: number;
    maxConcurrentRequests: number;
    debounceDelay: number;
    throttleDelay: number;
  };
  
  // Feature Flags
  features: {
    enableAnalytics: boolean;
    enableErrorReporting: boolean;
    enablePerformanceMonitoring: boolean;
    enableDevTools: boolean;
  };
  
  // UI Configuration
  ui: {
    toastDuration: number;
    loadingTimeout: number;
    animationDuration: number;
  };
}

// Get environment with fallback
function getEnvironment(): Environment {
  const env = process.env.NODE_ENV as Environment;
  return env === 'development' || env === 'staging' || env === 'production' 
    ? env 
    : 'development';
}

// Validate and normalize API URL
function getApiBaseUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    const parsedUrl = new URL(url);
    return parsedUrl.origin; // Removes path and ensures clean URL
  } catch {
    console.warn(`Invalid API URL: ${url}, falling back to localhost:8000`);
    return 'http://localhost:8000';
  }
}

// Get boolean environment variable with fallback
function getBooleanEnv(key: string, defaultValue: boolean): boolean {
  const value = process.env[key];
  if (value === undefined) return defaultValue;
  return value.toLowerCase() === 'true';
}

// Get number environment variable with fallback and validation
function getNumberEnv(key: string, defaultValue: number, min?: number, max?: number): number {
  const value = process.env[key];
  if (value === undefined) return defaultValue;
  
  const parsed = parseInt(value, 10);
  if (isNaN(parsed)) return defaultValue;
  
  if (min !== undefined && parsed < min) return min;
  if (max !== undefined && parsed > max) return max;
  
  return parsed;
}

// Create production-grade configuration
const environment = getEnvironment();

export const config: AppConfig = {
  // Environment
  env: environment,
  isDevelopment: environment === 'development',
  isProduction: environment === 'production',
  
  // API Configuration
  api: {
    baseUrl: getApiBaseUrl(),
    timeout: getNumberEnv('NEXT_PUBLIC_API_TIMEOUT', 30000, 5000, 120000), // 30s default, 5s-2min range
    retryAttempts: getNumberEnv('NEXT_PUBLIC_API_RETRY_ATTEMPTS', 3, 0, 10),
    retryDelay: getNumberEnv('NEXT_PUBLIC_API_RETRY_DELAY', 1000, 100, 10000),
  },
  
  // Authentication Configuration
  auth: {
    sessionCookieName: process.env.NEXT_PUBLIC_SESSION_COOKIE_NAME || 'ai_social_session',
    sessionCheckInterval: getNumberEnv('NEXT_PUBLIC_SESSION_CHECK_INTERVAL', 300000, 60000, 3600000), // 5min default, 1min-1hr range
    tokenRefreshThreshold: getNumberEnv('NEXT_PUBLIC_TOKEN_REFRESH_THRESHOLD', 300000, 60000, 1800000), // 5min default
    maxLoginAttempts: getNumberEnv('NEXT_PUBLIC_MAX_LOGIN_ATTEMPTS', 5, 1, 20),
    lockoutDuration: getNumberEnv('NEXT_PUBLIC_LOCKOUT_DURATION', 900000, 60000, 3600000), // 15min default
  },
  
  // Performance Configuration
  performance: {
    cacheTimeout: getNumberEnv('NEXT_PUBLIC_CACHE_TIMEOUT', 300000, 60000, 3600000), // 5min default
    maxConcurrentRequests: getNumberEnv('NEXT_PUBLIC_MAX_CONCURRENT_REQUESTS', 10, 1, 50),
    debounceDelay: getNumberEnv('NEXT_PUBLIC_DEBOUNCE_DELAY', 300, 100, 2000),
    throttleDelay: getNumberEnv('NEXT_PUBLIC_THROTTLE_DELAY', 1000, 100, 5000),
  },
  
  // Feature Flags
  features: {
    enableAnalytics: getBooleanEnv('NEXT_PUBLIC_ENABLE_ANALYTICS', environment === 'production'),
    enableErrorReporting: getBooleanEnv('NEXT_PUBLIC_ENABLE_ERROR_REPORTING', environment === 'production'),
    enablePerformanceMonitoring: getBooleanEnv('NEXT_PUBLIC_ENABLE_PERFORMANCE_MONITORING', environment === 'production'),
    enableDevTools: getBooleanEnv('NEXT_PUBLIC_ENABLE_DEV_TOOLS', environment === 'development'),
  },
  
  // UI Configuration
  ui: {
    toastDuration: getNumberEnv('NEXT_PUBLIC_TOAST_DURATION', 5000, 1000, 15000),
    loadingTimeout: getNumberEnv('NEXT_PUBLIC_LOADING_TIMEOUT', 30000, 5000, 120000),
    animationDuration: getNumberEnv('NEXT_PUBLIC_ANIMATION_DURATION', 300, 100, 1000),
  },
};

// Validation function to ensure configuration is valid
export function validateConfig(): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  // Validate API configuration
  if (!config.api.baseUrl) {
    errors.push('API base URL is required');
  }
  
  if (config.api.timeout < 1000) {
    errors.push('API timeout must be at least 1000ms');
  }
  
  // Validate auth configuration
  if (!config.auth.sessionCookieName) {
    errors.push('Session cookie name is required');
  }
  
  // Log configuration in development
  if (config.isDevelopment) {
    console.log('App Configuration:', {
      environment: config.env,
      apiBaseUrl: config.api.baseUrl,
      features: config.features,
    });
  }
  
  // Log validation errors
  if (errors.length > 0) {
    console.error('Configuration validation errors:', errors);
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
}

// Auto-validate configuration on import
const validation = validateConfig();
if (!validation.isValid) {
  console.error('Invalid application configuration detected!');
}

export default config;
