// Shared authentication logic using Zustand

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, AuthState } from '../types';

interface AuthStore extends AuthState {
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
  setLoading: (loading: boolean) => void;
}

// Demo user for MVP
const DEMO_USER: User = {
  id: 'demo-user-1',
  userName: 'Demo User',
  email: 'demo@aisocial.com',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: (user: User, token: string) => {
        set({
          user,
          token,
          isAuthenticated: true,
          isLoading: false,
        });
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },

      updateUser: (updates: Partial<User>) => {
        const currentUser = get().user;
        if (currentUser) {
          set({
            user: { ...currentUser, ...updates },
          });
        }
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Demo login function for MVP
export const loginWithDemo = async (): Promise<void> => {
  const { login, setLoading } = useAuthStore.getState();
  
  setLoading(true);
  
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  const demoToken = 'demo-jwt-token-' + Date.now();
  login(DEMO_USER, demoToken);
};

// Hook for easier usage in React components
export const useAuth = () => {
  const store = useAuthStore();
  
  return {
    ...store,
    loginWithDemo,
  };
};
