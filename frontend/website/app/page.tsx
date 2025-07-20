// Homepage - shows login for unauthenticated users, redirects to conversations for authenticated users
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import LoginModal from '@/components/LoginModal';
import Header from '@/components/Header';

export default function HomePage() {
  const { status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'authenticated') {
      router.push('/conversations');
    }
  }, [status, router]);

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-pure-black">
        {/* Royal Blue Background Gradients */}
        <div className="fixed top-0 left-0 w-full h-full pointer-events-none">
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-radial from-royal-blue/12 via-transparent to-transparent animate-royal-flow"></div>
          <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-brilliant-blue/8 rounded-full blur-3xl"></div>
          <div className="absolute bottom-1/4 left-1/4 w-80 h-80 bg-royal-blue/6 rounded-full blur-3xl"></div>
        </div>
        
        <Header />
        
        <div className="flex items-center justify-center min-h-[calc(100vh-100px)] pt-24">
          <div className="glass-elevated p-8">
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 border-2 border-brilliant-blue border-t-transparent rounded-full animate-spin"></div>
              <span className="text-ice-white">Loading...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-pure-black">
      {/* Royal Blue Background Gradients */}
      <div className="fixed top-0 left-0 w-full h-full pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-radial from-royal-blue/12 via-transparent to-transparent animate-royal-flow"></div>
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-brilliant-blue/8 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 left-1/4 w-80 h-80 bg-royal-blue/6 rounded-full blur-3xl"></div>
      </div>
      
      <Header />
      <div className="pt-24">
        <LoginModal />
      </div>
    </div>
  );
}
