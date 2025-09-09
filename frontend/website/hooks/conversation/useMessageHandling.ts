/**
 * Message Handling Hook
 * Production-grade hook for sending messages and handling AI streaming responses
 */

import { useState, useCallback } from 'react';
import { conversationService, Message, SendMessageRequest } from '@/lib/services/conversationService';
import { useErrorHandling } from './useErrorHandling';

export interface UseMessageHandlingReturn {
  // State
  messageText: string;
  isSending: boolean;
  isAIResponding: boolean;
  isComposing: boolean;
  
  // Actions
  setMessageText: (text: string) => void;
  setIsComposing: (composing: boolean) => void;
  sendMessage: (
    conversationId: string,
    onMessageAdded: (message: Message) => void,
    onMessageUpdated: (content: string) => void
  ) => Promise<void>;
  
  // Error handling
  error: string | null;
  clearError: () => void;
}

/**
 * Hook for managing message input, sending, and AI streaming responses
 */
export const useMessageHandling = (): UseMessageHandlingReturn => {
  const [messageText, setMessageText] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isAIResponding, setIsAIResponding] = useState(false);
  const [isComposing, setIsComposing] = useState(false);
  const { error, handleError, clearError } = useErrorHandling();

  const sendMessage = useCallback(async (
    conversationId: string,
    onMessageAdded: (message: Message) => void,
    onMessageUpdated: (content: string) => void
  ) => {
    if (!messageText.trim() || isSending) return;

    try {
      setIsSending(true);
      clearError();
      
      // Create optimistic user message for immediate display
      const tempUserMessage: Message = {
        messageId: `temp-${Date.now()}`,
        role: 'user',
        content: messageText.trim(),
        isBlog: false,
        createdAt: new Date().toISOString()
      };

      // Add user message to UI immediately  
      onMessageAdded(tempUserMessage);
      
      // Clear input immediately for better UX
      const userMessageText = messageText.trim();
      setMessageText('');
      
      // Send the user message to backend
      const sentMessage = await conversationService.sendMessage(conversationId, {
        content: userMessageText
      });

      // Get the real message ID from the sent message
      const messageId = sentMessage.messageId;
      
      // Add placeholder AI message immediately
      const aiMessage: Message = {
        messageId: `ai-${Date.now()}`,
        role: 'assistant',
        content: '', // Will be updated as streaming progresses
        isBlog: false,
        createdAt: new Date().toISOString(),
      };
      
      onMessageAdded(aiMessage);
      
      // Start AI streaming response
      setIsAIResponding(true);
      
      await conversationService.streamAIResponse(
        conversationId,
        messageId,
        // onChunk: Update the AI message content in real-time
        (chunk: string) => {
          onMessageUpdated(chunk);
        },
        // onComplete: Just clear streaming state - message already in conversation
        (fullResponse: string) => {
          setIsAIResponding(false);
          onMessageUpdated(fullResponse); // Ensure final content is set
        },
        // onError: Handle streaming errors
        (errorMessage: string) => {
          setIsAIResponding(false);
          console.error('AI streaming error:', errorMessage);
          onMessageUpdated('Sorry, I encountered an error. Please try again.');
          handleError(new Error(errorMessage));
        }
      );
      
    } catch (err) {
      console.error('Failed to send message:', err);
      handleError(err);
      setIsAIResponding(false);
    } finally {
      setIsSending(false);
    }
  }, [messageText, isSending, handleError, clearError]);

  return {
    // State
    messageText,
    isSending,
    isAIResponding,
    isComposing,
    
    // Actions
    setMessageText,
    setIsComposing,
    sendMessage,
    
    // Error handling
    error,
    clearError,
  };
};
