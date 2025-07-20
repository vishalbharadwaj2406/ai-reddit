/**
 * Button Component - Simplified for Royal Header Only
 */

import React from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

const buttonVariants = {
  primary: [
    'bg-gradient-to-r from-blue-900 to-blue-600',
    'text-white font-semibold',
    'shadow-lg shadow-blue-900/30',
    'hover:shadow-xl hover:shadow-blue-900/40',
    'hover:-translate-y-0.5',
    'active:translate-y-0',
    'transition-all duration-300',
  ],
  secondary: [
    'bg-white/10 backdrop-blur-lg',
    'border-2 border-white/30',
    'text-white font-medium',
    'hover:bg-white/15',
    'hover:border-blue-400/40',
    'transition-all duration-300',
  ],
  ghost: [
    'bg-transparent',
    'text-white/80 font-medium',
    'hover:bg-white/10',
    'hover:text-white',
    'transition-all duration-300',
  ],
};

const buttonSizes = {
  sm: 'px-4 py-2 text-sm rounded-xl',
  md: 'px-6 py-3 text-base rounded-2xl',
  lg: 'px-8 py-4 text-lg rounded-2xl',
};

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  className,
  children,
  ...props
}) => {
  return (
    <button
      className={cn(
        'relative overflow-hidden',
        'focus:outline-none focus:ring-2 focus:ring-blue-600/50',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        buttonVariants[variant],
        buttonSizes[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
};
