/**
 * Production-Grade Glass Layout System
 * 
 * Industry-standard position-based architecture with unified glass styling:
 * - Fixed glass elements (header, input) with identical visual treatment
 * - Content uses padding for clearance (like Discord, Slack, WhatsApp)
 * - Single glass layer strategy - no competing visual effects
 * - Dynamic input heights with proper overflow handling
 * - Clean, maintainable, extensible architecture
 * 
 * Architecture: Position-based glass scroll with header consistency
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
  
  /** Input container - fixed with exact header glass styling */
  inputClass: string;
  
  /** Panel container - relative positioning context */
  panelClass: string;
  
  /** Dynamic top padding for header clearance */
  topClearance: React.CSSProperties;
  
  /** Dynamic bottom padding for input clearance */
  bottomClearance: React.CSSProperties;
  
  /** Combined clearance for content areas */
  contentClearance: React.CSSProperties;
  
  /** Header-matching glass styles for input area */
  headerGlassStyle: React.CSSProperties;
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
  const inputMinHeight = LAYOUT_TOKENS.INPUT_MIN_HEIGHT;
  const safeZone = LAYOUT_TOKENS.SAFE_ZONE;
  
  const topClearance = headerHeight + safeZone;
  const bottomClearance = inputMinHeight + safeZone;

  // Exact header glass styling for perfect consistency
  const headerGlassStyle: React.CSSProperties = {
    background: 'rgba(0, 0, 0, 0.6)',
    backdropFilter: 'blur(24px) saturate(180%)',
    WebkitBackdropFilter: 'blur(24px) saturate(180%)',
    borderTop: '1px solid rgba(59, 130, 246, 0.15)',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3), 0 0 40px rgba(30, 58, 138, 0.12)',
  };

  return {
    // Page container - full viewport, clean slate
    pageClass: "h-screen bg-black overflow-hidden",
    
    // Content container - industry standard pattern
    contentClass: "h-full overflow-y-auto",
    
    // Input container - clean base for header glass styling
    inputClass: "absolute bottom-0 left-0 right-0 z-40",
    
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

    // Header-matching glass styles for perfect consistency
    headerGlassStyle,
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