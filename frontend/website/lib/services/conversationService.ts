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
      let lastChunkTime = Date.now();
      const RESPONSE_TIMEOUT = 120000; // 120 seconds timeout (same as backend)
      
      // Set up timeout to handle stalled connections
      const timeoutCheck = setInterval(() => {
        const now = Date.now();
        if (now - lastChunkTime > RESPONSE_TIMEOUT) {
          console.error('⏰ [CHAT] Response timeout - no data received for 120 seconds');
          clearInterval(timeoutCheck);
          eventSource.close();
          onError('Response timed out. This may be due to API rate limits or high server load. Please try again.');
        }
      }, 10000); // Check every 10 seconds

      const cleanup = () => {
        clearInterval(timeoutCheck);
        eventSource.close();
      };

      eventSource.onmessage = (event) => {
        lastChunkTime = Date.now(); // Reset timeout
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
              cleanup();
              onComplete(fullContent);
            }
          } else {
            console.warn('⚠️ SSE data missing success or data fields:', data);
          }
        } catch (parseError) {
          console.error('❌ Error parsing SSE data:', parseError, 'Raw data:', event.data);
          cleanup();
          onError('Error parsing streaming response');
        }
      };

      // Listen for ai_response events (streaming chunks)
      eventSource.addEventListener('ai_response', (event) => {
        lastChunkTime = Date.now(); // Reset timeout
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
          cleanup();
          onError('Error parsing streaming chunk');
        }
      });

      eventSource.onerror = (error) => {
        console.error('❌ SSE connection error:', error);
        console.log('🔌 EventSource readyState:', eventSource.readyState);
        cleanup();
        onError('Connection error during AI response streaming');
      };

      eventSource.addEventListener('ai_complete', (event) => {
        lastChunkTime = Date.now(); // Reset timeout
        console.log('🎯 AI completion event received:', event.data);
        try {
          const data = JSON.parse(event.data);
          if (data.success && data.data) {
            fullContent = data.data.accumulated_content || data.data.content || fullContent;
            console.log('✨ Final response:', fullContent);
            onComplete(fullContent);
          }
          cleanup();
        } catch (parseError) {
          console.error('❌ Error parsing completion event:', parseError);
          cleanup();
          onError('Error parsing completion response');
        }
      });

      // Handle error events specifically for timeout detection
      eventSource.addEventListener('error', (event) => {
        console.error('❌ [CHAT] Error event received:', event);
        try {
          const messageEvent = event as MessageEvent;
          if (messageEvent.data) {
            const data = JSON.parse(messageEvent.data);
            if (data.errorCode === 'AI_TIMEOUT_ERROR') {
              console.error('⏰ [CHAT] Backend timeout detected');
              cleanup();
              onError('Response timed out due to API rate limits or high server load. Please try again.');
              return;
            }
          }
        } catch (parseError) {
          // Fall through to generic error handling
        }
        cleanup();
        onError('AI service error occurred during streaming');
      });

    } catch (err) {
      if (err instanceof Error && err.message.includes('401')) {
        throw new AuthenticationRequiredError();
      }
      console.error('❌ [CHAT] Failed to start AI response streaming:', err);
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
      console.log('🚀 [BLOG] Starting blog generation SSE stream:', { conversationId, additionalContext });
      
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

      console.log('🌐 [BLOG] Response received:', { 
        status: response.status, 
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries())
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ [BLOG] Response not OK:', errorText);
        throw new Error(`Blog generation failed: ${response.status} ${errorText}`);
      }

      if (!response.body) {
        console.error('❌ [BLOG] No response body received');
        throw new Error('No response body received');
      }

      // Process the SSE stream manually since we used fetch
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let fullContent = '';
      let blogMessageId = '';
      let chunkCount = 0;
      let lastChunkTime = Date.now();
      const CHUNK_TIMEOUT = 30000; // 30 seconds timeout between chunks

      console.log('📡 [BLOG] Starting to read SSE stream...');

      try {
        while (true) {
          // Add timeout for individual chunk reads
          const readPromise = reader.read();
          const timeoutPromise = new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Chunk read timeout')), CHUNK_TIMEOUT)
          );
          
          const { done, value } = await Promise.race([readPromise, timeoutPromise]) as ReadableStreamReadResult<Uint8Array>;
          
          if (done) {
            console.log('📡 [BLOG] SSE stream ended', { 
              totalChunks: chunkCount, 
              finalContentLength: fullContent.length,
              finalContent: fullContent.substring(0, 200) + '...'
            });
            break;
          }

          lastChunkTime = Date.now(); // Reset timeout on successful chunk

          // Decode chunk and add to buffer
          buffer += decoder.decode(value, { stream: true });
          
          // Process complete SSE messages
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6); // Remove 'data: ' prefix
              
              if (data === '[DONE]') {
                console.log('✅ [BLOG] Blog generation marked as done');
                break;
              }

              try {
                const parsed = JSON.parse(data);
                chunkCount++;
                console.log(`📋 [BLOG] Chunk ${chunkCount} parsed:`, { 
                  success: parsed.success,
                  dataLength: parsed.data?.content?.length || 0,
                  isComplete: parsed.data?.is_complete,
                  messageId: parsed.data?.message_id,
                  preview: parsed.data?.content?.substring(0, 50) + '...'
                });
                
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
                  
                  console.log('📝 [BLOG] Content updated:', { 
                    length: fullContent.length, 
                    messageId: blogMessageId,
                    isComplete: parsed.data.is_complete 
                  });
                  onChunk(fullContent);
                  
                  // Check if generation is complete
                  if (parsed.data.is_complete) {
                    console.log('✨ [BLOG] Generation complete:', { 
                      length: fullContent.length, 
                      messageId: blogMessageId,
                      finalPreview: fullContent.substring(0, 100) + '...'
                    });
                    onComplete(fullContent, blogMessageId);
                    return;
                  }
                } else if (!parsed.success) {
                  const errorMessage = parsed.message || 'Blog generation failed';
                  console.error('❌ [BLOG] Backend error:', errorMessage);
                  onError(errorMessage);
                  return;
                }
              } catch (parseError) {
                console.warn('⚠️ [BLOG] Failed to parse SSE data:', data, parseError);
                // Continue processing other messages
              }
            } else if (line.startsWith('event: ')) {
              const eventType = line.slice(7); // Remove 'event: ' prefix
              console.log('📨 [BLOG] SSE event type:', eventType);
              
              // Handle different event types for better debugging
              if (eventType === 'blog_response') {
                console.log('📝 [BLOG] Received blog_response event - streaming content');
              } else if (eventType === 'blog_complete') {
                console.log('🎯 [BLOG] Received blog_complete event - generation finished');
              } else if (eventType === 'error') {
                console.error('❌ [BLOG] Received error event from backend');
              }
            }
          }
        }
        
        // If we reach here without completing, something went wrong
        if (!fullContent) {
          console.error('❌ [BLOG] Generation completed but no content received');
          onError('Blog generation completed but no content received');
        } else {
          console.log('🔄 [BLOG] Stream ended but completion not marked, treating as complete');
          onComplete(fullContent, blogMessageId);
        }
        
      } finally {
        reader.releaseLock();
      }

    } catch (err) {
      console.error('❌ [BLOG] Failed to generate blog:', err);
      
      if (err instanceof Error) {
        if (err.message.includes('401')) {
          throw new AuthenticationRequiredError();
        } else if (err.message.includes('timeout') || err.message.includes('Chunk read timeout')) {
          console.error('⏰ [BLOG] Request timed out - this may be due to Gemini API rate limits or long generation time');
          onError('Blog generation timed out. This may be due to API rate limits or complex content. Please try again.');
        } else {
          onError(err.message);
        }
      } else {
        onError('Failed to generate blog');
      }
    }
  }
}

export const conversationService = new ConversationService();
