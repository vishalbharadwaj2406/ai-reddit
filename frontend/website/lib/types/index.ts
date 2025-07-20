// Shared TypeScript types and interfaces

export interface User {
  id: string;
  userName: string;
  email: string;
  profileImage?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  updatedAt: string;
  messageCount: number;
  isPosted: boolean;
  userId: string;
  createdAt: string;
}

export interface Message {
  id: string;
  conversationId: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface Post {
  id: string;
  title: string;
  content: string;
  conversationId?: string;
  userId: string;
  createdAt: string;
  updatedAt: string;
  likes: number;
  shares: number;
  isPublished: boolean;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// Filter types
export type ConversationFilter = 'all' | 'posted' | 'unposted';
export type PostFilter = 'all' | 'published' | 'draft';

// Theme types
export interface Theme {
  colors: {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    text: {
      primary: string;
      secondary: string;
      muted: string;
    };
    border: string;
    accent: string;
  };
  spacing: {
    xs: number;
    sm: number;
    md: number;
    lg: number;
    xl: number;
  };
  borderRadius: {
    sm: number;
    md: number;
    lg: number;
    xl: number;
  };
}
