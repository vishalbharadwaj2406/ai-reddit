// Basic auth state management without external dependencies

import type { User, AuthState } from '../types';

// Demo user for MVP
const DEMO_USER: User = {
  id: 'demo-user-1',
  userName: 'Demo User',
  email: 'demo@aisocial.com',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

// Simple auth state manager (to be enhanced with Zustand in platform-specific implementations)
export class AuthManager {
  private state: AuthState = {
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: false,
  };

  private listeners: ((state: AuthState) => void)[] = [];

  getState(): AuthState {
    return { ...this.state };
  }

  subscribe(listener: (state: AuthState) => void): () => void {
    this.listeners.push(listener);
    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  private setState(updates: Partial<AuthState>): void {
    this.state = { ...this.state, ...updates };
    this.listeners.forEach(listener => listener(this.state));
  }

  login(user: User, token: string): void {
    this.setState({
      user,
      token,
      isAuthenticated: true,
      isLoading: false,
    });
  }

  logout(): void {
    this.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  }

  updateUser(updates: Partial<User>): void {
    if (this.state.user) {
      this.setState({
        user: { ...this.state.user, ...updates },
      });
    }
  }

  setLoading(loading: boolean): void {
    this.setState({ isLoading: loading });
  }

  // Demo login function for MVP
  async loginWithDemo(): Promise<void> {
    this.setLoading(true);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const demoToken = 'demo-jwt-token-' + Date.now();
    this.login(DEMO_USER, demoToken);
  }
}

// Singleton instance
export const authManager = new AuthManager();

// Export demo user for convenience
export { DEMO_USER };
