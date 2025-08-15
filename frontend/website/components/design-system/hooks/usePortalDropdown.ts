"use client";

import { useCallback, useEffect, useRef, useState } from 'react';

interface UseDropdownOptions {
  /**
   * Whether to use portal rendering to escape stacking contexts.
   * Recommended for dropdowns that may appear behind other elements.
   */
  usePortal?: boolean;
  /**
   * Whether the dropdown should close when clicking outside.
   */
  closeOnClickOutside?: boolean;
  /**
   * Whether the dropdown should close when pressing Escape.
   */
  closeOnEscape?: boolean;
  /**
   * Callback fired when the dropdown state changes.
   */
  onOpenChange?: (isOpen: boolean) => void;
}

interface DropdownPosition {
  top?: number;
  left?: number;
  right?: number;
  bottom?: number;
  width?: number;
  minWidth?: number;
  maxWidth?: number;
}

/**
 * Production-grade dropdown hook that handles positioning, portal rendering,
 * and accessibility for dropdown components.
 * 
 * Features:
 * - Portal rendering to escape stacking contexts
 * - Automatic positioning relative to trigger element
 * - Click outside and escape key handling
 * - Accessibility compliance
 * - TypeScript support with generics
 */
export function usePortalDropdown<T extends HTMLElement = HTMLDivElement>(
  options: UseDropdownOptions = {}
) {
  const {
    usePortal = true,
    closeOnClickOutside = true,
    closeOnEscape = true,
    onOpenChange
  } = options;

  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState<DropdownPosition>({});
  
  const triggerRef = useRef<T>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Calculate dropdown position relative to trigger
  const calculatePosition = useCallback(() => {
    if (!triggerRef.current || !usePortal) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;

    // Determine if dropdown should appear above or below trigger
    const spaceBelow = viewportHeight - triggerRect.bottom;
    const spaceAbove = triggerRect.top;
    const shouldRenderAbove = spaceBelow < 200 && spaceAbove > spaceBelow;

    // Calculate horizontal position - prefer right alignment for action menus
    const dropdownWidth = 192; // Default dropdown width
    const shouldAlignRight = triggerRect.right > viewportWidth / 2 || 
                            (triggerRect.right + dropdownWidth) > viewportWidth;

    const newPosition: DropdownPosition = {
      minWidth: Math.max(triggerRect.width, 192), // Ensure minimum width for action menus
      maxWidth: Math.min(400, viewportWidth - 32), // 16px margin on each side
    };

    if (shouldRenderAbove) {
      newPosition.bottom = viewportHeight - triggerRect.top + 8;
    } else {
      newPosition.top = triggerRect.bottom + 8;
    }

    if (shouldAlignRight) {
      newPosition.right = viewportWidth - triggerRect.right;
    } else {
      newPosition.left = triggerRect.left;
    }

    setPosition(newPosition);
  }, [usePortal]);

  // Handle dropdown open/close
  const toggle = useCallback(() => {
    const newIsOpen = !isOpen;
    setIsOpen(newIsOpen);
    onOpenChange?.(newIsOpen);
    
    if (newIsOpen && usePortal) {
      // Calculate position when opening
      calculatePosition();
    }
  }, [isOpen, onOpenChange, usePortal, calculatePosition]);

  const open = useCallback(() => {
    if (!isOpen) {
      setIsOpen(true);
      onOpenChange?.(true);
      
      if (usePortal) {
        calculatePosition();
      }
    }
  }, [isOpen, onOpenChange, usePortal, calculatePosition]);

  const close = useCallback(() => {
    if (isOpen) {
      setIsOpen(false);
      onOpenChange?.(false);
    }
  }, [isOpen, onOpenChange]);

  // Handle click outside
  useEffect(() => {
    if (!isOpen || !closeOnClickOutside) return;

    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      
      // Check if click is outside both trigger and dropdown
      const isOutsideTrigger = triggerRef.current && !triggerRef.current.contains(target);
      const isOutsideDropdown = dropdownRef.current && !dropdownRef.current.contains(target);
      
      if (isOutsideTrigger && isOutsideDropdown) {
        close();
      }
    };

    // Use capture phase to ensure we catch the event before other handlers
    document.addEventListener('mousedown', handleClickOutside, true);
    return () => document.removeEventListener('mousedown', handleClickOutside, true);
  }, [isOpen, closeOnClickOutside, close]);

  // Handle escape key
  useEffect(() => {
    if (!isOpen || !closeOnEscape) return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        close();
        // Return focus to trigger element
        triggerRef.current?.focus();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, closeOnEscape, close]);

  // Recalculate position on scroll/resize when using portal
  useEffect(() => {
    if (!isOpen || !usePortal) return;

    const handlePositionUpdate = () => {
      calculatePosition();
    };

    window.addEventListener('scroll', handlePositionUpdate, true);
    window.addEventListener('resize', handlePositionUpdate);
    
    return () => {
      window.removeEventListener('scroll', handlePositionUpdate, true);
      window.removeEventListener('resize', handlePositionUpdate);
    };
  }, [isOpen, usePortal, calculatePosition]);

  return {
    // State
    isOpen,
    position,
    
    // Actions
    toggle,
    open,
    close,
    
    // Refs
    triggerRef,
    dropdownRef,
    
    // Config
    usePortal,
  };
}
