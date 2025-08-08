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

const getErrorMessage = (err: unknown): string => {
  if (err instanceof Error) return err.message;
  if (typeof err === 'string') return err;
  return 'Unknown error';
};

export default function SidebarButton({ onClick, className = '' }: SidebarButtonProps) {
  const { isExpanded } = useSidebarStore()
  const router = useRouter()
  const [isCreating, setIsCreating] = useState(false)

  const handleClick = async () => {
    if (isCreating) return;
    try {
      setIsCreating(true)
      const conversation = await conversationService.createConversation({ title: 'Untitled' })
      router.push(`/conversations/${conversation.conversation_id}`)
      onClick?.()
    } catch (err) {
      const msg = getErrorMessage(err)
      if (err instanceof AuthenticationRequiredError) {
        console.error('Authentication required for creating conversation')
      } else if (err instanceof ConversationServiceError) {
        console.error('Conversation service error:', err.message)
      } else {
        console.error('Failed to create conversation:', msg)
      }
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <button
      className={`${styles.newChatButton} ${className}`}
      onClick={handleClick}
      disabled={isCreating}
      aria-label={isCreating ? 'Creating new conversation...' : 'Start new conversation'}
    >
      <MessageSquarePlus className={styles.buttonIcon} />
      {isExpanded && (
        <span className={styles.buttonText}>
          {isCreating ? 'Creating...' : 'New Chat'}
        </span>
      )}
    </button>
  )
}