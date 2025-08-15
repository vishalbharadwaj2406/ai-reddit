"use client";

import React from 'react';
import clsx from 'clsx';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, leftIcon, rightIcon, ...props }, ref) => {
    return (
      <div className={clsx("relative flex items-center group", className)}>
        {leftIcon && (
          <div className="pointer-events-none absolute left-4 z-10 flex items-center justify-center">
            <span className="text-gray-400 group-focus-within:text-white transition-colors duration-200">
              {leftIcon}
            </span>
          </div>
        )}
        <input
          ref={ref}
          {...props}
          className={clsx(
            // Clean glass input styling
            "glass-input w-full px-4 py-3.5 text-sm font-medium text-white placeholder:text-gray-400",
            "transition-all duration-200 ease-out",
            "focus:outline-none",
            // Icon spacing
            leftIcon && "pl-12",
            rightIcon && "pr-12",
          )}
        />
        {rightIcon && (
          <button
            type="button"
            tabIndex={-1}
            className={clsx(
              "absolute right-3 z-10 inline-flex h-8 w-8 items-center justify-center",
              "rounded-lg text-gray-400 transition-all duration-200",
              "hover:text-blue-400 hover:bg-white/10 active:scale-95"
            )}
          >
            {rightIcon}
          </button>
        )}
      </div>
    );
  }
);
Input.displayName = 'Input';
