"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import api from "@/src/lib/api";

const heroButtonsBase =
  "inline-flex items-center justify-center gap-2 rounded-full px-8 py-3 text-lg font-semibold transition-transform duration-200 ease-out will-change-transform";

const outlineButton =
  "border border-white/30 bg-white/5 backdrop-blur hover:border-white/60 hover:bg-white/10 hover:opacity-90 hover:scale-[1.03]";
const solidButton =
  "bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:scale-[1.05]";

const authButton =
  "rounded-full border border-white/20 bg-white/10 px-6 py-2 text-base font-medium text-white/90 transition duration-200 hover:border-white/40 hover:bg-white/20 hover:text-white";

function useStoredUser() {
  const [user, setUserState] = useState(null);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const stored = localStorage.getItem("user");
    if (!stored) {
      setUserState(null);
      return;
    }
    try {
      const parsed = JSON.parse(stored);
      setUserState(parsed);
    } catch (err) {
      console.warn("Failed to parse stored user", err);
      setUserState(null);
    }
  }, []);

  const setUser = useCallback((valueOrUpdater) => {
    setUserState((prev) => {
      const next =
        typeof valueOrUpdater === "function"
          ? valueOrUpdater(prev)
          : valueOrUpdater;

      if (typeof window !== "undefined") {
        try {
          if (next) {
            localStorage.setItem("user", JSON.stringify(next));
          } else {
            localStorage.removeItem("user");
            localStorage.removeItem("access_token");
          }
        } catch (err) {
          console.warn("Failed to update stored user", err);
        }
      }

      return next ?? null;
    });
  }, []);

  return [user, setUser];
}

function useDailyChallenge() {
  const [daily, setDaily] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isCancelled = false;

    const fetchDaily = async () => {
      setLoading(true);
      setError(null);

      try {
        const { data } = await api.get("/problems/random");
        if (!isCancelled) {
          setDaily(data);
        }
      } catch (err) {
        if (!isCancelled) {
          console.error("Daily challenge fetch failed", err);
          setError("Unable to load today's challenge. Please try again later.");
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    };

    fetchDaily();

    return () => {
      isCancelled = true;
    };
  }, []);

  return { daily, loading, error };
}

function difficultyStyles(difficulty) {
  switch ((difficulty || "").toLowerCase()) {
    case "easy":
      return "bg-emerald-500/10 text-emerald-300 border border-emerald-500/40";
    case "medium":
      return "bg-amber-500/10 text-amber-300 border border-amber-500/40";
    case "hard":
      return "bg-rose-500/10 text-rose-300 border border-rose-500/40";
    default:
      return "bg-slate-500/10 text-slate-200 border border-slate-500/30";
  }
}

function formatDifficulty(difficulty) {
  if (!difficulty || typeof difficulty !== "string") {
    return "Unknown";
  }
  return `${difficulty.charAt(0).toUpperCase()}${difficulty.slice(1)}`;
}

export default function HomePage() {
  const [storedUser, setStoredUser] = useStoredUser();
  const {
    daily,
    loading: dailyLoading,
    error: dailyError,
  } = useDailyChallenge();
  const [isAdmin, setIsAdmin] = useState(false);

  const userIdentifier = storedUser?.user_id ?? storedUser?.id ?? null;
  const cachedAdminFlag = Boolean(storedUser?.is_admin);

  useEffect(() => {
    if (!userIdentifier) {
      setIsAdmin(false);
      return;
    }

    let isCancelled = false;

    const hydrateProfile = async () => {
      try {
        const { data } = await api.get("/users/me");
        if (isCancelled) {
          return;
        }
        const adminFlag = Boolean(data?.is_admin);
        setIsAdmin(adminFlag);
        setStoredUser((prev) => {
          if (!prev) {
            return data;
          }
          return { ...prev, ...data, is_admin: adminFlag };
        });
      } catch (err) {
        if (isCancelled) {
          return;
        }
        if (err?.response?.status === 401) {
          setStoredUser(null);
          setIsAdmin(false);
          return;
        }
        setIsAdmin(cachedAdminFlag);
      }
    };

    hydrateProfile();

    return () => {
      isCancelled = true;
    };
  }, [userIdentifier, cachedAdminFlag, setStoredUser]);

  const greeting = useMemo(() => {
    if (!storedUser?.username && !storedUser?.email) {
      return null;
    }
    const name = storedUser.username || storedUser.email;
    return `Welcome, ${name}`;
  }, [storedUser]);

  const dailySummary = useMemo(() => {
    if (!daily?.description) {
      return "No description available for this challenge.";
    }
    const firstParagraph = daily.description
      .split("\n")
      .map((section) => section.trim())
      .filter(Boolean)[0];

    if (!firstParagraph) {
      return "No description available for this challenge.";
    }

    return firstParagraph.length > 220
      ? `${firstParagraph.slice(0, 220)}…`
      : firstParagraph;
  }, [daily]);

  const isLoggedIn = Boolean(storedUser);
  const dailyLink = daily?.id ? `/problems/${daily.id}/solve` : "/problems";

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      <div className="absolute inset-0 overflow-hidden">
        <div className="pointer-events-none absolute -top-24 right-24 h-72 w-72 rounded-full bg-purple-500/20 blur-[120px]" />
        <div className="pointer-events-none absolute bottom-0 left-10 h-80 w-80 rounded-full bg-blue-500/20 blur-[120px]" />
      </div>

      <main className="relative mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-16 px-6 pb-24 pt-20 sm:px-10">
        <section className="flex flex-col items-center gap-10 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-5 py-2 text-sm font-medium text-white/80 shadow-lg shadow-black/10">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            Coding practice for ambitious engineers
          </div>

          <div className="max-w-3xl space-y-6">
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
              Crack algorithms with confidence, guided by AI and daily
              challenges.
            </h1>
            <p className="text-lg text-white/70 md:text-xl">
              AlgoGenius combines curated practice with AI-generated problems so
              you can level up faster. Pick a challenge, code with stdin/stdout,
              and keep the streak alive.
            </p>
            {greeting && (
              <p className="text-base font-medium text-white/80">{greeting}</p>
            )}
          </div>

          <div className="flex flex-col items-center justify-center gap-4">
            <Link
              href="/generate"
              className={`${heroButtonsBase} ${solidButton} px-10 py-3 sm:px-12`}
            >
              ✨ Generate an AI Problem
            </Link>
            <div className="flex flex-wrap items-center justify-center gap-4">
              {isLoggedIn ? (
                <>
                  <Link
                    href="/problems"
                    className={`${heroButtonsBase} ${outlineButton}`}
                  >
                    💻 Solve Problems
                  </Link>
                  <Link
                    href="/problems/list"
                    className={`${heroButtonsBase} ${outlineButton}`}
                  >
                    📚 Existing Problems
                  </Link>
                  {isAdmin && (
                    <Link
                      href="/admin/generate"
                      className={`${heroButtonsBase} ${outlineButton}`}
                    >
                      🧠 Generate Problem
                    </Link>
                  )}
                </>
              ) : (
                <div className="flex flex-wrap items-center justify-center gap-3">
                  <Link href="/login" className={authButton}>
                    Login
                  </Link>
                  <Link
                    href="/signup"
                    className={`${authButton} bg-white/90 text-slate-900 hover:bg-white`}
                  >
                    Sign Up
                  </Link>
                </div>
              )}
            </div>
          </div>
        </section>

        <section className="grid gap-8 md:grid-cols-[1.2fr_1fr]">
          <div className="rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/30 backdrop-blur">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold text-white">
                Daily Challenge
              </h2>
              <span className="text-sm uppercase tracking-wide text-white/60">
                Fresh every refresh
              </span>
            </div>

            <div className="mt-6 space-y-6">
              {dailyLoading ? (
                <div className="animate-pulse space-y-4">
                  <div className="h-6 w-3/4 rounded bg-white/10" />
                  <div className="h-4 w-full rounded bg-white/10" />
                  <div className="h-4 w-5/6 rounded bg-white/10" />
                  <div className="h-10 w-40 rounded-full bg-white/10" />
                </div>
              ) : dailyError ? (
                <div className="rounded-2xl border border-rose-500/40 bg-rose-500/10 p-6 text-left text-rose-200">
                  {dailyError}
                </div>
              ) : daily ? (
                <>
                  <div className="flex flex-wrap items-center gap-3">
                    <h3 className="text-xl font-semibold text-white/95">
                      {daily.title}
                    </h3>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide ${difficultyStyles(
                        daily.difficulty
                      )}`}
                    >
                      {formatDifficulty(daily.difficulty)}
                    </span>
                  </div>

                  <p className="text-base leading-relaxed text-white/70">
                    {dailySummary}
                  </p>

                  <Link
                    href={dailyLink}
                    className="inline-flex items-center gap-2 rounded-full bg-white/90 px-6 py-2 text-sm font-semibold text-slate-900 transition duration-200 hover:bg-white"
                  >
                    Solve Now →
                  </Link>
                </>
              ) : (
                <p className="text-white/70">
                  No challenge available right now.
                </p>
              )}
            </div>
          </div>

          <aside className="flex flex-col gap-6 rounded-3xl border border-white/10 bg-gradient-to-br from-white/10 via-white/5 to-transparent p-8 text-white/80 shadow-2xl shadow-black/40 backdrop-blur">
            <div>
              <h3 className="text-lg font-semibold text-white">How it works</h3>
              <ul className="mt-4 space-y-3 text-sm leading-relaxed text-white/70">
                <li className="flex gap-2">
                  <span className="mt-1.5 h-2 w-2 flex-shrink-0 rounded-full bg-indigo-400" />
                  Pick a challenge, read the prompt, and inspect the sample
                  tests.
                </li>
                <li className="flex gap-2">
                  <span className="mt-1.5 h-2 w-2 flex-shrink-0 rounded-full bg-indigo-400" />
                  Write code directly in the browser and run against
                  stdin/stdout.
                </li>
                <li className="flex gap-2">
                  <span className="mt-1.5 h-2 w-2 flex-shrink-0 rounded-full bg-indigo-400" />
                  Keep your streak alive to climb the AlgoGenius leaderboard.
                </li>
              </ul>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
              <p className="text-sm text-white/60">
                Tip: Admins can generate fresh problems with Gemini under
                <Link
                  href="/admin/generate"
                  className="ml-2 font-semibold text-white hover:underline"
                >
                  AI Problem Generator
                </Link>
                .
              </p>
            </div>
          </aside>
        </section>
      </main>
    </div>
  );
}
