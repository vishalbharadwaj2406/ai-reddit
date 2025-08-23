'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { conversationService, ConversationDetail, Message, AuthenticationRequiredError, ConversationServiceError } from '../../../lib/services/conversationService';
import { postService } from '../../../lib/services/postService';
import { BlogEditor } from '../../../components/BlogEditor';
import { usePageLayout } from '../../../hooks/useViewportLayout';
import { useHeaderStore } from '../../../lib/stores/headerStore';

const getErrorMessage = (err: unknown): string => {
  if (err instanceof Error) return err.message;
  if (typeof err === 'string') return err;
  return 'Unknown error';
};

export default function ConversationPage() {
  const params = useParams();
  const conversationId = params.id as string;
  
  // Layout management hook for proper height calculations
  const layout = usePageLayout();
  
  // Header title management
  const { setConversationTitle } = useHeaderStore();
  
  // Panel visibility state
  const [showOriginalBlog, setShowOriginalBlog] = useState(false);
  const [showGeneratedBlog, setShowGeneratedBlog] = useState(false);
  
  // ✨ NEW: Blog editor state
  const [isEditingBlog, setIsEditingBlog] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  
  // Chat state
  const [messageText, setMessageText] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isAIResponding, setIsAIResponding] = useState(false);
  
  // ✨ NEW: Blog generation state
  const [isGeneratingBlog, setIsGeneratingBlog] = useState(false);
  
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
    try {
      setLoading(true);
      setError(null);
      
      const conversationData = await conversationService.getConversation(conversationId);
      setConversation(conversationData);
      
    } catch (err) {
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
    if (conversationId) {
      loadConversation();
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

      // Update the temp message with real message ID
      const messageId = (sentMessage as unknown as { message_id?: string }).message_id || sentMessage.messageId;
      
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

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
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
  const handleDeleteConversation = async () => {
    if (!conversation) return;
    
    // Confirm deletion
    const confirmed = window.confirm(`Delete "${conversation.title}"? This action cannot be undone.`);
    if (!confirmed) return;
    
    try {
      await conversationService.archiveConversation(conversationId);
      // Navigate back to conversations list
      window.location.href = '/conversations';
    } catch (err) {
      console.error('Failed to delete conversation:', getErrorMessage(err));
      alert('Failed to delete conversation. Please try again.');
    }
  };

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
      
      // Publish the blog as a post
      const publishedPost = await postService.publishBlogAsPost(
        markdown,
        title
      );
      
      console.log('Blog published as post:', publishedPost.post_id);
      
      // Close editor and show success
      setIsEditingBlog(false);
      setIsPublishing(false);
      
      // Optional: Show success notification
      // TODO: Add toast notification here
      
    } catch (error) {
      console.error('Failed to publish blog:', getErrorMessage(error));
      setIsPublishing(false);
      // TODO: Show error notification
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
  const isForked = Boolean(conversation.forkedFrom);
  
  // Check if conversation has messages (excluding system messages)
  const hasUserMessages = conversation.messages.some(m => m.role === 'user');
  
  // ✨ NEW: Blog detection logic
  const blogMessages = conversation.messages.filter(m => m.isBlog === true);
  const hasBlogMessages = blogMessages.length > 0;
  const mostRecentBlogMessage = hasBlogMessages ? blogMessages[blogMessages.length - 1] : null;
  
  // Calculate panel layout classes - equal width when visible + dynamic expansion
  const getPanelLayoutClasses = () => {
    const panels = [];
    
    // Left panel: Original Blog (only if forked and toggled on)
    if (isForked && showOriginalBlog) panels.push('original');
    
    // Center panel: Always visible (chat)
    panels.push('chat');
    
    // Right panel: Generated Blog (only if exists and toggled on)
    if (hasBlogMessages && showGeneratedBlog) panels.push('blog');
    
    // Return flex classes for equal width when multiple panels, expanded when single
    if (panels.length === 1) return 'w-full';
    if (panels.length === 2) return 'w-1/2';
    return 'w-1/3';
  };

  // Get actual visible panels for rendering
  const getVisiblePanels = () => {
    const panels = [];
    
    if (isForked && showOriginalBlog) panels.push('original');
    panels.push('chat'); // Always visible
    if (hasBlogMessages && showGeneratedBlog) panels.push('blog');
    
    return panels;
  };

  const visiblePanels = getVisiblePanels();

  return (
    <div className="h-screen flex flex-col bg-black overflow-hidden">
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

      {/* Main Content Area - Content scrolls behind header with proper z-layering */}
      <div className="absolute inset-0 flex overflow-hidden"> {/* Full screen, content starts at top */}
        {/* Dynamic 3-Panel Layout with Independent Scrolling */}
        <div className={`flex w-full h-full ${getPanelLayoutClasses()}`}>
          
          {/* Left Panel - Original Blog (only if forked and visible) */}
          {isForked && showOriginalBlog && (
            <div className={`${getPanelLayoutClasses()} border-r border-gray-700/30`}>
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

          {/* Main Chat Panel - Always Visible, Clean Design */}
          <div className={`${getPanelLayoutClasses()} ${visiblePanels.length > 1 ? 'border-r border-gray-700/30' : ''}`}>
            <div className="h-full flex flex-col">
              {/* Messages Container - Bottom-anchored modern chat layout */}
              <div 
                ref={chatPanelRef}
                className="flex-1 overflow-y-auto px-4 py-6 pt-20 pb-24"
                style={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  justifyContent: hasUserMessages ? 'flex-start' : 'center', // Start from top when has messages, centered when empty
                  minHeight: '100%'
                }}
              >
                {hasUserMessages ? (
                  <div className="space-y-4 max-w-4xl mx-auto w-full">
                    {conversation.messages.filter(m => m.role !== 'system').map((message, index) => {
                      const isLastAIMessage = message.role === 'assistant' && 
                                            index === conversation.messages.filter(m => m.role !== 'system').length - 1;
                      const isTyping = (isAIResponding && isLastAIMessage && !message.isBlog) || 
                                     (isGeneratingBlog && isLastAIMessage && message.isBlog);
                      const listKey = `${message.messageId || `${message.role}-${message.createdAt}-${index}`}-${index}`;
                      
                      return (
                        <div key={listKey} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                          <div className={`${message.role === 'user' ? 'glass-message-user' : 
                                          message.isBlog ? 'glass-message-blog' : 'glass-message-ai'} max-w-[85%]`}>
                            {/* Blog message indicator */}
                            {message.isBlog && (
                              <div className="flex items-center gap-2 mb-2 text-xs text-blue-300">
                                <span className="px-2 py-1 bg-blue-900/30 rounded-full">📝 Blog</span>
                                <button 
                                  className="glass-button-generate px-2 py-1 text-xs"
                                  onClick={handleEditBlog}
                                >
                                  ✍️ Edit and Post
                                </button>
                              </div>
                            )}
                            <div className="text-message">
                              {message.content || (isTyping ? (
                                <div className="flex items-center space-x-1">
                                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse delay-75"></div>
                                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse delay-150"></div>
                                </div>
                              ) : '')}
                              {isTyping && message.content && (
                                <span className="inline-block w-0.5 h-4 bg-blue-400 animate-pulse ml-1 align-middle"></span>
                              )}
                            </div>
                            <div className="text-xs opacity-70 mt-2">
                              {isTyping ? (message.isBlog ? 'Generating blog...' : 'Assistant is typing...') : 
                               (function() {
                                 try {
                                   const date = new Date(message.createdAt);
                                   return isNaN(date.getTime()) ? 'Just now' : date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                                 } catch {
                                   return 'Just now';
                                 }
                               })()}
                            </div>
                          </div>
                        </div>
                      );
                    })}

                    {/* Generate Blog Button (when conversation has messages) */}
                    {hasUserMessages && (
                      <div className="flex justify-center pt-4">
                        <button 
                          className="glass-button-generate px-6 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                          onClick={handleGenerateBlog}
                          disabled={isGeneratingBlog}
                        >
                          {isGeneratingBlog ? '✨ Generating Blog...' : '✍️ Generate Blog'}
                        </button>
                      </div>
                    )}
                    
                    {/* Auto-scroll target */}
                    <div ref={messagesEndRef} />
                  </div>
                ) : (
                  /* Empty State - Improved Visual Design */
                  <div className="h-full flex flex-col items-center justify-center space-y-6 max-w-2xl mx-auto">
                    {/* Generate Blog Button - Prominent in empty state */}
                    <button 
                      className="glass-button-generate px-8 py-4 text-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      onClick={handleGenerateBlog}
                      disabled={isGeneratingBlog}
                    >
                      {isGeneratingBlog ? '✨ Generating Blog...' : '✍️ Write Custom Blog'}
                    </button>
                    
                    {/* Improved Suggestion Cards */}
                    <div className="w-full space-y-3">
                      <p className="text-sm text-gray-400 text-center">Start with a suggestion:</p>
                      <div className="grid gap-3">
                        <button 
                          className="glass-button-toggle px-6 py-4 text-left text-sm hover:bg-blue-500/10 transition-colors"
                          onClick={() => fillSuggestion("Help me brainstorm ideas about the future of technology and its impact on society")}
                        >
                          💡 Help me brainstorm ideas about the future of technology...
                        </button>
                        <button 
                          className="glass-button-toggle px-6 py-4 text-left text-sm hover:bg-blue-500/10 transition-colors"
                          onClick={() => fillSuggestion("I want to explore the key principles of sustainable innovation in modern business")}
                        >
                          🚀 I want to explore the key principles of sustainable innovation...
                        </button>
                        <button 
                          className="glass-button-toggle px-6 py-4 text-left text-sm hover:bg-blue-500/10 transition-colors"
                          onClick={() => fillSuggestion("What are the most important skills needed for creative problem-solving in the digital age?")}
                        >
                          🔍 What are the most important skills for creative problem-solving...
                        </button>
                        <button 
                          className="glass-button-toggle px-6 py-4 text-left text-sm hover:bg-blue-500/10 transition-colors"
                          onClick={() => fillSuggestion("How can I improve my understanding of emerging trends in artificial intelligence and machine learning?")}
                        >
                          ✨ How can I improve my understanding of emerging AI trends...
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Panel - Generated Blog (only if exists and visible) */}
          {hasBlogMessages && showGeneratedBlog && mostRecentBlogMessage && (
            <div className={`${getPanelLayoutClasses()}`}>
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
                      <div 
                        className="whitespace-pre-wrap text-blue-100"
                        style={{ lineHeight: '1.6' }}
                      >
                        {mostRecentBlogMessage.content}
                      </div>
                    </div>
                    <div className="text-xs text-blue-400 pt-3 border-t border-blue-800">
                      Generated {new Date(mostRecentBlogMessage.createdAt).toLocaleString()} • 
                      {mostRecentBlogMessage.content.split(' ').length} words • Ready to edit
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
          
        </div>
      </div>

      {/* Fixed Message Input - Positioned at bottom with proper z-index */}
      <div className="fixed bottom-0 left-0 right-0 border-t border-gray-700/30 bg-black/60 backdrop-blur-md z-50">
        <div className="px-4 py-3">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end gap-3">
              <div className="flex-1">
                <textarea
                  className="glass-input w-full p-3 resize-none text-sm min-h-[48px] max-h-[160px]"
                  placeholder="Message..."
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  rows={1}
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