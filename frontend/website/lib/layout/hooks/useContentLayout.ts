/**
 * Content Layout Hook
 * Content-only layout for blog, settings, and other pages
 */

'use client';

import { useGlassHeader } from './useGlassHeader';
import { LAYOUT_TOKENS } from '@/lib/layout/tokens';
import { ContentLayoutSystem } from '@/lib/layout/types';

/**
 * Content-only layout (blog, settings, etc.)
 * Header clearance + minimal content padding
 */
export function useContentLayout(): ContentLayoutSystem {
  const base = useGlassHeader();
  
  return {
    ...base,
    
    // Content with header clearance + minimal padding
    contentPadding: {
      paddingTop: `${base.headerClearance.paddingTop}`,
      paddingLeft: `${LAYOUT_TOKENS.CONTENT_PADDING}px`,
      paddingRight: `${LAYOUT_TOKENS.CONTENT_PADDING}px`,
      paddingBottom: `${LAYOUT_TOKENS.CONTENT_PADDING}px`
    }
  };
}