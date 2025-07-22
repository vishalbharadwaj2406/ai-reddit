"use client";

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

// User type (customize as needed)
interface User {
  user_id: string;
  user_name: string;
  email: string;
  profile_picture?: string;
  is_private?: boolean;
  created_at?: string;
}

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  loading: boolean;
  error: string | null;
  loginWithGoogle: (googleIdToken: string) => Promise<void>;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load from localStorage on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('ai-social-user');
    const storedAccess = localStorage.getItem('ai-social-access');
    const storedRefresh = localStorage.getItem('ai-social-refresh');
    if (storedUser && storedAccess && storedRefresh) {
      setUser(JSON.parse(storedUser));
      setAccessToken(storedAccess);
      setRefreshToken(storedRefresh);
    }
  }, []);

  // Save to localStorage on change
  useEffect(() => {
    if (user && accessToken && refreshToken) {
      localStorage.setItem('ai-social-user', JSON.stringify(user));
      localStorage.setItem('ai-social-access', accessToken);
      localStorage.setItem('ai-social-refresh', refreshToken);
    } else {
      localStorage.removeItem('ai-social-user');
      localStorage.removeItem('ai-social-access');
      localStorage.removeItem('ai-social-refresh');
    }
  }, [user, accessToken, refreshToken]);

  // Google login handler
  const loginWithGoogle = useCallback(async (googleIdToken: string) => {
    setLoading(true);
    setError(null);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL;
      console.log('Making API call to:', `${API_URL}/auth/google`);
      console.log('Token being sent:', googleIdToken?.substring(0, 50) + '...');
      const res = await fetch(`${API_URL}/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ google_token: googleIdToken }),
      });
      console.log('Response status:', res.status);
      if (!res.ok) {
        const err = await res.json();
        console.log('Backend error details:', err);
        throw new Error(err.detail?.message || 'Login failed');
      }
      const data = await res.json();
      console.log('Login successful, user data:', data.user);
      setUser(data.user);
      setAccessToken(data.access_token);
      setRefreshToken(data.refresh_token);
      setLoading(false);
    } catch (e: unknown) {
      console.error('Login error:', e);
      setError(e instanceof Error ? e.message : 'Login failed');
      setLoading(false);
    }
  }, []);

  // Logout handler
  const signOut = useCallback(async () => {
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);
    setError(null);
    setLoading(false);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL;
      await fetch(`${API_URL}/auth/logout`, { method: 'POST' });
    } catch {}
  }, []);

  const value: AuthContextType = {
    user,
    accessToken,
    refreshToken,
    loading,
    error,
    loginWithGoogle,
    signOut,
  };

  return React.createElement(AuthContext.Provider, { value }, children);
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
