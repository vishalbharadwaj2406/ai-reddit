/**
 * Production-Grade Session Guard Component
 * 
 * Provides secure route protection with proper loading states, error handling,
 * and seamless user experience for both public and protected routes.
 */

'use client';

import React from 'react';
import { useSessionContext } from '../providers/SessionWrapper';

interface SessionGuardProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  requireAuth?: boolean;
  loadingComponent?: React.ReactNode;
}

/**
 * Production-grade Loading Spinner with proper accessibility
 */
function LoadingSpinner({ size = 'md', message = 'Loading...' }: { 
  size?: 'sm' | 'md' | 'lg'; 
  message?: string;
}) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8', 
    lg: 'w-12 h-12'
  };

  return (
    <div className="flex flex-col items-center justify-center p-8" role="status" aria-live="polite">
      <div 
        className={`${sizeClasses[size]} animate-spin rounded-full border-2 border-gray-300 border-t-blue-600`}
        aria-hidden="true"
      />
      <span className="sr-only">{message}</span>
      <p className="mt-2 text-sm text-gray-600">{message}</p>
    </div>
  );
}

/**
 * Production SessionGuard Component
 * 
 * Handles all authentication states with proper error boundaries and loading states.
 * 
 * @param children - Components to render when authenticated
 * @param fallback - Custom fallback for unauthenticated users
 * @param requireAuth - Whether authentication is required (default: true)
 * @param loadingComponent - Custom loading component
 */
export default function SessionGuard({ 
  children, 
  fallback = null,
  requireAuth = true,
  loadingComponent
}: SessionGuardProps) {
  const { isAuthenticated, loading, error, isInitialized } = useSessionContext();

  // Show loading state while session is being initialized
  if (!isInitialized || loading) {
    return loadingComponent || (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" message="Initializing session..." />
      </div>
    );
  }

  // Handle session errors gracefully
  if (error && requireAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <h2 className="text-xl font-semibold text-red-600 mb-2">
            Session Error
          </h2>
          <p className="text-gray-600 mb-4">
            {error}
          </p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Handle unauthenticated users on protected routes
  if (requireAuth && !isAuthenticated) {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Authentication Required
          </h2>
          <p className="text-gray-600 mb-4">
            Please sign in to access this page.
          </p>
          <button 
            onClick={() => window.location.href = '/api/v1/auth/google'} 
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Sign In
          </button>
        </div>
      </div>
    );
  }

  // Render protected content - session is fully initialized and valid
  return <>{children}</>;
}
