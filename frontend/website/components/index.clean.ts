/**
 * Production-Grade Layout System
 * Clean, direct exports without circular dependencies
 */

// Core layout components - direct exports only
export { ConditionalLayout } from './layout/ConditionalLayout';
export { default as AppLayout } from './layout/AppLayout';

// Header component
export { default as Header } from './Header/Header';

// Provider components
export { default as SessionWrapper } from './providers/SessionWrapper';
export { ToastProvider } from './feedback/ToastProvider';

// Error handling
export { default as ErrorBoundary } from './error/ErrorBoundary';

// Note: Feature components are imported directly from their specific paths
// to avoid complex barrel export chains that can cause circular dependencies
