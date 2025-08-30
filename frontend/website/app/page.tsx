'use client'

import { WelcomePage } from '@/components/Welcome';
import { useSessionContext } from '@/components/providers/SessionWrapper';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState, Suspense } from 'react';

function HomeContent() {
  const session = useSessionContext();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [authError, setAuthError] = useState<string | null>(null);

  useEffect(() => {
    // Check for auth error in URL parameters
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

  useEffect(() => {
    // If user is signed in, redirect to feed instead of showing welcome page
    if (session.isAuthenticated && session.user) {
      router.push('/feed');
    }
  }, [session.isAuthenticated, session.user, router]);

  // Show loading or welcome page only if not authenticated
  if (session.loading) {
    return null; // Or a loading spinner
  }

  if (session.isAuthenticated) {
    return null; // Will redirect, so don't render anything
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
