import { apiClient, endpoints } from '../api/client';
import { PostServiceError, extractErrorMessage } from '@/types/service-errors';
import type { ConversationDetail } from './conversationService';

// Type definitions for posts with comprehensive backend alignment
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

// Backend API response schemas
export interface PostCreateResponse {
  postId: string;
  title: string;
  content: string;
  createdAt: string;
}

// Standard API response wrapper (matches backend)
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
  errorCode?: string;
}

// FastAPI error response formats
export interface FastAPIErrorDetail {
  success: false;
  data: null;
  message: string;
  errorCode: string;
}

export interface FastAPIErrorResponse {
  detail: FastAPIErrorDetail | string | Array<{
    msg: string;
    type: string;
    loc: Array<string | number>;
  }>;
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

class PostService {
  /**
   * Wraps errors to provide consistent error handling with type safety
   */
  private wrapError(err: unknown, defaultMessage: string): never {
    const errorMessage = extractErrorMessage(err, defaultMessage);
    throw new PostServiceError(errorMessage, err);
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
      const response = await apiClient.get<ApiResponse<PostListResponse>>(
        endpoints.posts.list,
        { limit: limit.toString(), offset: offset.toString() }
      );
      return response.data;
    } catch (err) {
      this.wrapError(err, 'Failed to load posts');
    }
  }

  /**
   * Get specific post by ID
   */
  async getPost(postId: string): Promise<Post> {
    try {
      const response = await apiClient.get<ApiResponse<Post>>(
        endpoints.posts.getById(postId)
      );
      return response.data;
    } catch (err) {
      this.wrapError(err, 'Failed to load post');
    }
  }

  /**
   * Get public posts feed
   */
  async getPublicPosts(params: {
    limit?: number;
    offset?: number;
    sort?: 'hot' | 'new' | 'top';
    time_range?: 'hour' | 'day' | 'week' | 'month' | 'all';
    tag?: string;
  } = {}): Promise<PostListResponse> {
    try {
      const queryParams: Record<string, string> = {};
      
      if (params.limit) queryParams.limit = params.limit.toString();
      if (params.offset) queryParams.offset = params.offset.toString();
      if (params.sort) queryParams.sort = params.sort;
      if (params.time_range) queryParams.time_range = params.time_range;
      if (params.tag) queryParams.tag = params.tag;
      
      const response = await apiClient.get<ApiResponse<PostListResponse>>(
        endpoints.posts.list,
        queryParams
      );
      return response.data;
    } catch (err) {
      this.wrapError(err, 'Failed to load public posts');
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
   * Add or update reaction to a post
   */
  async addPostReaction(postId: string, reactionType: 'upvote' | 'downvote' | 'heart' | 'insightful' | 'accurate'): Promise<void> {
    try {
      await apiClient.post(
        `${endpoints.posts.getById(postId)}/reaction`,
        { reactionType }
      );
    } catch (err) {
      this.wrapError(err, 'Failed to add reaction');
    }
  }

  /**
   * Track post view
   */
  async trackPostView(postId: string): Promise<void> {
    try {
      await apiClient.post(`${endpoints.posts.getById(postId)}/view`);
    } catch (err) {
      // Don't throw error for view tracking - it's not critical
      console.warn('Failed to track post view:', err);
    }
  }

  /**
   * Share a post
   */
  async sharePost(postId: string, platform: string): Promise<void> {
    try {
      await apiClient.post(
        `${endpoints.posts.getById(postId)}/share`,
        { platform }
      );
    } catch (err) {
      this.wrapError(err, 'Failed to share post');
    }
  }

  /**
   * Get post conversation (if viewable)
   */
  async getPostConversation(postId: string): Promise<ConversationDetail> {
    try {
      const response = await apiClient.get<ApiResponse<ConversationDetail>>(
        `${endpoints.posts.getById(postId)}/conversation`
      );
      return response.data;
    } catch (err) {
      this.wrapError(err, 'Failed to load conversation');
    }
  }

  /**
   * Publish blog content as a post
   * Production-grade implementation with comprehensive error handling
   */
  async publishBlogAsPost(
    content: string, 
    title: string, 
    messageId?: string,
    tags: string[] = []
  ): Promise<Post> {
    const operationId = `publish-${Date.now()}`;
    
    try {
      // Validate inputs
      if (!title?.trim()) {
        throw new PostServiceError('Post title is required and cannot be empty');
      }
      
      if (!content?.trim()) {
        throw new PostServiceError('Post content is required and cannot be empty');
      }
      
      // Prepare payload according to backend schema
      const payload = {
        messageId: messageId || null,
        title: title.trim(),
        content: content.trim(),
        tags: tags.filter(tag => tag?.trim()).map(tag => tag.trim()),
        isConversationVisible: true
      };
      
      // Development logging
      if (process.env.NODE_ENV === 'development') {
        console.group(`📤 Publishing Post [${operationId}]`);
        console.log('Endpoint:', endpoints.posts.create);
        console.log('Payload:', payload);
        console.log('Payload size:', JSON.stringify(payload).length, 'bytes');
        console.groupEnd();
      }
      
      // Make API request
      const response = await apiClient.post<ApiResponse<PostCreateResponse>>(
        endpoints.posts.create,
        payload
      );
      
      // Development response logging
      if (process.env.NODE_ENV === 'development') {
        console.group(`📥 Post Response [${operationId}]`);
        console.log('Response:', response);
        console.log('Success:', response?.success);
        console.groupEnd();
      }
      
      // Validate response structure
      if (!response || typeof response !== 'object') {
        throw new PostServiceError('Invalid response format from server');
      }
      
      if (!response.success || !response.data) {
        const errorMsg = response.message || 'Post creation failed';
        throw new PostServiceError(errorMsg);
      }
      
      // Extract and validate post data
      const postData = response.data;
      if (!postData.postId || !postData.title || !postData.content) {
        throw new PostServiceError('Incomplete post data received from server');
      }
      
      // Map response to frontend Post interface
      const post: Post = {
        post_id: postData.postId,
        user_id: '', // Will be populated by backend response in full implementation
        title: postData.title,
        content: postData.content,
        content_type: 'markdown',
        post_type: 'original',
        status: 'published',
        created_at: postData.createdAt,
        updated_at: postData.createdAt
      };
      
      // Success logging
      if (process.env.NODE_ENV === 'development') {
        console.log(`✅ Post published successfully [${operationId}]:`, post.post_id);
      }
      
      return post;
      
    } catch (err) {
      // Comprehensive error logging
      if (process.env.NODE_ENV === 'development') {
        console.group(`❌ Post Publication Failed [${operationId}]`);
        console.log('Error type:', err?.constructor?.name || typeof err);
        console.log('Error details:', err);
        if (err instanceof Error) {
          console.log('Error message:', err.message);
          console.log('Error stack:', err.stack);
        }
        console.groupEnd();
      }
      
      // Production error monitoring (placeholder for monitoring service)
      if (process.env.NODE_ENV === 'production') {
        // TODO: Integrate with monitoring service (Sentry, LogRocket, etc.)
        console.error(`Post publication failed [${operationId}]:`, {
          error: err instanceof Error ? err.message : String(err),
          title: title?.substring(0, 50),
          contentLength: content?.length,
          messageId,
          tags
        });
      }
      
      // Re-throw with proper error handling
      this.wrapError(err, 'Failed to publish blog as post');
    }
  }
}

// Export singleton instance
export const postService = new PostService();
export default postService;
