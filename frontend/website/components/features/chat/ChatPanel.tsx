/**
 * ChatPanel Component
 * Production-grade chat interface with glass scroll and responsive design
 */

'use client';

import { useRef, useEffect } from 'react';
import { Message } from '@/lib/services/conversationService';
import { MessageList } from '@/components/features/chat/MessageList';
import { JumpToLatest } from '@/components/features/ui/JumpToLatest';
import { usePageLayout, LAYOUT_CONSTANTS, getGlassScrollPadding } from '@/hooks/useViewportLayout';

interface ChatPanelProps {
  // Data
  conversation: any; // ConversationDetail type
  messages: Message[];
  
  // States
  isAIResponding: boolean;
  isGeneratingBlog: boolean;
  showJumpToLatest: boolean;
  
  // Handlers
  onGenerateBlog: () => Promise<void>;
  onJumpToLatest: () => void;
  
  // Layout
  hasUserMessages: boolean;
  visiblePanelCount: number;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  conversation,
  messages,
  isAIResponding,
  isGeneratingBlog,
  showJumpToLatest,
  onGenerateBlog,
  onJumpToLatest,
  hasUserMessages,
  visiblePanelCount,
}) => {
  const layout = usePageLayout();
  const glassPadding = getGlassScrollPadding();
  
  // Panel refs for scrolling
  const chatPanelRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change or AI is responding
  useEffect(() => {
    if (chatPanelRef.current && messagesEndRef.current) {
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
      }, 100);
    }
  }, [messages, isAIResponding, isGeneratingBlog]);

  return (
    <div className={`flex-1 min-w-0 ${visiblePanelCount > 1 ? 'border-r border-gray-700/30' : ''}`}>
      <div className="h-full flex flex-col relative">
        
        {/* Messages Container with Glass Scroll Effect */}
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
            padding: '0'
          }}
        >
          {hasUserMessages ? (
            <div 
              className="space-y-4 max-w-4xl mx-auto w-full px-4"
              style={{
                // Glass scroll effect: Content scrolls behind header/input but remains readable
                paddingTop: `${glassPadding.top}px`,
                paddingBottom: `${glassPadding.bottom}px`,
                marginTop: `-${layout.headerHeight}px`,
                marginBottom: `-${LAYOUT_CONSTANTS.INPUT_HEIGHT}px`
              }}
            >
              <MessageList 
                messages={messages}
                isAIResponding={isAIResponding}
                isGeneratingBlog={isGeneratingBlog}
              />
              
              {/* Generate Blog Button */}
              <div className="flex justify-center pt-4">
                <button 
                  className="glass-button-secondary px-6 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={onGenerateBlog}
                  disabled={isGeneratingBlog}
                >
                  {isGeneratingBlog ? 'Generating blog...' : 'Generate Blog'}
                </button>
              </div>
              
              {/* Auto-scroll target */}
              <div ref={messagesEndRef} />
            </div>
          ) : (
            /* Empty State */
            <div 
              className="h-full flex flex-col items-center justify-center space-y-8 max-w-2xl mx-auto px-4"
              style={{
                paddingTop: `${glassPadding.top}px`,
                paddingBottom: `${glassPadding.bottom}px`,
                marginTop: `-${layout.headerHeight}px`,
                marginBottom: `-${LAYOUT_CONSTANTS.INPUT_HEIGHT}px`
              }}
            >
              <div className="text-center space-y-4">
                <h2 className="text-xl font-semibold text-gray-300">Start a conversation</h2>
                <p className="text-gray-400 text-sm">Ask questions, explore ideas, or generate content</p>
              </div>
            </div>
          )}
        </div>

        {/* Jump to Latest Button */}
        {showJumpToLatest && hasUserMessages && (
          <JumpToLatest 
            onJumpToLatest={onJumpToLatest}
            className="absolute bottom-4 right-4"
          />
        )}
      </div>
    </div>
  );
};
