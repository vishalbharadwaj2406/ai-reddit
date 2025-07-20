/**
 * Design System Constants
 * Based on Royal Ink Glass theme
 */

export const colors = {
  // Primary Palette
  black: '#000000',
  royalBlue: '#1E3A8A',
  brilliantBlue: '#3B82F6',
  lightBlue: '#60A5FA',
  iceWhite: '#E6F3FF',

  // Functional Colors
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',

  // Surfaces
  background: '#000000',
  glassLevel1: 'rgba(255, 255, 255, 0.03)',
  glassLevel2: 'rgba(255, 255, 255, 0.05)',
  glassElevated: 'rgba(30, 58, 138, 0.15)',
  border: 'rgba(59, 130, 246, 0.2)',
} as const;

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  '2xl': '48px',
  '3xl': '64px',
} as const;

export const typography = {
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "SF Pro Display", Roboto, sans-serif',
  sizes: {
    display: { size: '48px', lineHeight: '56px' },
    headingLg: { size: '28px', lineHeight: '36px' },
    headingMd: { size: '24px', lineHeight: '32px' },
    bodyLg: { size: '17px', lineHeight: '26px' },
    body: { size: '16px', lineHeight: '24px' },
    caption: { size: '14px', lineHeight: '20px' },
  },
  weights: {
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    heavy: 800,
  },
} as const;

export const glassMorphism = {
  standard: {
    background: 'rgba(255, 255, 255, 0.03)',
    backdropFilter: 'blur(32px) saturate(180%)',
    border: '2px solid rgba(59, 130, 246, 0.2)',
    borderRadius: '24px',
  },
  elevated: {
    background: 'linear-gradient(135deg, rgba(30, 58, 138, 0.15), rgba(59, 130, 246, 0.08))',
    backdropFilter: 'blur(40px) saturate(200%)',
    border: '2px solid rgba(59, 130, 246, 0.35)',
    borderRadius: '24px',
  },
} as const;

export const animations = {
  timing: {
    quick: '200ms',
    standard: '300ms',
    slow: '600ms',
    ultraSlow: '25s',
  },
  easing: {
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
    custom: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },
} as const;
