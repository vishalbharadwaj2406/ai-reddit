'use client'

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function FeedPage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    // If user is not signed in, redirect to home
    if (status === 'unauthenticated') {
      router.push('/');
    }
  }, [status, router]);

  if (status === 'loading') {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '60vh',
        color: '#FFFFFF'
      }}>
        Loading...
      </div>
    );
  }

  if (status === 'unauthenticated') {
    return null; // Will redirect
  }

  return (
    <div style={{ 
      padding: 'var(--space-2xl)', 
      color: '#FFFFFF',
      maxWidth: '1200px',
      margin: '0 auto'
    }}>
      <h1 style={{ 
        fontSize: 'var(--text-3xl)', 
        fontWeight: '800',
        marginBottom: 'var(--space-lg)',
        background: 'linear-gradient(135deg, #FFFFFF, #3B82F6)',
        backgroundClip: 'text',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        Welcome to AI Social, {session?.user?.name}!
      </h1>
      <p style={{ 
        fontSize: 'var(--text-lg)', 
        color: 'rgba(255, 255, 255, 0.8)',
        lineHeight: '1.6'
      }}>
        Your intelligent conversation feed is coming soon. Start by creating a new chat or exploring conversations.
      </p>
    </div>
  );
} 