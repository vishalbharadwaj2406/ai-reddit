import { apiClient, endpoints } from '../config/api';

// Type definitions for posts
export interface Post {
  post_id: string;
  user_id: string;
  title: string;
  content: string;
  content_type: 'text' | 'markdown' | 'html';
  post_type: 'original' | 'fork';
  status: 'draft' | 'published' | 'archived';
  created_at: string;
  updated_at: string;
  fork_count?: number;
  original_post_id?: string;
}

export interface CreatePostRequest {
  title: string;
  content: string;
  content_type?: 'markdown' | 'text' | 'html';
  post_type?: 'original' | 'fork';
  original_post_id?: string;
}

export interface PostListResponse {
  posts: Post[];
  total: number;
  has_more: boolean;
}

// Error types
export class PostServiceError extends Error {
  constructor(message: string, public code?: string) {
    super(message);
    this.name = 'PostServiceError';
  }
}

// Post Service
export class PostService {
  
  /**
   * Create a new post from blog content
   */
  async createPost(data: CreatePostRequest): Promise<Post> {
    try {
      const response = await apiClient.post<Post>(
        endpoints.posts.create,
        {
          ...data,
          content_type: data.content_type || 'markdown'
        }
      );
      
      if (response.success) {
        return response.data;
      }
      
      throw new PostServiceError(
        response.message || 'Failed to create post'
      );
      
    } catch (error: any) {
      if (error instanceof PostServiceError) {
        throw error;
      }
      
      throw new PostServiceError(
        `Failed to create post: ${error.message}`
      );
    }
  }

  /**
   * Get user's posts
   */
  async getPosts(limit = 20, offset = 0): Promise<PostListResponse> {
    try {
      const response = await apiClient.get<PostListResponse>(
        endpoints.posts.list,
        { 
          limit: limit.toString(), 
          offset: offset.toString() 
        }
      );
      
      if (response.success) {
        return response.data;
      }
      
      throw new PostServiceError(
        response.message || 'Failed to fetch posts'
      );
      
    } catch (error: any) {
      if (error instanceof PostServiceError) {
        throw error;
      }
      
      throw new PostServiceError(
        `Failed to load posts: ${error.message}`
      );
    }
  }

  /**
   * Get a specific post by ID
   */
  async getPost(postId: string): Promise<Post> {
    try {
      const response = await apiClient.get<Post>(
        endpoints.posts.getById(postId)
      );
      
      if (response.success) {
        return response.data;
      }
      
      throw new PostServiceError(
        response.message || 'Failed to fetch post'
      );
      
    } catch (error: any) {
      if (error instanceof PostServiceError) {
        throw error;
      }
      
      throw new PostServiceError(
        `Failed to load post: ${error.message}`
      );
    }
  }

  /**
   * Fork an existing post
   */
  async forkPost(postId: string, content: string, title?: string): Promise<Post> {
    try {
      const response = await apiClient.post<Post>(
        endpoints.posts.fork(postId),
        {
          content,
          title: title || 'Forked Conversation',
          content_type: 'markdown'
        }
      );
      
      if (response.success) {
        return response.data;
      }
      
      throw new PostServiceError(
        response.message || 'Failed to fork post'
      );
      
    } catch (error: any) {
      if (error instanceof PostServiceError) {
        throw error;
      }
      
      throw new PostServiceError(
        `Failed to fork post: ${error.message}`
      );
    }
  }

  /**
   * Convert blog content to a publishable post format
   */
  async publishBlogAsPost(
    blogContent: string, 
    title: string, 
    conversationId?: string
  ): Promise<Post> {
    try {
      // Clean up the blog content for publishing
      const cleanContent = this.cleanBlogContent(blogContent);
      
      // Generate a post title if not provided
      const postTitle = title || this.generateTitleFromContent(cleanContent);
      
      const postData: CreatePostRequest = {
        title: postTitle,
        content: cleanContent,
        content_type: 'markdown',
        post_type: 'original'
      };
      
      return await this.createPost(postData);
      
    } catch (error: any) {
      if (error instanceof PostServiceError) {
        throw error;
      }
      
      throw new PostServiceError(
        `Failed to publish blog as post: ${error.message}`
      );
    }
  }

  /**
   * Clean blog content for publishing
   */
  private cleanBlogContent(content: string): string {
    return content
      .trim()
      // Remove excessive newlines
      .replace(/\n{3,}/g, '\n\n')
      // Ensure proper heading spacing
      .replace(/^(#{1,3})\s*(.+)$/gm, '$1 $2')
      // Clean up list formatting
      .replace(/^\s*[-*+]\s+/gm, '- ')
      .replace(/^\s*(\d+)\.\s+/gm, '$1. ');
  }

  /**
   * Generate title from blog content
   */
  private generateTitleFromContent(content: string): string {
    // Try to extract first heading
    const headingMatch = content.match(/^#+\s*(.+)$/m);
    if (headingMatch) {
      return headingMatch[1].trim();
    }
    
    // Fallback to first line/sentence
    const firstLine = content.split('\n')[0].trim();
    if (firstLine.length > 0) {
      // Truncate if too long
      return firstLine.length > 60 
        ? firstLine.substring(0, 57) + '...'
        : firstLine;
    }
    
    return 'Untitled Post';
  }
}

// Export singleton instance
export const postService = new PostService();
