'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { conversationService, ConversationDetail, Message, AuthenticationRequiredError, ConversationServiceError } from '../../../lib/services/conversationService';
import { postService } from '../../../lib/services/postService';
import { BlogEditor } from '../../../components/BlogEditor';

const getErrorMessage = (err: unknown): string => {
  if (err instanceof Error) return err.message;
  if (typeof err === 'string') return err;
  return 'Unknown error';
};

export default function ConversationPage() {
  const params = useParams();
  const conversationId = params.id as string;
  
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

  // Auto-scroll ref
  const messagesEndRef = useRef<HTMLDivElement>(null);

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

  // Auto-scroll to bottom when messages change or AI is typing
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation?.messages, isAIResponding]);

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

  // ✨ NEW: Blog editor handlers
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
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-caption">Loading conversation...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error || !conversation) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error || 'Conversation not found'}</p>
          <Link href="/conversations">
            <button className="glass-button-secondary px-4 py-2">
              ← Back to Conversations
            </button>
          </Link>
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
  
  // Calculate panel layout classes - conditional based on forked status
  const getPanelLayoutClasses = () => {
    if (isForked) {
      // Forked conversation can show all 3 panels
      const panelsVisible = [showOriginalBlog, true, showGeneratedBlog && hasBlogMessages].filter(Boolean).length;
      if (panelsVisible === 1) return 'grid-cols-1';
      if (panelsVisible === 2) return 'grid-cols-2';
      return 'grid-cols-3';
    } else {
      // New conversation only shows conversation + generated blog (if it exists)
      return (showGeneratedBlog && hasBlogMessages) ? 'grid-cols-2' : 'grid-cols-1';
    }
  };

  return (
    <div className="h-screen flex flex-col">
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="px-6 py-6 flex-shrink-0">
          {/* Conversation Header */}
          <div className="glass-card mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Link href="/conversations">
                  <button className="glass-button-secondary px-4 py-2 text-sm">
                    ← Back
                  </button>
                </Link>
                <div>
                  <h1 className="text-heading text-white">{conversation.title}</h1>
                  <p className="text-caption">
                    {conversation.forkedFrom ? 'Forked conversation' : 'Original conversation'} • {conversation.messages.length} messages
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                {/* Conditional panel toggles - only show Original Blog toggle if forked */}
                {isForked && (
                  <button 
                    className={`glass-button-toggle px-4 py-2 text-sm ${showOriginalBlog ? 'active' : ''}`}
                    onClick={() => setShowOriginalBlog(!showOriginalBlog)}
                  >
                    👁 Original Blog
                  </button>
                )}
                {/* ✨ NEW: Only show Generated Blog toggle if blog messages exist */}
                {hasBlogMessages && (
                  <button 
                    className={`glass-button-toggle px-4 py-2 text-sm ${showGeneratedBlog ? 'active' : ''}`}
                    onClick={() => setShowGeneratedBlog(!showGeneratedBlog)}
                  >
                    📝 Generated Blog
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Three-Panel Workspace - Scrollable Content Area */}
        <div className="flex-1 px-6 overflow-hidden">
          <div className={`grid ${getPanelLayoutClasses()} gap-6 h-full`}>
            
            {/* Left Panel - Original Blog (only if forked) */}
            {isForked && showOriginalBlog && (
              <div className="glass-panel-subdued p-6 flex flex-col overflow-hidden">
                <div className="flex items-center justify-between mb-6 flex-shrink-0">
                  <h3 className="text-subheading text-gray-300">Original Blog Post</h3>
                  <button className="glass-button-toggle px-3 py-1 text-sm">
                    💬 View Conversation
                  </button>
                </div>
                <div className="flex-1 overflow-y-auto text-body text-gray-400 space-y-4">
                  <h4 className="text-lg font-semibold text-gray-200">
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
                  <div className="text-caption text-gray-500 pt-4 border-t border-gray-700">
                    Originally posted by @ethics_researcher • 2 days ago
                  </div>
                </div>
              </div>
            )}

            {/* Center Panel - Active Conversation (Always Visible) */}
            <div className="glass-elevated p-6 flex flex-col overflow-hidden">
              <h3 className="text-subheading mb-6 flex-shrink-0">Conversation</h3>
              
              {/* Messages Container - Scrollable */}
              <div className="flex-1 overflow-y-auto">
                {hasUserMessages ? (
                  <div className="space-y-6">
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
                            {/* ✨ NEW: Blog message indicator */}
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
                              {isTyping ? (message.isBlog ? 'Generating blog...' : 'Typing...') : 
                               new Date(message.createdAt).toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                      );
                    })}

                    {/* ✨ NEW: Floating Generate Blog Button (when conversation has messages) */}
                    {hasUserMessages && (
                      <div className="flex justify-center pt-6">
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
                  /* Empty State - ChatGPT Style */
                  <div className="h-full flex flex-col items-center justify-center space-y-8">
                    {/* ✨ NEW: Generate Blog Button */}
                    <button 
                      className="glass-button-generate px-8 py-4 text-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      onClick={handleGenerateBlog}
                      disabled={isGeneratingBlog}
                    >
                      {isGeneratingBlog ? '✨ Generating Blog...' : '✍️ Write Custom Blog'}
                    </button>
                    
                    {/* Autofill Suggestions */}
                    <div className="w-full max-w-2xl space-y-3">
                      <p className="text-caption text-gray-400 text-center">Start with a suggestion:</p>
                      <div className="grid gap-3">
                        <button 
                          className="glass-button-toggle px-6 py-4 text-left text-body"
                          onClick={() => fillSuggestion("Help me brainstorm ideas about the future of technology and its impact on society")}
                        >
                          💡 Help me brainstorm ideas about the future of technology...
                        </button>
                        <button 
                          className="glass-button-toggle px-6 py-4 text-left text-body"
                          onClick={() => fillSuggestion("I want to explore the key principles of sustainable innovation in modern business")}
                        >
                          🚀 I want to explore the key principles of sustainable innovation...
                        </button>
                        <button 
                          className="glass-button-toggle px-6 py-4 text-left text-body"
                          onClick={() => fillSuggestion("What are the most important skills needed for creative problem-solving in the digital age?")}
                        >
                          🔍 What are the most important skills for creative problem-solving...
                        </button>
                        <button 
                          className="glass-button-toggle px-6 py-4 text-left text-body"
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

            {/* Right Panel - Generated Blog */}
            {showGeneratedBlog && hasBlogMessages && mostRecentBlogMessage && (
              isEditingBlog ? (
                <BlogEditor
                  initialContent={mostRecentBlogMessage.content}
                  onSave={handleSaveDraft}
                  onCancel={handleCancelEdit}
                  onPublish={handlePublishBlog}
                  isPublishing={isPublishing}
                />
              ) : (
                <div className="glass-panel-active p-6 flex flex-col overflow-hidden">
                  <div className="flex items-center justify-between mb-6 flex-shrink-0">
                    <h3 className="text-subheading text-blue-300">Generated Blog Draft</h3>
                    <button 
                      className="glass-button-generate px-4 py-2 text-sm"
                      onClick={handleEditBlog}
                    >
                      ✍️ Edit and Post
                    </button>
                  </div>
                  <div className="flex-1 overflow-y-auto text-body text-blue-100 space-y-4">
                    {/* ✨ NEW: Display actual blog message content */}
                    <div className="prose prose-invert max-w-none">
                      <div 
                        className="whitespace-pre-wrap text-blue-100"
                        style={{ lineHeight: '1.6' }}
                      >
                        {mostRecentBlogMessage.content}
                      </div>
                    </div>
                    <div className="text-caption text-blue-400 pt-4 border-t border-blue-800">
                      Generated {new Date(mostRecentBlogMessage.createdAt).toLocaleString()} • 
                      {mostRecentBlogMessage.content.split(' ').length} words • Ready to edit
                    </div>
                  </div>
                </div>
              )
            )}
          </div>
        </div>
      </div>

      {/* Fixed Message Input - Completely Fixed at Bottom */}
      <div className="flex-shrink-0 border-t border-gray-700 bg-black/50 backdrop-blur-md">
        <div className="px-6 py-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end gap-3">
              <div className="flex-1">
                <textarea
                  className="glass-input w-full p-4 resize-none text-body min-h-[56px] max-h-[200px]"
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
                className="glass-button-primary px-6 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
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