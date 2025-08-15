"use client";

import React, { useState, useRef, useEffect } from 'react';
import clsx from 'clsx';
import { ChevronDown, Check } from 'lucide-react';
import { usePortalDropdown } from './hooks/usePortalDropdown';
import { Portal } from './Portal';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps {
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  'aria-label'?: string;
}

export const Select: React.FC<SelectProps> = ({
  value,
  onChange,
  options,
  placeholder = "Select option...",
  disabled = false,
  className,
  'aria-label': ariaLabel,
}) => {
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [isMounted, setIsMounted] = useState(false);
  const optionsRef = useRef<HTMLDivElement>(null);
  
  const { 
    isOpen, 
    toggle, 
    close, 
    triggerRef, 
    dropdownRef, 
    position,
    usePortal 
  } = usePortalDropdown<HTMLDivElement>({
    closeOnClickOutside: true,
    closeOnEscape: true,
    usePortal: true // Always use portal for Select components
  });

  // Ensure component is mounted before showing dropdown
  useEffect(() => {
    setIsMounted(true);
  }, []);

  const selectedOption = options.find(option => option.value === value);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!isOpen) return;

      switch (event.key) {
        case 'Escape':
          close();
          setHighlightedIndex(-1);
          event.preventDefault();
          break;
        case 'ArrowDown':
          setHighlightedIndex(prev => 
            prev < options.length - 1 ? prev + 1 : 0
          );
          event.preventDefault();
          break;
        case 'ArrowUp':
          setHighlightedIndex(prev => 
            prev > 0 ? prev - 1 : options.length - 1
          );
          event.preventDefault();
          break;
        case 'Enter':
          if (highlightedIndex >= 0) {
            const option = options[highlightedIndex];
            if (!option.disabled) {
              onChange(option.value);
              close();
              setHighlightedIndex(-1);
            }
          }
          event.preventDefault();
          break;
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, highlightedIndex, options, onChange, close]);

  // Auto-scroll highlighted option into view
  useEffect(() => {
    if (isOpen && highlightedIndex >= 0 && optionsRef.current) {
      const highlightedElement = optionsRef.current.children[highlightedIndex] as HTMLElement;
      if (highlightedElement) {
        highlightedElement.scrollIntoView({
          block: 'nearest',
          behavior: 'smooth'
        });
      }
    }
  }, [highlightedIndex, isOpen]);

  const handleToggle = () => {
    if (!disabled) {
      toggle();
      setHighlightedIndex(-1);
    }
  };

  const handleOptionClick = (option: SelectOption) => {
    if (!option.disabled) {
      onChange(option.value);
      close();
      setHighlightedIndex(-1);
    }
  };

  return (
    <div 
      ref={triggerRef}
      className={clsx(
        "relative", // Essential for dropdown positioning
        className
      )}
      aria-label={ariaLabel}
    >
      {/* Trigger Button */}
      <button
        type="button"
        onClick={handleToggle}
        disabled={disabled}
        className={clsx(
          // Clean glass input styling  
          "glass-input relative w-full px-4 py-3 text-left text-sm font-medium text-white",
          "transition-all duration-200 ease-out",
          // Interactive states
          !disabled && [
            "hover:border-white/15",
            "focus:outline-none"
          ],
          disabled && "opacity-50 cursor-not-allowed"
        )}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <span className={clsx(
          "block truncate pr-8",
          !selectedOption && "text-gray-400"
        )}>
          {selectedOption?.label || placeholder}
        </span>
        <span className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
          <ChevronDown 
            className={clsx(
              "h-4 w-4 text-gray-300 transition-transform duration-200",
              isOpen && "rotate-180"
            )}
            aria-hidden="true"
          />
        </span>
      </button>

      {/* Dropdown Options - Portal-based for stacking context escape */}
      {isMounted && (
        <Portal isActive={usePortal && isOpen}>
          {isOpen && (
            <div 
              ref={dropdownRef}
              className="glass-dropdown"
              style={{
                position: usePortal ? 'fixed' : 'absolute',
                top: usePortal ? position.top : '100%',
                left: usePortal ? position.left : 0,
                right: usePortal ? position.right : undefined,
                bottom: usePortal ? position.bottom : undefined,
                marginTop: usePortal ? 0 : '8px',
                minWidth: usePortal ? position.minWidth : '100%',
                maxWidth: usePortal ? position.maxWidth : '320px',
                width: usePortal ? undefined : 'max-content',
                zIndex: 'var(--z-dropdown)'
              }}
            >
              <div 
                ref={optionsRef}
                className="max-h-60 overflow-auto py-2"
                role="listbox"
              >
                {options.map((option, index) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => handleOptionClick(option)}
                    disabled={option.disabled}
                    className={clsx(
                      "glass-dropdown-item relative w-full px-4 py-3 text-left text-sm font-medium",
                      "focus:outline-none",
                      // Selection state
                      option.value === value ? [
                        "bg-white/[0.08] text-white border-l-2 border-white/30"
                      ] : "text-gray-300",
                      // Highlighted state (keyboard navigation)
                      index === highlightedIndex && option.value !== value && [
                        "bg-white/[0.06] text-white"
                      ],
                      // Hover state for mouse users
                      !option.disabled && option.value !== value && index !== highlightedIndex && [
                        "hover:bg-gradient-to-r hover:from-white/[0.06] hover:to-white/[0.03]",
                        "hover:text-white"
                      ],
                      // Disabled state
                      option.disabled && [
                        "opacity-50 cursor-not-allowed"
                      ]
                    )}
                    role="option"
                    aria-selected={option.value === value}
                  >
                    <div className="flex items-center">
                      <span className="flex-1">{option.label}</span>
                      {option.value === value && (
                        <Check className="h-4 w-4 text-white/80" aria-hidden="true" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </Portal>
      )}
    </div>
  );
};

export interface NativeSelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  helperText?: string;
}

// A styled native <select> that matches the glass theme and avoids OS-default look
export function NativeSelect({ label, helperText, className, children, ...props }: NativeSelectProps) {
  return (
    <label className="inline-flex flex-col gap-1 text-sm text-gray-300">
      {label && <span className="sr-only">{label}</span>}
      <div className="relative">
        <select
          {...props}
          className={clsx(
            "appearance-none rounded-xl border border-white/10",
            "bg-gradient-to-r from-white/[0.08] to-white/[0.04]",
            "backdrop-blur-lg px-4 py-3 text-sm font-medium text-white pr-10",
            "focus:outline-none focus:border-blue-400/50",
            "shadow-[0_4px_16px_rgba(0,0,0,0.25),inset_0_1px_0_rgba(255,255,255,0.1)]",
            className
          )}
        >
          {children}
        </select>
        <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
          <ChevronDown className="h-4 w-4 text-gray-400" />
        </div>
      </div>
      {helperText && <p className="text-xs text-gray-400 px-2">{helperText}</p>}
    </label>
  );
}
