'use client'

import React, { useState } from 'react'
import { MessageSquarePlus } from 'lucide-react'
import { useRouter } from 'next/navigation'
import styles from './SidebarButton.module.css'
import { useSidebarStore } from '@/lib/stores/sidebarStore'
import { conversationService, AuthenticationRequiredError, ConversationServiceError } from '@/lib/services/conversationService'

interface SidebarButtonProps {
  onClick?: () => void
  className?: string
}

export default function SidebarButton({ onClick, className = '' }: SidebarButtonProps) {
  const { isExpanded } = useSidebarStore()
  const router = useRouter()
  const [isCreating, setIsCreating] = useState(false)

  const handleClick = async () => {
    try {
      setIsCreating(true)
      
      // Create conversation immediately with default title
      const conversation = await conversationService.createConversation({
        title: 'Untitled'
      })

      // Navigate to the new conversation
      router.push(`/conversations/${conversation.conversation_id}`)
      
      // Reset creating state after successful redirect
      setIsCreating(false)
      
      onClick?.()
    } catch (err: any) {
      setIsCreating(false)
      
      // For sidebar button, we'll just log errors and try to show some feedback
      if (err instanceof AuthenticationRequiredError) {
        console.error('Authentication required for creating conversation')
        // Could show a toast notification here
      } else {
        console.error('Failed to create conversation:', err)
        // Could show a toast notification here
      }
    }
  }

  return (
    <button
      className={`${styles.newChatButton} ${className}`}
      onClick={handleClick}
      disabled={isCreating}
      aria-label={isCreating ? "Creating new conversation..." : "Start new conversation"}
    >
      <MessageSquarePlus 
        className={styles.buttonIcon}
      />
      {isExpanded && (
        <span className={styles.buttonText}>
          {isCreating ? 'Creating...' : 'New Chat'}
        </span>
      )}
    </button>
  )
} 