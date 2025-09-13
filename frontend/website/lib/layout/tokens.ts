/**
 * Production-Grade Layout Tokens
 * Clean design system with 4px scale and proper typography hierarchy
 */

import { TypographyScale } from './types';

// Core layout dimensions
export const LAYOUT_TOKENS = {
  // Header system
  HEADER_HEIGHT: 64,
  
  // Sidebar system  
  SIDEBAR_COLLAPSED: 64,
  SIDEBAR_EXPANDED: 256,
  
  // Input system - Dynamic with proper bounds
  INPUT_MIN_HEIGHT: 96,
  INPUT_MAX_HEIGHT: 200,
  
  // Spacing scale - 4px increments (industry standard)
  SPACE_1: 4,    // Minimal
  SPACE_2: 8,    // Small (content padding)  
  SPACE_3: 12,   // Medium-small
  SPACE_4: 16,   // Medium (safe zone)
  SPACE_5: 20,   // Medium-large
  SPACE_6: 24,   // Large
  SPACE_8: 32,   // Extra large
  
  // Semantic spacing (using scale above)
  SAFE_ZONE: 16,           // SPACE_4
  CONTENT_PADDING: 8,      // SPACE_2
} as const;

// Calculated clearances
export const CLEARANCES = {
  HEADER: LAYOUT_TOKENS.HEADER_HEIGHT + LAYOUT_TOKENS.SAFE_ZONE,                    // 80px
  INPUT: LAYOUT_TOKENS.INPUT_MIN_HEIGHT + LAYOUT_TOKENS.SAFE_ZONE,                 // 112px
  HEADER_WITH_CONTENT: LAYOUT_TOKENS.HEADER_HEIGHT + LAYOUT_TOKENS.SAFE_ZONE + LAYOUT_TOKENS.CONTENT_PADDING,  // 88px
  INPUT_WITH_CONTENT: LAYOUT_TOKENS.INPUT_MIN_HEIGHT + LAYOUT_TOKENS.SAFE_ZONE + LAYOUT_TOKENS.CONTENT_PADDING, // 120px
} as const;

// Typography scale - Proper visual hierarchy
export const TYPOGRAPHY_SCALE: Record<string, TypographyScale> = {
  H1: { fontSize: '1.875rem', fontWeight: 800, lineHeight: 1.2 }, // 30px
  H2: { fontSize: '1.5rem',   fontWeight: 700, lineHeight: 1.3 }, // 24px  
  H3: { fontSize: '1.25rem',  fontWeight: 600, lineHeight: 1.4 }, // 20px
  H4: { fontSize: '1.125rem', fontWeight: 600, lineHeight: 1.4 }, // 18px
  H5: { fontSize: '1rem',     fontWeight: 600, lineHeight: 1.5 }, // 16px
  H6: { fontSize: '0.875rem', fontWeight: 600, lineHeight: 1.5 }, // 14px
} as const;

// Text color hierarchy - Production-grade dark theme
export const TEXT_COLORS = {
  PRIMARY: 'rgba(255, 255, 255, 0.95)',
  SECONDARY: 'rgba(255, 255, 255, 0.9)', 
  TERTIARY: 'rgba(255, 255, 255, 0.7)',
  DISABLED: 'rgba(255, 255, 255, 0.4)',
  PURE: '#FFFFFF',
} as const;

// CSS custom properties - Clean, minimal set
export const CSS_VARIABLES = {
  // Core dimensions
  '--header-height': `${LAYOUT_TOKENS.HEADER_HEIGHT}px`,
  '--sidebar-collapsed': `${LAYOUT_TOKENS.SIDEBAR_COLLAPSED}px`,
  '--sidebar-expanded': `${LAYOUT_TOKENS.SIDEBAR_EXPANDED}px`,
  
  // Input system
  '--input-min-height': `${LAYOUT_TOKENS.INPUT_MIN_HEIGHT}px`,
  '--input-max-height': `${LAYOUT_TOKENS.INPUT_MAX_HEIGHT}px`,
  
  // Spacing system
  '--safe-zone': `${LAYOUT_TOKENS.SAFE_ZONE}px`,
  '--content-padding': `${LAYOUT_TOKENS.CONTENT_PADDING}px`,
  
  // Calculated clearances
  '--header-clearance': `${CLEARANCES.HEADER}px`,
  '--input-clearance': `${CLEARANCES.INPUT}px`,
  '--header-with-content': `${CLEARANCES.HEADER_WITH_CONTENT}px`,
  '--input-with-content': `${CLEARANCES.INPUT_WITH_CONTENT}px`,
} as const;

/**
 * Initialize layout system - Sets all CSS variables
 * Call this once when the app starts
 */
export function initializeLayoutSystem(): void {
  if (typeof document === 'undefined') return;
  
  const root = document.documentElement;
  
  // Set all CSS variables from tokens
  Object.entries(CSS_VARIABLES).forEach(([property, value]) => {
    root.style.setProperty(property, value);
  });
}

/**
 * Get current sidebar width as CSS value
 */
export function getSidebarWidthPx(isExpanded: boolean): string {
  return isExpanded ? `${LAYOUT_TOKENS.SIDEBAR_EXPANDED}px` : `${LAYOUT_TOKENS.SIDEBAR_COLLAPSED}px`;
}

/**
 * Update dynamic sidebar CSS variable
 */
export function updateSidebarVariable(isExpanded: boolean): void {
  if (typeof document === 'undefined') return;
  
  document.documentElement.style.setProperty(
    '--sidebar-current', 
    getSidebarWidthPx(isExpanded)
  );
}

// Type exports for TypeScript integration
export type LayoutToken = keyof typeof LAYOUT_TOKENS;
export type CSSVariable = keyof typeof CSS_VARIABLES;
