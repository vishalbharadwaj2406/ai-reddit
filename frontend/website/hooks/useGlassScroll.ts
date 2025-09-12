/**
 * Production-Grade Layout System
 * 
 * Clean, maintainable layout management using industry-standard patterns:
 * - CSS Grid for 2-panel layouts
 * - Flexbox for panel internal structure  
 * - CSS variables for consistent spacing
 * - Responsive design considerations
 * - No complex absolute positioning
 * 
 * Architecture:
 * - pageContainerProps: Main page with header clearance
 * - conversationContainerProps: 2-panel CSS Grid container
 * - chatPanelProps: Left panel (always visible)
 * - blogPanelProps: Right panel (conditional)
 * - Internal scrolling management per panel
 */

'use client';

import { useEffect } from 'react';
import { useSidebarStore } from '@/lib/stores/sidebarStore';
import { 
  initializeLayoutSystem, 
  updateSidebarVariable,
} from '@/lib/layout/tokens';

interface LayoutContainerProps {
  style: React.CSSProperties;
  className?: string;
}

interface SimpleLayoutSystem {
  /** Props for the main page container (with header padding) */
  pageContainerProps: LayoutContainerProps;
  /** Props for the conversation container (2-panel grid) */
  conversationContainerProps: LayoutContainerProps;
  /** Props for chat panel */
  chatPanelProps: LayoutContainerProps;
  /** Props for blog panel */
  blogPanelProps: LayoutContainerProps;
  /** Props for messages area in chat panel */
  messagesAreaProps: LayoutContainerProps;
  /** Props for input area in chat panel */
  inputAreaProps: LayoutContainerProps;
}

/**
 * Production-grade layout hook for conversation pages
 * 
 * Provides consistent layout props for:
 * - 2-panel conversation interface
 * - Single-panel mode when blog is hidden
 * - Proper height management and scrolling
 * - Glass morphism header integration
 * 
 * Uses CSS Grid for clean, predictable panel behavior
 */
export function useSimpleLayout(): SimpleLayoutSystem {
  const { isExpanded } = useSidebarStore();

  // Initialize layout system on mount
  useEffect(() => {
    initializeLayoutSystem();
  }, []);

  // Update sidebar variable when sidebar state changes
  useEffect(() => {
    updateSidebarVariable(isExpanded);
  }, [isExpanded]);

  return {
    // Main page container - creates space for fixed header
    pageContainerProps: {
      style: {
        paddingTop: 'var(--header-height)',
        height: '100vh',
        overflow: 'hidden',
      },
      className: 'bg-black',
    },

    // Conversation container - clean 2-panel CSS Grid
    conversationContainerProps: {
      style: {
        height: 'var(--available-height)',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gridTemplateRows: '1fr',
        gap: '1px',
      },
      className: 'bg-gray-700/30', // Visible grid gap
    },

    // Chat panel - flex column for messages + input
    chatPanelProps: {
      style: {
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        overflow: 'hidden',
      },
      className: 'bg-black',
    },

    // Blog panel - full height with internal scrolling
    blogPanelProps: {
      style: {
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      },
      className: 'bg-black border-l border-gray-700/30',
    },

    // Messages area - scrollable with padding for input
    messagesAreaProps: {
      style: {
        height: 'var(--chat-content-height)',
        overflowY: 'auto',
        padding: 'var(--content-safe-zone)',
      },
    },

    // Input area - fixed at bottom of chat panel
    inputAreaProps: {
      style: {
        height: 'var(--input-container-height)',
        background: 'rgba(0, 0, 0, 0.6)',
        backdropFilter: 'blur(20px) saturate(150%)',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        display: 'flex',
        alignItems: 'center',
        padding: 'var(--input-padding-vertical) var(--input-padding-horizontal)',
      },
    },
  };
}

/**
 * Hook for glass scroll effect on content that should scroll behind header
 * Much simpler than the old system - just adds top padding
 */
export function useGlassScrollContent(): LayoutContainerProps {
  return {
    style: {
      paddingTop: 'var(--glass-top-padding)',
      paddingBottom: 'var(--content-safe-zone)',
    },
  };
}
