/**
 * MessageInput Component
 * Production-grade message input with auto-resize and keyboard handling
 */

'use client';

import { useCallback } from 'react';
import TextareaAutosize from 'react-textarea-autosize';
import { JumpToLatest } from '@/components/features/ui/JumpToLatest';

interface MessageInputProps {
  messageText: string;
  onMessageTextChange: (text: string) => void;
  onSendMessage: (text: string) => Promise<void>;
  isSending: boolean;
  isComposing: boolean;
  onCompositionStart: () => void;
  onCompositionEnd: () => void;
  showJumpToLatest: boolean;
  onJumpToLatest: () => void;
  hasUserMessages: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  messageText,
  onMessageTextChange,
  onSendMessage,
  isSending,
  isComposing,
  onCompositionStart,
  onCompositionEnd,
  showJumpToLatest,
  onJumpToLatest,
  hasUserMessages,
}) => {
  const handleSend = useCallback(async () => {
    if (!messageText.trim() || isSending) return;
    
    const textToSend = messageText.trim();
    onMessageTextChange(''); // Clear input immediately for better UX
    
    try {
      await onSendMessage(textToSend);
    } catch (error) {
      // Restore text if sending failed
      onMessageTextChange(textToSend);
      console.error('Failed to send message:', error);
    }
  }, [messageText, isSending, onSendMessage, onMessageTextChange]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    // IME-safe send: ignore Enter while composing; allow Shift+Enter for newline
    if (!isComposing && e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [isComposing, handleSend]);

  return (
    <div className="flex items-end gap-3 relative">
      {/* Jump to Latest Button */}
      {showJumpToLatest && hasUserMessages && (
        <JumpToLatest 
          onJumpToLatest={onJumpToLatest}
          className="absolute -top-10 right-0"
        />
      )}
      
      <div className="flex-1">
        <TextareaAutosize
          className="glass-input w-full p-3 resize-none text-sm min-h-[48px] max-h-[160px]"
          placeholder="Message..."
          value={messageText}
          onChange={(e) => onMessageTextChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onCompositionStart={onCompositionStart}
          onCompositionEnd={onCompositionEnd}
          minRows={1}
          maxRows={6}
          disabled={isSending}
        />
      </div>
      
      <button
        onClick={handleSend}
        disabled={!messageText.trim() || isSending}
        className="glass-button-primary px-4 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isSending ? '...' : '→'}
      </button>
    </div>
  );
};
