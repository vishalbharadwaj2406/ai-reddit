/**
 * Production-Grade Conversation Page
 * Clean, professional layout using industry standards
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import SessionGuard from '../../../components/auth/SessionGuard';
import ResizableConversation from '@/components/ResizableConversation';
import { ChatPanel } from '@/components/features/chat/ChatPanel';
import { BlogPanel } from '@/components/features/blog/BlogPanel';
import { UnifiedToast } from '@/components/features/ui/UnifiedToast';
import { ConversationLoading } from '@/components/features/ui/LoadingStates';
import { Button } from '@/components/design-system/Button';
import { useGlassLayout } from '@/hooks/useGlassLayout';
import { useHeaderStore } from '@/lib/stores/headerStore';

// Import all conversation hooks
import {
  useConversationData,
  useMessageHandling,
  useBlogGeneration,
  useToast,
  useErrorHandling,
} from '@/hooks/conversation';

import { postService } from '@/lib/services/postService';
import { Message } from '@/lib/services/conversationService';

function ConversationPageContent() {
  const params = useParams();
  const conversationId = params.id as string;
  
  console.log('🆔 ConversationPage mounted - conversationId:', conversationId);
  
  const layout = useGlassLayout();
  const { setConversationTitle } = useHeaderStore();
  
  // Core conversation data hook
  const {
    conversation,
    loading,
    error: conversationError,
    loadConversation,
    addMessage,
    updateLastMessage,
    clearError: clearConversationError,
  } = useConversationData();
  
  // Message handling hook
  const {
    messageText,
    setMessageText,
    isSending,
    isAIResponding,
    isComposing,
    setIsComposing,
    sendMessage,
    error: messageError,
    clearError: clearMessageError,
  } = useMessageHandling();
  
  // Blog generation hook
  const {
    isGeneratingBlog,
    generateBlogPost,
    error: blogError,
    clearError: clearBlogError,
  } = useBlogGeneration();
  
  // Toast notifications
  const { toast, showToast, hideToast } = useToast();
  
  // Unified error handling
  const { error: unifiedError, handleError, clearError: clearUnifiedError } = useErrorHandling();
  
  // Blog editor state
  const [isEditingBlog, setIsEditingBlog] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  
  // Jump to latest functionality
  const [showJumpToLatest] = useState(false);
  
  // Load conversation on mount
  useEffect(() => {
    if (conversationId) {
      loadConversation(conversationId);
    }
  }, [conversationId, loadConversation]);
  
  // Update header title when conversation loads
  useEffect(() => {
    if (conversation?.title) {
      setConversationTitle(conversation.title);
    }
    return () => {
      setConversationTitle(null);
    };
  }, [conversation?.title, setConversationTitle]);
  
  // Handlers
  const handleSendMessage = useCallback(async () => {
    if (!conversation) return;
    
    try {
      await sendMessage(
        conversationId,
        addMessage,
        updateLastMessage
      );
    } catch (err) {
      handleError(err);
      showToast('error', 'Failed to send message');
    }
  }, [conversation, conversationId, sendMessage, addMessage, updateLastMessage, handleError, showToast]);
  
  const handleGenerateBlog = useCallback(async () => {
    if (!conversation) return;
    
    try {
      const additionalContext = messageText.trim();
      
      await generateBlogPost(
        conversationId,
        additionalContext,
        addMessage,
        updateLastMessage,
        (progress) => {
          console.log('Blog generation progress:', progress);
        }
      );
      
      setMessageText('');
      showToast('success', 'Blog generated successfully! 📝');
      
    } catch (err) {
      handleError(err);
      showToast('error', 'Failed to generate blog');
    }
  }, [conversation, conversationId, messageText, generateBlogPost, addMessage, updateLastMessage, setMessageText, handleError, showToast]);
  
  const handleEditBlog = useCallback(() => {
    setIsEditingBlog(true);
  }, []);
  
  const handleCancelEdit = useCallback(() => {
    setIsEditingBlog(false);
  }, []);
  
  const handleSaveDraft = useCallback((markdown: string) => {
    console.log('Draft saved:', markdown.length, 'characters');
    showToast('info', 'Draft saved locally');
  }, [showToast]);
  
  const handlePublishBlog = useCallback(async (markdown: string) => {
    if (!conversation || !markdown.trim()) return;
    
    try {
      setIsPublishing(true);
      
      const title = conversation.title || 'Blog Post';
      const extractTagsFromContent = (content: string): string[] => {
        const hashtagMatches = content.match(/#(\w+)/g);
        if (hashtagMatches) {
          return hashtagMatches.map(tag => tag.substring(1).toLowerCase());
        }
        return ['blog', 'ai-generated'];
      };
      
      const tags = extractTagsFromContent(markdown);
      const blogMessage = conversation.messages.find(m => m.isBlog && m.content.trim() === markdown.trim());
      const messageId = blogMessage?.messageId;
      
      console.log('Publishing blog with messageId:', messageId, 'tags:', tags);
      
      const publishedPost = await postService.publishBlogAsPost(
        markdown,
        title,
        messageId,
        tags
      );
      
      console.log('Blog published as post:', publishedPost.post_id);
      
      setIsEditingBlog(false);
      setIsPublishing(false);
      
      showToast('success', 'Blog published successfully! 🎉');
      
    } catch (error) {
      console.error('Failed to publish blog:', error);
      setIsPublishing(false);
      handleError(error);
      showToast('error', 'Failed to publish blog');
    }
  }, [conversation, handleError, showToast]);
  
  // Blog panel state  
  const [activeBlogMessage, setActiveBlogMessage] = useState<Message | null>(null);
  const [showBlogPanel, setShowBlogPanel] = useState(false);
  
  // Blog messages from conversation
  const blogMessages = conversation?.messages.filter((m: Message) => m.isBlog === true) || [];
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
  
  // Handlers for blog messages
  const handleBlogMessageClick = useCallback((message: Message) => {
    setActiveBlogMessage(message);
    setShowBlogPanel(true);
  }, []);
  
  const handleCloseBlogPanel = useCallback(() => {
    setShowBlogPanel(false);
    setActiveBlogMessage(null);
  }, []);

  const handleWriteBlog = useCallback(() => {
    console.log('Write blog functionality - opening empty editor');
    showToast('info', 'Empty blog editor functionality coming soon!');
  }, [showToast]);

  const handleJumpToLatest = useCallback(() => {
    console.log('Jump to latest triggered');
  }, []);
  
  // Show loading state
  if (loading) {
    return (
      <div className={layout.pageClass}>
        <ConversationLoading />
      </div>
    );
  }
  
  // Show error state
  if (conversationError || !conversation) {
    return (
      <div className={layout.pageClass}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-red-500 mb-4">{conversationError || 'Conversation not found'}</p>
            <Link href="/conversations">
              <Button variant="secondary" size="md">
                ← Back to Conversations
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }
  
  // Display unified error in toast if any hook has an error
  const activeError = unifiedError || messageError || blogError || conversationError;
  
  return (
    <div className={layout.pageClass}>
      {/* Toast Notifications */}
      <UnifiedToast 
        toast={activeError ? { type: 'error', message: activeError } : toast}
        onDismiss={activeError ? () => {
          clearUnifiedError();
          clearMessageError();
          clearBlogError();
          clearConversationError();
        } : hideToast}
      />

      {/* Main Content - Clean Resizable Layout */}
      <ResizableConversation 
        showBlogPanel={showBlogPanel}
        onBlogPanelToggle={setShowBlogPanel}
      >
        {/* Chat Panel */}
        <ChatPanel
          conversation={conversation}
          messageText={messageText}
          onMessageTextChange={setMessageText}
          isSending={isSending}
          isAIResponding={isAIResponding}
          isGeneratingBlog={isGeneratingBlog}
          isComposing={isComposing}
          onCompositionStart={() => setIsComposing(true)}
          onCompositionEnd={() => setIsComposing(false)}
          showJumpToLatest={showJumpToLatest}
          activeBlogMessageId={activeBlogMessage?.messageId}
          onSendMessage={handleSendMessage}
          onGenerateBlog={handleGenerateBlog}
          onWriteBlog={handleWriteBlog}
          onJumpToLatest={handleJumpToLatest}
          onBlogMessageClick={handleBlogMessageClick}
        />

        {/* Blog Panel */}
        <BlogPanel
          activeBlogMessage={activeBlogMessage}
          isEditingBlog={isEditingBlog}
          isPublishing={isPublishing}
          onEditBlog={handleEditBlog}
          onCancelEdit={handleCancelEdit}
          onSaveDraft={handleSaveDraft}
          onPublishBlog={handlePublishBlog}
          onClose={handleCloseBlogPanel}
        />
      </ResizableConversation>
    </div>
  );
}

// Default export required for Next.js App Router
export default function ConversationPage() {
  return (
    <SessionGuard>
      <ConversationPageContent />
    </SessionGuard>
  );
}
