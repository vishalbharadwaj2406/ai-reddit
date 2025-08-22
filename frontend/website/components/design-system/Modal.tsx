'use client'

import React, { useEffect, useRef } from 'react'
import styles from './Modal.module.css'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  className?: string
}

export default function Modal({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  className = '' 
}: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null)

  // Enhanced accessibility and keyboard handling
  useEffect(() => {
    if (!isOpen) return

    // Focus management
    const handleFocus = () => {
      if (modalRef.current) {
        modalRef.current.focus()
      }
    }

    // Keyboard navigation
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    // Prevent body scroll
    document.body.style.overflow = 'hidden'
    
    // Add listeners
    document.addEventListener('keydown', handleKeyDown)
    
    // Focus after entrance animation
    const timeoutId = setTimeout(handleFocus, 100)

    return () => {
      document.body.style.overflow = 'unset'
      document.removeEventListener('keydown', handleKeyDown)
      clearTimeout(timeoutId)
    }
  }, [isOpen, onClose])

  // Handle backdrop click
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div 
      className={styles.backdrop}
      onClick={handleBackdropClick}
      role="dialog" 
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div 
        className={`${styles.modal} ${className}`} 
        ref={modalRef}
        tabIndex={-1}
      >
        <div className={styles.header}>
          <h2 id="modal-title" className={styles.title}>
            {title}
          </h2>
          
          <button 
            className={styles.closeBtn} 
            onClick={onClose} 
            aria-label="Close modal"
            type="button"
          >
            ×
          </button>
        </div>
        
        <div className={styles.content}>
          {children}
        </div>
      </div>
    </div>
  )
}
