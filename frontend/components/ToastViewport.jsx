"use client";

import { useEffect, useState } from "react";
import { subscribeToToasts } from "@/lib/toast";

const TYPE_STYLES = {
  success:
    "border-emerald-400/60 bg-emerald-500/10 text-emerald-100 dark:text-emerald-200",
  error: "border-rose-400/60 bg-rose-500/10 text-rose-100 dark:text-rose-200",
  info: "border-white/20 bg-black/50 text-white/90",
};

export default function ToastViewport() {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const unsubscribe = subscribeToToasts((payload) => {
      setToasts((prev) => {
        const next = [
          ...prev.filter((item) => item.id !== payload.id),
          payload,
        ];
        return next;
      });

      if (payload.duration > 0) {
        setTimeout(
          () =>
            setToasts((prev) => prev.filter((item) => item.id !== payload.id)),
          payload.duration
        );
      }
    });

    return unsubscribe;
  }, []);

  if (!toasts.length) {
    return null;
  }

  return (
    <div className="pointer-events-none fixed bottom-6 right-6 z-50 flex w-80 flex-col gap-3">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`pointer-events-auto rounded-2xl border px-4 py-3 text-sm shadow-2xl backdrop-blur transition ${
            TYPE_STYLES[toast.type] ?? TYPE_STYLES.info
          }`}
        >
          {toast.title && (
            <p className="mb-1 text-xs font-semibold uppercase tracking-[0.2em] text-white/60">
              {toast.title}
            </p>
          )}
          <p className="leading-relaxed">{toast.message}</p>
        </div>
      ))}
    </div>
  );
}
