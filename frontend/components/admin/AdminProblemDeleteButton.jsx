"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/src/lib/api";
import ConfirmDeleteModal from "./ConfirmDeleteModal";

export default function AdminProblemDeleteButton({
  problemId,
  title,
  onDeleted,
}) {
  const router = useRouter();
  const [isModalOpen, setModalOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const handleDelete = async () => {
    setBusy(true);
    setError("");
    try {
      await api.delete(`/problems/${problemId}`);
      setModalOpen(false);
      if (typeof onDeleted === "function") {
        onDeleted(problemId);
      } else {
        router.refresh();
      }
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        "Failed to delete the problem.";
      setError(message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setModalOpen(true)}
        className="inline-flex items-center gap-1 rounded-full border border-rose-500/50 bg-rose-500/10 px-4 py-1.5 text-xs font-semibold text-rose-100 transition hover:border-rose-400 hover:bg-rose-500/20"
      >
        Delete
      </button>

      {isModalOpen && (
        <ConfirmDeleteModal
          title={`Delete “${title}”?`}
          description="This permanently removes the problem, examples, reference solutions, and all associated test cases. This action cannot be undone."
          confirmLabel={busy ? "Deleting…" : "Delete"}
          loading={busy}
          error={error}
          onConfirm={handleDelete}
          onCancel={() => {
            if (!busy) {
              setModalOpen(false);
              setError("");
            }
          }}
        />
      )}
    </>
  );
}
