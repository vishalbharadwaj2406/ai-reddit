/**
 * Production-Grade Conversation Layout
 * Clean, professional 2-panel system using pure CSS Grid
 */

'use client';

import React, { useState, useEffect } from 'react';
import { ChatPanel } from '../chat/ChatPanel';
import { BlogPanel } from '../blog/BlogPanel';
import { Message, ConversationDetail } from '@/lib/services/conversationService';
import { useSimpleLayout } from '@/hooks/useGlassScroll';

interface ConversationLayoutProps {
  conversation: ConversationDetail;
  onSendMessage: (text: string) => Promise<void>;
  onGenerateBlog: () => Promise<void>;
  onEditBlog: () => void;
  onCancelEdit: () => void;
  onSaveDraft: (markdown: string) => void;
  onPublishBlog: (markdown: string) => Promise<void>;
  onWriteBlog: () => void;
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
  const blogMessages = conversation.messages.filter((m: Message) => m.isBlog === true);
  const hasBlogMessages = blogMessages.length > 0;
  const mostRecentBlogMessage = hasBlogMessages ? blogMessages[blogMessages.length - 1] : null;
  
  // Auto-open blog panel when blog generation starts or when new blog is created
  useEffect(() => {
    if (mostRecentBlogMessage) {
      setActiveBlogMessage(mostRecentBlogMessage);
      setShowBlogPanel(true);
    }
  }, [mostRecentBlogMessage]);
  
  // Auto-open blog panel when blog generation starts
  useEffect(() => {
    if (isGeneratingBlog && !showBlogPanel) {
      setShowBlogPanel(true);
    }
  }, [isGeneratingBlog, showBlogPanel]);
  
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

  const layout = useSimpleLayout();

  // Dynamic grid template based on blog panel visibility
  // Mobile-first: stack panels on small screens
  const gridTemplate = showBlogPanel ? '1fr 1fr' : '1fr';

  return (
    <div 
      {...layout.conversationContainerProps}
      style={{
        ...layout.conversationContainerProps.style,
        gridTemplateColumns: gridTemplate,
      }}
      className={`${layout.conversationContainerProps.className} 
        max-md:grid-rows-2 max-md:grid-cols-1 max-md:gap-1`}
    >
      {/* Chat Panel - Always visible */}
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
      />

      {/* Blog Panel - Conditional rendering with placeholder */}
      {showBlogPanel && (
        activeBlogMessage ? (
          <BlogPanel
            activeBlogMessage={activeBlogMessage}
            isEditingBlog={isEditingBlog}
            isPublishing={isPublishing}
            onEditBlog={onEditBlog}
            onCancelEdit={onCancelEdit}
            onSaveDraft={onSaveDraft}
            onPublishBlog={onPublishBlog}
            onClose={handleCloseBlogPanel}
          />
        ) : (
          // Placeholder for blog panel when generating
          <div {...layout.blogPanelProps}>
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-400">
                {isGeneratingBlog ? (
                  <>
                    <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent mx-auto mb-4"></div>
                    <p>Generating your blog post...</p>
                  </>
                ) : (
                  <p>Generate a blog post to see it here</p>
                )}
              </div>
            </div>
          </div>
        )
      )}
    </div>
  );
};


