'use client'

import SessionGuard from '../../components/auth/SessionGuard';
import { useSessionContext } from '../../components/providers/SessionWrapper';

function FeedPageContent() {
  const { user, isInitialized } = useSessionContext();

  // Show loading state while session initializes
  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
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
        Welcome to AI Social{user?.user_name ? `, ${user.user_name}` : ''}!
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
    <SessionGuard>
      <FeedPageContent />
    </SessionGuard>
  );
} 