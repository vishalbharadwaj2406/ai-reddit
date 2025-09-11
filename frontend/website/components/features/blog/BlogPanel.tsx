/**
 * BlogPanel Component
 * Clean, minimal blog viewing interface (Claude-style)
 * 
 * Height Management:
 * - Receives full height from ResizablePanels CSS Grid
 * - Uses h-full flex-col for internal height distribution
 * - Header: flex-shrink-0 (fixed height)
 * - Content: flex-1 overflow-y-auto (scrollable area)
 * 
 * Note: Parent ResizablePanels.BLOG_PANEL has no overflow constraint
 * to allow this component's internal scrolling to work properly.
 */

'use client';

import { Message } from '@/lib/services/conversationService';
import { BlogEditor } from '@/components/BlogEditor';
import MarkdownRenderer from '@/components/Markdown/MarkdownRenderer';
import { BlogPanelHeader } from './BlogPanelHeader';
import { usePanelGlassScroll } from '@/hooks/useGlassScroll';

interface BlogPanelProps {
  // Data
  activeBlogMessage: Message | null;
  
  // Blog editor state
  isEditingBlog: boolean;
  isPublishing: boolean;
  
  // Actions
  onEditBlog: () => void;
  onCancelEdit: () => void;
  onSaveDraft: (markdown: string) => void;
  onPublishBlog: (markdown: string) => Promise<void>;
  onClose?: () => void;
}

export const BlogPanel: React.FC<BlogPanelProps> = ({
  activeBlogMessage,
  isEditingBlog,
  isPublishing,
  onEditBlog,
  onCancelEdit,
  onSaveDraft,
  onPublishBlog,
  onClose,
}) => {
  // If no blog message, don't render anything
  // Always call hooks at the top level
  const glassScroll = usePanelGlassScroll();
  
  // Early return after hooks
  if (!activeBlogMessage) {
    return null;
  }

  return (
    <div className="h-full bg-black border-l border-gray-700/30">
      {isEditingBlog ? (
        // Blog Editor Mode
        <BlogEditor
          initialContent={activeBlogMessage.content}
          onSave={onSaveDraft}
          onCancel={onCancelEdit}
          onPublish={onPublishBlog}
          isPublishing={isPublishing}
        />
      ) : (
        // Blog Viewer Mode - Glass Scroll System
        <div {...glassScroll.containerProps}>
          {/* Clean Header - Fixed */}
          <div 
            className="fixed top-0 left-0 right-0 z-10 bg-black/80 backdrop-blur-sm border-b border-gray-700/30"
            style={{ height: 'var(--header-height)' }}
          >
            <BlogPanelHeader
              title={activeBlogMessage.content}
              onEditBlog={onEditBlog}
              onClose={onClose}
            />
          </div>
          
          {/* Blog Content - Glass Scroll Content */}
          <div {...glassScroll.contentProps}>
            <div className="px-6 space-y-6">
              <div className="prose prose-invert max-w-none prose-lg">
                <MarkdownRenderer content={activeBlogMessage.content} />
              </div>
              
              {/* Minimal metadata */}
              <div className="text-xs text-gray-500 pt-6 mt-6 border-t border-gray-800/50">
                Generated {typeof window === 'undefined' ? 'recently' : new Date(activeBlogMessage.createdAt).toLocaleString()} • 
                {activeBlogMessage.content.split(' ').length} words
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
