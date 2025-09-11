/**
 * Production-Grade Icon Component
 * Consistent SVG icons for the AI Reddit application
 * All icons are 24x24 with proper accessibility
 */

import React from 'react';
import { clsx } from 'clsx';

export interface IconProps extends React.SVGAttributes<SVGElement> {
  /** Icon name */
  name: IconName;
  /** Icon size */
  size?: 'xs' | 'sm' | 'md' | 'lg';
  /** Custom className */
  className?: string;
}

export type IconName = 
  | 'copy'
  | 'edit'
  | 'close'
  | 'plus'
  | 'send'
  | 'loading'
  | 'check'
  | 'x-mark'
  | 'sparkles'
  | 'document-text'
  | 'arrow-right';

const Icon: React.FC<IconProps> = ({ 
  name, 
  size = 'md', 
  className,
  ...props 
}) => {
  const sizeClasses = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4', 
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  };

  const iconPaths: Record<IconName, React.ReactNode> = {
    copy: (
      <>
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
      </>
    ),
    edit: (
      <>
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
        <path d="m18.5 2.5-3 3L22 12l-5.5-5.5-3 3" />
      </>
    ),
    close: (
      <>
        <path d="m18 6-12 12" />
        <path d="m6 6 12 12" />
      </>
    ),
    plus: (
      <>
        <path d="M5 12h14" />
        <path d="M12 5v14" />
      </>
    ),
    send: (
      <path d="m22 2-7 20-4-9-9-4Z" />
    ),
    loading: (
      <>
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
      </>
    ),
    check: (
      <path d="m9 12 2 2 4-4" />
    ),
    'x-mark': (
      <>
        <path d="m18 6-12 12" />
        <path d="m6 6 12 12" />
      </>
    ),
    sparkles: (
      <>
        <path d="m12 3-1.912 5.813a2 2 0 01-1.275 1.275L3 12l5.813 1.912a2 2 0 011.275 1.275L12 21l1.912-5.813a2 2 0 011.275-1.275L21 12l-5.813-1.912a2 2 0 01-1.275-1.275L12 3Z" />
        <path d="M5 3v4" />
        <path d="M19 17v4" />
        <path d="M3 5h4" />
        <path d="M17 19h4" />
      </>
    ),
    'document-text': (
      <>
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14,2 14,8 20,8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
        <polyline points="10,9 9,9 8,9" />
      </>
    ),
    'arrow-right': (
      <>
        <path d="M5 12h14" />
        <path d="m12 5 7 7-7 7" />
      </>
    )
  };

  return (
    <svg
      className={clsx(
        sizeClasses[size],
        'flex-shrink-0',
        className
      )}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      {iconPaths[name]}
    </svg>
  );
};

export { Icon };
