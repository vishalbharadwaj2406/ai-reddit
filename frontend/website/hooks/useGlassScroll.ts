/**
 * Glass Scroll System Hook
 * Production-grade hook for managing glass morphism scroll layouts
 * Handles CSS variables, height calculations, and scroll behavior
 */

'use client';

import { useEffect, useCallback } from 'react';
import { useSidebarStore } from '@/lib/stores/sidebarStore';
import { 
  setCSSVariables, 
  updateSidebarVariable, 
  LAYOUT_TOKENS,
  GLASS_SCROLL_TOKENS,
  CSS_VARIABLES
} from '@/lib/layout/tokens';

interface UseGlassScrollOptions {
  /** Whether to enable the glass scroll system */
  enabled?: boolean;
  /** Custom input height override */
  inputHeight?: number;
}

interface GlassScrollSystem {
  /** CSS classes for scroll container */
  containerClasses: string;
  /** CSS classes for scroll content */
  contentClasses: string;
  /** CSS variables object for inline styles */
  cssVariables: Record<string, string>;
  /** Height for the scroll container */
  containerHeight: string;
  /** Whether the system is initialized */
  isInitialized: boolean;
}

/**
 * Hook to manage glass scroll system
 * 
 * This hook:
 * 1. Sets up CSS variables for layout dimensions
 * 2. Updates sidebar width dynamically
 * 3. Provides classes and styles for glass scroll components
 * 4. Handles responsive behavior
 */
export function useGlassScroll(options: UseGlassScrollOptions = {}): GlassScrollSystem {
  const { enabled = true, inputHeight } = options;
  const { isExpanded } = useSidebarStore();

  // Initialize CSS variables on mount
  useEffect(() => {
    if (!enabled) return;
    
    setCSSVariables();
    
    // Set custom input height if provided
    if (inputHeight && typeof document !== 'undefined') {
      document.documentElement.style.setProperty(
        '--input-height', 
        `${inputHeight}px`
      );
      document.documentElement.style.setProperty(
        '--glass-padding-bottom', 
        `${inputHeight + LAYOUT_TOKENS.GLASS_SAFE_ZONE}px`
      );
    }
  }, [enabled, inputHeight]);

  // Update sidebar variable when sidebar state changes
  useEffect(() => {
    if (!enabled) return;
    
    updateSidebarVariable(isExpanded);
  }, [isExpanded, enabled]);

  // Create CSS variables object for inline styles
  const cssVariables = useCallback((): Record<string, string> => {
    if (!enabled) return {};
    
    const variables: Record<string, string> = { ...CSS_VARIABLES };
    
    // Add dynamic sidebar width
    variables['--sidebar-current'] = isExpanded 
      ? LAYOUT_TOKENS.SIDEBAR_EXPANDED_PX 
      : LAYOUT_TOKENS.SIDEBAR_COLLAPSED_PX;
    
    // Add custom input height if provided
    if (inputHeight) {
      variables['--input-height'] = `${inputHeight}px`;
      variables['--glass-padding-bottom'] = `${inputHeight + LAYOUT_TOKENS.GLASS_SAFE_ZONE}px`;
    }
    
    return variables;
  }, [enabled, isExpanded, inputHeight]);

  return {
    containerClasses: enabled ? 'glass-scroll-container' : '',
    contentClasses: enabled ? 'glass-scroll-content' : '',
    cssVariables: cssVariables(),
    containerHeight: enabled ? GLASS_SCROLL_TOKENS.AVAILABLE_HEIGHT : '100%',
    isInitialized: enabled,
  };
}

/**
 * Hook specifically for page-level glass scroll containers
 * Provides full-height container setup with proper overflow handling
 */
export function usePageGlassScroll(): {
  containerProps: React.HTMLAttributes<HTMLDivElement>;
  contentProps: React.HTMLAttributes<HTMLDivElement>;
} {
  const glassScroll = useGlassScroll({ enabled: true });

  return {
    containerProps: {
      className: 'relative h-full overflow-hidden',
      style: {
        height: '100vh',
        ...glassScroll.cssVariables,
      },
    },
    contentProps: {
      className: glassScroll.containerClasses,
      style: {
        position: 'absolute',
        top: 'var(--header-height)',
        bottom: '0',
        left: 'var(--sidebar-current)',
        right: '0',
        overflowY: 'auto',
        transition: 'left 250ms cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  };
}

/**
 * Hook for panel-level glass scroll (chat, blog panels)
 * Provides scroll setup for individual panels within a layout
 */
export function usePanelGlassScroll(): {
  containerProps: React.HTMLAttributes<HTMLDivElement>;
  contentProps: React.HTMLAttributes<HTMLDivElement>;
} {
  const glassScroll = useGlassScroll({ enabled: true });

  return {
    containerProps: {
      className: 'h-full relative overflow-hidden',
      style: glassScroll.cssVariables,
    },
    contentProps: {
      className: `${glassScroll.contentClasses} h-full overflow-y-auto`,
      style: {
        // Content extends beyond bounds for glass effect
        marginTop: 'calc(-1 * var(--header-height))',
        marginBottom: '0', // No bottom margin for panel content
        paddingTop: 'var(--glass-padding-top)',
        paddingBottom: 'var(--glass-safe-zone)',
      },
    },
  };
}
