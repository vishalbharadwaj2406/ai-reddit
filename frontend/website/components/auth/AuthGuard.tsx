/**
 * Production-Grade Authentication Guard
 * 
 * Protects pages that require authentication.
 * Provides loading states and graceful authentication handling.
 */

'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { signInWithGoogle } from '../../lib/auth/auth.utils';

interface AuthGuardProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  redirectTo?: string;
  requireAuth?: boolean;
}

export default function AuthGuard({ 
  children, 
  fallback, 
  redirectTo = '/',
  requireAuth = true 
}: AuthGuardProps) {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [showSignIn, setShowSignIn] = useState(false);

  useEffect(() => {
    if (status === 'loading') return; // Still loading

    if (requireAuth && !session) {
      // Show sign-in UI instead of redirecting
      setShowSignIn(true);
    } else if (!requireAuth && session) {
      // User is signed in but page doesn't require auth, redirect
      router.push(redirectTo);
    }
  }, [session, status, requireAuth, redirectTo, router]);

  const handleSignIn = async () => {
    try {
      await signInWithGoogle();
    } catch (error) {
      console.error('Sign in failed:', error);
    }
  };

  // Loading state
  if (status === 'loading') {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  // Show sign-in UI if authentication required but user not signed in
  if (requireAuth && !session && showSignIn) {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8 p-8">
          <div className="text-center">
            <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
              Sign in to continue
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              You need to be signed in to access this page
            </p>
          </div>
          <div className="space-y-4">
            <button
              onClick={handleSignIn}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
            >
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Continue with Google
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render children if authenticated or authentication not required
  if (!requireAuth || (requireAuth && session)) {
    return <>{children}</>;
  }

  // Default fallback
  return null;
}

/**
 * Higher-order component for wrapping pages with auth guard
 */
export function withAuthGuard<P extends object>(
  Component: React.ComponentType<P>,
  options?: Omit<AuthGuardProps, 'children'>
) {
  return function AuthGuardedComponent(props: P) {
    return (
      <AuthGuard {...options}>
        <Component {...props} />
      </AuthGuard>
    );
  };
}
