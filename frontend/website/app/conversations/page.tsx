'use client'

import React, { useState, useEffect } from 'react'
import { Search, Users, MessageCircle, TrendingUp, Clock, LogOut, User } from 'lucide-react'
import { useSession, signOut } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import Header from '../../components/Header'

// Temporary types until we implement proper data layer
interface ConversationParticipant {
  id: string
  name: string
  avatar?: string
}

interface EnhancedConversation {
  id: string
  title: string
  description: string
  category: string
  lastMessage: string
  updatedAt: string
  messageCount: number
  unreadCount: number
  isActive: boolean
  participants: ConversationParticipant[]
}

// Temporary mock data - will be replaced with API calls
const mockConversations: EnhancedConversation[] = [
  {
    id: '1',
    title: 'Welcome to AI Social',
    description: 'Getting started with intelligent conversations',
    category: 'General',
    lastMessage: 'Welcome! How can I help you today?',
    updatedAt: new Date().toISOString(),
    messageCount: 3,
    unreadCount: 1,
    isActive: true,
    participants: [
      { id: 'ai-1', name: 'AI Assistant' }
    ]
  }
]

export default function ConversationsPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [searchTerm, setSearchTerm] = useState('')
  const [activeFilter, setActiveFilter] = useState('all')
  const [conversations, setConversations] = useState<EnhancedConversation[]>([])

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/')
    }
  }, [status, router])

  useEffect(() => {
    // Load conversations (in real app, this would be an API call)
    setConversations(mockConversations)
  }, [])

  const filteredConversations = conversations.filter(conv => {
    const matchesSearch = conv.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         conv.description.toLowerCase().includes(searchTerm.toLowerCase())
    
    if (activeFilter === 'all') return matchesSearch
    if (activeFilter === 'trending') return conv.isActive && matchesSearch
    if (activeFilter === 'recent') return conv.unreadCount > 0 && matchesSearch
    if (activeFilter === 'my') return conv.participants.some((p: ConversationParticipant) => p.id === session?.user?.email) && matchesSearch
    
    return matchesSearch
  })

  const stats = {
    total: conversations.length,
    active: conversations.filter(c => c.isActive).length,
    unread: conversations.reduce((sum, c) => sum + c.unreadCount, 0),
    participants: new Set(conversations.flatMap(c => c.participants.map((p: ConversationParticipant) => p.id))).size
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-pure-black flex items-center justify-center">
        <div className="glass-elevated p-8">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 border-2 border-brilliant-blue border-t-transparent rounded-full animate-spin"></div>
            <span className="text-ice-white">Loading conversations...</span>
          </div>
        </div>
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return (
      <div className="min-h-screen bg-pure-black flex items-center justify-center p-4">
        <div className="text-center text-ice-white">
          <MessageCircle className="w-16 h-16 mx-auto mb-4 opacity-50 text-brilliant-blue" />
          <h1 className="text-2xl font-bold mb-2">Please Sign In</h1>
          <p className="text-ice-white/70">You need to be signed in to view conversations</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-pure-black">
      {/* Royal Blue Background Gradients */}
      <div className="fixed top-0 left-0 w-full h-full pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-radial from-royal-blue/12 via-transparent to-transparent animate-royal-flow"></div>
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-brilliant-blue/8 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 left-1/4 w-80 h-80 bg-royal-blue/6 rounded-full blur-3xl"></div>
      </div>

      {/* Header Component */}
      <Header />

      {/* Main Content with top padding for fixed header */}
      <div className="pt-24 p-4">
        {/* Page Header */}
        <div className="max-w-7xl mx-auto mb-8 relative z-10">
          <div className="glass-elevated p-6">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gradient-to-r from-royal-blue to-brilliant-blue rounded-2xl flex items-center justify-center">
                  <MessageCircle className="w-6 h-6 text-ice-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-ice-white">AI Social Conversations</h1>
                  <p className="text-ice-white/70">Connect with AI and community through intelligent conversations</p>
                </div>
              </div>
              
              {/* Search Bar */}
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-ice-white/50" />
                <input
                  type="text"
                  placeholder="Search conversations..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-glass-level1 border-2 border-glass-border rounded-2xl text-ice-white placeholder:text-ice-white/40 focus:outline-none focus:ring-2 focus:ring-brilliant-blue/50 focus:border-brilliant-blue/60 transition-all duration-300 backdrop-blur-xl"
                />
              </div>
            </div>
          </div>
        </div>

      {/* Filter Tabs */}
      <div className="max-w-7xl mx-auto mb-6 relative z-10">
        <div className="glass-standard p-2">
          <div className="flex flex-wrap gap-2">
            {[
              { key: 'all', label: 'All Conversations', icon: MessageCircle },
              { key: 'trending', label: 'Trending', icon: TrendingUp },
              { key: 'recent', label: 'Recent', icon: Clock },
              { key: 'my', label: 'My Conversations', icon: Users }
            ].map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setActiveFilter(key)}
                className={`flex items-center gap-2 px-4 py-2 rounded-2xl transition-all duration-300 hover:-translate-y-0.5 ${
                  activeFilter === key
                    ? 'bg-gradient-to-r from-royal-blue to-brilliant-blue text-ice-white shadow-lg shadow-brilliant-blue/25'
                    : 'text-ice-white/70 hover:bg-glass-level2 hover:text-ice-white border border-glass-border/50'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="font-medium">{label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Conversations Grid */}
      <div className="max-w-7xl mx-auto mb-8 relative z-10">
        {filteredConversations.length === 0 ? (
          <div className="glass-standard p-12 text-center">
            <MessageCircle className="w-16 h-16 mx-auto mb-4 text-ice-white/40" />
            <h3 className="text-xl font-semibold text-ice-white mb-2">No conversations found</h3>
            <p className="text-ice-white/60">Try adjusting your search or filters</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredConversations.map((conversation) => (
              <div
                key={conversation.id}
                className="glass-elevated group hover:glass-floating transition-all duration-500 hover:-translate-y-1 cursor-pointer"
              >
                <div className="p-6">
                  {/* Conversation Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-r from-royal-blue to-brilliant-blue rounded-2xl flex items-center justify-center shadow-lg shadow-royal-blue/30">
                        <MessageCircle className="w-5 h-5 text-ice-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-ice-white group-hover:text-brilliant-blue transition-colors duration-300">
                          {conversation.title}
                        </h3>
                        <p className="text-sm text-ice-white/60">{conversation.category}</p>
                      </div>
                    </div>
                    {conversation.unreadCount > 0 && (
                      <span className="bg-gradient-to-r from-error to-error-light text-ice-white text-xs font-bold px-2 py-1 rounded-full shadow-lg shadow-error/30">
                        {conversation.unreadCount}
                      </span>
                    )}
                  </div>

                  {/* Description */}
                  <p className="text-ice-white/80 text-sm mb-4 line-clamp-2">
                    {conversation.description}
                  </p>

                  {/* Participants */}
                  <div className="flex items-center gap-2 mb-4">
                    <Users className="w-4 h-4 text-ice-white/60" />
                    <div className="flex -space-x-2">
                      {conversation.participants.slice(0, 3).map((participant: ConversationParticipant, index: number) => (
                        <div
                          key={participant.id}
                          className="w-6 h-6 bg-gradient-to-r from-brilliant-blue to-royal-blue rounded-full border-2 border-glass-border flex items-center justify-center shadow-lg"
                          style={{ zIndex: 10 - index }}
                        >
                          <span className="text-xs text-ice-white font-semibold">
                            {participant.name.charAt(0)}
                          </span>
                        </div>
                      ))}
                      {conversation.participants.length > 3 && (
                        <div className="w-6 h-6 bg-glass-level2 rounded-full border-2 border-glass-border flex items-center justify-center">
                          <span className="text-xs text-ice-white">+{conversation.participants.length - 3}</span>
                        </div>
                      )}
                    </div>
                    <span className="text-sm text-ice-white/60 ml-2">
                      {conversation.participants.length} participant{conversation.participants.length !== 1 ? 's' : ''}
                    </span>
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-glass-border/30">
                    <div className="flex items-center gap-4 text-sm text-ice-white/60">
                      <span>{conversation.messageCount} messages</span>
                      {conversation.isActive && (
                        <div className="flex items-center gap-1">
                          <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
                          <span className="text-success">Active</span>
                        </div>
                      )}
                    </div>
                    <button className="text-brilliant-blue hover:text-royal-blue font-medium text-sm transition-colors duration-300 hover:scale-105">
                      Join →
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Stats Footer */}
      <div className="max-w-7xl mx-auto relative z-10">
        <div className="glass-elevated p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-ice-white mb-1">{stats.total}</div>
              <div className="text-sm text-ice-white/60">Total Conversations</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-success mb-1">{stats.active}</div>
              <div className="text-sm text-ice-white/60">Active Now</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-brilliant-blue mb-1">{stats.unread}</div>
              <div className="text-sm text-ice-white/60">Unread Messages</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-royal-blue mb-1">{stats.participants}</div>
              <div className="text-sm text-ice-white/60">Total Participants</div>
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>
  )
}
