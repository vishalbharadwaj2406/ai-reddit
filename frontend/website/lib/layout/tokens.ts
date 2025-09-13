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
  
  // Input System - Dynamic height with minimum (ARCHITECTURAL FIX)
  INPUT_MIN_HEIGHT: 96,   // Minimum height for input area container
  INPUT_MAX_HEIGHT: 200,  // Maximum height before scrolling
  INPUT_PADDING: 16,
  
  // Glass scroll safe zones
  SAFE_ZONE: 16,
} as const;

// Text color hierarchy - Production-grade dark theme best practices
export const TEXT_COLORS = {
  // Primary text - high contrast for main content
  PRIMARY: 'rgba(255, 255, 255, 0.95)',
  
  // Secondary text - slightly muted for supporting content
  SECONDARY: 'rgba(255, 255, 255, 0.9)',
  
  // Tertiary text - muted for metadata, timestamps, etc.
  TERTIARY: 'rgba(255, 255, 255, 0.7)',
  
  // Disabled text - very muted for disabled states
  DISABLED: 'rgba(255, 255, 255, 0.4)',
  
  // Pure white - only for special emphasis
  PURE: '#FFFFFF',
} as const;

// CSS custom properties for runtime theming - Essential only
export const CSS_VARIABLES = {
  // Core dimensions
  '--header-height': `${LAYOUT_TOKENS.HEADER_HEIGHT}px`,
  '--sidebar-collapsed': `${LAYOUT_TOKENS.SIDEBAR_COLLAPSED}px`,
  '--sidebar-expanded': `${LAYOUT_TOKENS.SIDEBAR_EXPANDED}px`,
  
  // Input system - Dynamic values
  '--input-min-height': `${LAYOUT_TOKENS.INPUT_MIN_HEIGHT}px`,
  '--input-max-height': `${LAYOUT_TOKENS.INPUT_MAX_HEIGHT}px`,
  '--input-padding': `${LAYOUT_TOKENS.INPUT_PADDING}px`,
  
  // Safe zones for glass scroll
  '--safe-zone': `${LAYOUT_TOKENS.SAFE_ZONE}px`,
  
  // Calculated clearances (using minimum height for layout stability)
  '--top-clearance': `${LAYOUT_TOKENS.HEADER_HEIGHT + LAYOUT_TOKENS.SAFE_ZONE}px`,
  '--bottom-clearance': `${LAYOUT_TOKENS.INPUT_MIN_HEIGHT + LAYOUT_TOKENS.SAFE_ZONE}px`,
  
  // Text color system
  '--text-primary': TEXT_COLORS.PRIMARY,
  '--text-secondary': TEXT_COLORS.SECONDARY,
  '--text-tertiary': TEXT_COLORS.TERTIARY,
  '--text-disabled': TEXT_COLORS.DISABLED,
  '--text-pure': TEXT_COLORS.PURE,
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
