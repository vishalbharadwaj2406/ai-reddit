/**
 * Message Content Extraction Utilities
 * 
 * Production-grade utilities for extracting display-ready content
 * from different message types, especially blog messages with JSON content.
 */

import { Message } from '@/lib/services/conversationService';
import { parseBlogContent } from './blogParser';
import { markdownToPlain } from './markdown';

/**
 * Extract display-ready plain text content from any message
 * Handles special formatting for blog messages
 */
export function getDisplayContent(message: Message): string {
  if (!message.content) {
    return '';
  }

  // Handle blog messages specially
  if (message.isBlog) {
    const parsedBlog = parseBlogContent(message.content);
    
    if (parsedBlog.isValid) {
      // Format as readable blog content
      const lines: string[] = [];
      
      // Add title
      if (parsedBlog.title) {
        lines.push(parsedBlog.title);
        lines.push(''); // Empty line after title
      }
      
      // Add tags if present
      if (parsedBlog.tags.length > 0) {
        lines.push(`Tags: ${parsedBlog.tags.join(', ')}`);
        lines.push(''); // Empty line after tags
      }
      
      // Add content
      if (parsedBlog.content) {
        lines.push(parsedBlog.content);
      }
      
      return lines.join('\n').trim();
    }
    
    // Fallback: treat as regular content if parsing fails
    return markdownToPlain(message.content);
  }

  // Regular messages: convert from markdown to plain text
  return markdownToPlain(message.content);
}

/**
 * Extract markdown-formatted content from any message
 * Preserves markdown formatting for blog messages
 */
export function getMarkdownContent(message: Message): string {
  if (!message.content) {
    return '';
  }

  // Handle blog messages specially
  if (message.isBlog) {
    const parsedBlog = parseBlogContent(message.content);
    
    if (parsedBlog.isValid) {
      // Format as markdown blog content
      const lines: string[] = [];
      
      // Add title as H1
      if (parsedBlog.title) {
        lines.push(`# ${parsedBlog.title}`);
        lines.push(''); // Empty line after title
      }
      
      // Add tags as a list if present
      if (parsedBlog.tags.length > 0) {
        lines.push(`**Tags:** ${parsedBlog.tags.join(', ')}`);
        lines.push(''); // Empty line after tags
      }
      
      // Add content (already in markdown format)
      if (parsedBlog.content) {
        lines.push(parsedBlog.content);
      }
      
      return lines.join('\n').trim();
    }
    
    // Fallback: return raw content if parsing fails
    return message.content;
  }

  // Regular messages: return as-is (already markdown)
  return message.content;
}

/**
 * Get a preview/summary of message content
 * Useful for tooltips or short descriptions
 */
export function getContentPreview(message: Message, maxLength: number = 100): string {
  const content = getDisplayContent(message);
  
  if (content.length <= maxLength) {
    return content;
  }
  
  // Find a good break point (end of sentence or word)
  const truncated = content.substring(0, maxLength);
  const lastSentence = truncated.lastIndexOf('. ');
  const lastWord = truncated.lastIndexOf(' ');
  
  if (lastSentence > maxLength * 0.7) {
    return truncated.substring(0, lastSentence + 1).trim();
  } else if (lastWord > maxLength * 0.8) {
    return truncated.substring(0, lastWord).trim() + '...';
  } else {
    return truncated.trim() + '...';
  }
}