'use client'

import React from 'react'
import { useSessionContext } from '@/components/providers/SessionWrapper'
import { usePathname } from 'next/navigation'
import AppLayout from './AppLayout'

interface ConditionalLayoutProps {
  children: React.ReactNode
}

/**
 * Production-Grade Conditional Layout Component
 * 
 * Provides intelligent layout switching based on authentication state and route:
 * - Unauthenticated users on "/" get full-screen layout (no sidebar)
 * - Authenticated users get standard app layout with sidebar
 * - Loading states handled gracefully
 */
export function ConditionalLayout({ children }: ConditionalLayoutProps) {
  const { isAuthenticated, loading, isInitialized } = useSessionContext()
  const pathname = usePathname()

  // Show loading state while session is being determined
  if (!isInitialized || loading) {
    // For the home page, show content immediately without layout constraints
    // This prevents the blank page issue during loading
    if (pathname === '/') {
      return (
        <div className="min-h-screen">
          {children}
        </div>
      )
    }
    
    // For other pages, show a proper loading state
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // Full-screen layout for unauthenticated users on home page
  // This gives the beautiful welcome page the full viewport it deserves
  if (!isAuthenticated && pathname === '/') {
    return (
      <div className="min-h-screen">
        {children}
      </div>
    )
  }

  // Standard app layout with sidebar for authenticated users and other routes
  // This includes all protected routes like /feed, /conversations, etc.
  return (
    <AppLayout>
      {children}
    </AppLayout>
  )
}
