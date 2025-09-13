/**
 * Production-Grade Glass Layout System
 * 
 * Industry-standard position-based architecture:
 * - Fixed glass elements (header, input) float above content
 * - Content uses padding for clearance (like Discord, Slack, WhatsApp)
 * - No complex flex calculations or negative margins
 * - Clean, maintainable, extensible
 * 
 * Architecture: Position-based glass scroll (Industry Standard)
 */

'use client';

import { useEffect } from 'react';
import { useSidebarStore } from '@/lib/stores/sidebarStore';
import { initializeLayoutSystem, updateSidebarVariable, LAYOUT_TOKENS } from '@/lib/layout/tokens';

interface GlassLayoutSystem {
  /** Page container - full viewport height */
  pageClass: string;
  
  /** Content container - scrollable with glass clearance */
  contentClass: string;
  
  /** Input container - fixed within panel bounds */
  inputClass: string;
  
  /** Panel container - relative positioning context */
  panelClass: string;
  
  /** Dynamic top padding for header clearance */
  topClearance: React.CSSProperties;
  
  /** Dynamic bottom padding for input clearance */
  bottomClearance: React.CSSProperties;
  
  /** Combined clearance for content areas */
  contentClearance: React.CSSProperties;
}

/**
 * Production-grade glass layout hook
 * 
 * Provides industry-standard glass scroll architecture:
 * - Position: fixed for glass elements
 * - Simple padding for content clearance  
 * - Variable-driven spacing (no hardcoding)
 * - Scalable across entire application
 */
export function useGlassLayout(): GlassLayoutSystem {
  const { isExpanded } = useSidebarStore();

  // Initialize layout system on mount
  useEffect(() => {
    initializeLayoutSystem();
    updateSidebarVariable(isExpanded);
  }, [isExpanded]);

  // Calculate clearance using tokens (zero hardcoding)
  const headerHeight = LAYOUT_TOKENS.HEADER_HEIGHT;
  const inputHeight = LAYOUT_TOKENS.INPUT_HEIGHT;
  const safeZone = LAYOUT_TOKENS.SAFE_ZONE;
  
  const topClearance = headerHeight + safeZone;
  const bottomClearance = inputHeight + safeZone;

  return {
    // Page container - full viewport, clean slate
    pageClass: "h-screen bg-black overflow-hidden",
    
    // Content container - industry standard pattern
    contentClass: "h-full overflow-y-auto",
    
    // Input container - fixed within panel (Discord/Slack pattern)
    inputClass: "absolute bottom-0 left-0 right-0 bg-black/60 backdrop-blur-sm border-t border-gray-700/30 z-40",
    
    // Panel container - positioning context for fixed input
    panelClass: "h-full relative bg-black",
    
    // Dynamic clearance styles using variables
    topClearance: { 
      paddingTop: `${topClearance}px` 
    },
    
    bottomClearance: { 
      paddingBottom: `${bottomClearance}px` 
    },
    
    contentClearance: { 
      paddingTop: `${topClearance}px`,
      paddingBottom: `${bottomClearance}px`
    },
  };
}

/**
 * Simple utility for elements that need header clearance only
 */
export function useHeaderClearance() {
  const headerHeight = LAYOUT_TOKENS.HEADER_HEIGHT;
  const safeZone = LAYOUT_TOKENS.SAFE_ZONE;
  
  return {
    paddingTop: `${headerHeight + safeZone}px`
  };
}