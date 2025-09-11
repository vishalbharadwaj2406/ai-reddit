/**
 * ConversationLayout Component
 * Clean 2-panel layout (Claude-style) with resizable panels
 */

'use client';

import { useState, useEffect } from 'react';
import { ChatPanel } from '../chat/ChatPanel';
import { BlogPanel } from '../blog/BlogPanel';
import { ResizablePanels } from './ResizablePanels';
import { Message, ConversationDetail } from '@/lib/services/conversationService';

interface ConversationLayoutProps {
  // Data
  conversation: ConversationDetail;
  
  // Chat handlers
  onSendMessage: (text: string) => Promise<void>;
  onGenerateBlog: () => Promise<void>;
  
  // Blog handlers
  onEditBlog: () => void;
  onCancelEdit: () => void;
  onSaveDraft: (markdown: string) => void;
  onPublishBlog: (markdown: string) => Promise<void>;
  onWriteBlog: () => void; // For empty blog editor
  
  // States
  messageText: string;
  onMessageTextChange: (text: string) => void;
  isSending: boolean;
  isAIResponding: boolean;
  isGeneratingBlog: boolean;
  isComposing: boolean;
  onCompositionStart: () => void;
  onCompositionEnd: () => void;
  showJumpToLatest: boolean;
  onJumpToLatest: () => void;
  
  // Blog editor states
  isEditingBlog: boolean;
  isPublishing: boolean;
}

export const ConversationLayout: React.FC<ConversationLayoutProps> = ({
  conversation,
  onSendMessage,
  onGenerateBlog,
  onEditBlog,
  onCancelEdit,
  onSaveDraft,
  onPublishBlog,
  onWriteBlog,
  messageText,
  onMessageTextChange,
  isSending,
  isAIResponding,
  isGeneratingBlog,
  isComposing,
  onCompositionStart,
  onCompositionEnd,
  showJumpToLatest,
  onJumpToLatest,
  isEditingBlog,
  isPublishing,
}) => {
  // Blog panel state  
  const [activeBlogMessage, setActiveBlogMessage] = useState<Message | null>(null);
  const [showBlogPanel, setShowBlogPanel] = useState(false);
  
  // Blog messages from conversation
  const blogMessages = conversation.messages.filter(m => m.isBlog === true);
  const hasBlogMessages = blogMessages.length > 0;
  const mostRecentBlogMessage = hasBlogMessages ? blogMessages[blogMessages.length - 1] : null;
  
  // Auto-open blog panel when blog generation starts or when new blog is created
  useEffect(() => {
    if (mostRecentBlogMessage) {
      setActiveBlogMessage(mostRecentBlogMessage);
      setShowBlogPanel(true);
    }
  }, [mostRecentBlogMessage]);
  
  // Keep panel open until manually closed (per requirement B)
  // Don't auto-close when generation finishes
  
  // Handlers
  const handleBlogMessageClick = (message: Message) => {
    setActiveBlogMessage(message);
    setShowBlogPanel(true);
  };
  
  const handleCloseBlogPanel = () => {
    setShowBlogPanel(false);
    setActiveBlogMessage(null);
  };

  return (
    <div className="h-full bg-black">
      <ResizablePanels 
        showBlogPanel={showBlogPanel}
        onCloseBlogPanel={handleCloseBlogPanel}
      >
        {/* Chat Panel */}
        <ChatPanel
          conversation={conversation}
          messageText={messageText}
          onMessageTextChange={onMessageTextChange}
          isSending={isSending}
          isAIResponding={isAIResponding}
          isGeneratingBlog={isGeneratingBlog}
          isComposing={isComposing}
          onCompositionStart={onCompositionStart}
          onCompositionEnd={onCompositionEnd}
          showJumpToLatest={showJumpToLatest}
          activeBlogMessageId={activeBlogMessage?.messageId}
          onSendMessage={onSendMessage}
          onGenerateBlog={onGenerateBlog}
          onWriteBlog={onWriteBlog}
          onJumpToLatest={onJumpToLatest}
          onBlogMessageClick={handleBlogMessageClick}
          onEditBlog={onEditBlog}
        />

        {/* Blog Panel */}
        <BlogPanel
          activeBlogMessage={activeBlogMessage}
          isEditingBlog={isEditingBlog}
          isPublishing={isPublishing}
          onEditBlog={onEditBlog}
          onCancelEdit={onCancelEdit}
          onSaveDraft={onSaveDraft}
          onPublishBlog={onPublishBlog}
        />
      </ResizablePanels>
    </div>
  );
};


