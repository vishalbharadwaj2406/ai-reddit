/**
 * Blog Generation Hook
 * Production-grade hook for managing AI blog generation workflow
 */

import { useState, useCallback } from 'react';
import { conversationService, Message } from '@/lib/services/conversationService';
import { useErrorHandling } from './useErrorHandling';

export interface UseBlogGenerationReturn {
  // State
  isGeneratingBlog: boolean;
  blogGenerationProgress: number;
  
  // Actions
  generateBlogPost: (
    conversationId: string,
    additionalContext: string,
    onMessageAdded: (message: Message) => void,
    onMessageUpdated: (content: string) => void,
    onProgressUpdate?: (progress: number) => void
  ) => Promise<void>;
  
  // Error handling
  error: string | null;
  clearError: () => void;
}

/**
 * Hook for managing AI blog post generation with streaming and progress tracking
 */
export const useBlogGeneration = (): UseBlogGenerationReturn => {
  const [isGeneratingBlog, setIsGeneratingBlog] = useState(false);
  const [blogGenerationProgress, setBlogGenerationProgress] = useState(0);
  const { error, handleError, clearError } = useErrorHandling();

  const generateBlogPost = useCallback(async (
    conversationId: string,
    additionalContext: string,
    onMessageAdded: (message: Message) => void,
    onMessageUpdated: (content: string) => void,
    onProgressUpdate?: (progress: number) => void
  ) => {
    try {
      setIsGeneratingBlog(true);
      setBlogGenerationProgress(0);
      clearError();
      
      // Create placeholder blog message immediately for better UX
      const blogMessage: Message = {
        messageId: `blog-${Date.now()}`,
        role: 'assistant',
        content: 'Starting blog generation...',
        isBlog: true,
        createdAt: new Date().toISOString(),
      };
      
      onMessageAdded(blogMessage);
      
      // Simulate initial progress
      setBlogGenerationProgress(10);
      onProgressUpdate?.(10);
      
      // Request blog generation from the AI service
      await conversationService.generateBlogFromConversation(
        conversationId,
        additionalContext,
        // onChunk: Update blog content as it streams
        (chunk: string) => {
          onMessageUpdated(chunk);
          
          // Estimate progress based on content length (rough heuristic)
          const estimatedProgress = Math.min(90, 10 + (chunk.length / 50));
          setBlogGenerationProgress(estimatedProgress);
          onProgressUpdate?.(estimatedProgress);
        },
        // onComplete: Finalize blog generation
        (fullBlogContent: string, messageId: string) => {
          setBlogGenerationProgress(100);
          onProgressUpdate?.(100);
          onMessageUpdated(fullBlogContent);
          setIsGeneratingBlog(false);
          
          // Reset progress after a short delay for UX
          setTimeout(() => {
            setBlogGenerationProgress(0);
          }, 2000);
        },
        // onError: Handle blog generation errors
        (errorMessage: string) => {
          console.error('Blog generation error:', errorMessage);
          setIsGeneratingBlog(false);
          setBlogGenerationProgress(0);
          onProgressUpdate?.(0);
          
          // Update the blog message with error state
          onMessageUpdated(
            'Sorry, I encountered an error while generating the blog post. Please try again.'
          );
          
          handleError(new Error(errorMessage));
        }
      );
      
    } catch (err) {
      console.error('Failed to generate blog post:', err);
      handleError(err);
      setIsGeneratingBlog(false);
      setBlogGenerationProgress(0);
      onProgressUpdate?.(0);
      
      // Update the blog message with error state
      onMessageUpdated(
        'Sorry, I encountered an error while generating the blog post. Please try again.'
      );
    }
  }, [handleError, clearError]);

  return {
    // State
    isGeneratingBlog,
    blogGenerationProgress,
    
    // Actions
    generateBlogPost,
    
    // Error handling
    error,
    clearError,
  };
};
