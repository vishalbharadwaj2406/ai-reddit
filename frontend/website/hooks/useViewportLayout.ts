/**
 * DEPRECATED: Legacy viewport layout hook
 * 
 * ⚠️  This hook is deprecated and should not be used in new code.
 * 
 * Use the new glass scroll system instead:
 * - useGlassScroll() for glass morphism scroll layouts
 * - usePageGlassScroll() for page-level layouts  
 * - usePanelGlassScroll() for panel-level layouts
 * 
 * The new system provides:
 * - Centralized design tokens from @/lib/layout/tokens
 * - Automatic CSS variable management
 * - Production-grade glass scroll effects
 * - Better height cascade management
 * 
 * Migration guide:
 * - Replace usePageLayout() with usePageGlassScroll()
 * - Use layout tokens from @/lib/layout/tokens instead of hardcoded values
 * - Apply glass scroll classes to enable beautiful behind-glass scrolling
 * 
 * This file will be removed in a future version.
 */

import { useState, useEffect } from 'react';

interface ViewportLayout {
  /** @deprecated Use useGlassScroll instead */
  availableHeight: number;
  /** @deprecated Use LAYOUT_TOKENS.HEADER_HEIGHT instead */
  headerHeight: number;
  /** @deprecated Use window.innerHeight directly */
  viewportHeight: number;
  /** @deprecated Use glass scroll classes instead */
  contentHeightClass: string;
  /** @deprecated Use glass scroll inline styles instead */
  contentStyle: React.CSSProperties;
}

/**
 * @deprecated Use useGlassScroll() instead
 * This hook will be removed in a future version
 */
export function useViewportLayout(customHeaderHeight?: number): ViewportLayout {
  console.warn(
    '⚠️  useViewportLayout is deprecated. Use useGlassScroll() from @/hooks/useGlassScroll instead.'
  );
  
  const HEADER_HEIGHT = customHeaderHeight ?? 64;
  const [viewportHeight, setViewportHeight] = useState(0);
  
  useEffect(() => {
    const updateHeight = () => {
      setViewportHeight(window.innerHeight);
    };
    
    updateHeight();
    window.addEventListener('resize', updateHeight);
    window.addEventListener('orientationchange', () => {
      setTimeout(updateHeight, 100);
    });
    
    return () => {
      window.removeEventListener('resize', updateHeight);
      window.removeEventListener('orientationchange', updateHeight);
    };
  }, []);
  
  const availableHeight = Math.max(0, viewportHeight - HEADER_HEIGHT);
  
  return {
    availableHeight,
    headerHeight: HEADER_HEIGHT,
    viewportHeight,
    contentHeightClass: 'h-full',
    contentStyle: {
      height: '100%',
      maxHeight: '100%',
      overflow: 'hidden'
    }
  };
}

/**
 * @deprecated Use usePageGlassScroll() instead
 * This hook will be removed in a future version
 */
export function usePageLayout() {
  console.warn(
    '⚠️  usePageLayout is deprecated. Use usePageGlassScroll() from @/hooks/useGlassScroll instead.'
  );
  
  const layout = useViewportLayout();
  
  return {
    ...layout,
    containerProps: {
      className: 'flex flex-col',
      style: { 
        height: 'calc(100vh - 64px)', // Keep old broken behavior for compatibility
        maxHeight: 'calc(100vh - 64px)',
        overflow: 'hidden'
      }
    },
    scrollableProps: {
      className: 'flex-1 overflow-y-auto overflow-x-hidden',
      style: { minHeight: 0 }
    },
    fixedProps: {
      className: 'flex-shrink-0'
    }
  };
}

/**
 * CSS custom properties for consistent layout calculations
 * Can be used in CSS files for static calculations
 */
export const LAYOUT_CSS_VARS = {
  '--header-height': '64px',
  '--input-height': '100px', // Fixed input area height
  '--available-height': 'calc(100vh - var(--header-height))',
  '--content-height': 'calc(100vh - var(--header-height) - var(--input-height))',
  '--safe-area-height': 'calc(100vh - var(--header-height) - env(safe-area-inset-bottom))'
} as const;

/**
 * Layout constants for consistent spacing
 */
export const LAYOUT_CONSTANTS = {
  HEADER_HEIGHT: 64,
  INPUT_HEIGHT: 100,
  SIDEBAR_COLLAPSED: 64,
  SIDEBAR_EXPANDED: 256,
  // Glass scroll padding - ensures content doesn't hide behind glass elements
  GLASS_SAFE_ZONE: 20, // Extra padding for comfortable reading
  SCROLL_COMFORT_ZONE: 16 // Additional space for better UX
} as const;

/**
 * Calculate padding for glass scroll effect
 * Ensures content can scroll behind glass elements but remains readable
 */
export const getGlassScrollPadding = () => ({
  // Top padding: Header + safe zone for comfortable reading
  top: LAYOUT_CONSTANTS.HEADER_HEIGHT + LAYOUT_CONSTANTS.GLASS_SAFE_ZONE,
  // Bottom padding: Input + safe zone for comfortable reading  
  bottom: LAYOUT_CONSTANTS.INPUT_HEIGHT + LAYOUT_CONSTANTS.GLASS_SAFE_ZONE,
  // Content comfort zones for first/last items
  contentTop: LAYOUT_CONSTANTS.SCROLL_COMFORT_ZONE,
  contentBottom: LAYOUT_CONSTANTS.SCROLL_COMFORT_ZONE
});
