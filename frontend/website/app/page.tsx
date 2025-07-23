'use client'

import { WelcomePage } from '@/components/Welcome';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function Home() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    // If user is signed in, redirect to feed instead of showing welcome page
    if (status === 'authenticated' && session?.user) {
      router.push('/feed');
    }
  }, [session, status, router]);

  // Show loading or welcome page only if not authenticated
  if (status === 'loading') {
    return null; // Or a loading spinner
  }

  if (status === 'authenticated') {
    return null; // Will redirect, so don't render anything
  }

  return <WelcomePage />;
}
