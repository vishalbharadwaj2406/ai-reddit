/**
 * Centralized Error Handling Hook
 * Production-grade error handling for conversation features
 */

import { useState, useCallback } from 'react';
import { AuthenticationRequiredError, ConversationServiceError } from '@/lib/services/conversationService';

export interface ErrorState {
  error: string | null;
  isError: boolean;
  clearError: () => void;
  handleError: (err: unknown) => void;
}

/**
 * Centralized error handling hook for conversation features
 * Provides consistent error message extraction and state management
 */
export const useErrorHandling = (): ErrorState => {
  const [error, setError] = useState<string | null>(null);

  const getErrorMessage = useCallback((err: unknown): string => {
    // Handle PostServiceError (our custom errors)
    if (err && typeof err === 'object' && 'name' in err && (err as any).name === 'PostServiceError') {
      return (err as Error).message;
    }
    
    // Handle ApiError (from API client)
    if (err && typeof err === 'object' && 'name' in err && (err as any).name === 'ApiError') {
      return (err as Error).message;
    }
    
    // Handle AuthenticationRequiredError
    if (err instanceof AuthenticationRequiredError) {
      return 'Please sign in to continue';
    }
    
    // Handle ConversationServiceError
    if (err instanceof ConversationServiceError) {
      return err.message;
    }
    
    // Handle standard Error instances
    if (err instanceof Error) {
      return err.message;
    }
    
    // Handle string errors
    if (typeof err === 'string') {
      return err;
    }
    
    // Handle structured error objects
    if (err && typeof err === 'object') {
      const errorObj = err as any;
      
      // Try various error message locations
      if (errorObj.message) return errorObj.message;
      if (errorObj.detail?.message) return errorObj.detail.message;
      if (errorObj.detail && typeof errorObj.detail === 'string') return errorObj.detail;
      if (errorObj.error) return errorObj.error;
      
      // For validation errors array
      if (Array.isArray(errorObj.detail) && errorObj.detail.length > 0) {
        const firstError = errorObj.detail[0];
        if (firstError?.msg) {
          return firstError.msg;
        }
      }
      
      // Last resort: stringify the object
      try {
        return JSON.stringify(errorObj);
      } catch {
        return 'Invalid error object';
      }
    }
    
    // Ultimate fallback
    return 'An unknown error occurred';
  }, []);

  const handleError = useCallback((err: unknown) => {
    const errorMessage = getErrorMessage(err);
    setError(errorMessage);
    
    // Log error in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error handled by useErrorHandling:', err);
    }
  }, [getErrorMessage]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    error,
    isError: error !== null,
    clearError,
    handleError,
  };
};
