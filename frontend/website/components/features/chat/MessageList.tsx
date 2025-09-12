/**
 * MessageList Component
 * Production-grade message display with proper rendering and accessibility
 */

'use client';

import { Message } from '@/lib/services/conversationService';
import MarkdownRenderer from '@/components/Markdown/MarkdownRenderer';
import { copyText } from '@/lib/utils/copy';
import { markdownToPlain } from '@/lib/utils/markdown';
import { BlogMessageButton } from './BlogMessageButton';

interface MessageListProps {
  messages: Message[];
  isAIResponding: boolean;
  isGeneratingBlog: boolean;
  activeBlogMessageId?: string;
  onBlogMessageClick?: (message: Message) => void;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isAIResponding,
  isGeneratingBlog,
  activeBlogMessageId,
  onBlogMessageClick,
}) => {
  // Filter out system messages
  const displayMessages = messages.filter(m => m.role !== 'system');
  
  return (
    <>
      {displayMessages.map((message, index) => {
        const isLastAIMessage = message.role === 'assistant' && 
                              index === displayMessages.length - 1;
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
                            'glass-message-ai'} max-w-[85%] relative group`}>
              
              {/* Message content */}
              <div className="text-message">
                {message.content ? (
                  isTyping ? (
                    // During streaming, show content as plain text with cursor
                    <div className="whitespace-pre-wrap font-mono text-sm leading-relaxed">
                      {message.content}
                      <span className="inline-block w-0.5 h-4 bg-blue-400 animate-pulse ml-1 align-middle"></span>
                    </div>
                  ) : (
                    // Once streaming is complete, render as markdown
                    <MarkdownRenderer content={message.content} />
                  )
                ) : (
                  isTyping ? (
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse delay-75"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse delay-150"></div>
                    </div>
                  ) : null
                )}
              </div>
              
              {/* Blog message button */}
              {message.isBlog && onBlogMessageClick && (
                <BlogMessageButton
                  onClick={() => onBlogMessageClick(message)}
                  isActive={activeBlogMessageId === message.messageId}
                />
              )}
              
              {/* Message metadata and actions */}
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
                
                {/* Copy buttons */}
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
    </>
  );
};
