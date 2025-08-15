"use client";

import { createContext, useCallback, useContext, useMemo, useState } from "react";

export type Toast = {
  id: string;
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  variant?: "success" | "error" | "info" | "warning";
  durationMs?: number;
};

type ToastContextValue = {
  toasts: Toast[];
  show: (t: Omit<Toast, "id">) => string;
  dismiss: (id: string) => void;
};

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const show = useCallback((t: Omit<Toast, "id">) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const toast: Toast = { id, durationMs: 5000, variant: "info", ...t };
    setToasts((prev) => [...prev, toast]);
    if (toast.durationMs && !toast.onAction) {
      setTimeout(() => dismiss(id), toast.durationMs);
    }
    return id;
  }, [dismiss]);

  const value = useMemo(() => ({ toasts, show, dismiss }), [toasts, show, dismiss]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      {/* Portal-less simple toasts container. Can be portaled to body if needed. */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex flex-col gap-3 w-[calc(100vw-2rem)] max-w-md">
        {toasts.map((t) => (
          <div
            key={t.id}
            role="status"
            className={`rounded-xl border backdrop-blur px-4 py-3 shadow-lg transition-all bg-black/70 ${
              t.variant === "success" ? "border-emerald-700/40" :
              t.variant === "error" ? "border-red-700/40" :
              t.variant === "warning" ? "border-amber-700/40" :
              "border-blue-700/40"
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="flex-1">
                {t.title && <div className="text-sm font-medium text-white">{t.title}</div>}
                {t.description && <div className="text-xs text-gray-300 mt-0.5">{t.description}</div>}
              </div>
              {t.onAction && (
                <button
                  className="text-xs px-3 py-1 rounded-md bg-white/10 hover:bg-white/20 text-white"
                  onClick={() => {
                    const fn = t.onAction;
                    dismiss(t.id);
                    fn?.();
                  }}
                >
                  {t.actionLabel ?? "Undo"}
                </button>
              )}
              <button
                aria-label="Dismiss"
                className="text-xs px-2 py-1 rounded-md text-gray-300 hover:text-white"
                onClick={() => dismiss(t.id)}
              >
                ✕
              </button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
