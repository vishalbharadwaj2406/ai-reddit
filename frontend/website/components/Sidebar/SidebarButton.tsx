'use client'

import React from 'react'
import { MessageSquarePlus } from 'lucide-react'
import { useRouter } from 'next/navigation'
import styles from './SidebarButton.module.css'
import { useSidebarStore } from '@/lib/stores/sidebarStore'

interface SidebarButtonProps {
  onClick?: () => void
  className?: string
}

export default function SidebarButton({ onClick, className = '' }: SidebarButtonProps) {
  const { isExpanded } = useSidebarStore()
  const router = useRouter()

  const handleClick = () => {
    router.push('/conversations/new')
    onClick?.()
  }

  return (
    <button
      className={`${styles.newChatButton} ${className}`}
      onClick={handleClick}
      aria-label="Start new conversation"
    >
      <MessageSquarePlus 
        className={styles.buttonIcon}
      />
      {isExpanded && (
        <span className={styles.buttonText}>New Chat</span>
      )}
    </button>
  )
} 