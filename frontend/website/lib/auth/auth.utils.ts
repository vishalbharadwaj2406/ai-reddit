/**
 * Production-Grade NextAuth Utilities
 * 
 * Clean, enterprise-ready authentication utilities for NextAuth.
 * Designed for scalability and production use with millions of users.
 */

import { getSession, signIn, signOut } from 'next-auth/react';
import type { Session } from 'next-auth';

// Enhanced session type with custom properties
export interface ExtendedSession extends Session {
  idToken?: string;
  accessToken?: string;
  error?: string;
}

/**
 * Get current NextAuth session with error handling
 */
export async function getCurrentSession(): Promise<ExtendedSession | null> {
  try {
    const session = await getSession();
    
    if (session) {
      console.log('✅ Session retrieved successfully for user:', session.user?.email);
    } else {
      console.warn('⚠️ No active session found');
    }
    
    return session as ExtendedSession;
  } catch (error) {
    console.error('❌ Failed to get current session:', error);
    return null;
  }
}

/**
 * Check if user is authenticated
 */
export async function isAuthenticated(): Promise<boolean> {
  const session = await getCurrentSession();
  const authenticated = !!session?.user;
  
  console.log('🔍 Authentication check:', authenticated ? 'AUTHENTICATED' : 'NOT AUTHENTICATED');
  
  return authenticated;
}

/**
 * Get user from session
 */
export async function getCurrentUser() {
  const session = await getCurrentSession();
  return session?.user || null;
}

/**
 * Get auth token from session (for API calls)
 */
export async function getAuthToken(): Promise<string | null> {
  const session = await getCurrentSession();
  return session?.idToken || null;
}

/**
 * Trigger Google OAuth sign-in
 */
export async function signInWithGoogle(callbackUrl = '/conversations') {
  try {
    const result = await signIn('google', {
      redirect: false,
      callbackUrl,
    });
    
    if (result?.error) {
      throw new Error(result.error);
    }
    
    return result;
  } catch (error) {
    console.error('Google sign-in failed:', error);
    throw error;
  }
}

/**
 * Sign out user
 */
export async function signOutUser(callbackUrl = '/') {
  try {
    await signOut({ callbackUrl });
  } catch (error) {
    console.error('Sign out failed:', error);
    throw error;
  }
}

/**
 * Production-grade session validator
 */
export async function validateSession(): Promise<{
  isValid: boolean;
  session: ExtendedSession | null;
  error?: string;
}> {
  try {
    const session = await getCurrentSession();
    
    if (!session) {
      return { isValid: false, session: null, error: 'No session found' };
    }
    
    if (!session.user) {
      return { isValid: false, session: null, error: 'Invalid session data' };
    }
    
    // Check for session errors
    if (session.error) {
      return { isValid: false, session, error: session.error };
    }
    
    return { isValid: true, session };
  } catch (error) {
    return { 
      isValid: false, 
      session: null, 
      error: error instanceof Error ? error.message : 'Session validation failed' 
    };
  }
}

/**
 * React hook for authentication status
 */
export function useAuthStatus() {
  // This would typically use NextAuth's useSession hook
  // but keeping it simple for now
  return {
    getCurrentSession,
    isAuthenticated,
    getCurrentUser,
    getAuthToken,
    signInWithGoogle,
    signOutUser,
    validateSession,
  };
}

/**
 * Authentication error types
 */
export class AuthenticationError extends Error {
  constructor(message: string, public code?: string) {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class SessionExpiredError extends AuthenticationError {
  constructor() {
    super('Your session has expired. Please sign in again.', 'SESSION_EXPIRED');
  }
}

export class InvalidSessionError extends AuthenticationError {
  constructor() {
    super('Invalid session data. Please sign in again.', 'INVALID_SESSION');
  }
}
