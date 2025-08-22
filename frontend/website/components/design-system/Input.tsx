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
          <div className="pointer-events-none absolute left-0 z-10 flex items-center justify-center w-12 h-full">
            <span className="text-gray-400 group-focus-within:text-blue-400 transition-colors duration-200">
              {leftIcon}
            </span>
          </div>
        )}
        <input
          ref={ref}
          {...props}
          className={clsx(
            // Professional glass input styling with proper icon spacing
            "w-full px-4 py-3.5 text-sm font-medium text-white placeholder:text-gray-400",
            "bg-white/[0.08] border border-white/[0.12] rounded-lg",
            "backdrop-blur-xl transition-all duration-200 ease-out",
            "focus:outline-none focus:border-blue-400/50 focus:bg-white/[0.12]",
            // Proper icon spacing - no overlap
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
