"use client";

import clsx from 'clsx';

export function Badge({ variant = 'default', className = '', children }: { variant?: 'default' | 'muted' | 'blue' | 'danger'; className?: string; children: React.ReactNode }) {
  const styles = {
    default: 'border-white/10 text-gray-200 bg-white/5',
    muted: 'border-white/10 text-gray-400 bg-white/5',
    blue: 'border-blue-700/40 text-blue-300 bg-blue-900/20',
    danger: 'border-red-700/40 text-red-300 bg-red-900/20',
  } as const;
  return (
    <span className={clsx('px-2 py-0.5 rounded-full text-2xs border', styles[variant], className)}>
      {children}
    </span>
  );
}
