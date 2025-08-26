/**
 * Custom hook for managing viewport layout calculations
 * Provides consistent height management across the application
 * accounting for fixed header and responsive design
 */

import { useState, useEffect } from 'react';

interface ViewportLayout {
  /** Available height for page content (viewport minus header) */
  availableHeight: number;
  /** Height of the fixed header */
  headerHeight: number;
  /** Full viewport height */
  viewportHeight: number;
  /** CSS class for content container height */
  contentHeightClass: string;
  /** CSS style object for dynamic height calculations */
  contentStyle: React.CSSProperties;
}

/**
 * Hook that calculates layout dimensions accounting for fixed header
 * @param customHeaderHeight - Override default header height (default: 64px)
 * @returns Layout calculations and CSS helpers
 */
export function useViewportLayout(customHeaderHeight?: number): ViewportLayout {
  const HEADER_HEIGHT = customHeaderHeight ?? 64; // Fixed header height
  
  const [viewportHeight, setViewportHeight] = useState(0);
  
  // Update viewport height on resize and initial mount
  useEffect(() => {
    const updateHeight = () => {
      setViewportHeight(window.innerHeight);
    };
    
    // Set initial height
    updateHeight();
    
    // Listen for resize events
    window.addEventListener('resize', updateHeight);
    
    // Listen for orientation changes on mobile
    window.addEventListener('orientationchange', () => {
      // Delay to account for browser UI changes
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
    contentHeightClass: 'h-full', // Use h-full since AppLayout manages the height
    contentStyle: {
      height: '100%', // Full height of the available space
      maxHeight: '100%', // Prevent overflow
      overflow: 'hidden' // Each component manages its own scrolling
    }
  };
}

/**
 * Hook specifically for page containers that need full available height
 * Provides common patterns for full-height pages
 */
export function usePageLayout() {
  const layout = useViewportLayout();
  
  return {
    ...layout,
    /** Props for page container div */
    containerProps: {
      className: 'h-full flex flex-col',
      style: { height: '100%' }
    },
    /** Props for scrollable content area */
    scrollableProps: {
      className: 'flex-1 overflow-y-auto overflow-x-hidden',
      style: { minHeight: 0 } // Allow flex shrinking
    },
    /** Props for fixed elements (headers, footers) */
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
