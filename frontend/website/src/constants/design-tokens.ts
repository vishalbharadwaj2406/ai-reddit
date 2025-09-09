/**
 * Design System Tokens and Constants
 * Production-grade design system with type safety
 */

// 🎨 Color Palette
export const colors = {
  // Primary Palette
  primary: {
    50: '#eff6ff',
    100: '#dbeafe', 
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
    950: '#172554',
  },
  
  // Neutral Palette
  neutral: {
    0: '#ffffff',
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
    950: '#030712',
  },
  
  // Semantic Colors
  success: {
    50: '#f0fdf4',
    500: '#22c55e',
    600: '#16a34a',
    900: '#14532d',
  },
  
  error: {
    50: '#fef2f2',
    500: '#ef4444',
    600: '#dc2626',
    900: '#7f1d1d',
  },
  
  warning: {
    50: '#fffbeb',
    500: '#f59e0b',
    600: '#d97706',
    900: '#78350f',
  },
  
  // Glass Effects
  glass: {
    light: 'rgba(255, 255, 255, 0.1)',
    medium: 'rgba(255, 255, 255, 0.15)',
    heavy: 'rgba(255, 255, 255, 0.25)',
    border: 'rgba(255, 255, 255, 0.2)',
  }
} as const;

// 📏 Spacing Scale (rem values)
export const spacing = {
  0: '0',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
  16: '4rem',     // 64px
  20: '5rem',     // 80px
  24: '6rem',     // 96px
  32: '8rem',     // 128px
} as const;

// 🔤 Typography Scale
export const typography = {
  fontSize: {
    xs: '0.75rem',      // 12px
    sm: '0.875rem',     // 14px
    base: '1rem',       // 16px
    lg: '1.125rem',     // 18px
    xl: '1.25rem',      // 20px
    '2xl': '1.5rem',    // 24px
    '3xl': '1.875rem',  // 30px
    '4xl': '2.25rem',   // 36px
    '5xl': '3rem',      // 48px
  },
  
  fontWeight: {
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
  
  lineHeight: {
    tight: '1.25',
    normal: '1.5',
    relaxed: '1.75',
  },
} as const;

// 📐 Border Radius
export const borderRadius = {
  none: '0',
  sm: '0.125rem',    // 2px
  base: '0.25rem',   // 4px
  md: '0.375rem',    // 6px
  lg: '0.5rem',      // 8px
  xl: '0.75rem',     // 12px
  '2xl': '1rem',     // 16px
  '3xl': '1.5rem',   // 24px
  full: '9999px',
} as const;

// 🌫️ Shadows
export const shadows = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
  glass: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
} as const;

// 🎭 Animation & Transitions
export const animation = {
  duration: {
    75: '75ms',
    100: '100ms',
    150: '150ms',
    200: '200ms',
    300: '300ms',
    500: '500ms',
    700: '700ms',
    1000: '1000ms',
  },
  
  easing: {
    linear: 'linear',
    in: 'cubic-bezier(0.4, 0, 1, 1)',
    out: 'cubic-bezier(0, 0, 0.2, 1)',
    inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },
} as const;

// 📱 Breakpoints
export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// 🧩 Layout Constants
export const layout = {
  header: {
    height: '64px',
    zIndex: 50,
  },
  
  sidebar: {
    widthCollapsed: '64px',
    widthExpanded: '256px',
    zIndex: 40,
  },
  
  content: {
    maxWidth: '1280px',
    padding: {
      mobile: '16px',
      desktop: '24px',
    },
  },
  
  zIndex: {
    dropdown: 10,
    modal: 50,
    toast: 100,
    tooltip: 200,
  },
} as const;

// 🎯 Component Variants
export const variants = {
  button: {
    primary: 'glass-button-primary',
    secondary: 'glass-button-secondary',
    ghost: 'glass-button-ghost',
    danger: 'glass-button-danger',
  },
  
  card: {
    base: 'glass-card',
    elevated: 'glass-card-elevated',
    interactive: 'glass-card-interactive',
  },
  
  input: {
    base: 'glass-input',
    error: 'glass-input-error',
    success: 'glass-input-success',
  },
} as const;

// 🎨 CSS Variables for Runtime Theming
export const cssVariables = {
  '--color-primary-500': colors.primary[500],
  '--color-primary-600': colors.primary[600],
  '--color-neutral-0': colors.neutral[0],
  '--color-neutral-900': colors.neutral[900],
  '--spacing-4': spacing[4],
  '--spacing-6': spacing[6],
  '--border-radius-lg': borderRadius.lg,
  '--shadow-glass': shadows.glass,
  '--header-height': layout.header.height,
  '--sidebar-width-collapsed': layout.sidebar.widthCollapsed,
  '--sidebar-width-expanded': layout.sidebar.widthExpanded,
} as const;

// Type exports for TypeScript integration
export type Color = keyof typeof colors;
export type Spacing = keyof typeof spacing;
export type FontSize = keyof typeof typography.fontSize;
export type Shadow = keyof typeof shadows;
export type Breakpoint = keyof typeof breakpoints;
