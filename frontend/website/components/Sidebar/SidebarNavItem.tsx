'use client'

import React from 'react'
import Link from 'next/link'
import { LucideIcon } from 'lucide-react'
import styles from './Sidebar.module.css'
import { useSidebarStore } from '@/lib/stores/sidebarStore'

interface SidebarNavItemProps {
  icon: LucideIcon
  label: string
  href: string
  isActive?: boolean
  onClick?: () => void
}

export default function SidebarNavItem({ 
  icon: Icon, 
  label, 
  href, 
  isActive = false,
  onClick 
}: SidebarNavItemProps) {
  const { isExpanded, setMobileOpen } = useSidebarStore()

  const handleClick = () => {
    // Close mobile sidebar when navigating
    setMobileOpen(false)
    onClick?.()
  }

  return (
    <Link
      href={href}
      className={`${styles.navItem} ${isActive ? styles.active : ''}`}
      onClick={handleClick}
      aria-label={label}
    >
      <Icon className={styles.navIcon} />
      {isExpanded && (
        <span className={styles.navText}>{label}</span>
      )}
    </Link>
  )
} 