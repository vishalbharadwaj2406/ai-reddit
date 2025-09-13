/**
 * Base Glass Header Hook
 * Foundation hook providing universal header clearance
 */

'use client';

import { useEffect } from 'react';
import { useSidebarStore } from '@/lib/stores/sidebarStore';
import { initializeLayoutSystem, updateSidebarVariable, CLEARANCES } from '@/lib/layout/tokens';
import { BASE_CLASSES } from '@/lib/layout/constants';
import { HeaderLayoutSystem } from '@/lib/layout/types';

/**
 * Universal header clearance for all pages
 * Provides consistent header spacing across application
 */
export function useGlassHeader(): HeaderLayoutSystem {
  const { isExpanded } = useSidebarStore();

  // Initialize layout system once
  useEffect(() => {
    initializeLayoutSystem();
    updateSidebarVariable(isExpanded);
  }, [isExpanded]);

  return {
    // Base container classes
    pageClass: BASE_CLASSES.page,
    contentClass: BASE_CLASSES.content,
    panelClass: BASE_CLASSES.panel,
    
    // Header clearance with content padding
    headerClearance: { 
      paddingTop: `${CLEARANCES.HEADER_WITH_CONTENT}px` 
    },
  };
}