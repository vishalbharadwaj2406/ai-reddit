'use client'

import React, { useEffect } from 'react'
import { Sidebar } from '@/components/Sidebar'
import styles from './AppLayout.module.css'
import { useSidebarStore } from '@/lib/stores/sidebarStore'
import { initializeLayoutSystem, updateSidebarVariable } from '@/lib/layout/tokens'

interface AppLayoutProps {
  children: React.ReactNode
}

export default function AppLayout({ children }: AppLayoutProps) {
  const { isExpanded } = useSidebarStore()
  
  // Initialize layout system on mount and handle sidebar changes
  useEffect(() => {
    initializeLayoutSystem()
    updateSidebarVariable(isExpanded)
  }, [isExpanded])

  return (
    <div className={styles.layoutContainer}>
      <Sidebar />
      <main 
        className={`${styles.mainContent} ${isExpanded ? styles.expanded : styles.collapsed}`}
      >
        {children}
      </main>
    </div>
  )
} 