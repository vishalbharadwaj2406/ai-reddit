/**
 * ChatPanel Component  
 * Clean chat interface using professional layout patterns
 */

'use client';

import { Message, ConversationDetail } from '@/lib/services/conversationService';
import { MessageList } from './MessageList';
import { InputArea } from '../ui/InputArea';
import { useSimpleLayout } from '@/hooks/useGlassScroll';

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
  const layout = useSimpleLayout();

  return (
    <div {...layout.chatPanelProps}>
      {/* Messages Area - Scrollable with proper height */}
      <div {...layout.messagesAreaProps}>
        <MessageList
          messages={conversation.messages}
          isAIResponding={isAIResponding}
          isGeneratingBlog={isGeneratingBlog}
          activeBlogMessageId={activeBlogMessageId}
          onBlogMessageClick={onBlogMessageClick}
        />
      </div>

      {/* Input Area - Fixed at bottom of chat panel only */}
      <div {...layout.inputAreaProps}>
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
