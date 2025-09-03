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
   * Generate blog from conversation using real backend SSE streaming
   * Production-grade implementation matching the working AI chat system
   */
  async generateBlogFromConversation(
    conversationId: string,
    additionalContext: string,
    onChunk: (chunk: string) => void,
    onComplete: (fullResponse: string, messageId: string) => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      console.log('🚀 Starting blog generation SSE stream:', { conversationId, additionalContext });
      
      // Use fetch to initiate the SSE stream with POST data
      // This is necessary because EventSource doesn't support POST requests with body
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/conversations/${conversationId}/generate-blog`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
          },
          credentials: 'include', // Include HTTP-only cookies
          body: JSON.stringify({
            additional_context: additionalContext
          })
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Blog generation failed: ${response.status} ${errorText}`);
      }

      if (!response.body) {
        throw new Error('No response body received');
      }

      // Process the SSE stream manually since we used fetch
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let fullContent = '';
      let blogMessageId = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            console.log('📡 SSE stream ended');
            break;
          }

          // Decode chunk and add to buffer
          buffer += decoder.decode(value, { stream: true });
          
          // Process complete SSE messages
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6); // Remove 'data: ' prefix
              
              if (data === '[DONE]') {
                console.log('✅ Blog generation marked as done');
                break;
              }

              try {
                const parsed = JSON.parse(data);
                console.log('📋 Parsed SSE data:', parsed);
                
                if (parsed.success && parsed.data) {
                  // Extract content and message ID from response
                  // Use accumulated_content first (like working AI chat), fall back to content
                  if (parsed.data.accumulated_content !== undefined) {
                    fullContent = parsed.data.accumulated_content;
                  } else {
                    // Fallback for old format - append new chunk
                    const chunk = parsed.data.content || '';
                    fullContent += chunk;
                  }
                  blogMessageId = parsed.data.message_id || blogMessageId;
                  
                  console.log('📝 Blog content updated:', { length: fullContent.length, messageId: blogMessageId });
                  onChunk(fullContent);
                  
                  // Check if generation is complete
                  if (parsed.data.is_complete) {
                    console.log('✨ Blog generation complete:', { length: fullContent.length, messageId: blogMessageId });
                    onComplete(fullContent, blogMessageId);
                    return;
                  }
                } else if (!parsed.success) {
                  const errorMessage = parsed.message || 'Blog generation failed';
                  console.error('❌ Backend error:', errorMessage);
                  onError(errorMessage);
                  return;
                }
              } catch (parseError) {
                console.warn('⚠️ Failed to parse SSE data:', data, parseError);
                // Continue processing other messages
              }
            } else if (line.startsWith('event: ')) {
              const eventType = line.slice(7); // Remove 'event: ' prefix
              console.log('📨 SSE event type:', eventType);
              
              // Handle different event types for better debugging
              if (eventType === 'blog_response') {
                console.log('📝 Received blog_response event - streaming content');
              } else if (eventType === 'blog_complete') {
                console.log('🎯 Received blog_complete event - generation finished');
              } else if (eventType === 'error') {
                console.error('❌ Received error event from backend');
              }
            }
          }
        }
        
        // If we reach here without completing, something went wrong
        if (!fullContent) {
          onError('Blog generation completed but no content received');
        }
        
      } finally {
        reader.releaseLock();
      }

    } catch (err) {
      console.error('❌ Failed to generate blog:', err);
      if (err instanceof Error && err.message.includes('401')) {
        throw new AuthenticationRequiredError();
      }
      onError(err instanceof Error ? err.message : 'Failed to generate blog');
    }
  }
}

export const conversationService = new ConversationService();
