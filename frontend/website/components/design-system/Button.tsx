"use client";

import React from "react";
import clsx from "clsx";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md" | "lg" | "xl";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

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
    !disabled && !loading && "hover:shadow-lg"
  );

  const variants: Record<Variant, string> = {
    primary: clsx(
      // Clean glass primary button - no strong blue tint
      "bg-gradient-to-br from-white/10 via-white/5 to-white/10",
      "border border-white/20 text-white",
      "backdrop-filter backdrop-blur-xl backdrop-saturate-150",
      "shadow-[0_4px_16px_rgba(0,0,0,0.3),inset_0_1px_0_rgba(255,255,255,0.1)]",
      "hover:from-white/15 hover:via-white/8 hover:to-white/15",
      "hover:border-white/30 hover:shadow-[0_8px_32px_rgba(0,0,0,0.4)]"
    ),
    secondary: clsx(
      // Glass secondary with minimal styling
      "bg-gradient-to-br from-white/[0.08] to-white/[0.04]",
      "border border-white/15 text-gray-200",
      "backdrop-blur-lg backdrop-saturate-150",
      "shadow-[0_4px_16px_rgba(0,0,0,0.2),inset_0_1px_0_rgba(255,255,255,0.05)]",
      "hover:from-white/[0.12] hover:to-white/[0.06]",
      "hover:border-white/20 hover:text-white"
    ),
    ghost: clsx(
      "bg-transparent text-gray-300",
      "hover:bg-gradient-to-r hover:from-white/[0.06] hover:to-white/[0.03]",
      "hover:text-white hover:backdrop-blur-lg",
      "border border-transparent hover:border-white/10"
    ),
    danger: clsx(
      "bg-gradient-to-br from-red-600/80 via-red-700/80 to-red-800/80",
      "border border-red-500/30 text-white",
      "backdrop-blur-sm",
      "shadow-[0_4px_16px_rgba(220,38,38,0.25),inset_0_1px_0_rgba(255,255,255,0.1)]",
      "hover:from-red-500/90 hover:via-red-600/90 hover:to-red-700/90",
      "hover:border-red-400/40"
    ),
  };

  const sizes: Record<Size, string> = {
    sm: "text-xs px-3 py-2 gap-1.5",
    md: "text-sm px-4 py-2.5 gap-2",
    lg: "text-base px-6 py-3 gap-2.5",
    xl: "text-lg px-8 py-4 gap-3",
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
