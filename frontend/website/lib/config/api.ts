// API configuration and base client

export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000', // Will be overridden by platform-specific config
  ENDPOINTS: {
    AUTH: {
      LOGIN: '/auth/login',
      REGISTER: '/auth/register',
      LOGOUT: '/auth/logout',
      REFRESH: '/auth/refresh',
      PROFILE: '/auth/profile',
    },
    CONVERSATIONS: {
      LIST: '/conversations',
      CREATE: '/conversations',
      GET: (id: string) => `/conversations/${id}`,
      UPDATE: (id: string) => `/conversations/${id}`,
      DELETE: (id: string) => `/conversations/${id}`,
    },
    MESSAGES: {
      LIST: (conversationId: string) => `/conversations/${conversationId}/messages`,
      CREATE: (conversationId: string) => `/conversations/${conversationId}/messages`,
      GET: (conversationId: string, messageId: string) => `/conversations/${conversationId}/messages/${messageId}`,
    },
    POSTS: {
      LIST: '/posts',
      CREATE: '/posts',
      GET: (id: string) => `/posts/${id}`,
      UPDATE: (id: string) => `/posts/${id}`,
      DELETE: (id: string) => `/posts/${id}`,
      PUBLISH: (id: string) => `/posts/${id}/publish`,
    },
    USERS: {
      LIST: '/users',
      GET: (id: string) => `/users/${id}`,
      UPDATE: (id: string) => `/users/${id}`,
    },
  },
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
} as const;

// Environment-specific configurations
export const ENV_CONFIG = {
  development: {
    API_URL: 'http://localhost:8000',
    DEBUG: true,
    LOG_LEVEL: 'debug',
  },
  production: {
    API_URL: 'https://api.aisocial.app',
    DEBUG: false,
    LOG_LEVEL: 'error',
  },
  staging: {
    API_URL: 'https://staging-api.aisocial.app',
    DEBUG: true,
    LOG_LEVEL: 'info',
  },
} as const;

export type Environment = keyof typeof ENV_CONFIG;
