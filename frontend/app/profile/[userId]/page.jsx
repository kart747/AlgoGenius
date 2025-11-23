"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import api from "@/src/lib/api";
import ProfileLayout from "@/components/profile/ProfileLayout";

export default function PublicProfilePage() {
  const params = useParams();
  const userId = params?.userId;

  const [profile, setProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileError, setProfileError] = useState(null);

  const [solvedProblems, setSolvedProblems] = useState([]);
  const [solvedLoading, setSolvedLoading] = useState(false);
  const [solvedError, setSolvedError] = useState(null);

  const loadProfile = useCallback(async () => {
    if (!userId) {
      return;
    }
    setProfileLoading(true);
    setProfileError(null);
    try {
      const { data } = await api.get(`/users/profile/${userId}`);
      setProfile(data);
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        "Unable to load profile.";
      setProfile(null);
      setProfileError(detail);
    } finally {
      setProfileLoading(false);
    }
  }, [userId]);

  const loadSolved = useCallback(async () => {
    if (!userId) {
      return;
    }
    setSolvedLoading(true);
    setSolvedError(null);
    try {
      const { data } = await api.get(`/users/${userId}/solved`);
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
  }, [userId]);

  useEffect(() => {
    if (!userId) {
      return;
    }
    loadProfile();
    loadSolved();
  }, [loadProfile, loadSolved, userId]);

  if (!userId) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 text-white">
        <p className="text-lg text-white/80">Invalid profile URL.</p>
        <Link href="/profile" className="mt-6 text-sm font-semibold text-indigo-300">
          Return to your profile
        </Link>
      </div>
    );
  }

  if (profileLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <p className="text-sm uppercase tracking-[0.3em] text-white/60">Loading profile…</p>
      </div>
    );
  }

  if (profileError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute -top-24 right-24 h-72 w-72 rounded-full bg-blue-500/20 blur-[120px]" />
          <div className="absolute bottom-0 left-10 h-80 w-80 rounded-full bg-purple-500/25 blur-[120px]" />
        </div>
        <main className="relative mx-auto flex min-h-screen w-full max-w-xl flex-col items-center justify-center px-6 text-center">
          <p className="text-sm uppercase tracking-[0.3em] text-white/50">Profile unavailable</p>
          <h1 className="mt-4 text-3xl font-semibold">We couldn't find that user.</h1>
          <p className="mt-3 text-white/70">{profileError}</p>
          <Link
            href="/profile"
            className="mt-8 rounded-full border border-white/20 px-8 py-3 text-sm font-semibold text-white/80 transition hover:border-white/40 hover:text-white"
          >
            Go back to your profile
          </Link>
        </main>
      </div>
    );
  }

  if (!profile) {
    return null;
  }

  return (
    <ProfileLayout
      profile={profile}
      solvedProblems={solvedProblems}
      solvedLoading={solvedLoading}
      solvedError={solvedError}
      onRefreshProfile={loadProfile}
      onRefreshSolved={loadSolved}
      isOwnProfile={false}
    />
  );
}
