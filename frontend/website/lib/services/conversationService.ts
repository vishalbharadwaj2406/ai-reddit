/**
 * Unified Conversation Service
 * Uses the new backend-only authentication system with HTTP-only cookies
 */

import { apiClient } from '../api/client';

// Types
export interface Conversation {
  conversation_id: string;
  user_id?: string;
  title: string;
  forked_from?: string;
  status?: 'active' | 'archived';
  created_at: string;
  updated_at: string;
  message_count?: number;
  messages?: Message[];
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}

export interface Message {
  messageId: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  isBlog?: boolean;
  createdAt: string;
}

export interface SendMessageRequest {
  content: string;
}

// Custom error classes
export class ConversationServiceError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ConversationServiceError';
  }
}

export class AuthenticationRequiredError extends Error {
  constructor(message = 'Authentication required') {
    super(message);
    this.name = 'AuthenticationRequiredError';
  }
}

class ConversationService {
  /**
   * Get list of conversations
   */
  async getConversations(limit = 20, offset = 0): Promise<Conversation[]> {
    try {
      const response = await apiClient.get<{success: boolean; data: Conversation[]; message: string}>(
        `/api/v1/conversations?limit=${limit}&offset=${offset}`
      );
      // Extract the data array from the backend response wrapper
      return response?.data || [];
    } catch (err) {
      if (err instanceof Error && err.message.includes('401')) {
        throw new AuthenticationRequiredError();
      }
      throw new ConversationServiceError('Failed to fetch conversations');
    }
  }

  /**
   * Get conversation by ID with all messages
   */
  async getConversation(conversationId: string): Promise<ConversationDetail> {
    try {
      const response = await apiClient.get<{success: boolean; data: ConversationDetail; message: string}>(
        `/api/v1/conversations/${conversationId}`
      );
      // Extract the data from the backend response wrapper
      return response?.data;
    } catch (err) {
      if (err instanceof Error && err.message.includes('401')) {
        throw new AuthenticationRequiredError();
      }
      throw new ConversationServiceError('Failed to fetch conversation');
    }
  }

  /**
   * Send a message to a conversation
   */
  async sendMessage(conversationId: string, data: SendMessageRequest): Promise<Message> {
    try {
      const response = await apiClient.post<{success: boolean; data: {message_id: string; content: string; role: string; created_at: string}; message: string}>(
        `/api/v1/conversations/${conversationId}/messages`,
        data
      );
      
      // Convert backend response to frontend Message format
      const messageData = response?.data;
      return {
        messageId: messageData.message_id,
        role: messageData.role as 'user' | 'assistant' | 'system',
        content: messageData.content,
        isBlog: false,
        createdAt: messageData.created_at
      };
    } catch (err) {
      if (err instanceof Error && err.message.includes('401')) {
        throw new AuthenticationRequiredError();
      }
      throw new ConversationServiceError('Failed to send message');
    }
  }

  /**
   * Create a new conversation
   */
  async createConversation(title: string, firstMessage?: string): Promise<ConversationDetail> {
    try {
      const response = await apiClient.post<{success: boolean; data: {conversation: ConversationDetail}; message: string}>(
        '/api/v1/conversations',
        { title, firstMessage }
      );
      // Extract the conversation data from the nested response wrapper
      return response?.data?.conversation;
    } catch (err) {
      if (err instanceof Error && err.message.includes('401')) {
        throw new AuthenticationRequiredError();
      }
      throw new ConversationServiceError('Failed to create conversation');
    }
  }

  /**
   * Archive (delete) a conversation
   */
  async archiveConversation(conversationId: string): Promise<void> {
    try {
      await apiClient.delete<void>(`/api/v1/conversations/${conversationId}/archive`);
    } catch (err) {
      if (err instanceof Error && err.message.includes('401')) {
        throw new AuthenticationRequiredError();
      }
      throw new ConversationServiceError('Failed to archive conversation');
    }
  }

  /**
   * Stream AI response using Server-Sent Events
   */
  async streamAIResponse(
    conversationId: string,
    messageId: string,
    onChunk: (chunk: string) => void,
    onComplete: (fullResponse: string) => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      console.log('🌊 Starting SSE stream:', { conversationId, messageId });
      
      // EventSource with credentials - this works in modern browsers
      const eventSource = new EventSource(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/conversations/${conversationId}/stream?message_id=${messageId}`,
        { withCredentials: true }
      );

      let fullContent = '';

      eventSource.onmessage = (event) => {
        console.log('📨 SSE default message received:', event.data);
        try {
          const data = JSON.parse(event.data);
          console.log('📋 Parsed SSE data:', data);
          
          if (data.success && data.data) {
            // Use accumulated_content if available (new format), otherwise fall back to content
            if (data.data.accumulated_content !== undefined) {
              fullContent = data.data.accumulated_content;
              console.log('📝 Using accumulated_content:', fullContent);
            } else {
              // Fallback for old format - append new chunk
              const chunk = data.data.content || '';
              fullContent += chunk;
              console.log('📝 Appending chunk:', chunk, '-> Full content:', fullContent);
            }
            
            onChunk(fullContent);
            
            if (data.data.is_complete) {
              console.log('✅ Stream complete, closing connection');
              eventSource.close();
              onComplete(fullContent);
            }
          } else {
            console.warn('⚠️ SSE data missing success or data fields:', data);
          }
        } catch (parseError) {
          console.error('❌ Error parsing SSE data:', parseError, 'Raw data:', event.data);
          onError('Error parsing streaming response');
          eventSource.close();
        }
      };

      // Listen for ai_response events (streaming chunks)
      eventSource.addEventListener('ai_response', (event) => {
        console.log('🔄 AI response chunk received:', event.data);
        try {
          const data = JSON.parse(event.data);
          console.log('📋 Parsed chunk data:', data);
          
          if (data.success && data.data) {
            // Use accumulated_content if available (new format), otherwise fall back to content
            if (data.data.accumulated_content !== undefined) {
              fullContent = data.data.accumulated_content;
              console.log('📝 Using accumulated_content:', fullContent);
            } else {
              // Fallback for old format - append new chunk
              const chunk = data.data.content || '';
              fullContent += chunk;
              console.log('📝 Appending chunk:', chunk, '-> Full content:', fullContent);
            }
            
            onChunk(fullContent);
          }
        } catch (parseError) {
          console.error('❌ Error parsing ai_response event:', parseError);
          onError('Error parsing streaming chunk');
          eventSource.close();
        }
      });

      eventSource.onerror = (error) => {
        console.error('❌ SSE connection error:', error);
        console.log('🔌 EventSource readyState:', eventSource.readyState);
        eventSource.close();
        onError('Connection error during AI response streaming');
      };

      eventSource.addEventListener('ai_complete', (event) => {
        console.log('🎯 AI completion event received:', event.data);
        try {
          const data = JSON.parse(event.data);
          if (data.success && data.data) {
            fullContent = data.data.accumulated_content || data.data.content || fullContent;
            console.log('✨ Final response:', fullContent);
            onComplete(fullContent);
          }
          eventSource.close();
        } catch (parseError) {
          console.error('❌ Error parsing completion event:', parseError);
          onError('Error parsing completion response');
          eventSource.close();
        }
      });

    } catch (err) {
      if (err instanceof Error && err.message.includes('401')) {
        throw new AuthenticationRequiredError();
      }
      onError('Failed to start AI response streaming');
    }
  }

  /**
   * Generate blog from conversation (simplified)
   */
  async generateBlogFromConversation(
    conversationId: string,
    additionalContext: string,
    onChunk: (chunk: string) => void,
    onComplete: (fullResponse: string, messageId: string) => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      // For now, just generate a simple blog response
      const blogContent = `# Blog Post from Conversation

Based on the conversation, here's a generated blog post:

${additionalContext ? `Additional context: ${additionalContext}\n\n` : ''}

This is a generated blog post that summarizes the key points from our conversation. The content would normally be generated by AI based on the conversation history.

## Key Points

- Point 1 from the conversation
- Point 2 from the conversation  
- Point 3 from the conversation

## Conclusion

This blog post captures the essence of our discussion and provides valuable insights.`;

      // Simulate streaming
      const chunks = blogContent.split('\n');
      let currentContent = '';
      
      for (let i = 0; i < chunks.length; i++) {
        currentContent += (i > 0 ? '\n' : '') + chunks[i];
        onChunk(currentContent);
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      onComplete(blogContent, `blog-${Date.now()}`);
    } catch {
      onError('Failed to generate blog content');
    }
  }
}

export const conversationService = new ConversationService();
