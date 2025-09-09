/**
 * BlogPanel Component
 * Production-grade blog viewing and editing interface
 */

'use client';

import { Message } from '@/lib/services/conversationService';
import { BlogEditor } from '@/components/BlogEditor';
import MarkdownRenderer from '@/components/Markdown/MarkdownRenderer';

interface BlogPanelProps {
  // Data
  mostRecentBlogMessage: Message | null;
  
  // Blog editor state
  isEditingBlog: boolean;
  isPublishing: boolean;
  
  // Actions
  onEditBlog: () => void;
  onCancelEdit: () => void;
  onSaveDraft: (markdown: string) => void;
  onPublishBlog: (markdown: string) => Promise<void>;
  
  // Panel management
  onClose?: () => void;
}

export const BlogPanel: React.FC<BlogPanelProps> = ({
  mostRecentBlogMessage,
  isEditingBlog,
  isPublishing,
  onEditBlog,
  onCancelEdit,
  onSaveDraft,
  onPublishBlog,
  onClose,
}) => {
  // If no blog message, don't render anything
  if (!mostRecentBlogMessage) {
    return null;
  }

  return (
    <div className="flex-1 min-w-0">
      {isEditingBlog ? (
        // Blog Editor Mode
        <BlogEditor
          initialContent={mostRecentBlogMessage.content}
          onSave={onSaveDraft}
          onCancel={onCancelEdit}
          onPublish={onPublishBlog}
          isPublishing={isPublishing}
        />
      ) : (
        // Blog Viewer Mode
        <div className="glass-panel-active h-full flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-blue-500/20 flex-shrink-0">
            <h3 className="text-sm font-medium text-blue-300">Generated Blog Draft</h3>
            <div className="flex items-center gap-2">
              <button 
                className="glass-button-generate px-3 py-1.5 text-xs"
                onClick={onEditBlog}
              >
                ✍️ Edit and Post
              </button>
              {onClose && (
                <button 
                  className="glass-button-toggle px-2 py-1.5 text-xs"
                  onClick={onClose}
                  aria-label="Close blog panel"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
          
          {/* Blog Content */}
          <div className="flex-1 overflow-y-auto p-4 text-sm text-blue-100 space-y-3">
            <div className="prose prose-invert max-w-none prose-sm">
              <MarkdownRenderer content={mostRecentBlogMessage.content} />
            </div>
            
            {/* Blog metadata */}
            <div className="text-xs text-blue-400 pt-3 border-t border-blue-800">
              Generated {typeof window === 'undefined' ? 'recently' : new Date(mostRecentBlogMessage.createdAt).toLocaleString()} • 
              {mostRecentBlogMessage.content.split(' ').length} words • Ready to edit
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
