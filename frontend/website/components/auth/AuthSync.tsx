/**
 * Authentication Synchronization Bridge
 * 
 * Syncs NextAuth session with production auth store
 * This bridges the gap between NextAuth OAuth and the production auth system
 */

'use client';

import { useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useAuthStore } from '../../lib/stores/authStore.production';

export default function AuthSync() {
  const { data: session, status } = useSession();
  const authStore = useAuthStore();

  useEffect(() => {
    const syncAuth = async () => {
      // If NextAuth has a session but auth store doesn't know about it
      if (session?.user && !authStore.isAuthenticated) {
        try {
          // Extract Google ID token from NextAuth session
          const googleIdToken = (session as any).idToken;
          
          if (googleIdToken) {
            console.log('🔄 Syncing NextAuth session with production auth store...');
            
            // Use the production auth store's login method
            await authStore.login(googleIdToken);
            
            console.log('✅ Auth sync successful');
          } else {
            console.warn('⚠️ NextAuth session missing Google ID token');
          }
        } catch (error) {
          console.error('❌ Failed to sync auth:', error);
        }
      }
      
      // If NextAuth session is gone but auth store still thinks user is authenticated
      if (!session && authStore.isAuthenticated) {
        console.log('🔄 NextAuth session expired, clearing auth store...');
        authStore.logout();
      }
    };

    // Only sync when NextAuth status is no longer loading
    if (status !== 'loading') {
      syncAuth();
    }
  }, [session, status, authStore]);

  // Monitor auth store state changes
  useEffect(() => {
    // If auth store logs out, we might want to clear NextAuth session too
    // (This is optional depending on your requirements)
    
    if (!authStore.isAuthenticated && session) {
      console.log('🔄 Auth store logged out, NextAuth session still active');
      // Could trigger NextAuth signOut here if desired
      // signOut({ redirect: false });
    }
  }, [authStore.isAuthenticated, session]);

  return null; // This component doesn't render anything
}
