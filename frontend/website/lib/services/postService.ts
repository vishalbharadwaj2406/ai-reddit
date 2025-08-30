import { apiClient, endpoints } from '../api/client';

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

export interface ForkPostRequest {
  original_post_id: string;
  title?: string;
  content?: string;
}

// Custom error class
export class PostServiceError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'PostServiceError';
  }
}

class PostService {
  /**
   * Wraps errors to provide consistent error handling
   */
  private wrapError(err: unknown, defaultMessage: string): never {
    if (err instanceof Error) {
      throw new PostServiceError(err.message);
    }
    throw new PostServiceError(defaultMessage);
  }

  /**
   * Create a new post from blog content
   */
  async createPost(data: CreatePostRequest): Promise<Post> {
    try {
      const response = await apiClient.post<Post>(
        endpoints.posts.create,
        { ...data, content_type: data.content_type || 'markdown' }
      );
      return response;
    } catch (err) {
      this.wrapError(err, 'Failed to create post');
    }
  }

  /**
   * Get user's posts
   */
  async getPosts(limit = 20, offset = 0): Promise<PostListResponse> {
    try {
      const response = await apiClient.get<PostListResponse>(
        endpoints.posts.list,
        { limit: limit.toString(), offset: offset.toString() }
      );
      return response;
    } catch (err) {
      this.wrapError(err, 'Failed to load posts');
    }
  }

  /**
   * Get specific post by ID
   */
  async getPost(postId: string): Promise<Post> {
    try {
      const response = await apiClient.get<Post>(
        endpoints.posts.getById(postId)
      );
      return response;
    } catch (err) {
      this.wrapError(err, 'Failed to load post');
    }
  }

  /**
   * Fork an existing post
   */
  async forkPost(data: ForkPostRequest): Promise<Post> {
    try {
      const response = await apiClient.post<Post>(
        endpoints.posts.fork(data.original_post_id),
        data
      );
      return response;
    } catch (err) {
      this.wrapError(err, 'Failed to fork post');
    }
  }

  /**
   * Delete a post
   */
  async deletePost(postId: string): Promise<void> {
    try {
      await apiClient.delete(endpoints.posts.getById(postId));
    } catch (err) {
      this.wrapError(err, 'Failed to delete post');
    }
  }

  /**
   * Update post status
   */
  async updatePostStatus(postId: string, status: 'draft' | 'published' | 'archived'): Promise<Post> {
    try {
      const response = await apiClient.patch<Post>(
        endpoints.posts.getById(postId),
        { status }
      );
      return response;
    } catch (err) {
      this.wrapError(err, 'Failed to update post status');
    }
  }

  /**
   * Publish blog content as a post
   */
  async publishBlogAsPost(content: string, title: string): Promise<Post> {
    try {
      const response = await apiClient.post<Post>(
        endpoints.posts.create,
        {
          title,
          content,
          content_type: 'markdown',
          post_type: 'original',
          status: 'published'
        }
      );
      return response;
    } catch (err) {
      this.wrapError(err, 'Failed to publish blog as post');
    }
  }
}

// Export singleton instance
export const postService = new PostService();
export default postService;
