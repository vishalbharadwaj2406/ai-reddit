"use client";

import clsx from 'clsx';

export function Skeleton({ className }: { className?: string }) {
  return (
    <div className={clsx("animate-pulse rounded-md bg-white/5", className)} />
  );
}

export function SkeletonCardRow() {
  return (
    <div className="rounded-xl border border-white/5 bg-white/5 backdrop-blur-md p-4 md:p-5 space-y-3">
      <Skeleton className="h-4 w-40" />
      <Skeleton className="h-3 w-72" />
    </div>
  );
}
