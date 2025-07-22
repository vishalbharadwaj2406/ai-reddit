/**
 * AI Social Design System - Royal Ink Glass
 * Design tokens and utilities for the glass morphism system
 */

/**
 * Design Tokens
 */
export const designTokens = {
  colors: {
    pureBlack: '#000000',
    royalBlue: '#1E3A8A',
    brilliantBlue: '#3B82F6',
    lightBlue: '#60A5FA',
    iceWhite: '#E6F3FF',
  },
  
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    '2xl': '48px',
  },
  
  radius: {
    sm: '8px',
    md: '12px', 
    lg: '16px',
    xl: '20px',
    '2xl': '24px',
  },
  
  shadows: {
    sm: '0 2px 8px rgba(0, 0, 0, 0.1)',
    md: '0 4px 16px rgba(0, 0, 0, 0.2)',
    lg: '0 8px 32px rgba(0, 0, 0, 0.3)',
    xl: '0 20px 60px rgba(0, 0, 0, 0.4)',
  }
} as const

/**
 * CSS Class Names for Design System Components
 */
export const glassClasses = {
  // Base glass effects
  base: 'glass-base',
  card: 'glass-card',
  elevated: 'glass-elevated',
  header: 'glass-header',
  
  // Button system
  buttonPrimary: 'glass-button-primary',
  buttonSecondary: 'glass-button-secondary',
  
  // Text system
  textGradientPrimary: 'text-gradient-primary',
  textGradientLogo: 'text-gradient-logo',
  textAccent: 'text-accent',
  
  // Utilities
  glowBlue: 'glow-blue',
  glowBlueStrong: 'glow-blue-strong',
  focusRing: 'focus-ring',
} as const

// Legacy compatibility
export const glassHeader = () => glassClasses.header
