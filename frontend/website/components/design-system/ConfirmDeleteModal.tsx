'use client'

import React from 'react'
import Modal from './Modal'
import styles from './ConfirmDeleteModal.module.css'

interface ConfirmDeleteModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  conversationTitle: string
  isDeleting?: boolean
}

export default function ConfirmDeleteModal({ 
  isOpen, 
  onClose, 
  onConfirm, 
  conversationTitle, 
  isDeleting = false 
}: ConfirmDeleteModalProps) {
  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose} 
      title="Delete this conversation?"
      className={styles.confirmModal}
    >
      <p className={styles.message}>
        <span className={styles.conversationTitle}>&ldquo;{conversationTitle}&rdquo;</span> will be permanently deleted. This action cannot be undone.
      </p>
      
      <div className={styles.actions}>
        <button 
          className={styles.cancelButton}
          onClick={onClose}
          disabled={isDeleting}
          type="button"
        >
          Cancel
        </button>
        
        <button 
          className={styles.deleteButton}
          onClick={onConfirm}
          disabled={isDeleting}
          type="button"
        >
          {isDeleting ? (
            <>
              <div className={styles.spinner}></div>
              Deleting...
            </>
          ) : (
            <>
              <svg className={styles.deleteIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Delete
            </>
          )}
        </button>
      </div>
    </Modal>
  )
}
