"use client";

export default function ConfirmDeleteModal({
  title,
  description,
  confirmLabel,
  cancelLabel = "Cancel",
  loading = false,
  error = "",
  onConfirm,
  onCancel,
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-900">
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
            {title}
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            {description}
          </p>
          {error && (
            <div className="rounded-lg border border-rose-400 bg-rose-50 px-3 py-2 text-sm text-rose-600 dark:border-rose-500 dark:bg-rose-500/10 dark:text-rose-200">
              {error}
            </div>
          )}
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={loading}
            className="inline-flex items-center rounded-md bg-rose-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-700 disabled:opacity-60"
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
