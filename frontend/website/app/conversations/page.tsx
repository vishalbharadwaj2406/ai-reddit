'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { useRouter, useSearchParams } from 'next/navigation';
import { 
  conversationService, 
  type Conversation,
  AuthenticationRequiredError,
  ConversationServiceError 
} from '../../lib/services/conversationService.production';
import { signInWithGoogle, signOutUser } from '../../lib/auth/auth.utils';
import AuthGuard from '../../components/auth/AuthGuard';
import { ConversationListSkeleton } from '../../components/design-system/Skeleton';
import { useConversationsStore } from '../../lib/stores/conversationsStore';
import ConfirmDeleteModal from '../../components/design-system/ConfirmDeleteModal';

export default function ConversationsPage() {
  return (
    <AuthGuard>
      <ConversationsPageContent />
    </AuthGuard>
  );
}

function ConversationsPageContent() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const searchParams = useSearchParams();
  
  // Get search from URL params for persistence across navigation
  const urlSearchQuery = searchParams.get('search') || '';
  const [searchQuery, setSearchQuery] = useState(urlSearchQuery);
  const [filter, setFilter] = useState('all');
  
  // USE ZUSTAND STORE - Production-grade state management
  const { 
    conversations, 
    lastFetched, 
    setFromServer, 
    clear 
  } = useConversationsStore();
  
  // Local loading states only for initial load or refresh actions
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [needsAuth, setNeedsAuth] = useState(false);
  
  // Delete modal state
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [conversationToDelete, setConversationToDelete] = useState<Conversation | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // CACHE DURATION - 5 minutes for production-grade UX
  const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  // Sync search query from URL params
  useEffect(() => {
    setSearchQuery(urlSearchQuery);
  }, [urlSearchQuery]);

  // Update URL when search changes (for persistence)
  const updateSearchInUrl = (newSearch: string) => {
    const params = new URLSearchParams(searchParams.toString());
    if (newSearch) {
      params.set('search', newSearch);
    } else {
      params.delete('search');
    }
    router.replace(`/conversations?${params.toString()}`, { scroll: false });
  };

  // Smart loading - only fetch if cache is stale or empty
  useEffect(() => {
    // Wait for session to be determined (not loading)
    if (status === 'loading') {
      return; // Don't do anything while session is loading
    }
    
    const now = Date.now();
    const cacheIsStale = now - lastFetched > CACHE_DURATION;
    const hasNoData = conversations.length === 0;
    
    // Only load if we need to (cache miss or stale data)
    if (hasNoData || cacheIsStale) {
      loadConversations();
    }
  }, [session, status, lastFetched, conversations.length]);

  const loadConversations = async () => {
    let isMounted = true;
    
    try {
      setLoading(true);
      setError(null);
      setNeedsAuth(false);
      
      // Check authentication status first
      if (status === 'unauthenticated') {
        if (isMounted) {
          setNeedsAuth(true);
          setLoading(false);
        }
        return;
      }
      
      // If we have a session, load conversations using the production service
      if (status === 'authenticated') {
        const fetchedConversations = await conversationService.getConversations();
        if (isMounted) {
          setFromServer(fetchedConversations); // Cache in Zustand store
        }
      }
      
    } catch (err: any) {
      console.error('Failed to load conversations:', err);
      if (isMounted) {
        handleLoadError(err);
      }
    } finally {
      if (isMounted) {
        setLoading(false);
      }
    }
    
    // Cleanup function
    return () => {
      isMounted = false;
    };
  };

  // Manual refresh function - forces fresh data fetch
  const handleRefresh = async () => {
    setRefreshing(true);
    setError(null);
    try {
      const fetchedConversations = await conversationService.getConversations();
      setFromServer(fetchedConversations);
    } catch (err: any) {
      console.error('Refresh failed:', err);
      handleLoadError(err);
    } finally {
      setRefreshing(false);
    }
  };

  const handleLoadError = (err: any) => {
    if (err instanceof AuthenticationRequiredError) {
      setNeedsAuth(true);
      setError(null);
    } else if (err instanceof ConversationServiceError) {
      setError('Backend services are currently unavailable. Please try again later.');
    } else if (err.message?.includes('NetworkError') || err.message?.includes('Failed to fetch')) {
      setError('Network connection error. Please check your internet connection.');
    } else if (err.message?.includes('timeout')) {
      setError('Request timed out. The server may be experiencing high load.');
    } else {
      setError('Unable to load conversations. Please try again.');
    }
  };

  // Production-grade Google OAuth login
  const handleGoogleLogin = async () => {
    try {
      const result = await signInWithGoogle('/conversations');
      
      if (result?.ok) {
        // Sign-in successful, reload to update session
        window.location.reload();
      } else if (result?.error) {
        console.error('Sign-in error:', result.error);
        setError('Failed to sign in with Google. Please try again.');
      }
    } catch (error) {
      console.error('Login failed:', error);
      setError('Failed to sign in with Google. Please try again.');
    }
  };

  // Production-grade sign out
  const handleSignOut = async () => {
    try {
      await signOutUser('/');
    } catch (error) {
      console.error('Sign out failed:', error);
      setError('Failed to sign out. Please try again.');
    }
  };

  // Delete conversation handlers
  const handleDeleteClick = (e: React.MouseEvent, conversation: Conversation) => {
    e.preventDefault(); // Prevent navigation to conversation
    e.stopPropagation();
    setConversationToDelete(conversation);
    setDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!conversationToDelete) return;
    
    setIsDeleting(true);
    try {
      await conversationService.archiveConversation(conversationToDelete.conversation_id);
      
      // Remove from local store immediately for instant UI feedback
      const updatedConversations = conversations.filter(
        conv => conv.conversation_id !== conversationToDelete.conversation_id
      );
      setFromServer(updatedConversations);
      
      // Close modal
      setDeleteModalOpen(false);
      setConversationToDelete(null);
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      setError('Failed to delete conversation. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteModalOpen(false);
    setConversationToDelete(null);
  };

  // Filter conversations based on search and filter
  const filteredConversations = conversations.filter(conv => {
    const matchesSearch = conv.title.toLowerCase().includes(searchQuery.toLowerCase());
    
    // TODO: Implement proper status filtering when backend supports it
    const matchesFilter = filter === 'all'; // For now, only show all conversations
    
    return matchesSearch && matchesFilter;
  });

  // Format relative time
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

  // Loading state with professional skeleton loaders
  // FIXED: Better loading condition that prevents infinite loading
  const shouldShowLoading = (status === 'loading') || (loading && !error);
  
  // Show main content if we have data OR if we have an error (don't stay in loading forever)
  const shouldShowContent = !shouldShowLoading;
  
  if (shouldShowLoading) {
    return (
      <div className="min-h-screen">
        <div className="px-6 py-6 lg:px-12 lg:py-8">
          <div className="max-w-6xl mx-auto">
            <ConversationListSkeleton />
          </div>
        </div>
      </div>
    );
  }

  if (!shouldShowContent) {
    return null; // Should never reach here, but safety check
  }

  return (
    <div className="min-h-screen">
      <div className="px-6 py-6 lg:px-12 lg:py-8">
        <div className="max-w-6xl mx-auto">
          
          {/* Authentication Required State */}
          {needsAuth && status === 'unauthenticated' && (
            <div className="mb-6 p-4 bg-orange-900/20 border border-orange-700/30 rounded-lg">
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
                      onClick={handleRefresh}
                      disabled={refreshing}
                      className="px-3 py-1 text-xs bg-red-700/30 hover:bg-red-700/50 text-red-300 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {refreshing ? 'Retrying...' : 'Retry'}
                    </button>
                  </div>
                </div>
              </div>
            )}

          {/* Conversations List */}
          <div className="space-y-3">
            {filteredConversations.length === 0 ? (
              <div className="glass-card text-center py-16">
                <div className="text-subheading text-caption mb-4">
                  No conversations found
                </div>
                <p className="text-body text-caption">
                  {searchQuery ? 'Try adjusting your search terms' : 'Use the "New Chat" button above to start your first conversation'}
                </p>
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

                      <button
                        onClick={(e) => handleDeleteClick(e, conversation)}
                        className="text-gray-400 hover:text-red-500 hover:bg-red-900/20 p-2 rounded-lg transition-all ml-4 group"
                        title="Delete conversation"
                      >
                        <svg 
                          className="w-5 h-5 transition-transform group-hover:scale-110" 
                          viewBox="0 0 24 24" 
                          fill="none" 
                          stroke="currentColor"
                        >
                          <path 
                            strokeLinecap="round" 
                            strokeLinejoin="round" 
                            strokeWidth={2} 
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" 
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                </Link>
              ))
            )}
          </div>

        </div>
      </div>
      
      {/* Delete Confirmation Modal */}
      <ConfirmDeleteModal
        isOpen={deleteModalOpen}
        onClose={handleDeleteCancel}
        onConfirm={handleDeleteConfirm}
        conversationTitle={conversationToDelete?.title || ''}
        isDeleting={isDeleting}
      />
    </div>
  );
}
