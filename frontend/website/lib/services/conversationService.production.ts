/**
 * Production-Grade Conversation Service - NextAuth Only
 * 
 * Clean, professional implementation using only NextAuth for authentication.
 * Zero legacy code, production-ready for millions of users.
 */

import { apiClient } from '../config/api.production';
import { endpoints } from '../config/api.production';

// Types
export interface Conversation {
  conversation_id: string;
  user_id?: string; // Optional for list responses
  title: string;
  forked_from?: string;
  status?: 'active' | 'archived'; // Optional, defaults to active
  created_at: string;
  updated_at: string;
  message_count?: number; // Make optional for compatibility
}

export interface Message {
  messageId: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  isBlog: boolean;
  createdAt: string;
}

export interface ConversationDetail {
  conversationId: string;
  title: string;
  createdAt: string;
  forkedFrom?: string;
  messages: Message[];
}

export interface SendMessageRequest {
  content: string;
}

export interface ApiConversation {
  conversation_id: string;
  title: string;
  forked_from?: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ApiMessage {
  messageId: string;
  role: string;
  content: string;
  isBlog: boolean;
  createdAt: string;
}

export interface ApiConversationDetail {
  conversationId: string;
  title: string;
  createdAt: string;
  forkedFrom?: string;
  messages: ApiMessage[];
}

// Custom error classes
export class ConversationServiceError extends Error {
  constructor(message: string, public code?: string) {
    super(message);
    this.name = 'ConversationServiceError';
  }
}

export class AuthenticationRequiredError extends ConversationServiceError {
  constructor() {
    super('Authentication required to access conversations', 'AUTH_REQUIRED');
    this.name = 'AuthenticationRequiredError';
  }
}

// Data transformation utilities
const mapApiConversation = (api: ApiConversation): Conversation => ({
  conversation_id: api.conversation_id,
  title: api.title,
  forked_from: api.forked_from,
  created_at: api.created_at,
  updated_at: api.updated_at,
  message_count: api.message_count || 0
});

const mapApiMessage = (api: ApiMessage): Message => ({
  messageId: api.messageId,
  role: api.role as 'user' | 'assistant' | 'system',
  content: api.content,
  isBlog: api.isBlog,
  createdAt: api.createdAt
});

const mapApiConversationDetail = (api: ApiConversationDetail): ConversationDetail => ({
  conversationId: api.conversationId,
  title: api.title,
  createdAt: api.createdAt,
  forkedFrom: api.forkedFrom,
  messages: api.messages.map(mapApiMessage)
});

class ConversationService {
  /**
   * Handle service errors with comprehensive error mapping
   * Production-grade error handling for enterprise applications
   */
  private handleError(err: unknown, context: string): never {
    // Log error for monitoring (replace with your logging service)
    console.error(`[ConversationService] ${context}:`, err);
    
    if (err instanceof Error) {
      // Authentication errors - handled by NextAuth
      if (err.message.includes('Authentication') || err.message.includes('401')) {
        throw new AuthenticationRequiredError();
      }
      
      // Network connectivity errors
      if (err.message.includes('NetworkError') || err.message.includes('Failed to fetch')) {
        throw new ConversationServiceError(
          'Unable to connect to the server. Please check your internet connection.',
          'NETWORK_ERROR'
        );
      }
      
      // Permission errors
      if (err.message.includes('Access denied') || err.message.includes('403')) {
        throw new ConversationServiceError(
          'You do not have permission to perform this action.',
          'PERMISSION_DENIED'
        );
      }
      
      // Server errors
      if (err.message.includes('Server error') || err.message.includes('500')) {
        throw new ConversationServiceError(
          'Our servers are experiencing issues. Please try again in a few moments.',
          'SERVER_ERROR'
        );
      }
      
      // Rate limiting
      if (err.message.includes('429')) {
        throw new ConversationServiceError(
          'Too many requests. Please wait a moment and try again.',
          'RATE_LIMITED'
        );
      }
      
      // Pass through existing ConversationServiceError
      if (err instanceof ConversationServiceError) {
        throw err;
      }
      
      // Generic error with context
      throw new ConversationServiceError(
        `${context}: ${err.message}`,
        'UNKNOWN_ERROR'
      );
    }
    
    // Unknown error type
    throw new ConversationServiceError(
      `${context}: An unexpected error occurred`,
      'UNKNOWN_ERROR'
    );
  }

  /**
   * Get list of conversations with caching support
   */
  async getConversations(limit = 20, offset = 0): Promise<Conversation[]> {
    try {
      const response = await apiClient.get<ApiConversation[]>(
        endpoints.conversations.list,
        { limit: limit.toString(), offset: offset.toString() }
      );
      
      if (response.success && Array.isArray(response.data)) {
        return response.data.map(mapApiConversation);
      }
      
      throw new ConversationServiceError(response.message || 'Failed to fetch conversations');
    } catch (err) {
      this.handleError(err, 'Failed to load conversations');
    }
  }

  /**
   * Get single conversation with messages
   */
  async getConversation(conversationId: string): Promise<ConversationDetail> {
    try {
      const response = await apiClient.get<ApiConversationDetail>(
        endpoints.conversations.getById(conversationId)
      );
      
      if (response.success) {
        return mapApiConversationDetail(response.data);
      }
      
      throw new ConversationServiceError(response.message || 'Failed to fetch conversation');
    } catch (err) {
      this.handleError(err, 'Failed to load conversation');
    }
  }

  /**
   * Send message to conversation
   */
  async sendMessage(conversationId: string, data: SendMessageRequest): Promise<Message> {
    try {
      const response = await apiClient.post<ApiMessage>(
        endpoints.conversations.sendMessage(conversationId),
        data
      );
      
      if (response.success) {
        return mapApiMessage(response.data);
      }
      
      throw new ConversationServiceError(response.message || 'Failed to send message');
    } catch (err) {
      this.handleError(err, 'Failed to send message');
    }
  }

  /**
   * Create new conversation
   */
  async createConversation(title?: string): Promise<ConversationDetail> {
    try {
      const response = await apiClient.post<ApiConversationDetail>(
        endpoints.conversations.create,
        { title: title || 'New Conversation' }
      );
      
      if (response.success) {
        return mapApiConversationDetail(response.data);
      }
      
      throw new ConversationServiceError(response.message || 'Failed to create conversation');
    } catch (err) {
      this.handleError(err, 'Failed to create conversation');
    }
  }

  /**
   * Archive/delete conversation
   */
  async archiveConversation(conversationId: string): Promise<void> {
    try {
      const response = await apiClient.delete<void>(
        endpoints.conversations.archive(conversationId)
      );
      
      if (!response.success) {
        throw new ConversationServiceError(response.message || 'Failed to archive conversation');
      }
    } catch (err) {
      this.handleError(err, 'Failed to archive conversation');
    }
  }

  /**
   * Stream AI response with Server-Sent Events
   */
  async streamAIResponse(
    conversationId: string,
    messageId: string,
    onChunk: (chunk: string) => void,
    onComplete: (fullResponse: string) => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      const params = new URLSearchParams({ message_id: messageId });
      const eventSource = apiClient.createEventSource(
        endpoints.conversations.streamAI(conversationId),
        params
      );

      let fullResponse = '';

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'chunk' && data.content) {
            fullResponse += data.content;
            onChunk(fullResponse);
          } else if (data.type === 'complete') {
            eventSource.close();
            onComplete(fullResponse);
          } else if (data.type === 'error') {
            eventSource.close();
            onError(data.error || 'Unknown streaming error');
          }
        } catch (parseError) {
          console.error('Failed to parse SSE data:', parseError);
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        eventSource.close();
        onError('Connection to AI service lost. Please try again.');
      };

      // Cleanup timeout for long-running streams
      setTimeout(() => {
        if (eventSource.readyState !== EventSource.CLOSED) {
          eventSource.close();
          onError('Response timeout. Please try again.');
        }
      }, 60000); // 60 second timeout

    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to start AI response stream');
    }
  }

  /**
   * Generate blog from conversation
   */
  async generateBlogFromConversation(
    conversationId: string,
    additionalContext: string,
    onChunk: (chunk: string) => void,
    onComplete: (fullResponse: string, messageId: string) => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      const params = new URLSearchParams({ context: additionalContext });
      const eventSource = apiClient.createEventSource(
        endpoints.conversations.generateBlog(conversationId),
        params
      );

      let fullResponse = '';
      let messageId = '';

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'chunk' && data.content) {
            fullResponse += data.content;
            onChunk(fullResponse);
          } else if (data.type === 'complete') {
            messageId = data.messageId || '';
            eventSource.close();
            onComplete(fullResponse, messageId);
          } else if (data.type === 'error') {
            eventSource.close();
            onError(data.error || 'Unknown blog generation error');
          }
        } catch (parseError) {
          console.error('Failed to parse blog SSE data:', parseError);
        }
      };

      eventSource.onerror = (error) => {
        console.error('Blog SSE connection error:', error);
        eventSource.close();
        onError('Connection to blog generation service lost. Please try again.');
      };

      // Cleanup timeout
      setTimeout(() => {
        if (eventSource.readyState !== EventSource.CLOSED) {
          eventSource.close();
          onError('Blog generation timeout. Please try again.');
        }
      }, 120000); // 2 minute timeout for blog generation

    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to start blog generation');
    }
  }
}

// Export singleton instance
export const conversationService = new ConversationService();
export default conversationService;
