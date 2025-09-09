/**
 * Main Components Index
 * Centralized exports for commonly used components
 * 
 * This file provides barrel exports for components that need to be imported
 * with the @/components alias pattern.
 */

// Layout Components
export { ConditionalLayout } from './layout/ConditionalLayout';
export { default as AppLayout } from './layout/AppLayout';

// Feature Components (Re-export from features directory)
export * from './features';
