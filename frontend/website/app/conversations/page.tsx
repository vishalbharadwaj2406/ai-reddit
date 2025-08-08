'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useSession, signIn } from 'next-auth/react';
import { 
  conversationService, 
  type Conversation,
  AuthenticationRequiredError,
  ConversationServiceError 
} from '@/lib/services/conversationService';

export default function ConversationsPage() {
  const { data: session, status } = useSession();
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState('all');
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [needsAuth, setNeedsAuth] = useState(false);

  const handleLoadError = useCallback((err: unknown) => {
    if (err instanceof AuthenticationRequiredError) {
      setNeedsAuth(true);
      setError(null);
    } else if (err instanceof ConversationServiceError) {
      setError('Backend services are currently unavailable.');
    } else {
      setError('Unable to load conversations. Please try again.');
    }
  }, []);

  const connectToBackendAndLoadConversations = useCallback(async () => {
    if (!session?.user) {
      setNeedsAuth(true);
      return;
    }

    const googleIdToken = (session as unknown as { idToken?: string })?.idToken;
    if (!googleIdToken) {
      setError('Unable to connect to backend: Missing authentication token');
      return;
    }

    try {
      const authResponse = await fetch('http://localhost:8000/api/v1/auth/google', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ google_token: googleIdToken }),
      });

      if (!authResponse.ok) {
        throw new Error('Backend authentication failed');
      }

      const authData: { access_token?: string; expires_in?: number } = await authResponse.json();
      if (authData.access_token && authData.expires_in) {
        const expiryTime = Date.now() + authData.expires_in * 1000;
        localStorage.setItem('ai_social_backend_jwt', authData.access_token);
        localStorage.setItem('ai_social_backend_jwt_expiry', expiryTime.toString());
      }

      const list = await conversationService.getConversations();
      setConversations(list);
    } catch (error) {
      const msg = error instanceof Error ? error.message : 'Unknown error';
      if (msg.includes('Failed to fetch') || msg.includes('NetworkError')) {
        setError('Backend server is currently down. Please try again later.');
      } else {
        setError('Unable to connect to backend services.');
      }
    }
  }, [session]);

  const loadConversations = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      setNeedsAuth(false);
      if (status === 'unauthenticated') {
        setNeedsAuth(true);
        setLoading(false);
        return;
      }
      await connectToBackendAndLoadConversations();
    } catch (err) {
      handleLoadError(err);
    } finally {
      setLoading(false);
    }
  }, [status, connectToBackendAndLoadConversations, handleLoadError]);

  useEffect(() => {
    if (status !== 'loading') {
      loadConversations();
    }
  }, [status, loadConversations]);

  const handleGoogleLogin = async () => {
    try {
      await signIn('google', { callbackUrl: '/conversations' });
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  // Filter conversations based on search and filter
  const filteredConversations = conversations.filter(conv => {
    const matchesSearch = conv.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filter === 'all' || (filter === 'posted' && false) || (filter === 'draft' && true);
    return matchesSearch && matchesFilter;
  });

  const formatRelativeTime = (dateString: string) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInMs = now.getTime() - date.getTime();
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    if (diffInDays === 1) return '1 day ago';
    if (diffInDays < 7) return `${diffInDays} days ago`;
    return '1 week ago';
  };

  if (status === 'loading' || loading) {
    return (
      <div className="min-h-screen">
        <div className="px-12 py-12">
          <div className="max-w-4xl mx-auto">
            <div className="glass-card text-center py-16">
              <div className="animate-spin inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mb-4" />
              <div className="text-subheading text-caption mb-2">Loading Conversations</div>
              <p className="text-body text-caption">{status === 'loading' ? 'Checking authentication...' : 'Connecting to backend...'}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <div className="px-12 py-12">
        <div className="max-w-4xl mx-auto">
          
          {/* Page Header */}
          <div className="mb-12">
            <h1 className="text-display text-gradient-primary mb-4">
              Your Conversations
            </h1>
            <p className="text-body text-caption max-w-2xl">
              Manage your AI conversations and generate blogs.
            </p>
            
            {/* Authentication Required State */}
            {needsAuth && status === 'unauthenticated' && (
              <div className="mt-4 p-4 bg-orange-900/20 border border-orange-700/30 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-orange-400">⚠️</span>
                    <div>
                      <div className="text-sm font-medium text-orange-300">Authentication Required</div>
                      <div className="text-xs text-orange-400">
                        Sign in to access your conversations
                      </div>
                    </div>
                  </div>
                  <button 
                    onClick={handleGoogleLogin}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
                  >
                    Sign In with Google
                  </button>
                </div>
              </div>
            )}
            
            {/* Backend Error State */}
            {error && (
              <div className="mt-4 p-4 bg-red-900/20 border border-red-700/30 rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="text-red-400">❌</span>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-red-300">Connection Error</div>
                    <div className="text-xs text-red-400">{error}</div>
                    <div className="text-xs text-red-500 mt-1">
                      {error.includes('Token expired') ? (
                        <>Session expired. Please sign out and sign back in.</>
                      ) : (
                        <>Please check your connection and try again.</>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button 
                      onClick={loadConversations}
                      className="px-3 py-1 text-xs bg-red-700/30 hover:bg-red-700/50 text-red-300 rounded transition-colors"
                    >
                      Retry
                    </button>
                  </div>
                </div>
              </div>
            )}


          </div>

          {/* Search and Filters */}
          <div className="glass-card mb-8">
            <div className="space-y-6">
              {/* Search Bar */}
              <div>
                <input
                  type="text"
                  placeholder="🔍 Search conversations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="glass-input w-full px-6 py-4 text-body"
                />
              </div>

              {/* Filter Buttons */}
              <div className="flex gap-4 flex-wrap">
                <button 
                  className={`glass-button-toggle px-6 py-3 ${filter === 'all' ? 'active' : ''}`}
                  onClick={() => setFilter('all')}
                >
                  All Conversations
                </button>
                <button 
                  className={`glass-button-toggle px-6 py-3 ${filter === 'posted' ? 'active' : ''}`}
                  onClick={() => setFilter('posted')}
                >
                  Published
                </button>
                <button 
                  className={`glass-button-toggle px-6 py-3 ${filter === 'draft' ? 'active' : ''}`}
                  onClick={() => setFilter('draft')}
                >
                  Drafts
                </button>
              </div>
            </div>
          </div>

          {/* Conversations List */}
          <div className="space-y-6">
            {filteredConversations.length === 0 ? (
              <div className="glass-card text-center py-16">
                <div className="text-subheading text-caption mb-4">
                  No conversations found
                </div>
                <p className="text-body text-caption mb-8">
                  {searchQuery ? 'Try adjusting your search terms' : 'Start your first conversation to see it here'}
                </p>
                <Link href="/conversations/new">
                  <button className="glass-button-primary px-8 py-4">
                    ✨ Start New Conversation
                  </button>
                </Link>
              </div>
            ) : (
              filteredConversations.map((conversation) => (
                <Link 
                  key={conversation.conversation_id} 
                  href={`/conversations/${conversation.conversation_id}`}
                  className="block"
                >
                  <div className="glass-card hover:border-color transition-all cursor-pointer">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          {conversation.forked_from && (
                            <span className="text-blue-400 text-sm">🔄</span>
                          )}
                          <h3 className="text-subheading text-white">
                            {conversation.title}
                          </h3>
                          <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-900/30 text-blue-300 border border-blue-700/30">
                            💬 Active
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-6 text-caption">
                          <span>{formatRelativeTime(conversation.updated_at)}</span>
                          <span>{conversation.message_count || 0} messages</span>
                          {conversation.forked_from && (
                            <span className="text-blue-400">Forked conversation</span>
                          )}
                        </div>
                      </div>

                      <div className="text-blue-400 text-xl ml-4">
                        →
                      </div>
                    </div>
                  </div>
                </Link>
              ))
            )}
          </div>

          {/* New Conversation Button */}
          <div className="mt-12 text-center">
            <Link href="/conversations/new">
              <button className="glass-button-primary px-12 py-4">
                💬 Start New Conversation
              </button>
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
}
