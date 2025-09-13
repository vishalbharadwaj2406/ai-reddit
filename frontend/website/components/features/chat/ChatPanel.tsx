/**
 * ChatPanel Component  
 * Production-grade chat interface using industry-standard glass layout
 */

'use client';

import { Message, ConversationDetail } from '@/lib/services/conversationService';
import { MessageList } from './MessageList';
import { MessageSuggestions } from './MessageSuggestions';
import { InputArea } from '../ui/InputArea';
import { useChatLayout } from '@/lib/layout/hooks';

interface ChatPanelProps {
  // Data
  conversation: ConversationDetail;
  
  // State
  messageText: string;
  onMessageTextChange: (text: string) => void;
  isSending: boolean;
  isAIResponding: boolean;
  isGeneratingBlog: boolean;
  isComposing: boolean;
  onCompositionStart: () => void;
  onCompositionEnd: () => void;
  showJumpToLatest: boolean;
  activeBlogMessageId?: string;
  
  // Actions
  onSendMessage: (text: string) => Promise<void>;
  onGenerateBlog: () => void;
  onWriteBlog: () => void;
  onJumpToLatest: () => void;
  onBlogMessageClick: (message: Message) => void;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  conversation,
  messageText,
  onMessageTextChange,
  isSending,
  isAIResponding,
  isGeneratingBlog,
  isComposing,
  onCompositionStart,
  onCompositionEnd,
  showJumpToLatest,
  activeBlogMessageId,
  onSendMessage,
  onGenerateBlog,
  onWriteBlog,
  onJumpToLatest,
  onBlogMessageClick,
}) => {
  const hasUserMessages = conversation.messages.some(m => m.role === 'user');
  const layout = useChatLayout();

  return (
    <div className={layout.panelClass}>
      {/* Messages Area - Clean with proper clearance */}
      <div className={layout.contentClass} style={layout.contentClearance}>
        <div className="px-4">
          {/* Empty state suggestions */}
          {!hasUserMessages && (
            <div className="mb-6">
              <MessageSuggestions 
                onSuggestionClick={onMessageTextChange}
                onWriteBlog={onWriteBlog}
                isGeneratingBlog={isGeneratingBlog}
              />
            </div>
          )}
          
          <MessageList
            messages={conversation.messages}
            isAIResponding={isAIResponding}
            isGeneratingBlog={isGeneratingBlog}
            activeBlogMessageId={activeBlogMessageId}
            onBlogMessageClick={onBlogMessageClick}
          />
        </div>
      </div>

      {/* Input Area - Clean glass styling */}
      <div 
        className={layout.inputContainer.className} 
        style={layout.inputContainer.style}
      >
        <InputArea
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
  );
};
