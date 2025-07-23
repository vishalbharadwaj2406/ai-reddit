'use client'

import React from 'react'
import { Sidebar } from '@/components/Sidebar'
import styles from './AppLayout.module.css'
import { useSidebarStore } from '@/lib/stores/sidebarStore'

interface AppLayoutProps {
  children: React.ReactNode
}

export default function AppLayout({ children }: AppLayoutProps) {
  const { isExpanded } = useSidebarStore()

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