/**
 * ChatPanel Component  
 * Production-grade chat interface using industry-standard glass layout
 */

'use client';

import { Message, ConversationDetail } from '@/lib/services/conversationService';
import { MessageList } from './MessageList';
import { InputArea } from '../ui/InputArea';
import { useGlassLayout } from '@/hooks/useGlassLayout';
import { LAYOUT_TOKENS } from '@/lib/layout/tokens';

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
  const layout = useGlassLayout();

  return (
    <div className={layout.panelClass}>
      {/* Messages Area - Industry standard: content with glass clearance */}
      <div className={layout.contentClass} style={layout.contentClearance}>
        <div className="px-4">
          <MessageList
            messages={conversation.messages}
            isAIResponding={isAIResponding}
            isGeneratingBlog={isGeneratingBlog}
            activeBlogMessageId={activeBlogMessageId}
            onBlogMessageClick={onBlogMessageClick}
          />
        </div>
      </div>

      {/* Input Area - Fixed with header-matching glass styling */}
      <div 
        className={layout.inputClass} 
        style={{
          ...layout.headerGlassStyle,
          minHeight: `${LAYOUT_TOKENS.INPUT_MIN_HEIGHT}px`,
          maxHeight: `${LAYOUT_TOKENS.INPUT_MAX_HEIGHT}px`,
        }}
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
          onWriteBlog={onWriteBlog}
        />
      </div>
    </div>
  );
};
