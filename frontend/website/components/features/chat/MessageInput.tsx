/**
 * MessageInput Component
 * Production-grade message input with auto-resize and keyboard handling
 */

'use client';

import { useCallback } from 'react';
import TextareaAutosize from 'react-textarea-autosize';
import { Button } from '@/components/design-system/Button';
import { JumpToLatest } from '@/components/features/ui/JumpToLatest';

interface MessageInputProps {
  messageText: string;
  onMessageTextChange: (text: string) => void;
  onSendMessage: (text: string) => Promise<void>;
  onGenerateBlog: () => void;
  isSending: boolean;
  isGeneratingBlog: boolean;
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
  onGenerateBlog,
  isSending,
  isGeneratingBlog,
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
    <div className="w-full max-w-4xl mx-auto">
      {/* Jump to Latest - positioned above input when needed */}
      {showJumpToLatest && hasUserMessages && (
        <JumpToLatest
          onJumpToLatest={onJumpToLatest}
          className="absolute -top-12 right-4"
        />
      )}
      
      {/* Input Container - Clean flex layout */}
      <div className="flex items-end gap-3 w-full">
        {/* Text Input - Flexible width */}
        <div className="flex-1">
          <TextareaAutosize
            className="w-full resize-none text-sm min-h-[56px] max-h-[120px] px-4 py-3 rounded-2xl
                     bg-white/5 backdrop-blur-sm border-2 border-blue-500/20 
                     text-white placeholder-white/50 transition-all duration-200
                     focus:outline-none focus:border-blue-500/40 focus:bg-white/8"
            placeholder="Message..."
            value={messageText}
            onChange={(e) => onMessageTextChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onCompositionStart={onCompositionStart}
            onCompositionEnd={onCompositionEnd}
            minRows={1}
            maxRows={4}
            disabled={isSending || isGeneratingBlog}
          />
        </div>
        
        {/* Buttons - Send first, then Generate Blog */}
        <div className="flex items-end gap-2">
          {/* Send Button - Primary action */}
          <Button
            onClick={handleSend}
            disabled={!messageText.trim() || isSending || isGeneratingBlog}
            variant="primary"
            size="md"
            loading={isSending}
            className="min-w-[80px] h-[56px]"
          >
            {isSending ? 'Sending...' : '→'}
          </Button>
          
          {/* Generate Blog Button - Secondary action */}
          <Button
            onClick={onGenerateBlog}
            disabled={isGeneratingBlog}
            variant="secondary"
            size="md"
            loading={isGeneratingBlog}
            className="min-w-[140px] h-[56px]"
          >
            {isGeneratingBlog ? 'Generating...' : 'Generate Blog'}
          </Button>
        </div>
      </div>
    </div>
  );
};
