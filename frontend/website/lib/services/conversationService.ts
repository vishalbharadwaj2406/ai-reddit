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
      const response = await apiClient.get<Conversation[]>(
        `/api/v1/conversations?limit=${limit}&offset=${offset}`
      );
      return response || [];
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
      const response = await apiClient.get<ConversationDetail>(
        `/api/v1/conversations/${conversationId}`
      );
      return response;
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
      const response = await apiClient.post<Message>(
        `/api/v1/conversations/${conversationId}/messages`,
        data
      );
      return response;
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
      const response = await apiClient.post<ConversationDetail>(
        '/api/v1/conversations',
        { title, firstMessage }
      );
      return response;
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
   * Stream AI response (simplified - no real streaming for now)
   */
  async streamAIResponse(
    conversationId: string,
    messageId: string,
    onChunk: (chunk: string) => void,
    onComplete: (fullResponse: string) => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      // For now, just simulate streaming by calling the generate endpoint
      const response = await apiClient.post<{ content: string }>(
        '/api/v1/conversations/generate',
        { conversationId, messageId }
      );
      
      // Simulate streaming chunks
      const content = response.content || 'Response generated successfully.';
      const chunks = content.split(' ');
      let currentContent = '';
      
      for (let i = 0; i < chunks.length; i++) {
        currentContent += (i > 0 ? ' ' : '') + chunks[i];
        onChunk(currentContent);
        // Small delay to simulate streaming
        await new Promise(resolve => setTimeout(resolve, 50));
      }
      
      onComplete(content);
    } catch (err) {
      if (err instanceof Error && err.message.includes('401')) {
        throw new AuthenticationRequiredError();
      }
      onError('Failed to generate AI response');
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
