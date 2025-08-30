'use client'

import WelcomePage from '@/components/Welcome/WelcomePage';
import { useSessionContext } from '@/components/providers/SessionWrapper';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState, Suspense } from 'react';
import { isPostAuthentication, handlePostAuthSuccess } from '@/lib/auth/session';

function HomeContent() {
  const session = useSessionContext();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [authError, setAuthError] = useState<string | null>(null);
  const [isProcessingAuth, setIsProcessingAuth] = useState(false);

  // Handle authentication errors from URL parameters
  useEffect(() => {
    const authErrorParam = searchParams.get('auth_error');
    if (authErrorParam) {
      let errorMessage = 'Authentication failed. Please try again.';
      
      switch (authErrorParam) {
        case 'invalid_state':
          errorMessage = 'Security validation failed. Please try signing in again.';
          break;
        case 'oauth_failed':
          errorMessage = 'Google authentication failed. Please try again.';
          break;
        case 'server_error':
          errorMessage = 'Server error during authentication. Please try again.';
          break;
        case 'security_violation':
          errorMessage = 'Security check failed. Please try again.';
          break;
        default:
          errorMessage = `Authentication error: ${authErrorParam}`;
      }
      
      setAuthError(errorMessage);
      
      // Clear the error parameter from URL after 5 seconds
      setTimeout(() => {
        setAuthError(null);
        router.replace('/', undefined);
      }, 5000);
    }
  }, [searchParams, router]);

  // Enhanced post-authentication handling
  useEffect(() => {
    const handlePostAuth = async () => {
      if (isPostAuthentication() && !isProcessingAuth) {
        setIsProcessingAuth(true);
        
        try {
          console.log('🎉 Post-auth detected: Processing authentication completion');
          
          // Get callback URL from search params
          const callbackUrl = searchParams.get('callbackUrl') || '/feed';
          
          // Wait for session to be fully initialized
          if (session.isInitialized) {
            if (session.isAuthenticated && session.user) {
              // Authentication successful - handle post-auth
              await handlePostAuthSuccess(callbackUrl);
            } else {
              // Wait a bit more for session to update
              setTimeout(() => {
                if (session.isAuthenticated && session.user) {
                  handlePostAuthSuccess(callbackUrl);
                } else {
                  console.log('🚀 Post-auth: Session not yet authenticated, refreshing');
                  session.refresh();
                }
              }, 500);
            }
          }
        } catch (error) {
          console.error('Post-auth handling failed:', error);
          // Fallback: Direct navigation
          router.push('/feed');
        } finally {
          setIsProcessingAuth(false);
        }
      }
    };

    handlePostAuth();
  }, [session.isAuthenticated, session.isInitialized, session.user, searchParams, router, isProcessingAuth, session.refresh]);

  // Standard authentication redirect for already-authenticated users
  useEffect(() => {
    if (session.isAuthenticated && 
        session.user && 
        session.isInitialized && 
        !isPostAuthentication() && 
        !isProcessingAuth) {
      
      console.log('🚀 Redirecting authenticated user to feed');
      router.push('/feed');
    }
  }, [session.isAuthenticated, session.user, session.isInitialized, router, isProcessingAuth]);

  // Show loading states
  if (isProcessingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Completing authentication...</p>
        </div>
      </div>
    );
  }

  if (!session.isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing session...</p>
        </div>
      </div>
    );
  }

  // Show minimal loading state while redirecting authenticated users
  if (session.isAuthenticated && session.user && !isPostAuthentication()) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Redirecting to your feed...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {authError && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 max-w-md mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-red-800">{authError}</p>
              </div>
              <div className="ml-auto pl-3">
                <button
                  onClick={() => setAuthError(null)}
                  className="inline-flex text-red-400 hover:text-red-600"
                >
                  <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      <WelcomePage />
    </>
  );
}

export default function Home() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HomeContent />
    </Suspense>
  );
}
