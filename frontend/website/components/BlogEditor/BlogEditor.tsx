'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import { Button } from '@/components/design-system/Button';
import { TagInput } from '@/components/features/blog/TagInput';
import StarterKit from '@tiptap/starter-kit';
import { TextStyle } from '@tiptap/extension-text-style';
import { Color } from '@tiptap/extension-color';
import { TextAlign } from '@tiptap/extension-text-align';
import { Heading } from '@tiptap/extension-heading';
import { Bold } from '@tiptap/extension-bold';
import { Italic } from '@tiptap/extension-italic';
import { Underline } from '@tiptap/extension-underline';
import { Strike } from '@tiptap/extension-strike';
import { Link } from '@tiptap/extension-link';
import { CodeBlock } from '@tiptap/extension-code-block';
import { Blockquote } from '@tiptap/extension-blockquote';
import { BulletList } from '@tiptap/extension-bullet-list';
import { OrderedList } from '@tiptap/extension-ordered-list';
import { ListItem } from '@tiptap/extension-list-item';
import { HorizontalRule } from '@tiptap/extension-horizontal-rule';
import { useState, useEffect, useCallback, useRef } from 'react';
import TurndownService from 'turndown';
import { default as BlogEditorToolbar } from './BlogEditorToolbar';
import { useGlassHeader } from '@/lib/layout/hooks';

interface BlogEditorProps {
  initialTitle: string;
  initialContent: string;
  initialTags: string[];
  messageId: string;
  onSave: (title: string, content: string, tags: string[]) => void;
  onCancel: () => void;
  onPublish: (title: string, content: string, tags: string[], messageId: string) => Promise<void>;
  isPublishing?: boolean;
}

interface DraftData {
  title: string;
  content: string;
  tags: string[];
  messageId: string;
  timestamp: number;
}

/**
 * Convert markdown to HTML for TipTap editor
 */
const markdownToHtml = (markdown: string): string => {
  return markdown
    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/^\> (.*$)/gm, '<blockquote>$1</blockquote>')
    .replace(/^\- (.*$)/gm, '<ul><li>$1</li></ul>')
    .replace(/^(\d+)\. (.*$)/gm, '<ol><li>$2</li></ol>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
    .replace(/\n/g, '<br>');
};

const BlogEditor: React.FC<BlogEditorProps> = ({
  initialTitle,
  initialContent,
  initialTags,
  messageId,
  onSave,
  onCancel,
  onPublish,
  isPublishing = false
}) => {
  // State management
  const [title, setTitle] = useState(initialTitle);
  const [tags, setTags] = useState(initialTags);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [currentMarkdown, setCurrentMarkdown] = useState(initialContent);
  
  const layout = useGlassHeader();
  const autoSaveRef = useRef<NodeJS.Timeout | null>(null);

  // Turndown service for HTML to Markdown conversion
  const turndownService = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced',
    bulletListMarker: '-',
    linkStyle: 'inlined'
  });

  // TipTap Editor with full extensions
  const editor = useEditor({
    immediatelyRender: false,
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3],
        },
      }),
      TextStyle,
      Color,
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
      Bold,
      Italic,
      Underline,
      Strike,
      Link.configure({
        openOnClick: false,
      }),
      CodeBlock,
      Blockquote,
      BulletList,
      OrderedList,
      ListItem,
      HorizontalRule,
    ],
    content: markdownToHtml(initialContent),
    editorProps: {
      attributes: {
        class: 'blog-editor-content prose prose-invert prose-lg max-w-none focus:outline-none min-h-[300px]',
      },
    },
    onUpdate: ({ editor }) => {
      const html = editor.getHTML();
      const markdown = turndownService.turndown(html);
      setCurrentMarkdown(markdown);
      setIsDirty(true);
      scheduleAutoSave();
    },
  });

  // Draft management
  const getDraftKey = () => `blog-draft-${messageId}`;

  const saveDraft = useCallback(() => {
    const draftData: DraftData = {
      title,
      content: currentMarkdown,
      tags,
      messageId,
      timestamp: Date.now()
    };
    
    localStorage.setItem(getDraftKey(), JSON.stringify(draftData));
    setLastSaved(new Date());
    setIsDirty(false);
  }, [title, currentMarkdown, tags, messageId]);

  const loadDraft = useCallback(() => {
    try {
      const savedDraft = localStorage.getItem(getDraftKey());
      if (!savedDraft) return false;

      const draftData: DraftData = JSON.parse(savedDraft);
      
      // Only load if it's recent (within 24 hours) and matches messageId
      const isRecent = (Date.now() - draftData.timestamp) < (24 * 60 * 60 * 1000);
      if (!isRecent || draftData.messageId !== messageId) return false;

      // Load draft data
      setTitle(draftData.title);
      setTags(draftData.tags);
      setCurrentMarkdown(draftData.content);
      
      // Update editor content
      if (editor) {
        editor.commands.setContent(markdownToHtml(draftData.content));
      }
      
      setLastSaved(new Date(draftData.timestamp));
      return true;
    } catch (error) {
      console.warn('Failed to load draft:', error);
      return false;
    }
  }, [messageId, editor]);

  const resetToOriginal = useCallback(() => {
    setTitle(initialTitle);
    setTags(initialTags);
    setCurrentMarkdown(initialContent);
    
    if (editor) {
      editor.commands.setContent(markdownToHtml(initialContent));
    }
    
    // Clear draft
    localStorage.removeItem(getDraftKey());
    setLastSaved(null);
    setIsDirty(false);
  }, [initialTitle, initialTags, initialContent, editor, getDraftKey]);

  // Auto-save functionality
  const scheduleAutoSave = useCallback(() => {
    if (autoSaveRef.current) {
      clearTimeout(autoSaveRef.current);
    }
    
    autoSaveRef.current = setTimeout(() => {
      saveDraft();
    }, 2000); // Auto-save after 2 seconds of inactivity
  }, [saveDraft]);

  // Load draft on mount
  useEffect(() => {
    if (editor) {
      loadDraft();
    }
  }, [editor, loadDraft]);

  // Auto-save when title or tags change
  useEffect(() => {
    if (isDirty) {
      scheduleAutoSave();
    }
  }, [title, tags, scheduleAutoSave, isDirty]);

  // Mark as dirty when title or tags change
  useEffect(() => {
    setIsDirty(true);
  }, [title, tags]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (autoSaveRef.current) {
        clearTimeout(autoSaveRef.current);
      }
    };
  }, []);

  // Handlers
  const handleSave = () => {
    saveDraft();
    onSave(title, currentMarkdown, tags);
  };

  const handlePublish = async () => {
    // Clear draft when publishing
    localStorage.removeItem(getDraftKey());
    await onPublish(title, currentMarkdown, tags, messageId);
  };

  const handleCancel = () => {
    // Don't clear draft on cancel
    onCancel();
  };

  // Loading state
  if (!editor) {
    return (
      <div className={layout.panelClass}>
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  // Check if content is valid for publishing
  const canPublish = title.trim() && currentMarkdown.trim();

  return (
    <div className={layout.panelClass}>
      {/* Simple scrollable layout */}
      <div className={`${layout.contentClass} overflow-y-auto`} style={layout.headerClearance}>
        <div className="px-6 py-4">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <h3 className="text-lg font-semibold text-white">Edit Blog Post</h3>
              {lastSaved && (
                <span className="text-xs text-gray-400">
                  Auto-saved {lastSaved.toLocaleTimeString()}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Button 
                variant="ghost"
                size="sm"
                onClick={resetToOriginal}
                className="text-xs"
                disabled={isPublishing}
                title="Reset to original message content"
              >
                Reset
              </Button>
              <Button 
                variant="ghost"
                size="sm"
                onClick={handleSave}
                className="text-xs"
                disabled={isPublishing}
              >
                Save Draft
              </Button>
              <Button 
                variant="secondary"
                size="sm"
                onClick={handleCancel}
                className="text-xs"
                disabled={isPublishing}
              >
                Cancel
              </Button>
              <Button 
                variant="primary"
                size="sm"
                onClick={handlePublish}
                disabled={isPublishing || !canPublish}
                loading={isPublishing}
                className="text-xs"
              >
                {isPublishing ? 'Publishing...' : 'Publish'}
              </Button>
            </div>
          </div>

          {/* Title Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter blog title..."
              className="w-full px-3 py-2 rounded-lg border bg-black/20 backdrop-blur-sm border-white/10 focus:border-white/20 transition-colors text-white placeholder-gray-400 focus:outline-none"
              disabled={isPublishing}
            />
          </div>

          {/* Tags Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Tags
            </label>
            <TagInput
              value={tags}
              onChange={setTags}
              placeholder="Add tags..."
              maxTags={5}
              disabled={isPublishing}
            />
          </div>

          {/* Toolbar */}
          <div className="mb-4">
            <BlogEditorToolbar editor={editor} />
          </div>

          {/* Editor Content - Simple layout that works */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Content
            </label>
            <div className="blog-editor-container">
              <EditorContent editor={editor} />
            </div>
          </div>

          {/* Footer Stats */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-800/30 text-xs text-gray-400">
            <div>
              {currentMarkdown.split(' ').filter(word => word.length > 0).length} words • 
              {currentMarkdown.split('\n').length} lines • 
              {tags.length}/5 tags
            </div>
            <div>
              {canPublish ? 'Ready to publish' : 'Complete title and content to publish'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BlogEditor;
