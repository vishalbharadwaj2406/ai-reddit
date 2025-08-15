"use client";

import React from 'react';
import { MoreHorizontal } from 'lucide-react';
import { usePortalDropdown } from './hooks/usePortalDropdown';
import { Portal } from './Portal';

interface ConversationDropdownProps {
  conversationId: string;
  onOpenConversation: () => void;
  onDeleteConversation: () => void;
  className?: string;
}

/**
 * Production-grade conversation action dropdown using portal rendering.
 * Escapes stacking contexts and provides consistent positioning.
 */
export function ConversationDropdown({
  conversationId,
  onOpenConversation,
  onDeleteConversation,
  className
}: ConversationDropdownProps) {
  const {
    isOpen,
    toggle,
    close,
    triggerRef,
    dropdownRef,
    position,
    usePortal
  } = usePortalDropdown<HTMLButtonElement>({
    closeOnClickOutside: true,
    closeOnEscape: true,
    usePortal: true
  });

  const handleOpenConversation = (e: React.MouseEvent) => {
    e.stopPropagation();
    close();
    onOpenConversation();
  };

  const handleDeleteConversation = (e: React.MouseEvent) => {
    e.stopPropagation();
    close();
    onDeleteConversation();
  };

  return (
    <div className="relative">
      <button
        ref={triggerRef}
        aria-label="Actions"
        className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
        onClick={(e) => {
          e.stopPropagation();
          toggle();
        }}
      >
        <MoreHorizontal size={18} />
      </button>
      
      {/* Portal-rendered dropdown */}
      <Portal isActive={usePortal && isOpen}>
        {isOpen && (
          <div 
            ref={dropdownRef}
            className="glass-dropdown py-2"
            style={{
              position: usePortal ? 'fixed' : 'absolute',
              top: usePortal ? position.top : '100%',
              left: usePortal ? position.left : undefined,
              right: usePortal ? position.right : 0,
              bottom: usePortal ? position.bottom : undefined,
              marginTop: usePortal ? 0 : '8px',
              minWidth: usePortal ? position.minWidth || '192px' : '192px',
              maxWidth: usePortal ? position.maxWidth : undefined,
              zIndex: 'var(--z-dropdown)'
            }}
          >
            <button 
              className="glass-dropdown-item w-full text-left px-4 py-3 text-sm"
              onClick={handleOpenConversation}
            >
              Open conversation
            </button>
            <button 
              className="glass-dropdown-item danger w-full text-left px-4 py-3 text-sm"
              onClick={handleDeleteConversation}
            >
              Delete conversation
            </button>
          </div>
        )}
      </Portal>
    </div>
  );
}
