/**
 * Conversation Data Management Hook
 * Production-grade hook for managing conversation state and data fetching
 */

import { useState, useCallback, useEffect } from 'react';
import { 
  conversationService, 
  ConversationDetail, 
  Message,
  AuthenticationRequiredError, 
  ConversationServiceError 
} from '@/lib/services/conversationService';
import { useErrorHandling } from './useErrorHandling';

export interface UseConversationDataReturn {
  // Data state
  conversation: ConversationDetail | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  loadConversation: (conversationId: string) => Promise<void>;
  addMessage: (message: Message) => void;
  updateLastMessage: (content: string) => void;
  clearError: () => void;
  
  // Computed properties
  isForked: boolean;
  hasUserMessages: boolean;
  blogMessages: Message[];
  hasBlogMessages: boolean;
  mostRecentBlogMessage: Message | null;
}

/**
 * Hook for managing conversation data, loading states, and message updates
 */
export const useConversationData = (): UseConversationDataReturn => {
  const [conversation, setConversation] = useState<ConversationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const { error, handleError, clearError } = useErrorHandling();

  const loadConversation = useCallback(async (conversationId: string) => {
    console.log('🔄 Loading conversation:', conversationId);
    
    try {
      setLoading(true);
      clearError();
      
      console.log('📡 Calling conversationService.getConversation...');
      const conversationData = await conversationService.getConversation(conversationId);
      console.log('✅ Conversation loaded:', conversationData);
      
      setConversation(conversationData);
    } catch (err) {
      console.error('❌ Conversation loading error:', err);
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, [handleError, clearError]);

  const addMessage = useCallback((newMessage: Message) => {
    setConversation(prev => {
      if (!prev) return null;
      
      return {
        ...prev,
        messages: [...prev.messages, newMessage]
      };
    });
  }, []);

  const updateLastMessage = useCallback((content: string) => {
    setConversation(prev => {
      if (!prev) return null;
      
      const messages = [...prev.messages];
      const lastMessage = messages[messages.length - 1];
      
      if (lastMessage && (lastMessage.role === 'assistant' || lastMessage.isBlog)) {
        messages[messages.length - 1] = {
          ...lastMessage,
          content: content
        };
      }
      
      return {
        ...prev,
        messages: messages
      };
    });
  }, []);

  // Computed properties using useMemo for performance
  const isForked = Boolean(conversation?.forked_from);
  
  const hasUserMessages = conversation?.messages.some(m => m.role === 'user') ?? false;
  
  const blogMessages = conversation?.messages.filter(m => m.isBlog === true) ?? [];
  
  const hasBlogMessages = blogMessages.length > 0;
  
  const mostRecentBlogMessage = hasBlogMessages ? blogMessages[blogMessages.length - 1] : null;

  return {
    // Data state
    conversation,
    loading,
    error,
    
    // Actions
    loadConversation,
    addMessage,
    updateLastMessage,
    clearError,
    
    // Computed properties
    isForked,
    hasUserMessages,
    blogMessages,
    hasBlogMessages,
    mostRecentBlogMessage,
  };
};
