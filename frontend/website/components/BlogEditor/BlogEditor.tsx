'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import { Button } from '@/components/design-system/Button';
import StarterKit from '@tiptap/starter-kit';
import { TextStyle } from '@tiptap/extension-text-style';
import { Color } from '@tiptap/extension-color';
import { TextAlign } from '@tiptap/extension-text-align';
import { ListItem } from '@tiptap/extension-list-item';
import { BulletList } from '@tiptap/extension-bullet-list';
import { OrderedList } from '@tiptap/extension-ordered-list';
import { CodeBlock } from '@tiptap/extension-code-block';
import { Blockquote } from '@tiptap/extension-blockquote';
import { Heading } from '@tiptap/extension-heading';
import { Bold } from '@tiptap/extension-bold';
import { Italic } from '@tiptap/extension-italic';
import { Underline } from '@tiptap/extension-underline';
import { Strike } from '@tiptap/extension-strike';
import { Link } from '@tiptap/extension-link';
import { HorizontalRule } from '@tiptap/extension-horizontal-rule';
import { useState, useEffect, useCallback } from 'react';
import TurndownService from 'turndown';
import { default as BlogEditorToolbar } from './BlogEditorToolbar';
import { useGlassHeader } from '@/lib/layout/hooks';
import { TEXT_COLORS } from '@/lib/layout/tokens';

interface BlogEditorProps {
  initialContent: string;
  onSave: (markdown: string) => void;
  onCancel: () => void;
  onPublish: (markdown: string) => void;
  isPublishing?: boolean;
}

const BlogEditor: React.FC<BlogEditorProps> = ({
  initialContent,
  onSave,
  onCancel,
  onPublish,
  isPublishing = false
}) => {
  const [markdown, setMarkdown] = useState('');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const layout = useGlassHeader();

  // Initialize Turndown for HTML to Markdown conversion
  const turndownService = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced',
    bulletListMarker: '-'
  });

  // Convert markdown to HTML for initial content
  const markdownToHtml = (md: string) => {
    // Simple markdown to HTML conversion
    return md
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*)\*/gim, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  };

  const editor = useEditor({
    immediatelyRender: false,
    extensions: [
      StarterKit,
      TextStyle,
      Color,
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
      ListItem,
      BulletList.configure({
        HTMLAttributes: {
          class: 'blog-bullet-list',
        },
      }),
      OrderedList.configure({
        HTMLAttributes: {
          class: 'blog-ordered-list',
        },
      }),
      CodeBlock.configure({
        HTMLAttributes: {
          class: 'blog-code-block',
        },
      }),
      Blockquote.configure({
        HTMLAttributes: {
          class: 'blog-blockquote',
        },
      }),
      Heading.configure({
        levels: [1, 2, 3],
        HTMLAttributes: {
          class: 'blog-heading',
        },
      }),
      Bold,
      Italic,
      Underline,
      Strike,
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'blog-link',
        },
      }),
      HorizontalRule,
    ],
    content: markdownToHtml(initialContent),
    editorProps: {
      attributes: {
        class: 'blog-editor-content prose prose-invert max-w-none focus:outline-none',
      },
    },
    onUpdate: ({ editor }) => {
      // Convert HTML content to markdown
      const html = editor.getHTML();
      const md = turndownService.turndown(html);
      setMarkdown(md);
      handleAutoSave(md);
    },
  });

  // Auto-save functionality
  const handleAutoSave = useCallback((content: string) => {
    // Save to localStorage for persistence
    localStorage.setItem('blog-draft', content);
    setLastSaved(new Date());
  }, []);

  // Load draft from localStorage on mount
  useEffect(() => {
    const savedDraft = localStorage.getItem('blog-draft');
    if (savedDraft && savedDraft !== initialContent) {
      // If there's a saved draft different from initial content, use it
      editor?.commands.setContent(markdownToHtml(savedDraft));
      setMarkdown(savedDraft);
    } else {
      setMarkdown(initialContent);
    }
  }, [initialContent, editor]);

  const handleSave = () => {
    onSave(markdown);
    setLastSaved(new Date());
  };

  const handlePublish = () => {
    // Clear the draft when publishing
    localStorage.removeItem('blog-draft');
    onPublish(markdown);
  };

  const handleCancel = () => {
    // Don't clear draft on cancel - user might want to come back
    onCancel();
  };

  if (!editor) {
    return (
      <div className={layout.panelClass}>
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={layout.panelClass}>
      {/* Content area with proper header clearance */}
      <div className={layout.contentClass} style={layout.headerClearance}>
        <div className="px-6 py-4">
          {/* Minimal Header - Single row, smaller buttons */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <h3 className="text-sm font-medium" style={{ color: TEXT_COLORS.SECONDARY }}>
                Edit Blog Post
              </h3>
              {lastSaved && (
                <span className="text-xs" style={{ color: TEXT_COLORS.TERTIARY }}>
                  Auto-saved {lastSaved.toLocaleTimeString()}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Button 
                variant="ghost"
                size="sm"
                onClick={handleSave}
                className="text-xs"
              >
                Save Draft
              </Button>
              <Button 
                variant="secondary"
                size="sm"
                onClick={handleCancel}
                className="text-xs"
              >
                Cancel
              </Button>
              <Button 
                variant="primary"
                size="sm"
                onClick={handlePublish}
                disabled={isPublishing}
                loading={isPublishing}
                className="text-xs"
              >
                {isPublishing ? 'Publishing...' : 'Publish'}
              </Button>
            </div>
          </div>

          {/* Toolbar */}
          <BlogEditorToolbar editor={editor} />

          {/* Editor Content - Matching blog viewer typography */}
          <div className="mt-4 prose prose-invert max-w-none prose-lg">
            <EditorContent editor={editor} />
          </div>

          {/* Footer Stats */}
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-800/30">
            <div className="text-xs" style={{ color: TEXT_COLORS.TERTIARY }}>
              {markdown.split(' ').filter(word => word.length > 0).length} words • 
              {markdown.split('\n').length} lines
            </div>
            <div className="text-xs" style={{ color: TEXT_COLORS.TERTIARY }}>
              {markdown.length > 0 ? 'Ready to publish' : 'Start writing...'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BlogEditor;
