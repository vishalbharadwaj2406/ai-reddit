/**
 * ConversationLayout Component
 * Production-grade layout orchestrator with responsive 3-panel design
 */

'use client';

import { useState, useEffect } from 'react';
import { ChatPanel } from '../chat/ChatPanel';
import { BlogPanel } from '../blog/BlogPanel';
import { PanelControls } from './PanelControls';
import { InputArea } from '../ui/InputArea';
import { usePageLayout, LAYOUT_CONSTANTS } from '@/hooks/useViewportLayout';
import { useSidebarStore } from '@/lib/stores/sidebarStore';
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
  const layout = usePageLayout();
  const { isExpanded: sidebarExpanded } = useSidebarStore();
  
  // Panel visibility state
  const [showOriginalBlog, setShowOriginalBlog] = useState(false);
  const [showGeneratedBlog, setShowGeneratedBlog] = useState(false);
  
  // Mobile detection
  const [isMobile, setIsMobile] = useState(false);
  
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);
  
  // Computed properties
  const isForked = Boolean(conversation.forked_from);
  const hasUserMessages = conversation.messages.some(m => m.role === 'user');
  const blogMessages = conversation.messages.filter(m => m.isBlog === true);
  const hasBlogMessages = blogMessages.length > 0;
  const mostRecentBlogMessage = hasBlogMessages ? blogMessages[blogMessages.length - 1] : null;
  
  // Auto-open blog panel on first generation (as requested)
  useEffect(() => {
    if (hasBlogMessages && !showGeneratedBlog) {
      setShowGeneratedBlog(true);
    }
  }, [hasBlogMessages, showGeneratedBlog]);
  
  // Calculate visible panel count for layout
  const getVisiblePanelCount = () => {
    let count = 1; // Chat panel always visible
    
    if (isForked && showOriginalBlog) count++;
    if (hasBlogMessages && showGeneratedBlog) count++;
    
    return count;
  };
  
  const visiblePanelCount = getVisiblePanelCount();
  
  // Enhanced message sending that handles WriteBlog case
  const handleSendMessage = async (text: string) => {
    await onSendMessage(text);
  };
  
  const handleWriteBlog = () => {
    // This should open an empty blog editor
    // For now, we'll use the existing blog editor with empty content
    setShowGeneratedBlog(true);
    onWriteBlog();
  };

  return (
    <div className="h-screen flex flex-col bg-black overflow-hidden">
      {/* Panel Controls */}
      <PanelControls
        showOriginalBlog={showOriginalBlog}
        showGeneratedBlog={showGeneratedBlog}
        isForked={isForked}
        hasBlogMessages={hasBlogMessages}
        onToggleOriginalBlog={() => setShowOriginalBlog(!showOriginalBlog)}
        onToggleGeneratedBlog={() => setShowGeneratedBlog(!showGeneratedBlog)}
        isMobile={isMobile}
      />

      {/* Main Content Area */}
      <div 
        className="absolute flex overflow-hidden" 
        style={{ 
          left: sidebarExpanded ? `${LAYOUT_CONSTANTS.SIDEBAR_EXPANDED}px` : `${LAYOUT_CONSTANTS.SIDEBAR_COLLAPSED}px`,
          top: `${layout.headerHeight}px`,
          right: '0px',
          bottom: '96px',
          transition: 'left 0.3s ease'
        }}
      >
        {isMobile && visiblePanelCount > 1 ? (
          // Mobile: Tab-based layout
          <MobileTabLayout
            conversation={conversation}
            showOriginalBlog={showOriginalBlog}
            showGeneratedBlog={showGeneratedBlog}
            isForked={isForked}
            hasBlogMessages={hasBlogMessages}
            mostRecentBlogMessage={mostRecentBlogMessage}
            onGenerateBlog={onGenerateBlog}
            showJumpToLatest={showJumpToLatest}
            onJumpToLatest={onJumpToLatest}
            hasUserMessages={hasUserMessages}
            visiblePanelCount={visiblePanelCount}
            isEditingBlog={isEditingBlog}
            isPublishing={isPublishing}
            onEditBlog={onEditBlog}
            onCancelEdit={onCancelEdit}
            onSaveDraft={onSaveDraft}
            onPublishBlog={onPublishBlog}
            isAIResponding={isAIResponding}
            isGeneratingBlog={isGeneratingBlog}
          />
        ) : (
          // Desktop: Multi-panel layout
          <DesktopPanelLayout
            conversation={conversation}
            showOriginalBlog={showOriginalBlog}
            showGeneratedBlog={showGeneratedBlog}
            isForked={isForked}
            hasBlogMessages={hasBlogMessages}
            mostRecentBlogMessage={mostRecentBlogMessage}
            onGenerateBlog={onGenerateBlog}
            showJumpToLatest={showJumpToLatest}
            onJumpToLatest={onJumpToLatest}
            hasUserMessages={hasUserMessages}
            visiblePanelCount={visiblePanelCount}
            isEditingBlog={isEditingBlog}
            isPublishing={isPublishing}
            onEditBlog={onEditBlog}
            onCancelEdit={onCancelEdit}
            onSaveDraft={onSaveDraft}
            onPublishBlog={onPublishBlog}
            isAIResponding={isAIResponding}
            isGeneratingBlog={isGeneratingBlog}
          />
        )}
      </div>

      {/* Fixed Input Area */}
      <InputArea
        messageText={messageText}
        onMessageTextChange={onMessageTextChange}
        onSendMessage={handleSendMessage}
        isSending={isSending}
        isComposing={isComposing}
        onCompositionStart={onCompositionStart}
        onCompositionEnd={onCompositionEnd}
        showJumpToLatest={showJumpToLatest}
        onJumpToLatest={onJumpToLatest}
        hasUserMessages={hasUserMessages}
        isGeneratingBlog={isGeneratingBlog}
        onWriteBlog={handleWriteBlog}
      />
    </div>
  );
};

// Desktop layout component
interface LayoutProps {
  conversation: ConversationDetail;
  showOriginalBlog: boolean;
  showGeneratedBlog: boolean;
  isForked: boolean;
  hasBlogMessages: boolean;
  mostRecentBlogMessage: Message | null;
  onGenerateBlog: () => Promise<void>;
  showJumpToLatest: boolean;
  onJumpToLatest: () => void;
  hasUserMessages: boolean;
  visiblePanelCount: number;
  isEditingBlog: boolean;
  isPublishing: boolean;
  onEditBlog: () => void;
  onCancelEdit: () => void;
  onSaveDraft: (markdown: string) => void;
  onPublishBlog: (markdown: string) => Promise<void>;
  isAIResponding: boolean;
  isGeneratingBlog: boolean;
}

const DesktopPanelLayout: React.FC<LayoutProps> = (props) => {
  return (
    <div className="flex w-full h-full" data-panel-count={props.visiblePanelCount}>
      {/* Left Panel - Original Blog (only if forked and visible) */}
      {props.isForked && props.showOriginalBlog && (
        <div className="flex-1 border-r border-gray-700/30 min-w-0">
          <div className="glass-panel-subdued h-full flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-gray-700/30 flex-shrink-0">
              <h3 className="text-sm font-medium text-gray-300">Original Blog Post</h3>
              <button className="glass-button-toggle px-2 py-1 text-xs">
                💬 View
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 text-sm text-gray-400 space-y-3">
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

      {/* Main Chat Panel */}
      <ChatPanel
        conversation={props.conversation}
        messages={props.conversation.messages}
        isAIResponding={props.isAIResponding}
        isGeneratingBlog={props.isGeneratingBlog}
        showJumpToLatest={props.showJumpToLatest}
        onGenerateBlog={props.onGenerateBlog}
        onJumpToLatest={props.onJumpToLatest}
        hasUserMessages={props.hasUserMessages}
        visiblePanelCount={props.visiblePanelCount}
      />

      {/* Right Panel - Generated Blog */}
      {props.hasBlogMessages && props.showGeneratedBlog && (
        <BlogPanel
          mostRecentBlogMessage={props.mostRecentBlogMessage}
          isEditingBlog={props.isEditingBlog}
          isPublishing={props.isPublishing}
          onEditBlog={props.onEditBlog}
          onCancelEdit={props.onCancelEdit}
          onSaveDraft={props.onSaveDraft}
          onPublishBlog={props.onPublishBlog}
        />
      )}
    </div>
  );
};

const MobileTabLayout: React.FC<LayoutProps> = (props) => {
  const [activeTab, setActiveTab] = useState<'chat' | 'original' | 'blog'>('chat');
  
  const tabs = [
    { id: 'chat' as const, label: 'Chat', icon: '💬', available: true },
    { id: 'original' as const, label: 'Original', icon: '👁', available: props.isForked && props.showOriginalBlog },
    { id: 'blog' as const, label: 'Blog', icon: '📝', available: props.hasBlogMessages && props.showGeneratedBlog },
  ].filter(tab => tab.available);

  return (
    <div className="flex flex-col w-full h-full">
      {/* Mobile Tab Navigation */}
      {tabs.length > 1 && (
        <div className="flex border-b border-gray-700/30 bg-black/80 backdrop-blur-sm">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.id 
                  ? 'text-blue-400 border-b-2 border-blue-400' 
                  : 'text-gray-400 hover:text-gray-300'
              }`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>
      )}
      
      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'chat' && (
          <ChatPanel
            conversation={props.conversation}
            messages={props.conversation.messages}
            isAIResponding={props.isAIResponding}
            isGeneratingBlog={props.isGeneratingBlog}
            showJumpToLatest={props.showJumpToLatest}
            onGenerateBlog={props.onGenerateBlog}
            onJumpToLatest={props.onJumpToLatest}
            hasUserMessages={props.hasUserMessages}
            visiblePanelCount={1} // Always 1 in mobile tab view
          />
        )}
        
        {activeTab === 'blog' && props.mostRecentBlogMessage && (
          <BlogPanel
            mostRecentBlogMessage={props.mostRecentBlogMessage}
            isEditingBlog={props.isEditingBlog}
            isPublishing={props.isPublishing}
            onEditBlog={props.onEditBlog}
            onCancelEdit={props.onCancelEdit}
            onSaveDraft={props.onSaveDraft}
            onPublishBlog={props.onPublishBlog}
            onClose={() => setActiveTab('chat')}
          />
        )}
        
        {/* Original blog content would go here */}
      </div>
    </div>
  );
};
