/**
 * Refactored Conversation Page
 * Production-grade conversation interface using component architecture
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import SessionGuard from '../../../components/auth/SessionGuard';
import { ConversationLayout } from '@/components/features/layout/ConversationLayout';
import { UnifiedToast } from '@/components/features/ui/UnifiedToast';
import { ConversationLoading } from '@/components/features/ui/LoadingStates';
import { usePageLayout } from '@/hooks/useViewportLayout';
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

function ConversationPageContent() {
  const params = useParams();
  const conversationId = params.id as string;
  
  console.log('🆔 ConversationPage mounted - conversationId:', conversationId);
  
  const layout = usePageLayout();
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
    isForked,
    hasUserMessages,
    blogMessages,
    hasBlogMessages,
    mostRecentBlogMessage,
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
    blogGenerationProgress,
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
  const [showJumpToLatest, setShowJumpToLatest] = useState(false);
  
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
  
  // Scroll detection for Jump to Latest functionality would go here
  // (Implementation depends on refs from child components)
  
  // Handlers
  const handleSendMessage = useCallback(async (text: string) => {
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
      // Use current message text as additional context
      const additionalContext = messageText.trim();
      
      await generateBlogPost(
        conversationId,
        additionalContext,
        addMessage,
        updateLastMessage,
        (progress) => {
          // Optional progress updates could be used for UI feedback
          console.log('Blog generation progress:', progress);
        }
      );
      
      // Clear input since we used it for context
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
    // Auto-save functionality (could be enhanced with local storage)
    console.log('Draft saved:', markdown.length, 'characters');
    showToast('info', 'Draft saved locally');
  }, [showToast]);
  
  const handlePublishBlog = useCallback(async (markdown: string) => {
    if (!conversation || !markdown.trim()) return;
    
    try {
      setIsPublishing(true);
      
      // Generate title from content or use conversation title
      const title = conversation.title || 'Blog Post';
      
      // Extract simple tags from content
      const extractTagsFromContent = (content: string): string[] => {
        const hashtagMatches = content.match(/#(\w+)/g);
        if (hashtagMatches) {
          return hashtagMatches.map(tag => tag.substring(1).toLowerCase());
        }
        return ['blog', 'ai-generated'];
      };
      
      const tags = extractTagsFromContent(markdown);
      
      // Find the blog message to link the post properly
      const blogMessage = conversation.messages.find(m => m.isBlog && m.content.trim() === markdown.trim());
      const messageId = blogMessage?.messageId;
      
      console.log('Publishing blog with messageId:', messageId, 'tags:', tags);
      
      // Publish the blog as a post
      const publishedPost = await postService.publishBlogAsPost(
        markdown,
        title,
        messageId,
        tags
      );
      
      console.log('Blog published as post:', publishedPost.post_id);
      
      // Close editor and show success
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
  
  const handleWriteBlog = useCallback(() => {
    // This should open an empty blog editor
    // For now, we'll trigger the editing state with empty content
    console.log('Write blog functionality - opening empty editor');
    showToast('info', 'Empty blog editor functionality coming soon!');
  }, [showToast]);
  
  const handleJumpToLatest = useCallback(() => {
    // This will be handled by the ChatPanel component
    console.log('Jump to latest triggered');
  }, []);
  
  // Show loading state
  if (loading) {
    return (
      <div {...layout.containerProps}>
        <ConversationLoading />
      </div>
    );
  }
  
  // Show error state
  if (conversationError || !conversation) {
    return (
      <div {...layout.containerProps}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-red-500 mb-4">{conversationError || 'Conversation not found'}</p>
            <Link href="/conversations">
              <button className="glass-button-secondary px-4 py-2">
                ← Back to Conversations
              </button>
            </Link>
          </div>
        </div>
      </div>
    );
  }
  
  // Display unified error in toast if any hook has an error
  const activeError = unifiedError || messageError || blogError || conversationError;
  
  return (
    <>
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
      
      {/* Main Layout */}
      <ConversationLayout
        conversation={conversation}
        onSendMessage={handleSendMessage}
        onGenerateBlog={handleGenerateBlog}
        onEditBlog={handleEditBlog}
        onCancelEdit={handleCancelEdit}
        onSaveDraft={handleSaveDraft}
        onPublishBlog={handlePublishBlog}
        onWriteBlog={handleWriteBlog}
        messageText={messageText}
        onMessageTextChange={setMessageText}
        isSending={isSending}
        isAIResponding={isAIResponding}
        isGeneratingBlog={isGeneratingBlog}
        isComposing={isComposing}
        onCompositionStart={() => setIsComposing(true)}
        onCompositionEnd={() => setIsComposing(false)}
        showJumpToLatest={showJumpToLatest}
        onJumpToLatest={handleJumpToLatest}
        isEditingBlog={isEditingBlog}
        isPublishing={isPublishing}
      />
    </>
  );
}

export default function ConversationPage() {
  return (
    <SessionGuard>
      <ConversationPageContent />
    </SessionGuard>
  );
}
