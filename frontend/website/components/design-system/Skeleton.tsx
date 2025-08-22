"use client";

import clsx from 'clsx';

export function Skeleton({ className }: { className?: string }) {
  return (
    <div 
      className={clsx(
        "animate-pulse rounded-md bg-gradient-to-r from-white/5 via-white/8 to-white/5 bg-[length:200%_100%]",
        "animate-shimmer",
        className
      )} 
    />
  );
}

export function SkeletonCardRow() {
  return (
    <div className="rounded-xl border border-white/5 bg-white/5 backdrop-blur-md p-4 md:p-5 space-y-3">
      <div className="flex items-center justify-between">
        <div className="space-y-2 flex-1">
          <Skeleton className="h-5 w-48" />
          <Skeleton className="h-3 w-72" />
        </div>
        <Skeleton className="h-6 w-16 rounded-full" />
      </div>
      <div className="flex items-center gap-4">
        <Skeleton className="h-3 w-20" />
        <Skeleton className="h-3 w-24" />
      </div>
    </div>
  );
}

export function ConversationListSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <SkeletonCardRow key={i} />
      ))}
    </div>
  );
}
