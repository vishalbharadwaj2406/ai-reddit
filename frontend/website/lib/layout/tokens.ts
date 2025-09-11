/**
 * Production-Grade Layout Tokens
 * Self-contained token system for maximum reliability
 */

// Core layout dimensions - hardcoded for production stability
export const LAYOUT_TOKENS = {
  // Header
  HEADER_HEIGHT: 64, // 64px as number
  HEADER_HEIGHT_PX: '64px', // '64px' as string
  
  // Sidebar
  SIDEBAR_COLLAPSED: 64, // 64px
  SIDEBAR_EXPANDED: 256, // 256px
  SIDEBAR_COLLAPSED_PX: '64px',
  SIDEBAR_EXPANDED_PX: '256px',
  
  // Input area (measured from actual component)
  INPUT_HEIGHT: 100, // Height of input area including padding
  INPUT_HEIGHT_PX: '100px',
  
  // Glass scroll safe zones
  GLASS_SAFE_ZONE: 20, // Padding for readable content behind glass
  SCROLL_COMFORT_ZONE: 16, // Extra space for UX
} as const;

// Calculated values for glass scroll system
export const GLASS_SCROLL_TOKENS = {
  // Top padding: Header + safe zone
  PADDING_TOP: LAYOUT_TOKENS.HEADER_HEIGHT + LAYOUT_TOKENS.GLASS_SAFE_ZONE,
  PADDING_TOP_PX: `${LAYOUT_TOKENS.HEADER_HEIGHT + LAYOUT_TOKENS.GLASS_SAFE_ZONE}px`,
  
  // Bottom padding: Input + safe zone  
  PADDING_BOTTOM: LAYOUT_TOKENS.INPUT_HEIGHT + LAYOUT_TOKENS.GLASS_SAFE_ZONE,
  PADDING_BOTTOM_PX: `${LAYOUT_TOKENS.INPUT_HEIGHT + LAYOUT_TOKENS.GLASS_SAFE_ZONE}px`,
  
  // Available height calculations
  AVAILABLE_HEIGHT: `calc(100vh - ${LAYOUT_TOKENS.HEADER_HEIGHT_PX})`,
  CONTENT_HEIGHT: `calc(100vh - ${LAYOUT_TOKENS.HEADER_HEIGHT_PX} - ${LAYOUT_TOKENS.INPUT_HEIGHT_PX})`,
} as const;

// CSS custom properties for runtime theming
export const CSS_VARIABLES = {
  // Layout dimensions
  '--header-height': LAYOUT_TOKENS.HEADER_HEIGHT_PX,
  '--input-height': LAYOUT_TOKENS.INPUT_HEIGHT_PX,
  '--sidebar-collapsed': LAYOUT_TOKENS.SIDEBAR_COLLAPSED_PX,
  '--sidebar-expanded': LAYOUT_TOKENS.SIDEBAR_EXPANDED_PX,
  
  // Glass scroll variables
  '--glass-safe-zone': `${LAYOUT_TOKENS.GLASS_SAFE_ZONE}px`,
  '--glass-padding-top': GLASS_SCROLL_TOKENS.PADDING_TOP_PX,
  '--glass-padding-bottom': GLASS_SCROLL_TOKENS.PADDING_BOTTOM_PX,
  
  // Calculated heights
  '--available-height': GLASS_SCROLL_TOKENS.AVAILABLE_HEIGHT,
  '--content-height': GLASS_SCROLL_TOKENS.CONTENT_HEIGHT,
} as const;

/**
 * Set CSS variables on document root
 * Call this when layout system initializes
 */
export function setCSSVariables(): void {
  if (typeof document === 'undefined') return;
  
  const root = document.documentElement;
  
  Object.entries(CSS_VARIABLES).forEach(([property, value]) => {
    root.style.setProperty(property, value);
  });
}

/**
 * Get current sidebar width based on state
 */
export function getSidebarWidth(isExpanded: boolean): number {
  return isExpanded ? LAYOUT_TOKENS.SIDEBAR_EXPANDED : LAYOUT_TOKENS.SIDEBAR_COLLAPSED;
}

/**
 * Get current sidebar width as CSS value
 */
export function getSidebarWidthPx(isExpanded: boolean): string {
  return isExpanded ? LAYOUT_TOKENS.SIDEBAR_EXPANDED_PX : LAYOUT_TOKENS.SIDEBAR_COLLAPSED_PX;
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
export type GlassScrollToken = keyof typeof GLASS_SCROLL_TOKENS;
export type CSSVariable = keyof typeof CSS_VARIABLES;
