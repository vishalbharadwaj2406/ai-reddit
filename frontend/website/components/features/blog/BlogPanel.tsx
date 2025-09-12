/**
 * BlogPanel Component
 * Clean, simple blog viewing interface
 */

'use client';

import { Message } from '@/lib/services/conversationService';
import { BlogEditor } from '@/components/BlogEditor';
import MarkdownRenderer from '@/components/Markdown/MarkdownRenderer';
import { BlogPanelHeader } from './BlogPanelHeader';
import { useSimpleLayout } from '@/hooks/useGlassScroll';

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
  const layout = useSimpleLayout();

  // If no blog message, don't render anything
  if (!activeBlogMessage) {
    return null;
  }

  return (
    <div {...layout.blogPanelProps}>
      {isEditingBlog ? (
        // Blog Editor Mode - Full height
        <BlogEditor
          initialContent={activeBlogMessage.content}
          onSave={onSaveDraft}
          onCancel={onCancelEdit}
          onPublish={onPublishBlog}
          isPublishing={isPublishing}
        />
      ) : (
        // Blog Viewer Mode - Clean scrollable layout
        <>
          {/* Header - Fixed at top */}
          <div className="flex-shrink-0 bg-black/90 backdrop-blur-sm border-b border-gray-700/30 p-4">
            <BlogPanelHeader
              title={activeBlogMessage.content}
              onEditBlog={onEditBlog}
              onClose={onClose}
            />
          </div>
          
          {/* Blog Content - Scrollable area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            <div className="prose prose-invert max-w-none prose-lg">
              <MarkdownRenderer content={activeBlogMessage.content} />
            </div>
            
            {/* Metadata */}
            <div className="text-xs text-gray-500 pt-6 mt-6 border-t border-gray-800/50">
              Generated {typeof window === 'undefined' ? 'recently' : new Date(activeBlogMessage.createdAt).toLocaleString()} • 
              {activeBlogMessage.content.split(' ').length} words
            </div>
          </div>
        </>
      )}
    </div>
  );
};
