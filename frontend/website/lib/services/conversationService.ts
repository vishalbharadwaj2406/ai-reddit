import { apiClient, endpoints } from '../config/api';

// Type definitions for conversations
export interface Conversation {
  conversation_id: string;
  user_id: string;
  title: string;
  forked_from?: string;
  status: 'active' | 'archived';
  created_at: string;
  updated_at: string;
  message_count?: number;
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

export interface CreateConversationRequest {
  title?: string;
  forked_from?: string;
}

export interface SendMessageRequest {
  content: string;
}

// Simple error types
export class AuthenticationRequiredError extends Error {
  constructor(message = 'Authentication required') {
    super(message);
    this.name = 'AuthenticationRequiredError';
  }
}

export class ConversationServiceError extends Error {
  constructor(message: string, public code?: string) {
    super(message);
    this.name = 'ConversationServiceError';
  }
}

// Simple Conversation Service
export class ConversationService {
  
  /**
   * Get user's conversation list
   */
  async getConversations(limit = 20, offset = 0): Promise<Conversation[]> {
    try {
      const response = await apiClient.get<Conversation[]>(
        endpoints.conversations.list,
        { 
          limit: limit.toString(), 
          offset: offset.toString() 
        }
      );
      
      if (response.success) {
        return response.data;
      }
      
      throw new ConversationServiceError(
        response.message || 'Failed to fetch conversations'
      );
      
    } catch (error: any) {
      // Simple authentication error detection
      if (error.message?.includes('Authentication required') ||
          error.message?.includes('AUTH_REQUIRED') ||
          error.message?.includes('HTTP 401')) {
        throw new AuthenticationRequiredError();
      }
      
      if (error instanceof ConversationServiceError) {
        throw error;
      }
      
      throw new ConversationServiceError(
        `Failed to load conversations: ${error.message}`
      );
    }
  }

  /**
   * Create a new conversation
   */
  async createConversation(data: CreateConversationRequest): Promise<Conversation> {
    try {
      const response = await apiClient.post<{ conversation: Conversation }>(
        endpoints.conversations.create,
        data
      );
      
      if (response.success) {
        return response.data.conversation;
      }
      
      throw new ConversationServiceError(
        response.message || 'Failed to create conversation'
      );
      
    } catch (error: any) {
      if (error.message?.includes('Authentication required') ||
          error.message?.includes('AUTH_REQUIRED') ||
          error.message?.includes('HTTP 401')) {
        throw new AuthenticationRequiredError();
      }
      
      if (error instanceof ConversationServiceError) {
        throw error;
      }
      
      throw new ConversationServiceError(
        `Failed to create conversation: ${error.message}`
      );
    }
  }

  /**
   * Get conversation details with messages
   */
  async getConversation(conversationId: string): Promise<ConversationDetail> {
    try {
      const response = await apiClient.get<ConversationDetail>(
        endpoints.conversations.getById(conversationId)
      );
      
      if (response.success) {
        return response.data;
      }
      
      throw new ConversationServiceError(
        response.message || 'Failed to fetch conversation'
      );
      
    } catch (error: any) {
      if (error.message?.includes('Authentication required') ||
          error.message?.includes('AUTH_REQUIRED') ||
          error.message?.includes('HTTP 401')) {
        throw new AuthenticationRequiredError();
      }
      
      if (error instanceof ConversationServiceError) {
        throw error;
      }
      
      throw new ConversationServiceError(
        `Failed to load conversation: ${error.message}`
      );
    }
  }

  /**
   * Send a message to a conversation
   */
  async sendMessage(conversationId: string, data: SendMessageRequest): Promise<Message> {
    try {
      const response = await apiClient.post<Message>(
        endpoints.conversations.sendMessage(conversationId),
        data
      );
      
      if (response.success) {
        return response.data;
      }
      
      throw new ConversationServiceError(
        response.message || 'Failed to send message'
      );
      
    } catch (error: any) {
      if (error.message?.includes('Authentication required') ||
          error.message?.includes('AUTH_REQUIRED') ||
          error.message?.includes('HTTP 401')) {
        throw new AuthenticationRequiredError();
      }
      
      if (error instanceof ConversationServiceError) {
        throw error;
      }
      
      throw new ConversationServiceError(
        `Failed to send message: ${error.message}`
      );
    }
  }

  /**
   * Archive a conversation
   */
  async archiveConversation(conversationId: string): Promise<void> {
    try {
      const response = await apiClient.delete(
        endpoints.conversations.archive(conversationId)
      );
      
      if (!response.success) {
        throw new ConversationServiceError(
          response.message || 'Failed to archive conversation'
        );
      }
      
    } catch (error: any) {
      if (error.message?.includes('Authentication required') ||
          error.message?.includes('AUTH_REQUIRED') ||
          error.message?.includes('HTTP 401')) {
        throw new AuthenticationRequiredError();
      }
      
      if (error instanceof ConversationServiceError) {
        throw error;
      }
      
      throw new ConversationServiceError(
        `Failed to archive conversation: ${error.message}`
      );
    }
  }

  /**
   * Generate blog from conversation via Server-Sent Events
   */
  async generateBlogFromConversation(
    conversationId: string,
    additionalContext: string,
    onChunk: (chunk: string) => void,
    onComplete: (fullResponse: string, messageId: string) => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      // Use apiClient to make POST request with streaming response
      let fullResponse = '';
      let blogMessageId = '';
      
      // Create headers for the fetch request
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      };
      
      // Get auth token from localStorage (similar to apiClient)
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('ai_social_backend_jwt');
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
      }
      
      const response = await fetch(`${(apiClient as any).baseURL}${endpoints.conversations.generateBlog(conversationId)}`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          additional_context: additionalContext
        })
      });
      
      if (!response.ok) {
        throw new ConversationServiceError(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const reader = response.body?.getReader();
      if (!reader) {
        throw new ConversationServiceError('Failed to get response stream');
      }
      
      const decoder = new TextDecoder();
      let buffer = '';
      
      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;
          
          buffer += decoder.decode(value, { stream: true });
          
          // Process complete SSE messages
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.success && data.data) {
                  const chunk = data.data;
                  
                  if (chunk.content) {
                    if (chunk.message_id) {
                      blogMessageId = chunk.message_id;
                    }
                    
                    if (chunk.is_complete) {
                      fullResponse = chunk.content;
                      onComplete(fullResponse, blogMessageId);
                      return;
                    } else {
                      onChunk(chunk.content);
                    }
                  }
                }
              } catch (parseError) {
                console.error('Error parsing SSE data:', parseError);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
      
    } catch (error: any) {
      if (error.name === 'AbortError') {
        onError('Blog generation was cancelled');
      } else if (error.message?.includes('Authentication required') ||
          error.message?.includes('AUTH_REQUIRED') ||
          error.message?.includes('HTTP 401')) {
        throw new AuthenticationRequiredError();
      } else {
        onError(`Blog generation failed: ${error.message}`);
      }
    }
  }

  /**
   * Stream AI response to a user message via Server-Sent Events
   */
  async streamAIResponse(
    conversationId: string, 
    messageId: string,
    onChunk: (chunk: string) => void,
    onComplete: (fullResponse: string) => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      const url = `${endpoints.conversations.streamAI(conversationId)}?message_id=${messageId}`;
      const eventSource = await apiClient.createEventSource(url);
      
      let fullResponse = '';
      
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.success && data.data) {
            const chunk = data.data;
            
            if (chunk.content) {
              if (chunk.is_complete) {
                // Final complete response
                fullResponse = chunk.content;
                onComplete(fullResponse);
                eventSource.close();
              } else {
                // Streaming chunk
                onChunk(chunk.content);
              }
            }
          }
        } catch (err) {
          console.error('Error parsing SSE data:', err);
          onError('Failed to parse streaming response');
        }
      };
      
      eventSource.onerror = (event) => {
        console.error('SSE error:', event);
        onError('Connection error during AI response streaming');
        eventSource.close();
      };
      
      // Handle specific SSE events
      eventSource.addEventListener('ai_response', (event: any) => {
        try {
          const data = JSON.parse(event.data);
          if (data.success && data.data?.content) {
            onChunk(data.data.content);
          }
        } catch (err) {
          console.error('Error parsing ai_response event:', err);
        }
      });
      
      eventSource.addEventListener('ai_complete', (event: any) => {
        try {
          const data = JSON.parse(event.data);
          if (data.success && data.data?.content) {
            fullResponse = data.data.content;
            onComplete(fullResponse);
            eventSource.close();
          }
        } catch (err) {
          console.error('Error parsing ai_complete event:', err);
        }
      });
      
      eventSource.addEventListener('error', (event: any) => {
        try {
          const data = JSON.parse(event.data);
          onError(data.message || 'AI streaming error');
          eventSource.close();
        } catch (err) {
          onError('AI streaming encountered an error');
          eventSource.close();
        }
      });
      
    } catch (error: any) {
      if (error.message?.includes('Authentication required') ||
          error.message?.includes('AUTH_REQUIRED') ||
          error.message?.includes('HTTP 401')) {
        throw new AuthenticationRequiredError();
      }
      
      throw new ConversationServiceError(
        `Failed to stream AI response: ${error.message}`
      );
    }
  }
}

// Export singleton instance
export const conversationService = new ConversationService(); 