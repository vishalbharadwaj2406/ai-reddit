/**
 * Tag Service
 * 
 * Frontend service for managing tags including fetching existing tags,
 * normalization, and caching.
 */

import { apiClient } from '../api/client';

export interface Tag {
  tagId: string;
  name: string;
  postCount: number;
}

export interface TagsResponse {
  success: boolean;
  data: {
    tags: Tag[];
  };
  message: string;
}

class TagService {
  private cachedTags: Tag[] | null = null;
  private lastFetch: number = 0;
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  /**
   * Normalize tag name according to backend rules
   * - Convert to lowercase
   * - Strip whitespace
   * - Replace spaces with hyphens
   */
  normalizeTagName(name: string): string {
    if (!name) {
      return '';
    }
    
    const normalized = name.trim().toLowerCase();
    // Replace spaces and multiple spaces with single hyphen
    return normalized.split(/\s+/).join('-');
  }

  /**
   * Get display name from normalized tag name
   * Always returns the hyphenated lowercase format
   */
  getDisplayName(normalizedName: string): string {
    return normalizedName;
  }

  /**
   * Fetch all tags from backend with caching
   */
  async getAllTags(forceRefresh = false): Promise<Tag[]> {
    const now = Date.now();
    
    // Return cached tags if still valid and not forced refresh
    if (!forceRefresh && this.cachedTags && (now - this.lastFetch) < this.CACHE_DURATION) {
      return this.cachedTags;
    }

    try {
      const response = await apiClient.get<TagsResponse>('/api/v1/tags');
      
      if (response.success && response.data?.tags) {
        this.cachedTags = response.data.tags;
        this.lastFetch = now;
        return this.cachedTags;
      } else {
        throw new Error(response.message || 'Failed to fetch tags');
      }
    } catch (error) {
      console.error('Failed to fetch tags:', error);
      
      // Return cached tags as fallback if available
      if (this.cachedTags) {
        return this.cachedTags;
      }
      
      // Return empty array as final fallback
      return [];
    }
  }

  /**
   * Search tags by normalized name
   */
  async searchTags(query: string, limit = 5): Promise<Tag[]> {
    const allTags = await this.getAllTags();
    const normalizedQuery = this.normalizeTagName(query);
    
    if (!normalizedQuery) {
      return allTags.slice(0, limit);
    }

    // Filter tags that match the normalized query
    const matchingTags = allTags.filter(tag => 
      tag.name.includes(normalizedQuery)
    );

    // Sort by relevance: exact match first, then starts with, then contains
    const sorted = matchingTags.sort((a, b) => {
      if (a.name === normalizedQuery && b.name !== normalizedQuery) return -1;
      if (b.name === normalizedQuery && a.name !== normalizedQuery) return 1;
      if (a.name.startsWith(normalizedQuery) && !b.name.startsWith(normalizedQuery)) return -1;
      if (b.name.startsWith(normalizedQuery) && !a.name.startsWith(normalizedQuery)) return 1;
      return b.postCount - a.postCount; // Then by popularity
    });

    return sorted.slice(0, limit);
  }

  /**
   * Check if a normalized tag name exists
   */
  async tagExists(normalizedName: string): Promise<Tag | null> {
    const allTags = await this.getAllTags();
    return allTags.find(tag => tag.name === normalizedName) || null;
  }

  /**
   * Validate and normalize a list of tag names
   * Returns array of objects with normalized names and validation status
   */
  async validateTags(tagNames: string[]): Promise<Array<{
    original: string;
    normalized: string;
    exists: boolean;
    tag?: Tag;
  }>> {
    const allTags = await this.getAllTags();
    const tagMap = new Map(allTags.map(tag => [tag.name, tag]));

    return tagNames.map(tagName => {
      const normalized = this.normalizeTagName(tagName);
      const exists = tagMap.has(normalized);
      
      return {
        original: tagName,
        normalized,
        exists,
        tag: exists ? tagMap.get(normalized) : undefined
      };
    });
  }

  /**
   * Clear cache (useful after creating new tags)
   */
  clearCache(): void {
    this.cachedTags = null;
    this.lastFetch = 0;
  }
}

// Export singleton instance
export const tagService = new TagService();