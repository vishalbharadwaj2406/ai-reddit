"use client";

import clsx from 'clsx';
import React from 'react';

export function Card({ className, children, role, ...rest }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      role={role}
      {...rest}
      className={clsx(
        // Exact glass styling from website-sample.html
        "glass-card",
        className
      )}
    >
      {children}
    </div>
  );
}

export function CardRow({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <div className={clsx(
      "flex items-center justify-between gap-4 p-5 md:p-6",
      "transition-colors duration-200",
      className
    )}>
      {children}
    </div>
  );
}
