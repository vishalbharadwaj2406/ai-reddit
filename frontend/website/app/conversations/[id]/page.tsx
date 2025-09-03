'use client';

import SessionGuard from '../../../components/auth/SessionGuard';
import { useState, useEffect, useRef, useCallback } from 'react';
import TextareaAutosize from 'react-textarea-autosize';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { conversationService, ConversationDetail, Message, AuthenticationRequiredError, ConversationServiceError } from '../../../lib/services/conversationService';
import { postService } from '../../../lib/services/postService';
import { BlogEditor } from '../../../components/BlogEditor';
import MarkdownRenderer from '../../../components/Markdown/MarkdownRenderer';
import { usePageLayout, LAYOUT_CONSTANTS, getGlassScrollPadding } from '../../../hooks/useViewportLayout';
import { useHeaderStore } from '../../../lib/stores/headerStore';
import { useSidebarStore } from '../../../lib/stores/sidebarStore';
import { copyText } from '../../../lib/utils/copy';
import { markdownToPlain } from '../../../lib/utils/markdown';

const getErrorMessage = (err: unknown): string => {
  // Production-grade error message extraction
  
  // Handle PostServiceError (our custom errors)
  if (err && typeof err === 'object' && 'name' in err && (err as any).name === 'PostServiceError') {
    return (err as Error).message;
  }
  
  // Handle ApiError (from API client)
  if (err && typeof err === 'object' && 'name' in err && (err as any).name === 'ApiError') {
    return (err as Error).message;
  }
  
  // Handle standard Error instances
  if (err instanceof Error) {
    return err.message;
  }
  
  // Handle string errors
  if (typeof err === 'string') {
    return err;
  }
  
  // Handle structured error objects
  if (err && typeof err === 'object') {
    const errorObj = err as any;
    
    // Try various error message locations
    if (errorObj.message) return errorObj.message;
    if (errorObj.detail?.message) return errorObj.detail.message;
    if (errorObj.detail && typeof errorObj.detail === 'string') return errorObj.detail;
    if (errorObj.error) return errorObj.error;
    
    // For validation errors array
    if (Array.isArray(errorObj.detail) && errorObj.detail.length > 0) {
      const firstError = errorObj.detail[0];
      if (firstError?.msg) {
        return firstError.msg;
      }
    }
    
    // Last resort: stringify the object
    try {
      return JSON.stringify(errorObj);
    } catch {
      return 'Invalid error object';
    }
  }
  
  // Ultimate fallback
  return 'An unknown error occurred';
};

function ConversationPageContent() {
  const params = useParams();
  const conversationId = params.id as string;
  
  // Debug logging
  console.log('🆔 ConversationPage mounted - params:', params, 'conversationId:', conversationId);
  
  // Layout management hook for proper height calculations
  const layout = usePageLayout();
  
  // Header title management
  const { setConversationTitle } = useHeaderStore();
  
  // Sidebar state for responsive layout
  const { isExpanded: sidebarExpanded } = useSidebarStore();
  
  // Glass scroll padding calculation - no hardcoding
  const glassPadding = getGlassScrollPadding();
  
  // Panel visibility state
  const [showOriginalBlog, setShowOriginalBlog] = useState(false);
  const [showGeneratedBlog, setShowGeneratedBlog] = useState(false);
  
  // ✨ NEW: Blog editor state
  const [isEditingBlog, setIsEditingBlog] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  
  // ✨ NEW: Toast notification state
  const [toast, setToast] = useState<{
    type: 'success' | 'error';
    message: string;
  } | null>(null);

  // Auto-hide toast after 5 seconds
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message });
  };
  
  // Chat state
  const [messageText, setMessageText] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isAIResponding, setIsAIResponding] = useState(false);
  const [isComposing, setIsComposing] = useState(false);
  
  // Blog generation state
  const [isGeneratingBlog, setIsGeneratingBlog] = useState(false);
  
  // Jump to latest functionality
  const [showJumpToLatest, setShowJumpToLatest] = useState(false);
  
  // Real conversation data state
  const [conversation, setConversation] = useState<ConversationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Auto-scroll ref for messages
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Panel scroll refs for independent scrolling
  const leftPanelRef = useRef<HTMLDivElement>(null);
  const chatPanelRef = useRef<HTMLDivElement>(null);
  const rightPanelRef = useRef<HTMLDivElement>(null);

  // Declare the loader first so effects can reference it safely
  const loadConversation = useCallback(async () => {
    console.log('🔄 Loading conversation:', conversationId);
    try {
      setLoading(true);
      setError(null);
      
      console.log('📡 Calling conversationService.getConversation...');
      const conversationData = await conversationService.getConversation(conversationId);
      console.log('✅ Conversation loaded:', conversationData);
      setConversation(conversationData);
      
    } catch (err) {
      console.error('❌ Conversation loading error:', err);
      if (err instanceof AuthenticationRequiredError) {
        setError('Please sign in to view this conversation');
      } else if (err instanceof ConversationServiceError) {
        setError(err.message);
      } else {
        setError('Failed to load conversation');
      }
    } finally {
      setLoading(false);
    }
  }, [conversationId]);

  // Auto-scroll to bottom when messages change or AI is typing - only for chat panel
  useEffect(() => {
    if (chatPanelRef.current && messagesEndRef.current) {
      // Use a small delay to ensure DOM updates are complete
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
      }, 100);
    }
  }, [conversation?.messages, isAIResponding, isGeneratingBlog]);

  // Set layout CSS custom properties for global use
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--header-height', `${LAYOUT_CONSTANTS.HEADER_HEIGHT}px`);
    root.style.setProperty('--input-height', `${LAYOUT_CONSTANTS.INPUT_HEIGHT}px`);
    root.style.setProperty('--sidebar-collapsed', `${LAYOUT_CONSTANTS.SIDEBAR_COLLAPSED}px`);
    root.style.setProperty('--sidebar-expanded', `${LAYOUT_CONSTANTS.SIDEBAR_EXPANDED}px`);
    root.style.setProperty('--sidebar-current', sidebarExpanded ? `${LAYOUT_CONSTANTS.SIDEBAR_EXPANDED}px` : `${LAYOUT_CONSTANTS.SIDEBAR_COLLAPSED}px`);
    // Glass scroll padding properties for other components
    root.style.setProperty('--glass-safe-zone', `${LAYOUT_CONSTANTS.GLASS_SAFE_ZONE}px`);
    root.style.setProperty('--glass-padding-top', `${glassPadding.top}px`);
    root.style.setProperty('--glass-padding-bottom', `${glassPadding.bottom}px`);
  }, [sidebarExpanded, glassPadding]);

  // Scroll detection for Jump to Latest chip
  useEffect(() => {
    const chatPanel = chatPanelRef.current;
    if (!chatPanel) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = chatPanel;
      const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
      
      // Show chip when more than 200px from bottom and there are user messages
      const currentHasUserMessages = conversation?.messages.some(m => m.role === 'user') ?? false;
      const shouldShow = distanceFromBottom > 200 && currentHasUserMessages;
      setShowJumpToLatest(shouldShow);
    };

    chatPanel.addEventListener('scroll', handleScroll);
    // Initial check
    handleScroll();
    
    return () => chatPanel.removeEventListener('scroll', handleScroll);
  }, [conversation?.messages]); // Depend on messages instead of hasUserMessages

  // Jump to latest function
  const handleJumpToLatest = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  };

  // Update header title when conversation loads
  useEffect(() => {
    if (conversation?.title) {
      setConversationTitle(conversation.title);
    }
    return () => {
      // Clear title when leaving conversation
      setConversationTitle(null);
    };
  }, [conversation?.title, setConversationTitle]);

  // Load conversation data
  useEffect(() => {
    console.log('🎯 useEffect triggered - conversationId:', conversationId);
    if (conversationId) {
      console.log('📞 Calling loadConversation...');
      loadConversation();
    } else {
      console.log('⚠️ No conversationId provided');
    }
  }, [conversationId, loadConversation]);

  const addMessageToConversation = (newMessage: Message) => {
    if (!conversation) return;
    
    setConversation(prev => prev ? {
      ...prev,
      messages: [...prev.messages, newMessage]
    } : null);
  };

  const updateLastAIMessage = (content: string) => {
    if (!conversation) return;
    
    setConversation(prev => {
      if (!prev) return null;
      
      const messages = [...prev.messages];
      const lastMessage = messages[messages.length - 1];
      
      if (lastMessage && lastMessage.role === 'assistant') {
        messages[messages.length - 1] = {
          ...lastMessage,
          content: content
        };
      }
      
      return {
        ...prev,
        messages: messages
      };
    });
  };

  const handleSendMessage = async () => {
    if (!messageText.trim() || isSending || !conversation) return;

    try {
      setIsSending(true);
      
      // Create optimistic user message for immediate display
      const tempUserMessage: Message = {
        messageId: `temp-${Date.now()}`,
        role: 'user',
        content: messageText.trim(),
        isBlog: false,
        createdAt: new Date().toISOString()
      };

      // Add user message to UI immediately  
      addMessageToConversation(tempUserMessage);
      
      // Clear input immediately for better UX
      const userMessageText = messageText.trim();
      setMessageText('');
      
      // Send the user message to backend
      const sentMessage = await conversationService.sendMessage(conversationId, {
        content: userMessageText
      });

      // Get the real message ID from the sent message
      const messageId = sentMessage.messageId;
      
      // Add placeholder AI message immediately
      const aiMessage: Message = {
        messageId: `ai-${Date.now()}`,
        role: 'assistant',
        content: '', // Will be updated as streaming progresses
        isBlog: false,
        createdAt: new Date().toISOString(),
      };
      
      addMessageToConversation(aiMessage);
      
      // Start AI streaming response
      setIsAIResponding(true);
      
      await conversationService.streamAIResponse(
        conversationId,
        messageId,
        // onChunk: Update the AI message content in real-time
        (chunk: string) => {
          updateLastAIMessage(chunk);
        },
        // onComplete: Just clear streaming state - message already in conversation
        (fullResponse: string) => {
          setIsAIResponding(false);
          updateLastAIMessage(fullResponse); // Ensure final content is set
        },
        // onError: Handle streaming errors
        (error: string) => {
          setIsAIResponding(false);
          console.error('AI streaming error:', error);
          updateLastAIMessage('Sorry, I encountered an error. Please try again.');
        }
      );
      
    } catch (err) {
      console.error('Failed to send message:', getErrorMessage(err));
      setIsAIResponding(false);
    } finally {
      setIsSending(false);
    }
  };

  const handleInputKeyDown = (e: React.KeyboardEvent) => {
    // IME-safe send: ignore Enter while composing; allow Shift+Enter for newline
    if (!isComposing && e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const fillSuggestion = (text: string) => {
    setMessageText(text);
  };

  // ✨ NEW: Blog generation handler
  const handleGenerateBlog = async () => {
    if (!conversation || isGeneratingBlog) return;

    try {
      setIsGeneratingBlog(true);
      
      // Get current message text as additional context
      const additionalContext = messageText.trim();
      
      // Add placeholder blog message immediately for optimistic UI
      const blogMessage: Message = {
        messageId: `blog-${Date.now()}`,
        role: 'assistant',
        content: '', // Will be updated as streaming progresses
        isBlog: true,
        createdAt: new Date().toISOString()
      };
      
      addMessageToConversation(blogMessage);
      
      // Auto-open the blog panel to show generation
      setShowGeneratedBlog(true);
      
      // Clear the message text since we're using it for blog generation
      setMessageText('');
      
      // Start blog generation streaming with additional context
      await conversationService.generateBlogFromConversation(
        conversationId,
        additionalContext,
        // onChunk: Update the blog message content in real-time
        (chunk: string) => {
          // Update the last blog message in conversation
          setConversation(prev => {
            if (!prev) return null;
            
            const messages = [...prev.messages];
            const lastIdx = messages.length - 1;
            
            if (lastIdx >= 0 && messages[lastIdx].isBlog) {
              messages[lastIdx] = {
                ...messages[lastIdx],
                content: chunk
              };
            }
            
            return {
              ...prev,
              messages: messages
            };
          });
        },
        // onComplete: Final blog content with message ID
        (fullResponse: string, messageId: string) => {
          setIsGeneratingBlog(false);
          
          // Update with final content and real message ID
          setConversation(prev => {
            if (!prev) return null;
            
            const messages = [...prev.messages];
            const lastIdx = messages.length - 1;
            
            if (lastIdx >= 0 && messages[lastIdx].isBlog) {
              messages[lastIdx] = {
                ...messages[lastIdx],
                messageId: messageId || messages[lastIdx].messageId,
                content: fullResponse
              };
            }
            
            return {
              ...prev,
              messages: messages
            };
          });
        },
        // onError: Handle blog generation errors
        (errMsg: string) => {
          setIsGeneratingBlog(false);
          console.error('Blog generation error:', errMsg);
          
          // Update the blog message with error content
          setConversation(prev => {
            if (!prev) return null;
            
            const messages = [...prev.messages];
            const lastIdx = messages.length - 1;
            
            if (lastIdx >= 0 && messages[lastIdx].isBlog) {
              messages[lastIdx] = {
                ...messages[lastIdx],
                content: 'Sorry, I encountered an error generating the blog. Please try again.'
              };
            }
            
            return {
              ...prev,
              messages: messages
            };
          });
        }
      );
      
    } catch (err) {
      console.error('Failed to generate blog:', getErrorMessage(err));
      setIsGeneratingBlog(false);
    }
  };

  // ✨ Delete/Archive handler (maps to backend archive like list page)
  // const handleDeleteConversation = async () => {
  //   if (!conversation) return;
  //   
  //   // Confirm deletion
  //   const confirmed = window.confirm(`Delete "${conversation.title}"? This action cannot be undone.`);
  //   if (!confirmed) return;
  //   
  //   try {
  //     await conversationService.archiveConversation(conversationId);
  //     // Navigate back to conversations list
  //     window.location.href = '/conversations';
  //   } catch (err) {
  //     console.error('Failed to delete conversation:', getErrorMessage(err));
  //     alert('Failed to delete conversation. Please try again.');
  //   }
  // };

  // ✨ Blog editor handlers
  const handleEditBlog = () => {
    setIsEditingBlog(true);
    setShowGeneratedBlog(true);
  };

  const handleCancelEdit = () => {
    setIsEditingBlog(false);
    // Don't clear showGeneratedBlog - keep the read-only view
  };

  const handleSaveDraft = (markdown: string) => {
    // Just update local storage - already handled by BlogEditor
    console.log('Draft saved:', markdown.length, 'characters');
  };

  const handlePublishBlog = async (markdown: string) => {
    if (!conversation || !markdown.trim()) return;

    try {
      setIsPublishing(true);
      
      // Generate title from content or use conversation title
      const title = conversation.title || 'Blog Post';
      
      // Extract simple tags from content (basic implementation)
      const extractTagsFromContent = (content: string): string[] => {
        // Look for hashtags in content
        const hashtagMatches = content.match(/#(\w+)/g);
        if (hashtagMatches) {
          return hashtagMatches.map(tag => tag.substring(1).toLowerCase());
        }
        
        // Default tags based on conversation or content
        const defaultTags = ['blog', 'ai-generated'];
        return defaultTags;
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
      
      // Show success notification
      showToast('success', 'Blog published successfully! 🎉');
      console.log('✅ Blog published successfully!');
      
    } catch (error) {
      console.error('Failed to publish blog:', getErrorMessage(error));
      setIsPublishing(false);
      
      // Show error notification
      showToast('error', `Failed to publish blog: ${getErrorMessage(error)}`);
    }
  };

  // Show loading state
  if (loading) {
    return (
      <div {...layout.containerProps}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-caption">Loading conversation...</p>
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (error || !conversation) {
    return (
      <div {...layout.containerProps}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-red-500 mb-4">{error || 'Conversation not found'}</p>
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

  // Check if conversation is forked
  const isForked = Boolean(conversation.forked_from);
  
  // Check if conversation has messages (excluding system messages)
  const hasUserMessages = conversation.messages.some(m => m.role === 'user');
  
  // Blog detection logic
  const blogMessages = conversation.messages.filter(m => m.isBlog === true);
  const hasBlogMessages = blogMessages.length > 0;
  const mostRecentBlogMessage = hasBlogMessages ? blogMessages[blogMessages.length - 1] : null;
  
  // Calculate visible panels count for layout decisions
  const getVisiblePanelCount = () => {
    let count = 1; // Chat panel always visible
    
    // Left panel: Original Blog (only if forked and toggled on)
    if (isForked && showOriginalBlog) count++;
    
    // Right panel: Generated Blog (only if exists and toggled on)
    if (hasBlogMessages && showGeneratedBlog) count++;
    
    return count;
  };

  const visiblePanelCount = getVisiblePanelCount();

  return (
    <div className="h-screen flex flex-col bg-black overflow-hidden">
      {/* Toast Notification */}
      {toast && (
        <div 
          className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg border max-w-sm transition-all duration-300 ${
            toast.type === 'success' 
              ? 'bg-green-900/90 border-green-500/30 text-green-100' 
              : 'bg-red-900/90 border-red-500/30 text-red-100'
          }`}
          style={{ backdropFilter: 'blur(10px)' }}
        >
          <div className="flex items-center justify-between">
            <p className="text-sm">{toast.message}</p>
            <button 
              onClick={() => setToast(null)}
              className="ml-2 text-lg hover:opacity-70"
            >
              ×
            </button>
          </div>
        </div>
      )}
      
      {/* Floating Panel Controls - Positioned to not interfere with header */}
      <div className="absolute top-20 right-4 z-10 flex flex-col gap-2">
        {/* Only show Original Blog toggle if forked */}
        {isForked && (
          <button 
            className={`glass-button-toggle px-3 py-2 text-xs ${showOriginalBlog ? 'active' : ''}`}
            onClick={() => setShowOriginalBlog(!showOriginalBlog)}
          >
            👁 Original
          </button>
        )}
        {/* Only show Generated Blog toggle if blog messages exist */}
        {hasBlogMessages && (
          <button 
            className={`glass-button-toggle px-3 py-2 text-xs ${showGeneratedBlog ? 'active' : ''}`}
            onClick={() => setShowGeneratedBlog(!showGeneratedBlog)}
          >
            📝 Blog
          </button>
        )}
      </div>

      {/* Main Content Area - Glass scroll: content can scroll behind header/input */}
      <div 
        className="absolute flex overflow-hidden" 
        style={{ 
          left: sidebarExpanded ? `${LAYOUT_CONSTANTS.SIDEBAR_EXPANDED}px` : `${LAYOUT_CONSTANTS.SIDEBAR_COLLAPSED}px`,
          top: `${layout.headerHeight}px`, // Start below header for scrollbar containment
          right: '0px',
          bottom: '96px', // End above input (80px input + 16px spacing)
          transition: 'left 0.3s ease'
        }}
      >
        {/* Dynamic 3-Panel Layout - Flex distributes space automatically */}
        <div className="flex w-full h-full" data-panel-count={visiblePanelCount}>
          
          {/* Left Panel - Original Blog (only if forked and visible) */}
          {isForked && showOriginalBlog && (
            <div className="flex-1 border-r border-gray-700/30 min-w-0">
              <div className="glass-panel-subdued h-full flex flex-col">
                <div className="flex items-center justify-between p-4 border-b border-gray-700/30 flex-shrink-0">
                  <h3 className="text-sm font-medium text-gray-300">Original Blog Post</h3>
                  <button className="glass-button-toggle px-2 py-1 text-xs">
                    💬 View
                  </button>
                </div>
                <div 
                  ref={leftPanelRef}
                  className="flex-1 overflow-y-auto p-4 text-sm text-gray-400 space-y-3"
                >
                  <h4 className="text-base font-semibold text-gray-200">
                    The Future of AI in Workplace Ethics
                  </h4>
                  <p>
                    As artificial intelligence becomes increasingly integrated into our professional lives, 
                    we must carefully consider the ethical implications of these powerful technologies...
                  </p>
                  <p>
                    This blog post explores key considerations for implementing AI systems responsibly, 
                    with particular focus on fairness, transparency, and accountability.
                  </p>
                  <div className="text-xs text-gray-500 pt-3 border-t border-gray-700">
                    Originally posted by @ethics_researcher • 2 days ago
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Main Chat Panel - Always Visible, Flex grows to fill available space */}
          <div className={`flex-1 min-w-0 ${visiblePanelCount > 1 ? 'border-r border-gray-700/30' : ''}`}>
            <div className="h-full flex flex-col relative">

              {/* Messages Container - Glass scroll: scrollbar contained, content extends behind glass */}
              <div 
                ref={chatPanelRef}
                role="log"
                aria-live="polite"
                aria-label="Conversation messages"
                className="flex-1 overflow-y-auto"
                style={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  justifyContent: hasUserMessages ? 'flex-start' : 'center',
                  minHeight: '100%',
                  // Remove padding from container - let content handle spacing
                  padding: '0'
                }}
              >
                {hasUserMessages ? (
                  <div 
                    className="space-y-4 max-w-4xl mx-auto w-full px-4"
                    style={{
                      // Glass scroll effect: Content can scroll behind header/input but remains readable
                      paddingTop: `${glassPadding.top}px`, // Header height + safe zone
                      paddingBottom: '100px', // Input area + safe zone (using fixed value instead of LAYOUT_CONSTANTS)
                      // Content starts above normal area (allows scroll behind header)
                      marginTop: `-${layout.headerHeight}px`,
                      // Content extends below normal area (allows scroll behind input)  
                      marginBottom: '-80px' // Match the new input area height
                    }}
                  >
                    {conversation.messages.filter(m => m.role !== 'system').map((message, index) => {
                      const isLastAIMessage = message.role === 'assistant' && 
                                            index === conversation.messages.filter(m => m.role !== 'system').length - 1;
                      const isTyping = (isAIResponding && isLastAIMessage && !message.isBlog) || 
                                     (isGeneratingBlog && isLastAIMessage && message.isBlog);
                      const listKey = `${message.messageId || `${message.role}-${message.createdAt}-${index}`}-${index}`;
                      
                      return (
                        <div 
                          key={listKey} 
                          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                          role="article"
                          aria-label={`${message.role === 'user' ? 'User' : 'Assistant'} message`}
                        >
                          <div className={`${message.role === 'user' ? 'glass-message-user' : 
                                          message.isBlog ? 'glass-message-blog' : 'glass-message-ai'} max-w-[85%] relative group`}>
                            {/* Blog message indicator */}
                            {message.isBlog && (
                              <div className="flex items-center gap-2 mb-2 text-xs text-blue-300">
                                <span className="px-2 py-1 bg-blue-900/30 rounded-full">Blog</span>
                                <button 
                                  className="glass-button-secondary px-2 py-1 text-xs"
                                  onClick={handleEditBlog}
                                >
                                  Edit and Post
                                </button>
                              </div>
                            )}
                            <div className="text-message">
                              {message.content ? (
                                <MarkdownRenderer content={message.content} />
                              ) : (
                                isTyping ? (
                                  <div className="flex items-center space-x-1">
                                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse delay-75"></div>
                                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse delay-150"></div>
                                  </div>
                                ) : null
                              )}
                              {isTyping && message.content && (
                                <span className="inline-block w-0.5 h-4 bg-blue-400 animate-pulse ml-1 align-middle"></span>
                              )}
                            </div>
                            <div className="mt-2 flex items-center justify-between">
                              <div className="text-xs opacity-70">
                                {isTyping ? (message.isBlog ? 'Generating blog...' : 'Assistant is typing...') : 
                                 (function() {
                                   // Prevent hydration mismatch by returning static text during SSR
                                   if (typeof window === 'undefined') {
                                     return 'Recently';
                                   }
                                   try {
                                     const date = new Date(message.createdAt);
                                     return isNaN(date.getTime()) ? 'Just now' : date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                                   } catch {
                                     return 'Just now';
                                   }
                                 })()}
                              </div>
                              {message.content && (
                                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                                  <button
                                    className="inline-flex items-center gap-1 rounded-md border border-white/10 bg-white/5 backdrop-blur-md px-2 py-1 text-[10px] text-white/80 hover:bg-white/10"
                                    onClick={async () => { await copyText(markdownToPlain(message.content)); }}
                                    aria-label="Copy Plain Text"
                                    title="Copy Plain Text"
                                  >
                                    <svg aria-hidden="true" viewBox="0 0 24 24" className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                                    </svg>
                                    TXT
                                  </button>
                                  <button
                                    className="inline-flex items-center gap-1 rounded-md border border-white/10 bg-white/5 backdrop-blur-md px-2 py-1 text-[10px] text-white/80 hover:bg-white/10"
                                    onClick={async () => { await copyText(message.content); }}
                                    aria-label="Copy Markdown"
                                    title="Copy Markdown"
                                  >
                                    <svg aria-hidden="true" viewBox="0 0 24 24" className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                                    </svg>
                                    MD
                                  </button>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}

                    {/* Generate Blog Button (when conversation has messages) */}
                    {hasUserMessages && (
                      <div className="flex justify-center pt-4">
                        <button 
                          className="glass-button-secondary px-6 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                          onClick={handleGenerateBlog}
                          disabled={isGeneratingBlog}
                        >
                          {isGeneratingBlog ? 'Generating blog...' : 'Generate Blog'}
                        </button>
                      </div>
                    )}
                    
                    {/* Auto-scroll target */}
                    <div ref={messagesEndRef} />
                  </div>
                ) : (
                  /* Empty State - Positioned with glass scroll awareness */
                  <div 
                    className="h-full flex flex-col items-center justify-center space-y-8 max-w-2xl mx-auto px-4"
                    style={{
                      // Match the glass scroll padding for consistent layout
                      paddingTop: `${glassPadding.top}px`,
                      paddingBottom: '100px', // Input area + safe zone (using fixed value)
                      marginTop: `-${layout.headerHeight}px`,
                      marginBottom: '-80px' // Match the new input area height
                    }}
                  >
                    <div className="text-center space-y-4">
                      <h2 className="text-xl font-semibold text-gray-300">Start a conversation</h2>
                      <p className="text-gray-400 text-sm">Ask questions, explore ideas, or generate content</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Panel - Generated Blog (only if exists and visible) */}
          {hasBlogMessages && showGeneratedBlog && mostRecentBlogMessage && (
            <div className="flex-1 min-w-0">
              {isEditingBlog ? (
                <BlogEditor
                  initialContent={mostRecentBlogMessage.content}
                  onSave={handleSaveDraft}
                  onCancel={handleCancelEdit}
                  onPublish={handlePublishBlog}
                  isPublishing={isPublishing}
                />
              ) : (
                <div className="glass-panel-active h-full flex flex-col">
                  <div className="flex items-center justify-between p-4 border-b border-blue-500/20 flex-shrink-0">
                    <h3 className="text-sm font-medium text-blue-300">Generated Blog Draft</h3>
                    <button 
                      className="glass-button-generate px-3 py-1.5 text-xs"
                      onClick={handleEditBlog}
                    >
                      ✍️ Edit and Post
                    </button>
                  </div>
                  <div 
                    ref={rightPanelRef}
                    className="flex-1 overflow-y-auto p-4 text-sm text-blue-100 space-y-3"
                  >
                    <div className="prose prose-invert max-w-none prose-sm">
                      <MarkdownRenderer content={mostRecentBlogMessage.content} />
                    </div>
                    <div className="text-xs text-blue-400 pt-3 border-t border-blue-800">
                      Generated {typeof window === 'undefined' ? 'recently' : new Date(mostRecentBlogMessage.createdAt).toLocaleString()} • 
                      {mostRecentBlogMessage.content.split(' ').length} words • Ready to edit
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
          
        </div>
      </div>

      {/* Fixed Message Input - Using layout constants for maintainability */}
      <div 
        className="fixed right-0 border-t border-gray-700/30 bg-black/60 backdrop-blur-md z-50"
        style={{ 
          left: sidebarExpanded ? `${LAYOUT_CONSTANTS.SIDEBAR_EXPANDED}px` : `${LAYOUT_CONSTANTS.SIDEBAR_COLLAPSED}px`,
          bottom: '16px', // Moved up from bottom-0 to add some spacing from screen edge
          minHeight: '80px', // Reduced from 100px to ensure it fits
          maxHeight: '200px', // Allow for expansion
          transition: 'left 0.3s ease'
        }}
      >
        <div className="px-4 py-3">
          <div className="max-w-4xl mx-auto">
            
            {/* Suggestions - Above Input (Best Practice) */}
            {!hasUserMessages && (
              <div className="mb-4 space-y-3">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-sm text-gray-400">Quick start</p>
                  <button 
                    className="glass-button-secondary px-3 py-1.5 text-xs"
                    onClick={handleGenerateBlog}
                    disabled={isGeneratingBlog}
                  >
                    {isGeneratingBlog ? 'Generating...' : 'Write Blog'}
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  <button 
                    className="glass-button-toggle px-4 py-3 text-left text-sm hover:bg-blue-500/10 transition-colors"
                    onClick={() => fillSuggestion("Help me brainstorm ideas about the future of technology and its impact on society")}
                  >
                    Technology and society impact
                  </button>
                  <button 
                    className="glass-button-toggle px-4 py-3 text-left text-sm hover:bg-blue-500/10 transition-colors"
                    onClick={() => fillSuggestion("I want to explore the key principles of sustainable innovation in modern business")}
                  >
                    Sustainable business innovation
                  </button>
                  <button 
                    className="glass-button-toggle px-4 py-3 text-left text-sm hover:bg-blue-500/10 transition-colors"
                    onClick={() => fillSuggestion("What are the most important skills needed for creative problem-solving in the digital age?")}
                  >
                    Creative problem-solving skills
                  </button>
                  <button 
                    className="glass-button-toggle px-4 py-3 text-left text-sm hover:bg-blue-500/10 transition-colors"
                    onClick={() => fillSuggestion("How can I improve my understanding of emerging trends in artificial intelligence and machine learning?")}
                  >
                    AI and machine learning trends
                  </button>
                </div>
              </div>
            )}

            <div className="flex items-end gap-3 relative">
              {/* Subtle glass morphism scroll to bottom arrow - positioned near input */}
              {showJumpToLatest && hasUserMessages && (
                <button
                  onClick={handleJumpToLatest}
                  className="absolute -top-10 right-0 w-7 h-7 rounded-full bg-white/5 backdrop-blur-xl border border-white/10 flex items-center justify-center hover:bg-white/10 hover:border-white/20 transition-all duration-300 shadow-2xl hover:shadow-blue-500/20 hover:scale-110"
                  aria-label="Scroll to latest message"
                  style={{ 
                    backdropFilter: 'blur(20px)',
                    background: 'rgba(255, 255, 255, 0.05)',
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.1)'
                  }}
                >
                  <svg className="w-3 h-3 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 14l-7 7m0 0l-7-7" />
                  </svg>
                </button>
              )}
              
              <div className="flex-1">
                <TextareaAutosize
                  className="glass-input w-full p-3 resize-none text-sm min-h-[48px] max-h-[160px]"
                  placeholder="Message..."
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  onKeyDown={handleInputKeyDown}
                  onCompositionStart={() => setIsComposing(true)}
                  onCompositionEnd={() => setIsComposing(false)}
                  minRows={1}
                  maxRows={6}
                  disabled={isSending}
                />
              </div>
              <button
                onClick={handleSendMessage}
                disabled={!messageText.trim() || isSending}
                className="glass-button-primary px-4 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSending ? '...' : '→'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ConversationPage() {
  return (
    <SessionGuard>
      <ConversationPageContent />
    </SessionGuard>
  );
}