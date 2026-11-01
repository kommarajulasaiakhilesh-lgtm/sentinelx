"use client";

import {
  createContext,
  useCallback,
  useContext,
  useState,
  type ReactNode,
} from "react";
import { AnimatePresence, motion } from "motion/react";
import { CheckCircle2, Info, TriangleAlert, X, XCircle } from "lucide-react";

type ToastVariant = "success" | "error" | "info" | "warning";

type Toast = {
  id: number;
  title: string;
  description?: string;
  variant: ToastVariant;
};

type ToastInput = Omit<Toast, "id">;

const ToastContext = createContext<{
  toast: (t: ToastInput) => void;
} | null>(null);

const variantStyles: Record<
  ToastVariant,
  { icon: typeof Info; accent: string; ring: string }
> = {
  success: { icon: CheckCircle2, accent: "text-emerald-600", ring: "border-emerald-200" },
  error: { icon: XCircle, accent: "text-red-600", ring: "border-red-200" },
  warning: { icon: TriangleAlert, accent: "text-amber-600", ring: "border-amber-200" },
  info: { icon: Info, accent: "text-indigo-600", ring: "border-indigo-200" },
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const remove = useCallback((id: number) => {
    setToasts((cur) => cur.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback(
    (input: ToastInput) => {
      const id = Date.now() + Math.random();
      setToasts((cur) => [...cur, { ...input, id }]);
      setTimeout(() => remove(id), 4500);
    },
    [remove],
  );

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-[min(92vw,360px)] flex-col gap-2">
        <AnimatePresence initial={false}>
          {toasts.map((t) => {
            const style = variantStyles[t.variant];
            const Icon = style.icon;
            return (
              <motion.div
                key={t.id}
                layout
                initial={{ opacity: 0, x: 40, scale: 0.96 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 40, scale: 0.96 }}
                transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
                className={`pointer-events-auto flex items-start gap-3 rounded-xl border ${style.ring} bg-white p-3.5 shadow-lg shadow-slate-900/10`}
              >
                <Icon className={`mt-0.5 size-5 shrink-0 ${style.accent}`} />
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-medium text-slate-900">
                    {t.title}
                  </div>
                  {t.description && (
                    <div className="mt-0.5 text-xs text-slate-500">
                      {t.description}
                    </div>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => remove(t.id)}
                  className="rounded p-0.5 text-slate-400 transition hover:text-slate-600"
                  aria-label="Dismiss"
                >
                  <X className="size-4" />
                </button>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast must be used within ToastProvider");
  }
  return ctx.toast;
}
