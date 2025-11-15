"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "@/lib/toast";
import api from "@/src/lib/api";
import ConfirmDeleteModal from "@/components/admin/ConfirmDeleteModal";
import { useUserContext } from "@/components/UserProvider";

export default function AdminDeleteProblem({
  problemId,
  problemTitle,
  onDeleted,
}) {
  const router = useRouter();
  const { isAdmin } = useUserContext();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!isAdmin) {
    return null;
  }

  const handleDelete = async () => {
    setLoading(true);
    setError("");
    try {
      await api.delete(`/problems/${problemId}`);
      toast.success("Problem deleted successfully.");
      setOpen(false);
      if (typeof onDeleted === "function") {
        onDeleted(problemId);
      } else {
        router.refresh();
        router.push("/problems/list");
      }
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        "Failed to delete problem.";
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-2 rounded-full border border-rose-500/70 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-rose-200 transition hover:border-rose-400 hover:text-rose-100"
      >
        Delete Problem
      </button>

      {open && (
        <ConfirmDeleteModal
          title={`Delete “${problemTitle ?? "this problem"}”?`}
          description="This action permanently removes the problem, examples, hidden tests, and submissions."
          confirmLabel={loading ? "Deleting…" : "Delete"}
          loading={loading}
          error={error}
          onConfirm={handleDelete}
          onCancel={() => {
            if (!loading) {
              setOpen(false);
              setError("");
            }
          }}
        />
      )}
    </>
  );
}
