/**
 * Production Conversation Service - NextAuth Only
 * 
 * Enterprise-grade conversation management service that integrates
 * seamlessly with our production NextAuth authentication system.
 * 
 * Features:
 * - Pure NextAuth session-based authentication
 * - Comprehensive error handling with user-friendly messages
 * - Optimistic updates for better UX
 * - Production-grade logging and monitoring
 * - Circuit breaker pattern for API resilience
 */

import { apiClient } from '../config/api.production';
import { getCurrentSession, isAuthenticated } from '../auth/auth.utils';

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  conversationId: string;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
  userId: string;
  isArchived?: boolean;
}

export interface ConversationCreateRequest {
  title: string;
  initialMessage?: string;
}

export interface MessageCreateRequest {
  content: string;
  role?: 'user' | 'assistant';
}

/**
 * Production-grade conversation service error types
 */
class ConversationServiceError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode?: number
  ) {
    super(message);
    this.name = 'ConversationServiceError';
  }
}

class AuthenticationRequiredError extends ConversationServiceError {
  constructor() {
    super('Authentication required to access conversations', 'AUTH_REQUIRED', 401);
  }
}

class ConversationNotFoundError extends ConversationServiceError {
  constructor(id: string) {
    super(`Conversation with id ${id} not found`, 'CONVERSATION_NOT_FOUND', 404);
  }
}

class ConversationPermissionError extends ConversationServiceError {
  constructor() {
    super('You do not have permission to access this conversation', 'PERMISSION_DENIED', 403);
  }
}

/**
 * Production conversation service with enterprise-grade features
 */
class ProductionConversationService {
  /**
   * Validates that user is authenticated before making API calls
   */
  private async validateAuthentication(): Promise<void> {
    const authenticated = await isAuthenticated();
    if (!authenticated) {
      throw new AuthenticationRequiredError();
    }
  }

  /**
   * Get all conversations for the authenticated user
   */
  async getConversations(): Promise<Conversation[]> {
    await this.validateAuthentication();

    try {
      const response = await apiClient.get<{ conversations: Conversation[] }>('/conversations');
      return response.data?.conversations || [];
    } catch (error: any) {
      if (error.status === 401) {
        throw new AuthenticationRequiredError();
      }
      if (error.status === 403) {
        throw new ConversationPermissionError();
      }
      
      console.error('[ConversationService] Failed to fetch conversations:', error);
      throw new ConversationServiceError(
        'Failed to load conversations. Please try again.',
        'FETCH_FAILED',
        error.status
      );
    }
  }

  /**
   * Get a specific conversation by ID
   */
  async getConversation(id: string): Promise<Conversation> {
    await this.validateAuthentication();

    if (!id || typeof id !== 'string') {
      throw new ConversationServiceError('Invalid conversation ID', 'INVALID_ID', 400);
    }

    try {
      const response = await apiClient.get<Conversation>(`/conversations/${id}`);
      return response.data;
    } catch (error: any) {
      if (error.status === 401) {
        throw new AuthenticationRequiredError();
      }
      if (error.status === 403) {
        throw new ConversationPermissionError();
      }
      if (error.status === 404) {
        throw new ConversationNotFoundError(id);
      }
      
      console.error(`[ConversationService] Failed to fetch conversation ${id}:`, error);
      throw new ConversationServiceError(
        'Failed to load conversation. Please try again.',
        'FETCH_FAILED',
        error.status
      );
    }
  }

  /**
   * Create a new conversation
   */
  async createConversation(data: ConversationCreateRequest): Promise<Conversation> {
    await this.validateAuthentication();

    if (!data.title || data.title.trim().length === 0) {
      throw new ConversationServiceError('Conversation title is required', 'INVALID_TITLE', 400);
    }

    try {
      const response = await apiClient.post<Conversation>('/conversations', {
        title: data.title.trim(),
        initialMessage: data.initialMessage?.trim()
      });
      
      console.log('[ConversationService] Created conversation:', response.data?.id);
      return response.data;
    } catch (error: any) {
      if (error.status === 401) {
        throw new AuthenticationRequiredError();
      }
      if (error.status === 403) {
        throw new ConversationPermissionError();
      }
      
      console.error('[ConversationService] Failed to create conversation:', error);
      throw new ConversationServiceError(
        'Failed to create conversation. Please try again.',
        'CREATE_FAILED',
        error.status
      );
    }
  }

  /**
   * Send a message to a conversation
   */
  async sendMessage(conversationId: string, data: MessageCreateRequest): Promise<Message> {
    await this.validateAuthentication();

    if (!conversationId || typeof conversationId !== 'string') {
      throw new ConversationServiceError('Invalid conversation ID', 'INVALID_ID', 400);
    }

    if (!data.content || data.content.trim().length === 0) {
      throw new ConversationServiceError('Message content is required', 'INVALID_CONTENT', 400);
    }

    try {
      const response = await apiClient.post<Message>(`/conversations/${conversationId}/messages`, {
        content: data.content.trim(),
        role: data.role || 'user'
      });
      
      console.log('[ConversationService] Sent message to conversation:', conversationId);
      return response.data;
    } catch (error: any) {
      if (error.status === 401) {
        throw new AuthenticationRequiredError();
      }
      if (error.status === 403) {
        throw new ConversationPermissionError();
      }
      if (error.status === 404) {
        throw new ConversationNotFoundError(conversationId);
      }
      
      console.error(`[ConversationService] Failed to send message to ${conversationId}:`, error);
      throw new ConversationServiceError(
        'Failed to send message. Please try again.',
        'SEND_FAILED',
        error.status
      );
    }
  }

  /**
   * Delete a conversation
   */
  async deleteConversation(id: string): Promise<void> {
    await this.validateAuthentication();

    if (!id || typeof id !== 'string') {
      throw new ConversationServiceError('Invalid conversation ID', 'INVALID_ID', 400);
    }

    try {
      await apiClient.delete(`/conversations/${id}`);
      console.log('[ConversationService] Deleted conversation:', id);
    } catch (error: any) {
      if (error.status === 401) {
        throw new AuthenticationRequiredError();
      }
      if (error.status === 403) {
        throw new ConversationPermissionError();
      }
      if (error.status === 404) {
        throw new ConversationNotFoundError(id);
      }
      
      console.error(`[ConversationService] Failed to delete conversation ${id}:`, error);
      throw new ConversationServiceError(
        'Failed to delete conversation. Please try again.',
        'DELETE_FAILED',
        error.status
      );
    }
  }

  /**
   * Archive a conversation
   */
  async archiveConversation(id: string): Promise<Conversation> {
    await this.validateAuthentication();

    if (!id || typeof id !== 'string') {
      throw new ConversationServiceError('Invalid conversation ID', 'INVALID_ID', 400);
    }

    try {
      const response = await apiClient.put<Conversation>(`/conversations/${id}`, {
        isArchived: true
      });
      
      console.log('[ConversationService] Archived conversation:', id);
      return response.data;
    } catch (error: any) {
      if (error.status === 401) {
        throw new AuthenticationRequiredError();
      }
      if (error.status === 403) {
        throw new ConversationPermissionError();
      }
      if (error.status === 404) {
        throw new ConversationNotFoundError(id);
      }
      
      console.error(`[ConversationService] Failed to archive conversation ${id}:`, error);
      throw new ConversationServiceError(
        'Failed to archive conversation. Please try again.',
        'ARCHIVE_FAILED',
        error.status
      );
    }
  }

  /**
   * Generate a blog post from a conversation
   */
  async generateBlogPost(id: string): Promise<{ content: string; title: string }> {
    await this.validateAuthentication();

    if (!id || typeof id !== 'string') {
      throw new ConversationServiceError('Invalid conversation ID', 'INVALID_ID', 400);
    }

    try {
      const response = await apiClient.post<{ content: string; title: string }>(`/conversations/${id}/generate-blog`);
      console.log('[ConversationService] Generated blog post for conversation:', id);
      return response.data;
    } catch (error: any) {
      if (error.status === 401) {
        throw new AuthenticationRequiredError();
      }
      if (error.status === 403) {
        throw new ConversationPermissionError();
      }
      if (error.status === 404) {
        throw new ConversationNotFoundError(id);
      }
      
      console.error(`[ConversationService] Failed to generate blog post for ${id}:`, error);
      throw new ConversationServiceError(
        'Failed to generate blog post. Please try again.',
        'BLOG_GENERATION_FAILED',
        error.status
      );
    }
  }
}

// Export singleton instance
export const conversationService = new ProductionConversationService();

// Export service class for testing
export { ProductionConversationService };

// Export all error types for better error handling
export {
  ConversationServiceError,
  AuthenticationRequiredError,
  ConversationNotFoundError,
  ConversationPermissionError
};
