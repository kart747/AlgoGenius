"use client";

import Link from "next/link";
import { useCallback } from "react";
import { useUserContext } from "@/components/UserProvider";

export default function Navbar() {
  const { user, setUser } = useUserContext();
  const isAuthenticated = Boolean(user);

  const handleLogout = useCallback(() => {
    try {
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
      }
    } catch (err) {
      // ignore storage errors
    }
    setUser(null);
    window.location.href = "/";
  }, [setUser]);

  return (
    <nav className="bg-slate-950/95 text-white shadow-lg shadow-black/20 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
        <Link
          href="/"
          className="text-2xl font-semibold tracking-tight transition hover:text-slate-200"
        >
          AlgoGenius
        </Link>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-5 text-sm font-medium text-white/80">
            <Link href="/profile" className="transition hover:text-white">
              Profile
            </Link>
            <Link href="/leaderboard" className="transition hover:text-white">
              Leaderboard
            </Link>
            <Link href="/problems" className="transition hover:text-white">
              Problems
            </Link>
          </div>

          {isAuthenticated ? (
            <div className="flex items-center gap-3">
              <span className="hidden text-sm text-white/70 sm:block">
                {user?.username || user?.email || "Coder"}
              </span>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-full border border-white/20 px-4 py-2 text-sm font-semibold text-white/80 transition hover:border-white/40 hover:text-white"
              >
                Logout
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3 text-sm font-semibold">
              <Link
                href="/login"
                className="rounded-full px-4 py-2 transition hover:bg-white/10"
              >
                Login
              </Link>
              <Link
                href="/signup"
                className="rounded-full bg-indigo-500 px-4 py-2 text-white transition hover:bg-indigo-600"
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
