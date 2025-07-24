'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function ConversationsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState('all');

  // Mock data for development
  const mockConversations = [
    {
      id: '1',
      title: 'AI Ethics Discussion',
      createdAt: '2 hours ago',
      status: 'draft',
      messageCount: 12,
      isForked: false
    },
    {
      id: '2', 
      title: 'Future of Remote Work',
      createdAt: '1 day ago',
      status: 'posted',
      messageCount: 8,
      isForked: false
    },
    {
      id: '3',
      title: 'Fork: Digital Minimalism',
      createdAt: '3 days ago',
      status: 'draft',
      messageCount: 15,
      isForked: true
    },
    {
      id: '4',
      title: 'Machine Learning Basics',
      createdAt: '1 week ago',
      status: 'posted',
      messageCount: 22,
      isForked: false
    }
  ];

  const filteredConversations = mockConversations.filter(conv => {
    const matchesSearch = conv.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filter === 'all' || conv.status === filter;
    return matchesSearch && matchesFilter;
  });

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
              Manage your AI conversations, generate blogs, and track your content creation journey.
            </p>
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
                  key={conversation.id} 
                  href={`/conversations/${conversation.id}`}
                  className="block"
                >
                  <div className="glass-card hover:border-color transition-all cursor-pointer">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          {conversation.isForked && (
                            <span className="text-blue-400 text-sm">🔄</span>
                          )}
                          <h3 className="text-subheading text-white">
                            {conversation.title}
                          </h3>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            conversation.status === 'posted' 
                              ? 'bg-green-900/30 text-green-300 border border-green-700/30'
                              : 'bg-orange-900/30 text-orange-300 border border-orange-700/30'
                          }`}>
                            {conversation.status === 'posted' ? '✅ Published' : '📝 Draft'}
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-6 text-caption">
                          <span>{conversation.createdAt}</span>
                          <span>{conversation.messageCount} messages</span>
                          {conversation.isForked && (
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
