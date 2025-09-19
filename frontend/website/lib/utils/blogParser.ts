/**
 * Blog Content Parser Utilities
 * 
 * Utilities for parsing and handling blog content that comes from the backend
 * as stringified JSON with title, content, and tags.
 */

export interface ParsedBlogContent {
  title: string;
  content: string;
  tags: string[];
  isValid: boolean;
  rawContent: string; // Original content for fallback
}

/**
 * Parse blog content from JSON string with safe fallbacks
 */
export function parseBlogContent(rawContent: string): ParsedBlogContent {
  // Default fallback structure
  const fallback: ParsedBlogContent = {
    title: 'Untitled Blog Post',
    content: rawContent,
    tags: [],
    isValid: false,
    rawContent
  };

  if (!rawContent?.trim()) {
    return fallback;
  }

  try {
    // Try to parse as JSON
    const parsed = JSON.parse(rawContent);
    
    // Validate the parsed structure
    if (typeof parsed === 'object' && parsed !== null) {
      const title = typeof parsed.title === 'string' ? parsed.title.trim() : '';
      const content = typeof parsed.content === 'string' ? parsed.content.trim() : '';
      const tags = Array.isArray(parsed.tags) 
        ? parsed.tags.filter((tag: any) => typeof tag === 'string' && tag.trim())
        : [];

      // Must have at least title or content to be valid
      if (title || content) {
        return {
          title: title || 'Untitled Blog Post',
          content: content || '',
          tags: tags.slice(0, 5), // Enforce 5 tag limit
          isValid: true,
          rawContent
        };
      }
    }
  } catch (error) {
    // JSON parsing failed, treat as markdown content
    console.log('Blog content is not JSON, treating as markdown:', error);
    
    // Try to extract title from markdown (first # heading)
    const lines = rawContent.split('\n');
    let title = 'Untitled Blog Post';
    let content = rawContent;
    
    const firstLine = lines[0]?.trim();
    if (firstLine?.startsWith('#')) {
      title = firstLine.replace(/^#+\s*/, '').trim();
      content = lines.slice(1).join('\n').trim();
    }
    
    return {
      title,
      content,
      tags: [],
      isValid: true,
      rawContent
    };
  }

  return fallback;
}

/**
 * Serialize blog content back to JSON format for backend
 */
export function serializeBlogContent(title: string, content: string, tags: string[]): string {
  return JSON.stringify({
    title: title.trim(),
    content: content.trim(),
    tags: tags.slice(0, 5) // Enforce 5 tag limit
  });
}

/**
 * Extract display data for blog preview
 */
export function getBlogDisplayData(parsedContent: ParsedBlogContent) {
  return {
    title: parsedContent.title,
    content: parsedContent.content,
    tags: parsedContent.tags,
    wordCount: parsedContent.content.split(' ').filter(word => word.length > 0).length,
    lineCount: parsedContent.content.split('\n').length
  };
}