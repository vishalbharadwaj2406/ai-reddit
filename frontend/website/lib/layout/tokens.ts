/**
 * Production-Grade Layout Tokens - Single Source of Truth
 * Clean, minimal token system for glass scroll architecture
 */

// Core layout dimensions - Essential values only
export const LAYOUT_TOKENS = {
  // Header
  HEADER_HEIGHT: 64,
  
  // Sidebar  
  SIDEBAR_COLLAPSED: 64,
  SIDEBAR_EXPANDED: 256,
  
  // Input System - Clean fixed height
  INPUT_HEIGHT: 80,
  INPUT_PADDING: 16,
  
  // Glass scroll safe zones
  SAFE_ZONE: 16,
} as const;

// CSS custom properties for runtime theming - Essential only
export const CSS_VARIABLES = {
  // Core dimensions
  '--header-height': `${LAYOUT_TOKENS.HEADER_HEIGHT}px`,
  '--sidebar-collapsed': `${LAYOUT_TOKENS.SIDEBAR_COLLAPSED}px`,
  '--sidebar-expanded': `${LAYOUT_TOKENS.SIDEBAR_EXPANDED}px`,
  
  // Input system
  '--input-height': `${LAYOUT_TOKENS.INPUT_HEIGHT}px`,
  '--input-padding': `${LAYOUT_TOKENS.INPUT_PADDING}px`,
  
  // Safe zones for glass scroll
  '--safe-zone': `${LAYOUT_TOKENS.SAFE_ZONE}px`,
  
  // Calculated clearances (for CSS usage)
  '--top-clearance': `${LAYOUT_TOKENS.HEADER_HEIGHT + LAYOUT_TOKENS.SAFE_ZONE}px`,
  '--bottom-clearance': `${LAYOUT_TOKENS.INPUT_HEIGHT + LAYOUT_TOKENS.SAFE_ZONE}px`,
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
