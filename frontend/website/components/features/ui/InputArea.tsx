/**
 * InputArea Component
 * Production-grade message input area with suggestions and proper positioning
 */

'use client';

import { MessageInput } from '../chat/MessageInput';
import { MessageSuggestions } from '../chat/MessageSuggestions';
import { JumpToLatest } from './JumpToLatest';
import { LAYOUT_CONSTANTS } from '@/hooks/useViewportLayout';
import { useSidebarStore } from '@/lib/stores/sidebarStore';

interface InputAreaProps {
  // Message state
  messageText: string;
  onMessageTextChange: (text: string) => void;
  
  // Message handlers
  onSendMessage: (text: string) => Promise<void>;
  isSending: boolean;
  isComposing: boolean;
  onCompositionStart: () => void;
  onCompositionEnd: () => void;
  
  // Jump to latest
  showJumpToLatest: boolean;
  onJumpToLatest: () => void;
  
  // State conditions
  hasUserMessages: boolean;
  isGeneratingBlog: boolean;
  
  // Blog handler
  onWriteBlog: () => void;
}

export const InputArea: React.FC<InputAreaProps> = ({
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
  isGeneratingBlog,
  onWriteBlog,
}) => {
  const { isExpanded: sidebarExpanded } = useSidebarStore();

  return (
    <div 
      className="fixed right-0 border-t border-gray-700/30 bg-black/60 backdrop-blur-md z-50"
      style={{ 
        left: sidebarExpanded ? `${LAYOUT_CONSTANTS.SIDEBAR_EXPANDED}px` : `${LAYOUT_CONSTANTS.SIDEBAR_COLLAPSED}px`,
        bottom: '16px',
        minHeight: `${LAYOUT_CONSTANTS.INPUT_HEIGHT}px`,
        maxHeight: '200px',
        transition: 'left 0.3s ease'
      }}
    >
      <div className="px-4 py-3">
        <div className="max-w-4xl mx-auto">
          
          {/* Suggestions for empty state */}
          {!hasUserMessages && (
            <MessageSuggestions 
              onSuggestionClick={onMessageTextChange}
              onWriteBlog={onWriteBlog}
              isGeneratingBlog={isGeneratingBlog}
            />
          )}

          <MessageInput
            messageText={messageText}
            onMessageTextChange={onMessageTextChange}
            onSendMessage={onSendMessage}
            isSending={isSending}
            isComposing={isComposing}
            onCompositionStart={onCompositionStart}
            onCompositionEnd={onCompositionEnd}
            showJumpToLatest={showJumpToLatest}
            onJumpToLatest={onJumpToLatest}
            hasUserMessages={hasUserMessages}
          />
        </div>
      </div>
    </div>
  );
};
