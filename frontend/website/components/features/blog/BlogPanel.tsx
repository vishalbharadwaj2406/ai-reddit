/**
 * BlogPanel Component
 * Production-grade blog interface with industry-standard glass scroll
 */

'use client';

import { Message } from '@/lib/services/conversationService';
import { BlogEditor } from '@/components/BlogEditor';
import MarkdownRenderer from '@/components/Markdown/MarkdownRenderer';
import { Button } from '@/components/design-system/Button';
import { useGlassLayout } from '@/hooks/useGlassLayout';

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
  const layout = useGlassLayout();

  // If no blog message, don't render anything
  if (!activeBlogMessage) {
    return null;
  }

  return (
    <div className={layout.panelClass}>
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
        // Blog Viewer Mode - Clean glass scroll with content clearance
        <div className={layout.contentClass} style={layout.contentClearance}>
          <div className="p-6">
            {/* Minimal Header - Just buttons */}
            <div className="flex items-center justify-end gap-2 mb-6">
              <Button
                variant="primary"
                size="sm"
                onClick={onEditBlog}
                className="text-xs"
              >
                Edit & Post
              </Button>
              {onClose && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onClose}
                  className="text-xs w-8 h-8 p-0"
                >
                  ✕
                </Button>
              )}
            </div>
            
            {/* Blog Content with title integrated */}
            <div className="prose prose-invert max-w-none prose-lg">
              <MarkdownRenderer content={activeBlogMessage.content} />
            </div>
            
            {/* Metadata */}
            <div className="text-xs text-gray-500 pt-6 mt-6 border-t border-gray-800/50">
              Generated {typeof window === 'undefined' ? 'recently' : new Date(activeBlogMessage.createdAt).toLocaleString()} • 
              {activeBlogMessage.content.split(' ').length} words
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
