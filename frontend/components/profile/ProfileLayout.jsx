"use client";

import Link from "next/link";
import { useMemo } from "react";

const STAT_STYLES = [
  "from-sky-500/20 via-sky-500/10 to-transparent",
  "from-purple-500/20 via-purple-500/10 to-transparent",
  "from-emerald-500/20 via-emerald-500/10 to-transparent",
  "from-amber-500/20 via-amber-500/10 to-transparent",
];

const formatDate = (input) => {
  if (!input) {
    return "Not available";
  }
  try {
    const parsed = new Date(input);
    return parsed.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch (err) {
    return String(input);
  }
};

function humanDifficulty(difficulty) {
  if (!difficulty || typeof difficulty !== "string") return "Unknown";
  return `${difficulty.charAt(0).toUpperCase()}${difficulty.slice(1)}`;
}

function badgeStyle(difficulty) {
  switch ((difficulty || "").toLowerCase()) {
    case "easy":
      return "bg-emerald-500/10 text-emerald-300 border border-emerald-500/30";
    case "medium":
      return "bg-amber-500/10 text-amber-300 border border-amber-500/30";
    case "hard":
      return "bg-rose-500/10 text-rose-300 border border-rose-500/30";
    default:
      return "bg-slate-500/10 text-slate-200 border border-slate-500/25";
  }
}

export default function ProfileLayout({
  profile,
  solvedProblems,
  solvedLoading,
  solvedError,
  onRefreshProfile,
  onRefreshSolved,
  isOwnProfile = false,
}) {
  const solvedList = solvedProblems || [];
  const solvedCount = profile?.solved_count ?? solvedList.length ?? 0;
  const profileInitial =
    profile?.username?.slice(0, 1)?.toUpperCase() ||
    profile?.email?.slice(0, 1)?.toUpperCase() ||
    "?";

  const statCards = useMemo(() => {
    if (!profile) {
      return [];
    }

    return [
      {
        label: "Total XP",
        value: profile.xp ?? 0,
        helper: "Earn XP by solving harder challenges.",
        icon: "⚡",
      },
      {
        label: "Current Streak",
        value: profile.current_streak ?? 0,
        helper:
          profile.current_streak
            ? "Keep shipping daily submissions."
            : "Start a streak today!",
        icon: "🔥",
      },
      {
        label: "Problems Solved",
        value: solvedCount,
        helper:
          solvedCount === 1
            ? "1 challenge completed"
            : `${solvedCount} challenges completed`,
        icon: "✓",
      },
      {
        label: "Last Submission",
        value: profile.last_submission_date
          ? formatDate(profile.last_submission_date)
          : "No submissions yet",
        helper: profile.last_submission_date
          ? "Great job staying active."
          : "Jump into a problem to get started.",
        icon: "📅",
      },
    ];
  }, [profile, solvedCount]);

  const solvedHeading = isOwnProfile
    ? "Your recent victories"
    : `${profile?.username || "User"}'s recent victories`;

  const handleRefresh = async () => {
    if (onRefreshProfile) {
      await onRefreshProfile();
    }
    if (onRefreshSolved) {
      await onRefreshSolved();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-24 right-24 h-72 w-72 rounded-full bg-blue-500/20 blur-[120px]" />
        <div className="absolute bottom-0 left-10 h-80 w-80 rounded-full bg-purple-500/25 blur-[120px]" />
      </div>
      <main className="relative mx-auto w-full max-w-5xl px-6 pb-24 pt-20 sm:px-10">
        <header className="rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/30 backdrop-blur">
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 text-3xl font-semibold">
                {profileInitial}
              </div>
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-white/50">
                  {isOwnProfile ? "Profile" : "User Profile"}
                </p>
                <h1 className="text-3xl font-semibold text-white">
                  {profile?.username || profile?.email || "AlgoGenius user"}
                </h1>
                {profile?.email && (
                  <p className="text-sm text-white/70">{profile.email}</p>
                )}
                {profile?.id != null && (
                  <p className="text-xs text-white/60">User ID: {profile.id}</p>
                )}
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              {onRefreshProfile && (
                <button
                  type="button"
                  onClick={handleRefresh}
                  className="rounded-full border border-white/20 px-5 py-2 text-sm font-semibold text-white/80 transition hover:border-white/40 hover:text-white"
                >
                  Refresh Stats
                </button>
              )}
              <Link
                href="/leaderboard"
                className="rounded-full bg-white/90 px-5 py-2 text-sm font-semibold text-slate-900 transition hover:bg-white"
              >
                View Leaderboard →
              </Link>
            </div>
          </div>
        </header>

        <section className="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          {statCards.map((card, index) => (
            <div
              key={card.label}
              className={`rounded-3xl border border-white/15 bg-gradient-to-br ${
                STAT_STYLES[index % STAT_STYLES.length]
              } p-6 shadow-lg shadow-black/20 backdrop-blur`}
            >
              <div className="flex items-center justify-between text-sm uppercase tracking-[0.25em] text-white/60">
                <span>{card.label}</span>
                <span className="text-lg">{card.icon}</span>
              </div>
              <p className="mt-4 text-4xl font-semibold text-white">{card.value}</p>
              {card.helper && <p className="mt-2 text-sm text-white/70">{card.helper}</p>}
            </div>
          ))}
        </section>

        <section className="mt-12 rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/30 backdrop-blur">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-white/50">Solved problems</p>
              <h2 className="text-2xl font-semibold text-white">{solvedHeading}</h2>
              <p className="text-sm text-white/70">
                {solvedCount
                  ? `Showing the latest ${Math.min(solvedList.length, solvedCount)} solutions.`
                  : isOwnProfile
                  ? "No solved problems yet. Tackle a challenge to show progress."
                  : "This user has not solved any problems yet."}
              </p>
            </div>
            {onRefreshSolved && (
              <button
                type="button"
                onClick={onRefreshSolved}
                className="rounded-full border border-white/20 px-4 py-2 text-xs font-semibold uppercase tracking-[0.3em] text-white/70 transition hover:border-white/40 hover:text-white"
              >
                Refresh List
              </button>
            )}
          </div>

          {solvedLoading ? (
            <div className="mt-8 space-y-4">
              {[...Array(3)].map((_, idx) => (
                <div
                  key={idx}
                  className="animate-pulse rounded-2xl border border-white/10 bg-white/10 p-5"
                >
                  <div className="h-4 w-1/3 rounded bg-white/20" />
                  <div className="mt-3 h-3 w-2/3 rounded bg-white/10" />
                  <div className="mt-4 h-24 rounded bg-white/5" />
                </div>
              ))}
            </div>
          ) : solvedError ? (
            <div className="mt-8 rounded-2xl border border-rose-500/40 bg-rose-500/10 p-6 text-sm text-rose-100">
              {solvedError}
            </div>
          ) : solvedList.length === 0 ? (
            <div className="mt-8 rounded-2xl border border-white/10 bg-white/5 p-6 text-sm text-white/70">
              {isOwnProfile
                ? "Nothing here yet. Head to the problems page and earn that first checkmark."
                : "No public solves to display."}
            </div>
          ) : (
            <div className="mt-8 space-y-5">
              {solvedList.map((entry) => {
                const badge = badgeStyle(entry.difficulty);
                const snippet = entry.solution_code?.length > 360
                  ? `${entry.solution_code.slice(0, 360)}…`
                  : entry.solution_code;
                const problemLink = `/problems/${entry.problem_id}/solve`;
                return (
                  <article
                    key={`${entry.problem_id}-${entry.solved_at}`}
                    className="rounded-2xl border border-white/10 bg-black/20 p-6 shadow-inner shadow-black/40"
                  >
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                      <div>
                        <h3 className="text-xl font-semibold text-white/95">
                          {entry.problem_title}
                        </h3>
                        <p className="text-sm text-white/60">
                          Solved {formatDate(entry.solved_at)} · {entry.language?.toUpperCase()}
                        </p>
                      </div>
                      <div className="flex flex-wrap items-center gap-3">
                        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${badge}`}>
                          {humanDifficulty(entry.difficulty)}
                        </span>
                        <Link
                          href={problemLink}
                          className="rounded-full border border-white/20 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-white/80 transition hover:border-white/40 hover:text-white"
                        >
                          {isOwnProfile ? "Solve again" : "View problem"}
                        </Link>
                      </div>
                    </div>
                    {isOwnProfile && snippet && (
                      <pre className="mt-5 max-h-52 overflow-auto rounded-2xl border border-white/5 bg-black/40 p-4 text-xs leading-relaxed text-emerald-100">
                        {snippet}
                      </pre>
                    )}
                  </article>
                );
              })}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
