"use client";

import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';

interface PortalProps {
  children: React.ReactNode;
  /**
   * The container element to portal to. Defaults to document.body
   */
  container?: Element | null;
  /**
   * Whether the portal should be active. If false, renders children normally.
   */
  isActive?: boolean;
}

/**
 * Production-grade Portal component for rendering content outside the normal DOM tree.
 * 
 * This is essential for dropdowns, modals, and tooltips that need to escape
 * stacking contexts created by backdrop-filter, transform, or overflow properties.
 * 
 * Usage:
 * ```tsx
 * <Portal isActive={isOpen}>
 *   <div className="dropdown">Content that escapes stacking contexts</div>
 * </Portal>
 * ```
 */
export function Portal({ children, container, isActive = true }: PortalProps) {
  const [mounted, setMounted] = useState(false);
  const [portalContainer, setPortalContainer] = useState<Element | null>(null);

  useEffect(() => {
    // Ensure we're on the client side
    setMounted(true);
    
    // Set the portal container (default to document.body)
    const targetContainer = container || (typeof document !== 'undefined' ? document.body : null);
    setPortalContainer(targetContainer);
  }, [container]);

  // Don't render anything on server side or if not mounted
  if (!mounted || !portalContainer) {
    return null;
  }

  // If portal is not active, render children normally
  if (!isActive) {
    return <>{children}</>;
  }

  // Render children into the portal container
  return createPortal(children, portalContainer);
}
