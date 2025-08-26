'use client'

import AuthGuard from '../../components/auth/AuthGuard';
import { useSession } from 'next-auth/react';

function FeedPageContent() {
  const { data: session } = useSession();

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

export default function FeedPage() {
  return (
    <AuthGuard>
      <FeedPageContent />
    </AuthGuard>
  );
} 