/**
 * Service Error Types - Production-grade error handling
 */

import { ApiError } from '@/lib/api/client';

// Base service error class
export class ServiceError extends Error {
  constructor(
    message: string,
    public readonly cause?: unknown,
    public readonly code?: string
  ) {
    super(message);
    this.name = this.constructor.name;
  }
}

// Post service specific errors
export class PostServiceError extends ServiceError {
  constructor(message: string, cause?: unknown, code?: string) {
    super(message, cause, code);
  }
}

// Type guards for error handling
export function isApiError(error: unknown): error is ApiError {
  return error instanceof Error && error.name === 'ApiError';
}

export function isServiceError(error: unknown): error is ServiceError {
  return error instanceof ServiceError;
}

// Error extraction utilities
export interface ErrorLike {
  message?: string;
  detail?: string | { message?: string };
  error?: string;
}

export function extractErrorMessage(error: unknown, fallback: string): string {
  if (isApiError(error)) {
    return error.message;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  if (error && typeof error === 'object') {
    const errorObj = error as ErrorLike;
    
    if (errorObj.message) {
      return errorObj.message;
    }
    
    if (typeof errorObj.detail === 'string') {
      return errorObj.detail;
    }
    
    if (errorObj.detail && typeof errorObj.detail === 'object' && errorObj.detail.message) {
      return errorObj.detail.message;
    }
    
    if (errorObj.error) {
      return errorObj.error;
    }
    
    // Last resort - stringify the object
    try {
      return JSON.stringify(errorObj);
    } catch {
      // If stringify fails, use fallback
    }
  }
  
  return fallback;
}
