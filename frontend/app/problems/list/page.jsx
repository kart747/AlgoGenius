"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import api from "@/src/lib/api";
import AdminProblemDeleteButton from "@/components/admin/AdminProblemDeleteButton";
import { useUserContext } from "@/components/UserProvider";

const DIFFICULTY_OPTIONS = [
  { label: "All", value: "" },
  { label: "Easy", value: "easy" },
  { label: "Medium", value: "medium" },
  { label: "Hard", value: "hard" },
];

const SORT_OPTIONS = [
  { label: "Newest", value: "latest" },
  { label: "Oldest", value: "oldest" },
  { label: "A → Z", value: "alphabetical" },
];

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

function humanDifficulty(difficulty) {
  if (!difficulty || typeof difficulty !== "string") return "Unknown";
  return `${difficulty.charAt(0).toUpperCase()}${difficulty.slice(1)}`;
}

export default function ProblemsListPage() {
  const [difficultyFilter, setDifficultyFilter] = useState("");
  const [sortOrder, setSortOrder] = useState("latest");
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [solvedProblems, setSolvedProblems] = useState([]);
  const { user } = useUserContext();

  useEffect(() => {
    let cancelled = false;

    const fetchProblems = async () => {
      setLoading(true);
      setError(null);

      try {
        const params = {};
        if (difficultyFilter) {
          params.difficulty = difficultyFilter;
        }
        if (sortOrder) {
          params.sort = sortOrder;
        }
        const { data } = await api.get("/problems", { params });
        if (!cancelled) {
          setProblems(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        if (!cancelled) {
          const detail =
            err?.response?.data?.detail ||
            err?.response?.data?.message ||
            err?.message ||
            "Unable to load problems.";
          setError(detail);
          setProblems([]);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchProblems();

    return () => {
      cancelled = true;
    };
  }, [difficultyFilter, sortOrder]);

  useEffect(() => {
    let cancelled = false;

    const hydrateAdmin = async () => {
      try {
        if (typeof window !== "undefined") {
          const stored = localStorage.getItem("user");
          if (stored) {
            const parsed = JSON.parse(stored);
            if (!cancelled && parsed?.is_admin) {
              setIsAdmin(true);
            }
          }
        }
      } catch (err) {
        // ignore parse errors
      }

      try {
        const { data } = await api.get("/users/me");
        if (!cancelled) {
          setIsAdmin(Boolean(data?.is_admin));
        }
      } catch (err) {
        if (!cancelled) {
          setIsAdmin((prev) => prev);
        }
      }
    };

    hydrateAdmin();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    const fetchSolvedProblems = async () => {
      if (!user) {
        setSolvedProblems([]);
        return;
      }

      try {
        const { data } = await api.get("/users/me/solved");
        if (!cancelled) {
          setSolvedProblems(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        if (!cancelled) {
          setSolvedProblems([]);
        }
      }
    };

    fetchSolvedProblems();

    return () => {
      cancelled = true;
    };
  }, [user]);

  const solvedIds = useMemo(() => {
    if (!solvedProblems?.length) {
      return new Set();
    }
    return new Set(solvedProblems.map((entry) => entry.problem_id));
  }, [solvedProblems]);

  const summaryText = useMemo(() => {
    if (!problems.length) {
      return "No problems available for the selected filters.";
    }
    const counts = problems.reduce(
      (acc, prob) => {
        const key = (prob.difficulty || "unknown").toLowerCase();
        acc[key] = (acc[key] || 0) + 1;
        acc.total += 1;
        return acc;
      },
      { total: 0 }
    );

    const parts = [`${counts.total} problems`];
    if (counts.easy) parts.push(`${counts.easy} easy`);
    if (counts.medium) parts.push(`${counts.medium} medium`);
    if (counts.hard) parts.push(`${counts.hard} hard`);

    return parts.join(" · ");
  }, [problems]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="pointer-events-none absolute -top-32 left-16 h-72 w-72 rounded-full bg-blue-500/20 blur-[120px]" />
        <div className="pointer-events-none absolute bottom-0 right-10 h-80 w-80 rounded-full bg-purple-500/20 blur-[120px]" />
      </div>

      <main className="relative mx-auto flex w-full max-w-5xl flex-col gap-10 px-6 pb-24 pt-20 sm:px-10">
        <header className="space-y-4 text-center sm:text-left">
          <p className="text-sm uppercase tracking-[0.2em] text-white/50">
            Problem Library
          </p>
          <h1 className="text-3xl font-bold sm:text-4xl">
            Browse all AlgoGenius challenges
          </h1>
          <p className="text-white/60">{summaryText}</p>
        </header>

        <section className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-wrap gap-2">
              {DIFFICULTY_OPTIONS.map((option) => (
                <button
                  key={option.value || "all"}
                  onClick={() => setDifficultyFilter(option.value)}
                  className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                    difficultyFilter === option.value
                      ? "bg-white text-slate-900"
                      : "bg-white/10 text-white/80 hover:bg-white/20"
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>

            <label className="flex items-center gap-3 text-sm text-white/70">
              Sort by
              <select
                value={sortOrder}
                onChange={(event) => setSortOrder(event.target.value)}
                className="rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm text-white focus:border-white/40 focus:outline-none"
              >
                {SORT_OPTIONS.map((option) => (
                  <option
                    key={option.value}
                    value={option.value}
                    className="text-slate-900"
                  >
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="space-y-4">
            {loading ? (
              <div className="space-y-4">
                {[...Array(5)].map((_, idx) => (
                  <div
                    key={idx}
                    className="animate-pulse rounded-2xl border border-white/10 bg-white/10 p-5"
                  >
                    <div className="h-5 w-2/3 rounded bg-white/20" />
                    <div className="mt-3 h-3 w-full rounded bg-white/10" />
                    <div className="mt-2 h-3 w-4/5 rounded bg-white/10" />
                  </div>
                ))}
              </div>
            ) : error ? (
              <div className="rounded-2xl border border-rose-500/40 bg-rose-500/10 p-6 text-sm text-rose-200">
                {error}
              </div>
            ) : problems.length === 0 ? (
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-sm text-white/70">
                No problems match the current filters.
              </div>
            ) : (
              problems.map((problem) => {
                const solved = solvedIds.has(problem.id);

                return (
                <article
                  key={problem.id}
                    className={`group flex flex-col gap-4 rounded-2xl border p-5 transition hover:border-white/40 hover:bg-white/10 ${
                      solved
                        ? "border-emerald-400/40 bg-emerald-500/5"
                        : "border-white/10 bg-white/5"
                    }`}
                >
                  <div className="flex flex-wrap items-center gap-3">
                    <h2 className="text-lg font-semibold text-white/95">
                      {problem.title}
                    </h2>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${badgeStyle(
                        problem.difficulty
                      )}`}
                    >
                      {humanDifficulty(problem.difficulty)}
                    </span>
                      {solved && (
                        <span className="inline-flex items-center gap-1 rounded-full border border-emerald-400/40 bg-emerald-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-emerald-200">
                          <span className="text-base">✓</span>
                          Solved
                        </span>
                      )}
                  </div>

                  <p className="text-sm leading-relaxed text-white/70">
                    {problem.description?.length > 200
                      ? `${problem.description.slice(0, 200)}…`
                      : problem.description || "No description provided."}
                  </p>

                  <div className="flex flex-wrap items-center gap-3 text-sm text-white/50">
                    <span>
                      {problem.test_cases?.length || 0} test case
                      {(problem.test_cases?.length || 0) === 1 ? "" : "s"}
                    </span>
                    <span>
                      Updated{" "}
                      {new Date(
                        problem.updated_at || problem.created_at
                      ).toLocaleDateString()}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-3">
                    <Link
                      href={`/problems/${problem.id}/solve`}
                      className="inline-flex items-center gap-2 rounded-full bg-white/90 px-5 py-2 text-sm font-semibold text-slate-900 transition duration-200 hover:bg-white"
                    >
                      Solve Now →
                    </Link>
                    <Link
                      href={`/problems/${problem.id}/solve`}
                      className="inline-flex items-center gap-2 rounded-full border border-white/20 px-5 py-2 text-sm font-semibold text-white/80 transition duration-200 hover:border-white/40 hover:text-white"
                    >
                      View Details
                    </Link>
                    {isAdmin && (
                      <AdminProblemDeleteButton
                        problemId={problem.id}
                        title={problem.title}
                        onDeleted={(deletedId) =>
                          setProblems((prev) =>
                            prev.filter((entry) => entry.id !== deletedId)
                          )
                        }
                      />
                    )}
                  </div>
                </article>
                );
              })
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
