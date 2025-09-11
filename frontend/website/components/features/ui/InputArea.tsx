/**
 * InputArea Component
 * Production-grade message input area with suggestions and proper positioning
 */

'use client';

import { MessageInput } from '../chat/MessageInput';
import { MessageSuggestions } from '../chat/MessageSuggestions';
import { JumpToLatest } from './JumpToLatest';

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
  
  // Blog handlers
  onGenerateBlog: () => void;
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
  onGenerateBlog,
  onWriteBlog,
}) => {
  return (
    <div className="bg-black/90 backdrop-blur-sm">
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
            onGenerateBlog={onGenerateBlog}
            isSending={isSending}
            isGeneratingBlog={isGeneratingBlog}
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
