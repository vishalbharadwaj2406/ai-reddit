import { apiClient, endpoints } from '../config/api';

// Domain model types used by UI
export interface Conversation {
  conversation_id: string; // keeping backend shape for list usage
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

// Raw API shapes (snake_case) -----------------------------
interface ApiMessage {
  message_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  is_blog: boolean;
  created_at: string;
}
interface ApiConversationDetail {
  conversation_id: string;
  title: string;
  created_at: string;
  forked_from?: string;
  messages: ApiMessage[];
}

// Error helpers ------------------------------------------
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

const isAuthErrorMessage = (msg: string): boolean =>
  msg.includes('Authentication required') || msg.includes('AUTH_REQUIRED') || msg.includes('HTTP 401');

const getErrorMessage = (err: unknown): string => {
  if (err instanceof Error) return err.message;
  if (typeof err === 'string') return err;
  try { return JSON.stringify(err); } catch { return 'Unknown error'; }
};

// Mapping helpers ---------------------------------------
const mapApiMessage = (m: ApiMessage): Message => ({
  messageId: m.message_id,
  role: m.role,
  content: m.content,
  isBlog: m.is_blog,
  createdAt: m.created_at,
});

const mapApiConversationDetail = (c: ApiConversationDetail): ConversationDetail => ({
  conversationId: c.conversation_id,
  title: c.title,
  createdAt: c.created_at,
  forkedFrom: c.forked_from,
  messages: c.messages.map(mapApiMessage),
});

// SSE types ---------------------------------------------
interface SSEChunkPayload {
  content?: string;
  is_complete?: boolean;
  message_id?: string;
}
interface SSEEnvelope<T> {
  success: boolean;
  data?: T;
  message?: string;
}

export class ConversationService {
  private handleError(err: unknown, fallback: string): never {
    const msg = getErrorMessage(err);
    if (isAuthErrorMessage(msg)) {
      throw new AuthenticationRequiredError();
    }
    if (err instanceof ConversationServiceError) throw err;
    throw new ConversationServiceError(`${fallback}: ${msg}`);
  }

  async getConversations(limit = 20, offset = 0): Promise<Conversation[]> {
    try {
      const response = await apiClient.get<Conversation[]>(
        endpoints.conversations.list,
        { limit: limit.toString(), offset: offset.toString() }
      );
      if (response.success) return response.data;
      throw new ConversationServiceError(response.message || 'Failed to fetch conversations');
    } catch (err) {
      this.handleError(err, 'Failed to load conversations');
    }
  }

  async createConversation(data: CreateConversationRequest): Promise<Conversation> {
    try {
      const response = await apiClient.post<{ conversation: Conversation }>(
        endpoints.conversations.create,
        data
      );
      if (response.success) return response.data.conversation;
      throw new ConversationServiceError(response.message || 'Failed to create conversation');
    } catch (err) {
      this.handleError(err, 'Failed to create conversation');
    }
  }

  async getConversation(conversationId: string): Promise<ConversationDetail> {
    try {
      const response = await apiClient.get<ApiConversationDetail>(
        endpoints.conversations.getById(conversationId)
      );
      if (response.success) return mapApiConversationDetail(response.data);
      throw new ConversationServiceError(response.message || 'Failed to fetch conversation');
    } catch (err) {
      this.handleError(err, 'Failed to load conversation');
    }
  }

  async sendMessage(conversationId: string, data: SendMessageRequest): Promise<Message> {
    try {
      const response = await apiClient.post<ApiMessage>(
        endpoints.conversations.sendMessage(conversationId),
        data
      );
      if (response.success) return mapApiMessage(response.data);
      throw new ConversationServiceError(response.message || 'Failed to send message');
    } catch (err) {
      this.handleError(err, 'Failed to send message');
    }
  }

  async archiveConversation(conversationId: string): Promise<void> {
    try {
      const response = await apiClient.delete<unknown>(
        endpoints.conversations.archive(conversationId)
      );
      if (!response.success) {
        throw new ConversationServiceError(response.message || 'Failed to archive conversation');
      }
    } catch (err) {
      this.handleError(err, 'Failed to archive conversation');
    }
  }

  async generateBlogFromConversation(
    conversationId: string,
    additionalContext: string,
    onChunk: (chunk: string) => void,
    onComplete: (fullResponse: string, messageId: string) => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      let fullResponse = '';
      let blogMessageId = '';
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      };
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('ai_social_backend_jwt');
        if (token) headers['Authorization'] = `Bearer ${token}`;
      }
      const response = await fetch(`${apiClient.getBaseURL()}${endpoints.conversations.generateBlog(conversationId)}`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ additional_context: additionalContext })
      });
      if (!response.ok) {
        throw new ConversationServiceError(`HTTP ${response.status}: ${response.statusText}`);
      }
      const reader = response.body?.getReader();
      if (!reader) throw new ConversationServiceError('Failed to get response stream');
      const decoder = new TextDecoder();
      let buffer = '';
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const envelope: SSEEnvelope<SSEChunkPayload> = JSON.parse(line.slice(6));
                if (envelope.success && envelope.data && envelope.data.content) {
                  const chunk = envelope.data;
                  if (chunk.message_id) blogMessageId = chunk.message_id;
                  if (chunk.is_complete) {
                    fullResponse = chunk.content || '';
                    onComplete(fullResponse, blogMessageId);
                    return;
                  } else {
                    onChunk(chunk.content || '');
                  }
                }
              } catch (parseErr) {
                console.error('Error parsing SSE data:', parseErr);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    } catch (err) {
      const msg = getErrorMessage(err);
      if (isAuthErrorMessage(msg)) {
        throw new AuthenticationRequiredError();
      }
      if (msg === 'AbortError') {
        onError('Blog generation was cancelled');
      } else {
        onError(`Blog generation failed: ${msg}`);
      }
    }
  }

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

      eventSource.onmessage = (event: MessageEvent<string>) => {
        try {
          const envelope: SSEEnvelope<SSEChunkPayload> = JSON.parse(event.data);
          if (envelope.success && envelope.data && envelope.data.content) {
            const chunk = envelope.data;
            if (chunk.is_complete) {
              fullResponse = chunk.content || '';
              onComplete(fullResponse);
              eventSource.close();
            } else {
              onChunk(chunk.content || '');
            }
          }
        } catch (parseErr) {
          console.error('Error parsing SSE data:', parseErr);
          onError('Failed to parse streaming response');
        }
      };

      eventSource.onerror = () => {
        onError('Connection error during AI response streaming');
        eventSource.close();
      };

      eventSource.addEventListener('ai_response', (event: MessageEvent<string>) => {
        try {
          const envelope: SSEEnvelope<SSEChunkPayload> = JSON.parse(event.data);
          if (envelope.success && envelope.data?.content) {
            onChunk(envelope.data.content);
          }
        } catch (e) {
          console.error('Error parsing ai_response event:', e);
        }
      });

      eventSource.addEventListener('ai_complete', (event: MessageEvent<string>) => {
        try {
          const envelope: SSEEnvelope<SSEChunkPayload> = JSON.parse(event.data);
          if (envelope.success && envelope.data?.content) {
            fullResponse = envelope.data.content;
            onComplete(fullResponse);
            eventSource.close();
          }
        } catch (e) {
          console.error('Error parsing ai_complete event:', e);
        }
      });

      eventSource.addEventListener('error', (event: MessageEvent<string>) => {
        try {
          const envelope: SSEEnvelope<unknown> = JSON.parse(event.data);
          onError(envelope.message || 'AI streaming error');
          eventSource.close();
        } catch {
          onError('AI streaming encountered an error');
          eventSource.close();
        }
      });
    } catch (err) {
      this.handleError(err, 'Failed to stream AI response');
    }
  }
}

export const conversationService = new ConversationService();