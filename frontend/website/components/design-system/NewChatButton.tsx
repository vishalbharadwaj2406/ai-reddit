'use client'

import React, { useState } from 'react'
import { MessageSquarePlus } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { conversationService, AuthenticationRequiredError, ConversationServiceError } from '@/lib/services/conversationService'
import styles from './NewChatButton.module.css'

interface NewChatButtonProps {
  variant?: 'sidebar' | 'header'
  onClick?: () => void
  className?: string
  showText?: boolean
}

const getErrorMessage = (err: unknown): string => {
  if (err instanceof Error) return err.message;
  if (typeof err === 'string') return err;
  return 'Unknown error';
};

export default function NewChatButton({ 
  variant = 'sidebar', 
  onClick, 
  className = '',
  showText = true 
}: NewChatButtonProps) {
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
      className={`${styles.newChatButton} ${styles[variant]} ${className}`}
      onClick={handleClick}
      disabled={isCreating}
      aria-label={isCreating ? 'Creating new conversation...' : 'Start new conversation'}
    >
      <MessageSquarePlus className={styles.buttonIcon} />
      {showText && (
        <span className={styles.buttonText}>
          {isCreating ? 'Creating...' : 'New Chat'}
        </span>
      )}
    </button>
  )
}
