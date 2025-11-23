"use client";

import Link from "next/link";
import { useCallback, useState } from "react";
import { useUserContext } from "@/components/UserProvider";

const navLinks = [
  { href: "/problems", label: "Problems" },
  { href: "/leaderboard", label: "Leaderboard" },
  { href: "/generate", label: "Generate" },
  { href: "/profile", label: "Profile" },
];

export default function Navbar() {
  const { user, setUser } = useUserContext();
  const isAuthenticated = Boolean(user);
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = useCallback(() => {
    try {
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
      }
    } catch (err) {
      /* swallow storage errors */
    }
    setUser(null);
    window.location.href = "/";
  }, [setUser]);

  const closeMobile = useCallback(() => setMobileOpen(false), []);

  return (
    <nav
      className="relative z-50 isolate border-b border-white/5 bg-slate-950/70 text-white shadow-lg shadow-black/40 backdrop-blur-xl supports-[backdrop-filter]:backdrop-blur-xl sticky top-0"
      style={{ minHeight: "var(--navbar-height, 72px)" }}
    >
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -left-16 top-1/2 h-40 w-40 -translate-y-1/2 rounded-full bg-indigo-500/20 blur-[100px]" />
        <div className="absolute right-10 top-0 h-32 w-32 rounded-full bg-blue-500/20 blur-[90px]" />
      </div>

      <div className="relative mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
        <Link
          href="/"
          className="flex cursor-pointer items-center gap-2 text-2xl font-semibold tracking-tight text-white transition hover:text-white/80"
          onClick={closeMobile}
        >
          <span className="rounded-full bg-white/10 px-3 py-1 text-sm font-semibold uppercase tracking-[0.2em] text-white/70">
            AG
          </span>
          AlgoGenius
        </Link>

        <div className="flex items-center gap-4">
          <div className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/5 px-2 py-1 text-sm font-medium text-white/80 shadow-inner shadow-black/20 backdrop-blur sm:flex">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="rounded-full px-3 py-1 transition hover:bg-white/10 hover:text-white cursor-pointer"
                onClick={closeMobile}
              >
                {link.label}
              </Link>
            ))}
          </div>

          <button
            type="button"
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-white/20 text-white/80 transition hover:border-white/40 hover:text-white sm:hidden cursor-pointer"
            onClick={() => setMobileOpen((prev) => !prev)}
            aria-label="Toggle navigation"
          >
            <span className="sr-only">Toggle navigation</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="h-5 w-5"
            >
              {mobileOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 5.25h16.5M3.75 12h16.5m-16.5 6.75h16.5" />
              )}
            </svg>
          </button>

          {isAuthenticated ? (
            <div className="flex items-center gap-3">
              <span className="hidden rounded-full border border-white/10 bg-white/5 px-3 py-1 text-sm text-white/80 sm:inline-flex">
                {user?.username || user?.email || "Coder"}
              </span>
              <button
                type="button"
                onClick={handleLogout}
                className="cursor-pointer rounded-full bg-gradient-to-r from-rose-500 via-fuchsia-500 to-indigo-500 px-4 py-2 text-sm font-semibold text-white shadow-md shadow-rose-500/30 transition hover:scale-[1.02]"
              >
                Logout
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3 text-sm font-semibold">
              <Link
                href="/login"
                className="cursor-pointer rounded-full border border-white/20 px-4 py-2 text-white/80 transition hover:border-white/40 hover:text-white"
              >
                Login
              </Link>
              <Link
                href="/signup"
                className="cursor-pointer rounded-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 px-4 py-2 text-white shadow-md shadow-indigo-500/30 transition hover:scale-[1.02]"
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>

      {mobileOpen && (
        <div className="sm:hidden">
          <div className="mx-4 mb-4 rounded-3xl border border-white/10 bg-slate-950/95 p-4 shadow-xl shadow-black/40">
            <div className="flex flex-col gap-2 text-base font-semibold text-white/80">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="rounded-2xl px-4 py-3 transition hover:bg-white/10 hover:text-white cursor-pointer"
                  onClick={closeMobile}
                >
                  {link.label}
                </Link>
              ))}
            </div>
            <div className="mt-4 flex flex-col gap-2">
              {isAuthenticated ? (
                <>
                  <div className="rounded-2xl border border-white/10 px-4 py-3 text-sm text-white/70">
                    Signed in as {user?.username || user?.email || "Coder"}
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      closeMobile();
                      handleLogout();
                    }}
                    className="cursor-pointer rounded-full bg-gradient-to-r from-rose-500 via-fuchsia-500 to-indigo-500 px-4 py-2 text-center text-sm font-semibold text-white"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="cursor-pointer rounded-full border border-white/20 px-4 py-2 text-center text-sm text-white/80 transition hover:border-white/40 hover:text-white"
                    onClick={closeMobile}
                  >
                    Login
                  </Link>
                  <Link
                    href="/signup"
                    className="cursor-pointer rounded-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 px-4 py-2 text-center text-sm font-semibold text-white"
                    onClick={closeMobile}
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
