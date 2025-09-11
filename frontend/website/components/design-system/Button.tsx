"use client";

import React from "react";
import clsx from "clsx";

type Variant = "primary" | "secondary" | "ghost" | "copy" | "danger";
type Size = "sm" | "md" | "lg" | "xl";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

/**
 * Production-Grade Button Component
 * 
 * Matches header aesthetic with glass morphism effects
 * No excessive hover transforms - professional UX only
 * Used consistently across the entire application
 */
export const Button: React.FC<ButtonProps> = ({
  className,
  variant = "primary",
  size = "md",
  loading = false,
  leftIcon,
  rightIcon,
  children,
  disabled,
  ...props
}) => {
  const base = clsx(
    "inline-flex items-center justify-center font-semibold tracking-wide",
    "rounded-xl transition-all duration-300 ease-out",
    "focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50 focus-visible:ring-offset-2 focus-visible:ring-offset-black",
    "disabled:opacity-40 disabled:cursor-not-allowed",
    "cursor-pointer"
  );

  const variants: Record<Variant, string> = {
    primary: clsx(
      // Glass morphism primary - beautiful blue without glow
      "bg-blue-600/80 backdrop-blur-xl backdrop-saturate-150",
      "border border-blue-500/30 text-white",
      "shadow-lg shadow-black/25",
      "hover:bg-blue-500/80 hover:border-blue-400/40",
      "hover:shadow-xl hover:shadow-black/30",
      "font-semibold"
    ),
    secondary: clsx(
      // Glass morphism secondary - gray tones with glass effect
      "bg-white/10 backdrop-blur-xl backdrop-saturate-150",
      "border border-white/20 text-white/90",
      "shadow-lg shadow-black/25",
      "hover:bg-white/15 hover:border-white/30 hover:text-white",
      "font-medium"
    ),
    ghost: clsx(
      "bg-transparent text-gray-300",
      "hover:bg-white/[0.06] hover:text-white",
      "border border-transparent hover:border-white/10"
    ),
    copy: clsx(
      // Glass morphism copy button - visible with professional styling
      "bg-white/12 backdrop-blur-xl backdrop-saturate-150",
      "border border-white/30 text-white/85",
      "shadow-md shadow-black/20",
      "hover:bg-white/18 hover:border-white/40 hover:text-white",
      "hover:shadow-lg hover:shadow-black/25",
      "font-medium"
    ),
    danger: clsx(
      "bg-red-600/80 backdrop-blur-xl backdrop-saturate-150",
      "border border-red-500/30 text-white",
      "shadow-lg shadow-black/25",
      "hover:bg-red-500/80 hover:border-red-400/40",
      "hover:shadow-xl hover:shadow-black/30"
    ),
  };

  const sizes: Record<Size, string> = {
    sm: "text-xs px-3 py-2 gap-1.5 rounded-lg",           // Small buttons
    md: "text-sm px-6 py-2.5 gap-2 rounded-xl",          // Header size - matches current
    lg: "text-base px-8 py-3 gap-2.5 rounded-xl",        // Welcome page size
    xl: "text-lg px-10 py-4 gap-3 rounded-2xl",          // Extra large for special cases
  };

  return (
    <button
      className={clsx(base, variants[variant], sizes[size], className)}
      disabled={disabled || loading}
      {...props}
    >
      {leftIcon && (
        <span className={clsx("inline-flex shrink-0", loading && "opacity-70")}>
          {leftIcon}
        </span>
      )}
      <span className={clsx("inline-flex items-center", loading && "opacity-70")}>
        {children}
      </span>
      {rightIcon && (
        <span className={clsx("inline-flex shrink-0", loading && "opacity-70")}>
          {rightIcon}
        </span>
      )}
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        </div>
      )}
    </button>
  );
};
