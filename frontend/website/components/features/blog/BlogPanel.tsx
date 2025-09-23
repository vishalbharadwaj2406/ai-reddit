/**
 * BlogPanel Component
 * Production-grade blog interface with industry-standard glass scroll
 */

'use client';

import { useMemo } from 'react';
import { Message } from '@/lib/services/conversationService';
import { BlogEditor } from '@/components/BlogEditor';
import MarkdownRenderer from '@/components/Markdown/MarkdownRenderer';
import { Button } from '@/components/design-system/Button';
import { Badge } from '@/components/design-system/Badge';
import { useContentLayout } from '@/lib/layout/hooks';
import { parseBlogContent, getBlogDisplayData, type ParsedBlogContent } from '@/lib/utils/blogParser';
import { validateMarkdown } from '@/lib/utils/markdownConverter';

interface BlogPanelProps {
  // Data
  activeBlogMessage: Message | null;
  
  // Blog editor state
  isEditingBlog: boolean;
  isPublishing: boolean;
  
  // Actions
  onEditBlog: (parsedContent: ParsedBlogContent) => void;
  onCancelEdit: () => void;
  onSaveDraft: (title: string, content: string, tags: string[]) => void;
  onPublishBlog: (title: string, content: string, tags: string[], messageId: string) => Promise<void>;
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
  const layout = useContentLayout();

  // Parse blog content
  const parsedContent = useMemo(() => {
    if (!activeBlogMessage?.content) return null;
    
    const parsed = parseBlogContent(activeBlogMessage.content);
    
    // Validate and clean the markdown content
    if (parsed.isValid && parsed.content) {
      const validation = validateMarkdown(parsed.content);
      return {
        ...parsed,
        content: validation.cleaned,
        validationErrors: validation.errors
      };
    }
    
    return parsed;
  }, [activeBlogMessage?.content]);

  const displayData = useMemo(() => {
    if (!parsedContent) return null;
    return getBlogDisplayData(parsedContent);
  }, [parsedContent]);

  // If no blog message, don't render anything
  if (!activeBlogMessage || !parsedContent || !displayData) {
    return null;
  }

  return (
    <div className={layout.panelClass}>
      {isEditingBlog ? (
        // Blog Editor Mode - Full height with structured editing
        <BlogEditor
          initialTitle={parsedContent.title}
          initialContent={parsedContent.content}
          initialTags={parsedContent.tags}
          messageId={activeBlogMessage.messageId}
          onSave={onSaveDraft}
          onCancel={onCancelEdit}
          onPublish={onPublishBlog}
          isPublishing={isPublishing}
        />
      ) : (
        // Blog Viewer Mode - Clean layout with structured display
        <div className={layout.contentClass} style={layout.contentPadding}>
          {/* Header with actions */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <h2 className="text-sm font-medium text-gray-300">
                Generated Blog Post
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="primary"
                size="sm"
                onClick={() => onEditBlog(parsedContent)}
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
          </div>

          {/* Blog Title */}
          <div className="mb-4">
            <h1 className="text-2xl font-bold text-white mb-2">
              {parsedContent.title}
            </h1>
            
            {/* Tags */}
            {parsedContent.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {parsedContent.tags.map((tag) => (
                  <Badge 
                    key={tag} 
                    variant="blue" 
                    className="text-xs"
                  >
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
          </div>
          
          {/* Blog Content */}
          <div className="prose prose-invert max-w-none prose-lg">
            <MarkdownRenderer content={parsedContent.content} />
          </div>
          
          {/* Validation warnings (dev mode) */}
          {process.env.NODE_ENV === 'development' && parsedContent.validationErrors && parsedContent.validationErrors.length > 0 && (
            <div className="mt-4 p-3 bg-yellow-900/20 border border-yellow-600/30 rounded-lg">
              <h4 className="text-yellow-400 text-sm font-medium mb-2">Markdown Validation Warnings:</h4>
              <ul className="text-yellow-300 text-xs space-y-1">
                {parsedContent.validationErrors.map((error: string, index: number) => (
                  <li key={index}>• {error}</li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Metadata */}
          <div className="text-xs text-gray-500 pt-4 mt-6 border-t border-gray-800/50 flex justify-between">
            <span>
              Generated {typeof window === 'undefined' ? 'recently' : new Date(activeBlogMessage.createdAt).toLocaleString()}
            </span>
            <span>
              {displayData.wordCount} words • {displayData.lineCount} lines
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
