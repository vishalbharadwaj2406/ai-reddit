/**
 * InputArea Component
 * Clean input area that lives within chat panel only
 */

'use client';

import { MessageInput } from '../chat/MessageInput';
import { MessageSuggestions } from '../chat/MessageSuggestions';

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
    <div className="w-full space-y-4">
      {/* Suggestions for empty state - Better integrated spacing */}
      {!hasUserMessages && (
        <div className="px-4 pt-4">
          <MessageSuggestions 
            onSuggestionClick={onMessageTextChange}
            onWriteBlog={onWriteBlog}
            isGeneratingBlog={isGeneratingBlog}
          />
        </div>
      )}

      {/* Main input component - Clean integration */}
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
  );
};
