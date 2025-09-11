/**
 * ChatPanel Component  
 * Clean chat interface for the left panel
 */

'use client';

import { Message, ConversationDetail } from '@/lib/services/conversationService';
import { MessageList } from './MessageList';
import { InputArea } from '../ui/InputArea';
import { usePanelGlassScroll } from '@/hooks/useGlassScroll';

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
  onEditBlog?: () => void;
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
  onEditBlog,
}) => {
  const hasUserMessages = conversation.messages.some(m => m.role === 'user');
  const glassScroll = usePanelGlassScroll();

  return (
    <div {...glassScroll.containerProps}>
      {/* Messages Area - Glass Scroll Content */}
      <div {...glassScroll.contentProps}>
        <div className="px-4 space-y-4">
          <MessageList
            messages={conversation.messages}
            isAIResponding={isAIResponding}
            isGeneratingBlog={isGeneratingBlog}
            activeBlogMessageId={activeBlogMessageId}
            onBlogMessageClick={onBlogMessageClick}
            onEditBlog={onEditBlog}
          />
        </div>
      </div>

      {/* Input Area - Fixed at bottom with glass effect */}
      <div 
        className="fixed bottom-0 left-0 right-0 z-10"
        style={{
          left: 'var(--sidebar-current)',
          background: 'rgba(0, 0, 0, 0.6)',
          backdropFilter: 'blur(20px) saturate(150%)',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
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
