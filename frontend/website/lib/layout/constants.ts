/**
 * Layout System Constants
 * Production-grade constants for glass effects and layout behavior
 */

import { GlassStyles } from './types';

/**
 * Glass effect styling - matches header exactly
 */
export const GLASS_STYLES: GlassStyles = {
  background: 'rgba(0, 0, 0, 0.6)',
  backdropFilter: 'blur(24px) saturate(180%)',
  WebkitBackdropFilter: 'blur(24px) saturate(180%)', 
  borderTop: '1px solid rgba(59, 130, 246, 0.15)',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3), 0 0 40px rgba(30, 58, 138, 0.12)',
};

/**
 * Base CSS classes used across layout system
 */
export const BASE_CLASSES = {
  page: 'h-screen bg-black overflow-hidden',
  content: 'h-full overflow-y-auto',
  panel: 'h-full relative bg-black',
  inputContainer: 'absolute bottom-0 left-0 right-0 z-40',
} as const;