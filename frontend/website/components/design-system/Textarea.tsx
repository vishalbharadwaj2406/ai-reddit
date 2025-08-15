"use client";

import React, { forwardRef } from "react";
import TextareaAutosize, { TextareaAutosizeProps } from "react-textarea-autosize";
import clsx from "clsx";

export interface DSTextareaProps extends TextareaAutosizeProps {
  label?: string;
  error?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, DSTextareaProps>(
  ({ className, minRows = 1, maxRows = 10, label, error, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block mb-1 text-xs text-gray-300">{label}</label>
        )}
        <TextareaAutosize
          ref={ref}
          minRows={minRows}
          maxRows={maxRows}
          className={clsx(
            "w-full resize-none rounded-lg bg-white/5 border border-white/10 px-4 py-3 text-body text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500",
            error && "border-red-700/50",
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-1 text-xs text-red-400">{error}</p>
        )}
      </div>
    );
  }
);
Textarea.displayName = "Textarea";
