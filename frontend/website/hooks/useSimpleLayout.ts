/**
 * Simple Layout Hook
 * Professional, industry-standard layout system
 * Replaces the overcomplicated glass scroll system
 */

'use client';

import { useEffect } from 'react';
import { useSidebarStore } from '@/lib/stores/sidebarStore';
import { 
  initializeLayoutSystem, 
  updateSidebarVariable,
} from '@/lib/layout/tokens';

interface SimpleLayoutProps {
  className?: string;
  style?: React.CSSProperties;
}

interface SimpleLayoutSystem {
  // Page container with padding-top approach
  pageContainerProps: SimpleLayoutProps;
  
  // Panel grid for 2-panel layout
  panelGridProps: SimpleLayoutProps;
  
  // Chat panel with proper height
  chatPanelProps: SimpleLayoutProps;
  
  // Blog panel with simple scroll
  blogPanelProps: SimpleLayoutProps;
  
  // Messages area within chat panel
  messagesAreaProps: SimpleLayoutProps;
  
  // Input area within chat panel
  inputAreaProps: SimpleLayoutProps;
}

/**
 * Simple, professional layout hook
 * Uses industry-standard padding-top approach for fixed header
 */
export function useSimpleLayout(): SimpleLayoutSystem {
  const { isExpanded } = useSidebarStore();
  
  // Initialize layout system
  useEffect(() => {
    initializeLayoutSystem();
    updateSidebarVariable(isExpanded);
  }, [isExpanded]);
  
  return {
    // Page container - padding-top approach for glass effect
    pageContainerProps: {
      style: {
        paddingTop: 'var(--header-height)',
        height: '100vh',
        overflow: 'hidden',
      }
    },
    
    // Panel grid - simple CSS Grid
    panelGridProps: {
      style: {
        height: 'var(--available-height)',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
      }
    },
    
    // Chat panel - flex column layout
    chatPanelProps: {
      style: {
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative', // For input area positioning
      }
    },
    
    // Blog panel - simple scroll
    blogPanelProps: {
      style: {
        height: '100%',
        overflowY: 'auto',
        padding: 'var(--content-safe-zone)',
      }
    },
    
    // Messages area - scrollable with padding for input
    messagesAreaProps: {
      style: {
        flex: 1,
        overflowY: 'auto',
        padding: 'var(--content-safe-zone)',
        paddingBottom: 'var(--content-safe-zone)', // Extra space for input
      }
    },
    
    // Input area - fixed within chat panel only
    inputAreaProps: {
      style: {
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: 'var(--input-container-height)',
        background: 'rgba(0, 0, 0, 0.6)',
        backdropFilter: 'blur(20px) saturate(150%)',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        zIndex: 10,
      }
    },
  };
}

/**
 * Hook for pages that don't need complex layout (feed, conversations list)
 */
export function useSimplePageLayout() {
  const { isExpanded } = useSidebarStore();
  
  useEffect(() => {
    initializeLayoutSystem();
    updateSidebarVariable(isExpanded);
  }, [isExpanded]);
  
  return {
    containerProps: {
      style: {
        paddingTop: 'var(--header-height)',
        minHeight: 'var(--available-height)',
        padding: 'var(--content-safe-zone)',
      }
    }
  };
}
