/**
 * Production-Grade Layout Tokens - Single Source of Truth
 * All layout dimensions and calculations centralized here
 */

// Core layout dimensions - Measured from actual components
export const LAYOUT_TOKENS = {
  // Header
  HEADER_HEIGHT: 64,
  
  // Sidebar
  SIDEBAR_COLLAPSED: 64,
  SIDEBAR_EXPANDED: 256,
  
  // Input System - Properly measured and tokenized
  INPUT_CONTAINER_HEIGHT: 120,  // Full container with padding
  INPUT_FIELD_HEIGHT: 56,       // Actual input field
  INPUT_PADDING_VERTICAL: 16,   // Top/bottom padding
  INPUT_PADDING_HORIZONTAL: 20, // Left/right padding
  
  // Glass effect safe zones
  GLASS_SAFE_ZONE: 20,          // Reading comfort zone behind glass
  CONTENT_SAFE_ZONE: 16,        // Content spacing
} as const;

// Calculated layout values - Never hardcode these anywhere
export const CALCULATED_TOKENS = {
  // Available heights
  AVAILABLE_HEIGHT: `calc(100vh - ${LAYOUT_TOKENS.HEADER_HEIGHT}px)`,
  CHAT_CONTENT_HEIGHT: `calc(100vh - ${LAYOUT_TOKENS.HEADER_HEIGHT}px - ${LAYOUT_TOKENS.INPUT_CONTAINER_HEIGHT}px)`,
  BLOG_CONTENT_HEIGHT: `calc(100vh - ${LAYOUT_TOKENS.HEADER_HEIGHT}px)`,
  
  // Glass scroll paddings for when content scrolls behind glass elements
  GLASS_TOP_PADDING: LAYOUT_TOKENS.HEADER_HEIGHT + LAYOUT_TOKENS.GLASS_SAFE_ZONE,
  GLASS_BOTTOM_PADDING: LAYOUT_TOKENS.INPUT_CONTAINER_HEIGHT + LAYOUT_TOKENS.GLASS_SAFE_ZONE,
} as const;

// CSS custom properties for runtime theming
export const CSS_VARIABLES = {
  // Core dimensions
  '--header-height': `${LAYOUT_TOKENS.HEADER_HEIGHT}px`,
  '--sidebar-collapsed': `${LAYOUT_TOKENS.SIDEBAR_COLLAPSED}px`,
  '--sidebar-expanded': `${LAYOUT_TOKENS.SIDEBAR_EXPANDED}px`,
  
  // Input system
  '--input-container-height': `${LAYOUT_TOKENS.INPUT_CONTAINER_HEIGHT}px`,
  '--input-field-height': `${LAYOUT_TOKENS.INPUT_FIELD_HEIGHT}px`,
  '--input-padding-vertical': `${LAYOUT_TOKENS.INPUT_PADDING_VERTICAL}px`,
  '--input-padding-horizontal': `${LAYOUT_TOKENS.INPUT_PADDING_HORIZONTAL}px`,
  
  // Safe zones
  '--glass-safe-zone': `${LAYOUT_TOKENS.GLASS_SAFE_ZONE}px`,
  '--content-safe-zone': `${LAYOUT_TOKENS.CONTENT_SAFE_ZONE}px`,
  
  // Calculated heights
  '--available-height': CALCULATED_TOKENS.AVAILABLE_HEIGHT,
  '--chat-content-height': CALCULATED_TOKENS.CHAT_CONTENT_HEIGHT,
  '--blog-content-height': CALCULATED_TOKENS.BLOG_CONTENT_HEIGHT,
  '--glass-top-padding': `${CALCULATED_TOKENS.GLASS_TOP_PADDING}px`,
  '--glass-bottom-padding': `${CALCULATED_TOKENS.GLASS_BOTTOM_PADDING}px`,
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
export type CalculatedToken = keyof typeof CALCULATED_TOKENS;
export type CSSVariable = keyof typeof CSS_VARIABLES;
