/**
 * MessageInput Component
 * Production-grade message input with clean inner styling
 * Works within glass container from layout system for perfect header consistency
 */

'use client';

import { useCallback } from 'react';
import TextareaAutosize from 'react-textarea-autosize';
import { Button } from '@/components/design-system/Button';
import { JumpToLatest } from '@/components/features/ui/JumpToLatest';
import { TEXT_COLORS } from '@/lib/layout/tokens';

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
      
      {/* Inner Content - Clean styling that works within glass container */}
      <div className="flex items-end gap-3 w-full p-4">
        {/* Text Input - Clean inner styling without competing glass effects */}
        <div className="flex-1">
          <TextareaAutosize
            className="w-full resize-none text-sm min-h-[48px] max-h-[120px] px-4 py-3 rounded-xl
                     bg-white/5 border border-white/10 
                     placeholder-white/50 transition-all duration-200
                     focus:outline-none focus:border-blue-400/40 focus:bg-white/8
                     focus:shadow-sm focus:shadow-blue-500/20"
            style={{ 
              resize: 'none',
              color: TEXT_COLORS.SECONDARY
            }}
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
        
        {/* Buttons - Clean styling within glass container */}
        <div className="flex items-end gap-2">
          {/* Send Button - Primary action */}
          <Button
            onClick={handleSend}
            disabled={!messageText.trim() || isSending || isGeneratingBlog}
            variant="primary"
            size="sm"
            loading={isSending}
            className="min-w-[60px] h-[48px] px-4"
          >
            {isSending ? '...' : '→'}
          </Button>
          
          {/* Generate Blog Button - Secondary action */}
          <Button
            onClick={onGenerateBlog}
            disabled={isGeneratingBlog}
            variant="secondary"
            size="sm"
            loading={isGeneratingBlog}
            className="min-w-[120px] h-[48px] px-4 text-xs font-medium"
          >
            {isGeneratingBlog ? 'Generating...' : 'Generate Blog'}
          </Button>
        </div>
      </div>
    </div>
  );
};
