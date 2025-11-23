"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { toast } from "@/lib/toast";
import api from "@/src/lib/api";
import { useUserContext } from "../UserProvider";

function formatTimestamp(value) {
  if (!value) return "";
  try {
    const date = new Date(value);
    return date.toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch (err) {
    return value;
  }
}

export default function ProblemComments({ problemId }) {
  const { user, loading: userLoading } = useUserContext();
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [draft, setDraft] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const canPost = useMemo(() => Boolean(user && draft.trim().length > 0 && !submitting), [draft, submitting, user]);

  const fetchComments = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get(`/problems/${problemId}/comments`);
      setComments(Array.isArray(data) ? data : []);
    } catch (err) {
      const message = err?.response?.data?.detail || "Unable to load comments.";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }, [problemId]);

  useEffect(() => {
    fetchComments();
  }, [fetchComments]);

  const handleSubmit = useCallback(async () => {
    if (!canPost) {
      if (!user && !userLoading) {
        toast.error("Log in to join the discussion.");
      }
      return;
    }

    setSubmitting(true);
    try {
      const payload = { content: draft.trim() };
      const { data } = await api.post(`/problems/${problemId}/comments`, payload);
      setDraft("");
      setComments((prev) => [...prev, data]);
      toast.success("Comment posted.");
    } catch (err) {
      const message = err?.response?.data?.detail || "Failed to post comment.";
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  }, [canPost, draft, problemId, user, userLoading]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-xs uppercase tracking-wide text-slate-400">
        <span>{comments.length} comment{comments.length === 1 ? "" : "s"}</span>
        <button
          type="button"
          onClick={fetchComments}
          className="rounded-full border border-slate-600 px-3 py-1 text-[10px] font-semibold text-slate-300 transition hover:border-emerald-500 hover:text-emerald-200"
          disabled={loading}
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="rounded-lg border border-slate-800 bg-slate-950/40 p-4 text-sm text-slate-400">
          Loading comments...
        </div>
      ) : comments.length === 0 ? (
        <div className="rounded-lg border border-slate-800 bg-slate-950/40 p-4 text-sm text-slate-400">
          No comments yet. Be the first to start the discussion!
        </div>
      ) : (
        <div className="space-y-3">
          {comments.map((comment) => (
            <div
              key={comment.id}
              className="rounded-2xl border border-slate-800/70 bg-slate-950/40 p-4"
            >
              <div className="flex items-center justify-between text-xs text-slate-400">
                {comment.user_id ? (
                  <Link
                    href={`/profile/${comment.user_id}`}
                    className="font-semibold text-emerald-300 transition hover:text-emerald-200"
                  >
                    {comment.username}
                  </Link>
                ) : (
                  <span className="font-semibold text-slate-200">{comment.username}</span>
                )}
                <span>{formatTimestamp(comment.updated_at || comment.created_at)}</span>
              </div>
              <p className="mt-2 text-sm leading-relaxed text-slate-100 whitespace-pre-wrap">
                {comment.content}
              </p>
            </div>
          ))}
        </div>
      )}

      <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          {user ? "Add a comment" : "Sign in to comment"}
        </label>
        <textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder={user ? "Share an idea, ask a question, or discuss approaches." : "You must be logged in to participate."}
          className="mt-2 h-28 w-full rounded-xl border border-slate-800 bg-slate-900/60 p-3 text-sm text-slate-100 placeholder:text-slate-500 focus:border-emerald-400 focus:outline-none"
          disabled={!user || submitting}
        />
        <div className="mt-3 flex justify-end">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!canPost}
            className={`rounded-lg px-4 py-2 text-sm font-semibold transition ${
              canPost
                ? "bg-emerald-500 text-emerald-950 hover:bg-emerald-400"
                : "bg-slate-800 text-slate-500"
            }`}
          >
            {submitting ? "Posting..." : "Post comment"}
          </button>
        </div>
      </div>
    </div>
  );
}
