/**
 * Toast Notification Hook
 * Production-grade toast notification system with auto-dismiss
 */

import { useState, useEffect, useCallback } from 'react';

export interface ToastState {
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}

export interface UseToastReturn {
  toast: ToastState | null;
  showToast: (type: ToastState['type'], message: string) => void;
  hideToast: () => void;
  isVisible: boolean;
}

/**
 * Hook for managing toast notifications with auto-dismiss functionality
 * @param autoHideDuration Duration in milliseconds before auto-hiding (default: 5000ms)
 */
export const useToast = (autoHideDuration: number = 5000): UseToastReturn => {
  const [toast, setToast] = useState<ToastState | null>(null);

  // Auto-hide toast after specified duration
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => {
        setToast(null);
      }, autoHideDuration);

      return () => clearTimeout(timer);
    }
  }, [toast, autoHideDuration]);

  const showToast = useCallback((type: ToastState['type'], message: string) => {
    setToast({ type, message });
  }, []);

  const hideToast = useCallback(() => {
    setToast(null);
  }, []);

  return {
    toast,
    showToast,
    hideToast,
    isVisible: toast !== null,
  };
};
