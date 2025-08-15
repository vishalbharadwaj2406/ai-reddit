import { useState, useRef, useEffect } from 'react';

interface UseDropdownOptions {
  closeOnEscape?: boolean;
  closeOnClickOutside?: boolean;
}

export function useDropdown<T extends HTMLElement = HTMLElement>(options: UseDropdownOptions = {}) {
  const {
    closeOnEscape = true,
    closeOnClickOutside = true,
  } = options;

  const [isOpen, setIsOpen] = useState(false);
  const triggerRef = useRef<T>(null);
  const dropdownRef = useRef<T>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    if (!isOpen || !closeOnClickOutside) return;

    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Node;
      const isInsideTrigger = triggerRef.current?.contains(target);
      const isInsideDropdown = dropdownRef.current?.contains(target);
      
      if (!isInsideTrigger && !isInsideDropdown) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, closeOnClickOutside]);

  // Close dropdown on Escape key
  useEffect(() => {
    if (!isOpen || !closeOnEscape) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, closeOnEscape]);

  const toggle = () => setIsOpen(prev => !prev);
  const open = () => setIsOpen(true);
  const close = () => setIsOpen(false);

  return {
    isOpen,
    setIsOpen,
    toggle,
    open,
    close,
    triggerRef,
    dropdownRef,
  };
}
