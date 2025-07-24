'use client'

import React, { useEffect } from 'react'
import { Home, MessageCircle } from 'lucide-react'
import { usePathname } from 'next/navigation'
import styles from './Sidebar.module.css'
import SidebarButton from './SidebarButton'
import SidebarNavItem from './SidebarNavItem'
import { useSidebarStore } from '@/lib/stores/sidebarStore'

export default function Sidebar() {
  const pathname = usePathname()
  const { 
    isExpanded, 
    isMobileOpen, 
    setMobileOpen, 
    setExpanded 
  } = useSidebarStore()

  // Auto-collapse on mobile screens
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth <= 767) {
        setExpanded(false)
      }
    }

    handleResize() // Check on mount
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [setExpanded])

  // Close mobile sidebar on route changes
  useEffect(() => {
    setMobileOpen(false)
  }, [pathname, setMobileOpen])

  // Determine if we're on mobile
  const [isMobile, setIsMobile] = React.useState(false)
  
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 767)
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Single sidebar with conditional classes
  const sidebarClasses = `
    ${styles.sidebar} 
    ${isExpanded ? styles.expanded : styles.collapsed}
    ${isMobile ? styles.mobile : ''}
    ${isMobile && isMobileOpen ? styles.open : ''}
  `.trim()

  return (
    <>
      {/* Mobile Backdrop - only show on mobile when open */}
      {isMobile && (
        <div 
          className={`${styles.mobileBackdrop} ${isMobileOpen ? styles.open : ''}`}
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Single Sidebar */}
      <aside className={sidebarClasses} aria-label="Navigation sidebar">
        <div className={styles.sidebarContent}>
          {/* New Chat Button */}
          <div className={styles.newChatContainer}>
            <SidebarButton />
          </div>

          {/* Navigation Items */}
          <nav className={styles.navSection} role="navigation">
            <SidebarNavItem
              icon={Home}
              label="Feed"
              href="/feed"
              isActive={pathname === '/' || pathname === '/feed'}
            />
            <SidebarNavItem
              icon={MessageCircle}
              label="Conversations"
              href="/conversations"
              isActive={pathname.startsWith('/conversations')}
            />
          </nav>
        </div>
      </aside>
    </>
  )
} 