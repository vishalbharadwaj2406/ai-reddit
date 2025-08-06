'use client';

import { useState } from 'react';
import { BlogEditor } from '../../components/BlogEditor';

const sampleBlogContent = `# The Future of AI in Creative Writing

Artificial intelligence is revolutionizing the way we approach creative writing and content creation. As we stand at the intersection of technology and creativity, we're witnessing unprecedented changes in how stories are told and content is produced.

## Key Benefits of AI-Assisted Writing

- **Enhanced Productivity**: AI tools can help writers overcome creative blocks and generate ideas faster
- **Improved Quality**: Grammar and style suggestions help create more polished content
- **Accessibility**: AI democratizes writing tools for non-professional writers

## The Human Element Remains Essential

While AI provides powerful assistance, the human touch remains irreplaceable:

> "The best AI-assisted writing combines technological capability with human creativity and emotional intelligence."

### What This Means for Content Creators

The future of writing isn't about replacing human creativity—it's about **amplifying** it. Writers who embrace AI tools while maintaining their unique voice will find themselves at a significant advantage.

## Looking Forward

As we continue to develop these technologies, we must remember that AI is a tool to enhance human creativity, not replace it. The stories that resonate most deeply will always come from human experience and emotion.

---

*What are your thoughts on AI-assisted writing? Share your experiences in the comments below.*`;

export default function BlogEditorDemo() {
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishedContent, setPublishedContent] = useState<string | null>(null);

  const handleSave = (markdown: string) => {
    console.log('Demo: Saved draft with', markdown.length, 'characters');
    alert('Draft saved locally! ✅');
  };

  const handleCancel = () => {
    alert('Edit cancelled - returning to read-only view');
  };

  const handlePublish = async (markdown: string) => {
    setIsPublishing(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setPublishedContent(markdown);
    setIsPublishing(false);
    alert('Blog published successfully! 🚀');
  };

  const handleReset = () => {
    setPublishedContent(null);
  };

  return (
    <div className="min-h-screen">
      <div className="px-6 py-6">
        <div className="max-w-6xl mx-auto">
          
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-display text-gradient-primary mb-4">
              Blog Editor Demo
            </h1>
            <p className="text-body text-caption max-w-2xl">
              Test the beautiful Tiptap-based blog editor with glass morphism design. 
              This demonstrates the editing experience users will have when creating posts.
            </p>
          </div>

          {/* Demo Controls */}
          <div className="glass-card mb-6 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-subheading text-white mb-2">Demo Controls</h3>
                <p className="text-caption">
                  The editor below contains sample blog content. Try editing, formatting, and "publishing" it.
                </p>
              </div>
              {publishedContent && (
                <button 
                  onClick={handleReset}
                  className="glass-button-secondary px-4 py-2"
                >
                  Reset Demo
                </button>
              )}
            </div>
          </div>

          {/* Blog Editor */}
          <div className="grid grid-cols-1 gap-6 h-[600px]">
            {publishedContent ? (
              <div className="glass-panel-active p-6 flex flex-col">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-subheading text-blue-300">Published Blog Post</h3>
                  <div className="text-xs text-blue-400">
                    {publishedContent.split(' ').length} words • Published successfully
                  </div>
                </div>
                <div className="flex-1 overflow-y-auto prose prose-invert max-w-none">
                  <div className="whitespace-pre-wrap text-blue-100">
                    {publishedContent}
                  </div>
                </div>
              </div>
            ) : (
              <BlogEditor
                initialContent={sampleBlogContent}
                onSave={handleSave}
                onCancel={handleCancel}
                onPublish={handlePublish}
                isPublishing={isPublishing}
              />
            )}
          </div>

          {/* Features Showcase */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="glass-card p-6">
              <h4 className="text-subheading text-white mb-3">✨ Beautiful Design</h4>
              <p className="text-body text-caption">
                Glass morphism interface with elegant blue accents and smooth animations.
              </p>
            </div>
            
            <div className="glass-card p-6">
              <h4 className="text-subheading text-white mb-3">🛠 Rich Editing</h4>
              <p className="text-body text-caption">
                Full-featured toolbar with headings, lists, links, quotes, and more.
              </p>
            </div>
            
            <div className="glass-card p-6">
              <h4 className="text-subheading text-white mb-3">💾 Auto-Save</h4>
              <p className="text-body text-caption">
                Local draft persistence with auto-save functionality.
              </p>
            </div>
            
            <div className="glass-card p-6">
              <h4 className="text-subheading text-white mb-3">📱 Responsive</h4>
              <p className="text-body text-caption">
                Mobile-friendly design that works perfectly on all devices.
              </p>
            </div>
            
            <div className="glass-card p-6">
              <h4 className="text-subheading text-white mb-3">🚀 Publishing</h4>
              <p className="text-body text-caption">
                One-click publishing to your post system with loading states.
              </p>
            </div>
            
            <div className="glass-card p-6">
              <h4 className="text-subheading text-white mb-3">📝 Markdown</h4>
              <p className="text-body text-caption">
                Exports clean markdown format for consistent content storage.
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
