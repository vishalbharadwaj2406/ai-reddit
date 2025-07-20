/**
 * Input Component - Simplified
 */

import React from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: 'default' | 'glass' | 'elevated';
  error?: string;
}

const inputVariants = {
  default: [
    'bg-white/10 backdrop-blur-lg',
    'border-2 border-white/20',
    'text-white placeholder:text-white/50',
    'focus:border-blue-400/60',
    'focus:bg-white/15',
  ],
  glass: [
    'bg-white/5 backdrop-blur-xl',
    'border border-white/20',
    'text-white placeholder:text-white/50',
    'focus:border-blue-400/40',
  ],
  elevated: [
    'bg-white/15 backdrop-blur-2xl',
    'border-2 border-blue-400/35',
    'text-white placeholder:text-white/60',
    'focus:border-blue-400/60',
  ],
};

export const Input: React.FC<InputProps> = ({
  variant = 'default',
  error,
  className,
  ...props
}) => {
  return (
    <div className="relative">
      <input
        className={cn(
          'w-full px-4 py-3 rounded-2xl',
          'outline-none transition-all duration-300',
          'font-medium text-base',
          inputVariants[variant],
          error && 'border-red-500/60 focus:border-red-500',
          className
        )}
        {...props}
      />
      {error && (
        <p className="mt-2 text-sm text-red-400 font-medium">{error}</p>
      )}
    </div>
  );
};
