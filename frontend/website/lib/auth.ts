// Web-specific authentication utilities using shared auth manager
import { useState, useEffect } from 'react';
import { authManager, type AuthState, type User } from '@ai-social/shared';

// Web-specific auth hook that adds localStorage persistence
export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>(authManager.getState());

  useEffect(() => {
    // Subscribe to auth state changes
    const unsubscribe = authManager.subscribe(setAuthState);

    // Check for existing token in localStorage on mount
    const token = localStorage.getItem('ai-social-token');
    const userData = localStorage.getItem('ai-social-user');
    
    if (token && userData && !authManager.getState().isAuthenticated) {
      try {
        const user = JSON.parse(userData);
        authManager.login(user, token);
      } catch {
        // Clear invalid data
        localStorage.removeItem('ai-social-token');
        localStorage.removeItem('ai-social-user');
      }
    }

    return unsubscribe;
  }, []);

  // Web-specific login that persists to localStorage
  const login = async (user: User, token: string) => {
    localStorage.setItem('ai-social-token', token);
    localStorage.setItem('ai-social-user', JSON.stringify(user));
    authManager.login(user, token);
  };

  // Web-specific logout that clears localStorage
  const logout = () => {
    localStorage.removeItem('ai-social-token');
    localStorage.removeItem('ai-social-user');
    authManager.logout();
  };

  return {
    ...authState,
    login,
    logout,
    loginWithDemo: authManager.loginWithDemo.bind(authManager),
    updateUser: authManager.updateUser.bind(authManager),
  };
};
