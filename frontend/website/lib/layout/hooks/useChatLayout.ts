/**
 * Chat Layout Hook  
 * Chat-specific layout with header and input clearances
 */

'use client';

import { useGlassHeader } from './useGlassHeader';
import { LAYOUT_TOKENS, CLEARANCES } from '@/lib/layout/tokens';
import { BASE_CLASSES, GLASS_STYLES } from '@/lib/layout/constants';
import { ChatLayoutSystem } from '@/lib/layout/types';

/**
 * Chat-specific layout with input area
 * Composes header clearance + input positioning
 */
export function useChatLayout(): ChatLayoutSystem {
  const base = useGlassHeader();
  
  return {
    ...base,
    
    // Chat content with both header and input clearances
    contentClearance: {
      paddingTop: `${CLEARANCES.HEADER_WITH_CONTENT}px`,
      paddingBottom: `${CLEARANCES.INPUT_WITH_CONTENT}px`
    },
    
    // Input container with glass styling
    inputContainer: {
      className: BASE_CLASSES.inputContainer,
      style: {
        minHeight: `${LAYOUT_TOKENS.INPUT_MIN_HEIGHT}px`,
        maxHeight: `${LAYOUT_TOKENS.INPUT_MAX_HEIGHT}px`,
        ...GLASS_STYLES,
      }
    }
  };
}