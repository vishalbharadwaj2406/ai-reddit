/**
 * UnifiedToast Component
 * Production-grade toast notification system with proper positioning
 */

'use client';

import { useToast, ToastState } from '@/hooks/conversation/useToast';

interface UnifiedToastProps {
  toast?: ToastState | null;
  onDismiss?: () => void;
}

export const UnifiedToast: React.FC<UnifiedToastProps> = ({
  toast: externalToast,
  onDismiss,
}) => {
  const { toast: internalToast, hideToast } = useToast();
  
  // Use external toast if provided, otherwise use internal toast
  const activeToast = externalToast !== undefined ? externalToast : internalToast;
  const handleDismiss = onDismiss || hideToast;

  if (!activeToast) return null;

  return (
    <div className="fixed top-4 right-4 z-50">
      <div 
        className={`px-4 py-3 rounded-lg shadow-lg border max-w-sm transition-all duration-300 ${
          activeToast.type === 'success' 
            ? 'bg-green-900/90 border-green-500/30 text-green-100' 
            : activeToast.type === 'error'
            ? 'bg-red-900/90 border-red-500/30 text-red-100'
            : activeToast.type === 'warning'
            ? 'bg-yellow-900/90 border-yellow-500/30 text-yellow-100'
            : 'bg-blue-900/90 border-blue-500/30 text-blue-100'
        }`}
        style={{ backdropFilter: 'blur(10px)' }}
      >
        <div className="flex items-center justify-between">
          <p className="text-sm">{activeToast.message}</p>
          <button 
            onClick={handleDismiss}
            className="ml-2 text-lg hover:opacity-70 transition-opacity"
            aria-label="Dismiss notification"
          >
            ×
          </button>
        </div>
      </div>
    </div>
  );
};
