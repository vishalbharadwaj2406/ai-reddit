/**
 * Production-Grade Markdown Conversion Utilities
 * 
 * Uses the same ecosystem as MarkdownRenderer for consistent processing.
 * Leverages react-markdown, remark-gfm, and turndown for robust conversion.
 */

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import TurndownService from 'turndown';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';

/**
 * Configured Turndown service matching BlogEditor settings
 */
const turndownService = new TurndownService({
  headingStyle: 'atx',
  codeBlockStyle: 'fenced',
  bulletListMarker: '-',
  linkStyle: 'inlined',
  emDelimiter: '*',
  strongDelimiter: '**'
});

// Configure turndown for better HTML to markdown conversion
turndownService.addRule('preserveCodeBlocks', {
  filter: ['pre'],
  replacement: function (content, node) {
    const codeElement = node.querySelector('code');
    const language = codeElement?.className?.match(/language-(\w+)/)?.[1] || '';
    const code = codeElement?.textContent || content;
    return `\n\`\`\`${language}\n${code}\n\`\`\`\n`;
  }
});

turndownService.addRule('preserveLineBreaks', {
  filter: 'br',
  replacement: function () {
    return '\n';
  }
});

/**
 * Convert markdown to HTML using the same system as MarkdownRenderer
 * This ensures consistent rendering between preview and editor
 */
export function markdownToHtml(markdown: string): string {
  try {
    if (!markdown?.trim()) {
      return '';
    }

    // Use react-markdown to convert markdown to React elements,
    // then render to static HTML for consistency
    const markdownElement = createElement(ReactMarkdown, {
      remarkPlugins: [remarkGfm],
      components: {
        // Simplified components that match MarkdownRenderer behavior
        h1: ({ children }) => createElement('h1', {}, children),
        h2: ({ children }) => createElement('h2', {}, children),
        h3: ({ children }) => createElement('h3', {}, children),
        p: ({ children }) => createElement('p', {}, children),
        strong: ({ children }) => createElement('strong', {}, children),
        em: ({ children }) => createElement('em', {}, children),
        code: ({ children, className }: { children?: React.ReactNode; className?: string }) => {
          const inline = !className?.includes('language-');
          if (inline) {
            return createElement('code', {}, children);
          }
          const language = className?.replace('language-', '') || '';
          return createElement('pre', {}, 
            createElement('code', { className: `language-${language}` }, children)
          );
        },
        blockquote: ({ children }) => createElement('blockquote', {}, children),
        ul: ({ children }) => createElement('ul', {}, children),
        ol: ({ children }) => createElement('ol', {}, children),
        li: ({ children }) => createElement('li', {}, children),
        a: ({ href, children }) => createElement('a', { href, target: '_blank', rel: 'noopener noreferrer' }, children),
        hr: () => createElement('hr'),
        del: ({ children }) => createElement('del', {}, children),
      }
    }, markdown);

    // Render to static HTML
    const html = renderToStaticMarkup(markdownElement);
    return html;
  } catch (error) {
    console.warn('Markdown to HTML conversion failed:', error);
    // Fallback: return safely escaped content
    return `<p>${escapeHtml(markdown)}</p>`;
  }
}

/**
 * Convert HTML back to markdown using TurndownService
 * Maintains formatting consistency for round-trip conversion
 */
export function htmlToMarkdown(html: string): string {
  try {
    if (!html?.trim()) {
      return '';
    }

    return turndownService.turndown(html).trim();
  } catch (error) {
    console.warn('HTML to Markdown conversion failed:', error);
    // Fallback: return cleaned text content
    return stripHtmlTags(html);
  }
}

/**
 * Synchronous markdown to HTML conversion for TipTap editor
 * Uses simplified but reliable conversion for real-time editing
 */
export function markdownToHtmlSync(markdown: string): string {
  try {
    if (!markdown?.trim()) {
      return '';
    }

    // Use the async version but handle it synchronously for editor use
    // This ensures consistency with the preview
    return markdownToHtml(markdown);
  } catch (error) {
    console.warn('Synchronous markdown conversion failed:', error);
    return `<p>${escapeHtml(markdown)}</p>`;
  }
}

/**
 * Escape HTML characters for safe rendering
 */
function escapeHtml(text: string): string {
  if (typeof document !== 'undefined') {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
  
  // Server-side fallback
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * Strip HTML tags and return plain text
 */
function stripHtmlTags(html: string): string {
  if (typeof document !== 'undefined') {
    const div = document.createElement('div');
    div.innerHTML = html;
    return div.textContent || div.innerText || '';
  }
  
  // Server-side fallback
  return html.replace(/<[^>]*>/g, '');
}

/**
 * Validate and clean markdown content
 */
export function validateMarkdown(markdown: string): { isValid: boolean; cleaned: string; errors: string[] } {
  const errors: string[] = [];
  let cleaned = markdown;
  
  try {
    // Basic validation
    if (!markdown || typeof markdown !== 'string') {
      errors.push('Invalid markdown content');
      return { isValid: false, cleaned: '', errors };
    }
    
    // Clean up common issues
    cleaned = cleaned.trim();
    
    // Remove excessive whitespace
    cleaned = cleaned.replace(/\n{3,}/g, '\n\n');
    
    // Validate code blocks are properly closed
    const codeBlocks = cleaned.match(/```/g);
    if (codeBlocks && codeBlocks.length % 2 !== 0) {
      errors.push('Unclosed code block detected');
    }
    
    // Validate link syntax
    const invalidLinks = cleaned.match(/\[[^\]]*\]\([^)]*$/g);
    if (invalidLinks) {
      errors.push('Invalid link syntax detected');
    }
    
    return {
      isValid: errors.length === 0,
      cleaned,
      errors
    };
  } catch (error) {
    errors.push(`Validation error: ${error}`);
    return { isValid: false, cleaned: markdown, errors };
  }
}

/**
 * Get markdown processing statistics
 */
export function getMarkdownStats(markdown: string): {
  wordCount: number;
  lineCount: number;
  characterCount: number;
  headingCount: number;
  linkCount: number;
  codeBlockCount: number;
} {
  const lines = markdown.split('\n');
  const words = markdown.split(/\s+/).filter(word => word.length > 0);
  const headings = markdown.match(/^#+\s/gm) || [];
  const links = markdown.match(/\[([^\]]+)\]\(([^)]+)\)/g) || [];
  const codeBlocks = markdown.match(/```[\s\S]*?```/g) || [];

  return {
    wordCount: words.length,
    lineCount: lines.length,
    characterCount: markdown.length,
    headingCount: headings.length,
    linkCount: links.length,
    codeBlockCount: codeBlocks.length
  };
}