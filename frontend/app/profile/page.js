"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import api from "@/src/lib/api";
import { useUserContext } from "@/components/UserProvider";
import ProfileLayout from "@/components/profile/ProfileLayout";

export default function ProfilePage() {
  const { user, loading: userLoading, refresh } = useUserContext();
  const [solvedProblems, setSolvedProblems] = useState([]);
  const [solvedLoading, setSolvedLoading] = useState(false);
  const [solvedError, setSolvedError] = useState(null);

  const loadSolved = useCallback(async () => {
    if (!user) {
      setSolvedProblems([]);
      setSolvedError(null);
      return;
    }

    setSolvedLoading(true);
    setSolvedError(null);

    try {
      const { data } = await api.get("/users/me/solved");
      setSolvedProblems(Array.isArray(data) ? data : []);
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        "Unable to load solved problems.";
      setSolvedProblems([]);
      setSolvedError(detail);
    } finally {
      setSolvedLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    loadSolved();
  }, [loadSolved]);

  const handleRefreshAll = useCallback(async () => {
    await Promise.all([refresh(), loadSolved()]);
  }, [refresh, loadSolved]);

  if (userLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <p className="text-sm uppercase tracking-[0.3em] text-white/60">Loading profile…</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute -top-24 right-16 h-72 w-72 rounded-full bg-indigo-500/20 blur-[120px]" />
          <div className="absolute bottom-0 left-8 h-80 w-80 rounded-full bg-purple-500/20 blur-[120px]" />
        </div>
        <main className="relative mx-auto flex min-h-screen w-full max-w-3xl flex-col items-center justify-center px-6 text-center">
          <h1 className="text-4xl font-semibold">Log in to view your progress</h1>
          <p className="mt-4 text-white/70">
            Track solved problems, streaks, and personal milestones once you sign in.
          </p>
          <div className="mt-8 flex flex-col gap-4 sm:flex-row">
            <Link
              href="/login"
              className="rounded-full bg-white px-8 py-3 text-sm font-semibold text-slate-900 shadow-lg shadow-white/20"
            >
              Login
            </Link>
            <Link
              href="/signup"
              className="rounded-full border border-white/20 px-8 py-3 text-sm font-semibold text-white/80 transition hover:border-white/40 hover:text-white"
            >
              Create Account
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <ProfileLayout
      profile={user}
      solvedProblems={solvedProblems}
      solvedLoading={solvedLoading}
      solvedError={solvedError}
      onRefreshProfile={handleRefreshAll}
      onRefreshSolved={loadSolved}
      isOwnProfile
    />
  );
}
