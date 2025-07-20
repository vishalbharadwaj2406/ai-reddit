// Protected route component that requires authentication
'use client';

import { useAuth } from '@/lib/auth';
import LoginModal from '@/components/LoginModal';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading while checking auth status
  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // Show login modal if not authenticated
  if (!isAuthenticated) {
    return <LoginModal />;
  }

  // Render children if authenticated
  return <>{children}</>;
}
