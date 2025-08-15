'use client';

import { useState, useEffect, useCallback, Suspense } from 'react';
import Link from 'next/link';
import { useSession, signIn } from 'next-auth/react';
import { 
  conversationService, 
  AuthenticationRequiredError,
  ConversationServiceError 
} from '@/lib/services/conversationService';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/design-system/Button';
import { Card, CardRow } from '@/components/design-system/Card';
import { Select, NativeSelect } from '@/components/design-system/Select';
import { Input } from '@/components/design-system/Input';
import { useToast } from '@/components/feedback/ToastProvider';
import { formatRelativeTime } from '@/lib/utils/time';
import { useConversationsStore } from '@/lib/stores/conversationsStore';
import { ArrowRight, MoreHorizontal, Search, MessageCircle, Plus } from 'lucide-react';
import { SkeletonCardRow } from '@/components/design-system/Skeleton';
import { ConversationDropdown } from '@/components/design-system/ConversationDropdown';

function ConversationsContent() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const params = useSearchParams();
  const [searchQuery, setSearchQuery] = useState(params.get('q') ?? '');
  const [debouncedQuery, setDebouncedQuery] = useState(searchQuery);
  const [isRefreshing, setIsRefreshing] = useState(false);
  // replaced by statusFilter synced with URL
  const conversations = useConversationsStore(s => s.conversations);
  const setFromServer = useConversationsStore(s => s.setFromServer);
  const setStatus = useConversationsStore(s => s.setStatus);
  const lastFetched = useConversationsStore(s => s.lastFetched);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [needsAuth, setNeedsAuth] = useState(false);
  const { show } = useToast();

  // URL-synced state
  const [sort, setSort] = useState<string>(params.get('sort') ?? 'updated_desc');

  // Debounce search query to avoid URL churn and navigation flicker
  useEffect(() => {
    const t = setTimeout(() => setDebouncedQuery(searchQuery), 350);
    return () => clearTimeout(t);
  }, [searchQuery]);

  // Prevent unnecessary router.replace calls (which feel like reloads)
  useEffect(() => {
    const p = new URLSearchParams(params.toString());
    // Only include q when non-empty for cleaner URLs
    if (debouncedQuery) p.set('q', debouncedQuery); else p.delete('q');
    p.set('sort', sort);
    const next = p.toString();
    const current = params.toString();
    if (next !== current) {
      router.replace(`/conversations${next ? `?${next}` : ''}`);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedQuery, sort]);

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

  const REFRESH_TTL_MS = 60_000; // avoid refetch for 60s when we have cache

  const connectToBackendAndLoadConversations = useCallback(async () => {
    if (!session?.user) {
      setNeedsAuth(true);
      return;
    }

    // If we already have a valid backend JWT, skip re-auth and load directly
    const jwt = typeof window !== 'undefined' ? localStorage.getItem('ai_social_backend_jwt') : null;
    const expStr = typeof window !== 'undefined' ? localStorage.getItem('ai_social_backend_jwt_expiry') : null;
    const exp = expStr ? parseInt(expStr, 10) : 0;
    const hasValidJwt = !!jwt && exp > Date.now() + 5 * 60 * 1000; // 5 min safety window

    try {
      const hasCache = conversations.length > 0;
      const freshEnough = Date.now() - lastFetched < REFRESH_TTL_MS;
      // If we have fresh cache, skip any network/auth entirely
      if (hasCache && freshEnough) {
        return;
      }
      if (hasCache) setIsRefreshing(true);
      if (!hasValidJwt) {
        const googleIdToken = (session as unknown as { idToken?: string })?.idToken;
        if (!googleIdToken) {
          setError('Unable to connect to backend: Missing authentication token');
          return;
        }
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
      }
    const list = await conversationService.getConversations();
    setFromServer(list);
    } catch (error) {
      const msg = error instanceof Error ? error.message : 'Unknown error';
      if (msg.includes('Failed to fetch') || msg.includes('NetworkError')) {
        setError('Backend server is currently down. Please try again later.');
      } else {
        setError('Unable to connect to backend services.');
      }
    } finally {
      setIsRefreshing(false);
    }
  }, [session, conversations.length, lastFetched, setFromServer]);

  const loadConversations = useCallback(async () => {
    try {
      // Only show blocking loading when there is no cached data
      const hasCache = conversations.length > 0;
      setLoading(!hasCache);
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
  }, [status, connectToBackendAndLoadConversations, handleLoadError, conversations.length]);

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

  // Derived list: search + hide archived (UI has no archived concept)
  const filteredConversations = conversations
    .filter(conv => conv.status !== 'archived')
    .filter(conv => conv.title.toLowerCase().includes(searchQuery.toLowerCase()))
    .sort((a, b) => {
      if (sort === 'updated_desc') return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
      if (sort === 'created_desc') return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      if (sort === 'title_asc') return a.title.localeCompare(b.title);
      if (sort === 'messages_desc') return (b.message_count ?? 0) - (a.message_count ?? 0);
      return 0;
    });

  // Delete (soft: archive) with undo toast, and hide immediately from UI
  const archiveWithUndo = useCallback(async (id: string) => {
    setStatus(id, 'archived');

    show({
      title: 'Conversation deleted',
      description: 'Undo to restore within a few seconds.',
      actionLabel: 'Undo',
      onAction: () => setStatus(id, 'active'),
      variant: 'success',
      durationMs: 6000,
    });

    try {
      await conversationService.archiveConversation(id);
  } catch (_err) {
      // Reload from server on failure to ensure consistency
      const list = await conversationService.getConversations();
      setFromServer(list);
      show({ title: 'Failed to delete', description: 'Please try again.', variant: 'error' });
    }
  }, [setStatus, setFromServer, show]);

  // Keyboard shortcuts
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === '/' && !e.metaKey && !e.ctrlKey) {
        const el = document.querySelector<HTMLInputElement>('input[data-conversations-search]');
        el?.focus();
        e.preventDefault();
      }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'n') {
        router.push('/conversations/new');
      }
      if (e.key === 'Escape') {
        // Escape handling is now managed by individual dropdown components
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [router]);

  // Note: Click outside handling is now managed by usePortalDropdown hook

  if (status === 'loading' || loading) {
    return (
      <div className="min-h-screen">
        <div className="px-12 py-12">
          <div className="max-w-5xl mx-auto space-y-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <SkeletonCardRow key={i} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <div className="relative px-6 py-8 lg:px-12 lg:py-12">
        <div className="max-w-6xl mx-auto">
          {/* Header Section with improved typography and spacing */}
          <div className="mb-8 flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
            <div className="space-y-3">
              <h1 className="text-3xl lg:text-4xl font-bold text-white tracking-tight">
                Your Conversations
              </h1>
              <p className="text-base text-gray-300 max-w-lg leading-relaxed">
                Manage your AI conversations and generate blogs with sophisticated tools.
              </p>
            </div>
            <Button 
              onClick={() => router.push('/conversations/new')} 
              variant="primary" 
              size="lg"
              leftIcon={<Plus size={18} />}
              className="shrink-0"
            >
              New Conversation
            </Button>
          </div>

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
                  {error.includes('Missing authentication token') && (
                    <button
                      onClick={() => signIn('google', { callbackUrl: '/conversations' })}
                      className="px-3 py-1 text-xs bg-blue-700/30 hover:bg-blue-700/50 text-blue-200 rounded transition-colors"
                    >
                      Re-authenticate
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Controls Card with enhanced spacing and modern select */}
          <Card className="mb-6">
            <div className="p-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className="lg:col-span-2 flex flex-col justify-end">
                  <label className="block text-sm font-medium text-gray-300 mb-3">
                    Search conversations
                  </label>
                  <Input
                    type="text"
                    placeholder="Search conversations... (/ to focus)"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(ev) => { if (ev.key === 'Escape') (ev.target as HTMLInputElement).blur(); }}
                    data-conversations-search
                    aria-label="Search conversations"
                    leftIcon={<Search size={18} />}
                    className="w-full"
                  />
                  <div className="mt-2 text-xs text-gray-400">
                    Press <kbd className="px-1.5 py-0.5 bg-white/10 rounded text-gray-300">/</kbd> to focus search
                  </div>
                </div>
                <div className="space-y-3 flex flex-col justify-end">
                  <label className="block text-sm font-medium text-gray-300">
                    Sort by
                  </label>
                  <Select
                    value={sort}
                    onChange={setSort}
                    options={[
                      { value: 'updated_desc', label: 'Recently updated' },
                      { value: 'created_desc', label: 'Newest created' },
                      { value: 'title_asc', label: 'Title A–Z' },
                      { value: 'messages_desc', label: 'Most messages' },
                    ]}
                    aria-label="Sort conversations"
                  />
                </div>
              </div>
            </div>
            {isRefreshing && (
              <div className="absolute left-0 right-0 bottom-0 h-1 overflow-hidden bg-gray-800/50">
                <div className="h-full w-full bg-gradient-to-r from-blue-600 via-blue-400 to-blue-600 animate-pulse" />
              </div>
            )}
          </Card>

          {/* Conversation List with enhanced design */}
          <div className="space-y-4" role="list" aria-label="Conversations">
            {filteredConversations.length === 0 ? (
              <Card className="text-center py-16">
                <div className="max-w-md mx-auto space-y-4">
                  <div className="w-16 h-16 mx-auto bg-gradient-to-br from-blue-600/20 to-blue-700/10 rounded-2xl flex items-center justify-center">
                    <MessageCircle size={32} className="text-blue-400" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-xl font-semibold text-white">No conversations found</h3>
                    <p className="text-gray-300 leading-relaxed">
                      {searchQuery 
                        ? 'Try different keywords or clear your search' 
                        : 'Start your first conversation with AI to explore ideas and generate content'
                      }
                    </p>
                  </div>
                  <Button 
                    onClick={() => router.push('/conversations/new')} 
                    variant="primary" 
                    size="lg"
                    leftIcon={<Plus size={18} />}
                  >
                    Start New Conversation
                  </Button>
                </div>
              </Card>
            ) : (
              filteredConversations.map((c) => (
                <div 
                  key={c.conversation_id} 
                  role="listitem" 
                  className="glass-card cursor-pointer"
                  onClick={() => router.push(`/conversations/${c.conversation_id}`)}
                >
                  <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0 space-y-3">
                        <div className="flex items-center gap-3">
                          {c.forked_from && (
                            <div className="flex items-center gap-1.5 text-blue-400 text-sm bg-blue-400/10 px-2 py-1 rounded-lg">
                              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M7.707 3.293a1 1 0 010 1.414L5.414 7H11a7 7 0 017 7v2a1 1 0 11-2 0v-2a5 5 0 00-5-5H5.414l2.293 2.293a1 1 0 11-1.414 1.414L2.586 8l3.707-3.707a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                              <span>Forked</span>
                            </div>
                          )}
                          <h3 className="text-lg font-semibold text-white truncate">
                            {c.title || 'Untitled Conversation'}
                          </h3>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          <div className="flex items-center gap-1.5">
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                            </svg>
                            <span title={new Date(c.updated_at).toLocaleString()}>
                              {formatRelativeTime(c.updated_at)}
                            </span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            <MessageCircle size={16} />
                            <span>
                              {(c.message_count ?? 0).toLocaleString()} {(c.message_count ?? 0) === 1 ? 'message' : 'messages'}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Production-grade portal dropdown */}
                      <ConversationDropdown
                        conversationId={c.conversation_id}
                        onOpenConversation={() => router.push(`/conversations/${c.conversation_id}`)}
                        onDeleteConversation={() => archiveWithUndo(c.conversation_id)}
                      />
                    </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ConversationsPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen">
          <div className="px-12 py-12">
            <div className="max-w-5xl mx-auto space-y-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="rounded-lg border border-white/10 bg-white/5 h-16" />
              ))}
            </div>
          </div>
        </div>
      }
    >
      <ConversationsContent />
    </Suspense>
  );
}
