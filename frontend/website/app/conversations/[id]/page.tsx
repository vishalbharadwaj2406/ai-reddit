'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

export default function ConversationPage() {
  const params = useParams();
  const conversationId = params.id as string;
  
  // Panel visibility state
  const [showOriginalBlog, setShowOriginalBlog] = useState(false);
  const [showGeneratedBlog, setShowGeneratedBlog] = useState(false);
  
  // Chat state
  const [messageText, setMessageText] = useState('');
  const [characterCount, setCharacterCount] = useState(0);

  // Mock conversation data
  const conversation = {
    id: conversationId,
    title: 'AI Ethics Discussion',
    isForked: false,
    forkedFrom: null,
    messages: [
      {
        id: '1',
        role: 'assistant',
        content: 'Hello! I\'m here to help you explore AI ethics through thoughtful conversation. What aspects of AI ethics are you most curious about?',
        timestamp: '10:30 AM'
      },
      {
        id: '2', 
        role: 'user',
        content: 'I\'m interested in how we can ensure AI systems are fair and unbiased, especially in hiring processes.',
        timestamp: '10:32 AM'
      }
    ]
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    setMessageText(text);
    setCharacterCount(text.length);
  };

  const getCounterClass = () => {
    if (characterCount > 4500) return 'glass-counter error';
    if (characterCount > 4000) return 'glass-counter warning';
    return 'glass-counter';
  };

  // Calculate panel layout classes
  const getPanelLayoutClasses = () => {
    const panelsVisible = [showOriginalBlog, true, showGeneratedBlog].filter(Boolean).length;
    
    if (panelsVisible === 1) return 'grid-cols-1';
    if (panelsVisible === 2) return 'grid-cols-2';
    return 'grid-cols-3';
  };

  return (
    <div className="min-h-screen">
      <div className="px-6 py-6">
        
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
                  {conversation.isForked ? 'Forked conversation' : 'Original conversation'} • {conversation.messages.length} messages
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Panel toggles */}
              <button 
                className={`glass-button-toggle px-4 py-2 text-sm ${showOriginalBlog ? 'active' : ''}`}
                onClick={() => setShowOriginalBlog(!showOriginalBlog)}
              >
                👁 Original Blog
              </button>
              <button 
                className={`glass-button-toggle px-4 py-2 text-sm ${showGeneratedBlog ? 'active' : ''}`}
                onClick={() => setShowGeneratedBlog(!showGeneratedBlog)}
              >
                📝 Generated Blog
              </button>
            </div>
          </div>
        </div>

        {/* Three-Panel Workspace */}
        <div className={`grid ${getPanelLayoutClasses()} gap-6 min-h-[600px]`}>
          
          {/* Left Panel - Original Blog */}
          {showOriginalBlog && (
            <div className="glass-panel-subdued p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-subheading text-gray-300">Original Blog Post</h3>
                <button className="glass-button-toggle px-3 py-1 text-sm">
                  💬 View Conversation
                </button>
              </div>
              <div className="text-body text-gray-400 space-y-4">
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
          <div className="glass-elevated p-6 flex flex-col">
            <h3 className="text-subheading mb-6">Conversation</h3>
            
            {/* Messages */}
            <div className="flex-1 space-y-6 mb-6 overflow-y-auto">
              {conversation.messages.map((message) => (
                <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`${message.role === 'user' ? 'glass-message-user' : 'glass-message-ai'} max-w-[85%]`}>
                    <div className="text-message">{message.content}</div>
                    <div className="text-xs opacity-70 mt-2">{message.timestamp}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Message Input */}
            <div className="space-y-4">
              <div className="flex items-end justify-between">
                <label className="text-caption">Your Message</label>
                <div className={getCounterClass()}>
                  {characterCount} / 5000
                </div>
              </div>
              
              <textarea
                className="glass-input w-full p-4 min-h-[120px] resize-none text-body"
                placeholder="Continue the conversation..."
                value={messageText}
                onChange={handleTextChange}
                maxLength={5000}
              />
              
              <div className="flex gap-4">
                <button className="glass-button-primary px-8 py-3 flex-1">
                  Send Message
                </button>
                <button className="glass-button-generate px-8 py-3 flex-1">
                  ✨ Generate Blog
                </button>
              </div>
            </div>
          </div>

          {/* Right Panel - Generated Blog */}
          {showGeneratedBlog && (
            <div className="glass-panel-active p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-subheading text-blue-300">Generated Blog Draft</h3>
                <button className="glass-button-generate px-4 py-2 text-sm">
                  📤 Publish Post
                </button>
              </div>
              <div className="text-body text-blue-100 space-y-4">
                <input 
                  type="text"
                  className="glass-input w-full p-3 text-lg font-semibold"
                  placeholder="Blog post title..."
                  defaultValue="Ensuring Fairness in AI-Powered Hiring"
                />
                <div className="space-y-4 min-h-[300px]">
                  <p>
                    The integration of artificial intelligence in hiring processes represents both 
                    an opportunity and a challenge for modern organizations. While AI can help 
                    streamline recruitment and reduce human bias, it also introduces new forms 
                    of potential discrimination that we must carefully address.
                  </p>
                  <p>
                    Key considerations include ensuring diverse training data, regular bias 
                    auditing, and maintaining human oversight in final decisions. The goal 
                    is to leverage AI's efficiency while preserving fairness and transparency 
                    in the hiring process.
                  </p>
                </div>
                <div className="flex gap-3 pt-4 border-t border-blue-800">
                  <span className="px-3 py-1 bg-blue-900/30 text-blue-300 rounded-full text-sm">
                    #AIEthics
                  </span>
                  <span className="px-3 py-1 bg-blue-900/30 text-blue-300 rounded-full text-sm">
                    #Hiring
                  </span>
                  <span className="px-3 py-1 bg-blue-900/30 text-blue-300 rounded-full text-sm">
                    #Fairness
                  </span>
                </div>
                <div className="text-caption text-blue-400 pt-2">
                  Draft • 847 words • Ready to publish
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        {!showOriginalBlog && !showGeneratedBlog && (
          <div className="mt-8">
            <div className="glass-card text-center py-12">
              <h3 className="text-subheading text-caption mb-4">
                Expand Your Workspace
              </h3>
              <p className="text-body text-caption mb-8">
                Toggle panels to view original content or work on your blog draft
              </p>
              <div className="flex gap-4 justify-center">
                <button 
                  className="glass-button-secondary px-6 py-3"
                  onClick={() => setShowOriginalBlog(true)}
                >
                  📖 Show Original Blog
                </button>
                <button 
                  className="glass-button-primary px-6 py-3"
                  onClick={() => setShowGeneratedBlog(true)}
                >
                  ✨ Generate Blog Draft
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
} 