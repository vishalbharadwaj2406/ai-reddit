'use client'

import React from 'react'
import { MessageSquarePlus } from 'lucide-react'
import styles from './SidebarButton.module.css'
import { useSidebarStore } from '@/lib/stores/sidebarStore'

interface SidebarButtonProps {
  onClick?: () => void
  className?: string
}

export default function SidebarButton({ onClick, className = '' }: SidebarButtonProps) {
  const { isExpanded } = useSidebarStore()

  const handleClick = () => {
    // TODO: Implement new chat functionality
    console.log('New chat clicked')
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