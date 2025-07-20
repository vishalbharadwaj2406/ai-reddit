/**
 * Card Component - Simplified
 */

import React from 'react';
import { cn } from '@/lib/utils';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'standard' | 'elevated' | 'ghost';
  padding?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

const cardVariants = {
  standard: 'bg-white/5 backdrop-blur-lg border-2 border-blue-600/20 rounded-2xl shadow-lg',
  elevated: 'bg-white/10 backdrop-blur-xl border-2 border-blue-600/30 rounded-2xl shadow-xl',
  ghost: 'bg-transparent border border-white/20',
};

const cardPadding = {
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

export const Card: React.FC<CardProps> = ({
  variant = 'standard',
  padding = 'md',
  className,
  children,
  ...props
}) => {
  return (
    <div
      className={cn(
        'transition-all duration-300',
        cardVariants[variant],
        cardPadding[padding],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
