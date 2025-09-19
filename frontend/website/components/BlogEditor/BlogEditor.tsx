'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import { Button } from '@/components/design-system/Button';
import { TagInput } from '@/components/features/blog/TagInput';
import StarterKit from '@tiptap/starter-kit';
import { useState, useEffect, useCallback } from 'react';
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
  const [title, setTitle] = useState(initialTitle);
  const [tags, setTags] = useState(initialTags);
  const [markdown, setMarkdown] = useState('');
  const layout = useGlassHeader();

  // Initialize Turndown for HTML to Markdown conversion
  const turndownService = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced',
    bulletListMarker: '-'
  });

  const editor = useEditor({
    immediatelyRender: false,
    extensions: [StarterKit],
    content: initialContent,
    onUpdate: ({ editor }) => {
      const html = editor.getHTML();
      const md = turndownService.turndown(html);
      setMarkdown(md);
    },
  });

  const handleSave = () => {
    onSave(title, markdown, tags);
  };

  const handlePublish = async () => {
    await onPublish(title, markdown, tags, messageId);
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
      <div className={layout.contentClass} style={layout.headerClearance}>
        <div className="px-6 py-4">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">Edit Blog Post</h3>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" onClick={handleSave}>Save Draft</Button>
              <Button variant="secondary" size="sm" onClick={onCancel}>Cancel</Button>
              <Button 
                variant="primary" 
                size="sm" 
                onClick={handlePublish}
                disabled={isPublishing || !title.trim() || !markdown.trim()}
                loading={isPublishing}
              >
                {isPublishing ? 'Publishing...' : 'Publish'}
              </Button>
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter blog title..."
              className="w-full px-3 py-2 rounded-lg border bg-black/20 backdrop-blur-sm border-white/10 focus:border-white/20 transition-colors text-white placeholder-gray-400 focus:outline-none"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">Tags</label>
            <TagInput
              value={tags}
              onChange={setTags}
              placeholder="Add tags..."
              maxTags={5}
            />
          </div>

          <BlogEditorToolbar editor={editor} />

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">Content</label>
            <div className="prose prose-invert max-w-none prose-lg border border-white/10 rounded-lg bg-black/10 p-4 min-h-[300px]">
              <EditorContent editor={editor} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BlogEditor;
