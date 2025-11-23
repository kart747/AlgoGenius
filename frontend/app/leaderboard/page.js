import Link from "next/link";

// Async function to fetch leaderboard data
async function fetchLeaderboard() {
  const base =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";
  const res = await fetch(`${base}/users/leaderboard`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch leaderboard data");
  }

  return res.json();
}

export default async function LeaderboardPage() {
  const leaderboardData = await fetchLeaderboard();

  const topThree = leaderboardData.slice(0, 3);
  const rest = leaderboardData.slice(3);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="pointer-events-none absolute -top-32 right-10 h-72 w-72 rounded-full bg-emerald-500/15 blur-[130px]" />
        <div className="pointer-events-none absolute bottom-0 left-12 h-72 w-72 rounded-full bg-blue-500/10 blur-[110px]" />
      </div>

      <main className="relative mx-auto flex max-w-6xl flex-col gap-10 px-6 pb-16 pt-24">
        <div className="text-center space-y-4">
          <p className="text-sm uppercase tracking-[0.4em] text-white/60">Community Rankings</p>
          <h1 className="text-4xl font-bold text-white md:text-5xl">AlgoGenius Leaderboard</h1>
          <p className="text-white/70">
            Grinding daily builds streaks, XP, and reputation. Sit on the throne or catch the ones who do.
          </p>
        </div>

        <section className="grid gap-6 md:grid-cols-3">
          {topThree.map((user, index) => (
            <article
              key={user.id || index}
              className={`relative rounded-3xl border border-white/10 bg-white/5 p-6 text-center shadow-2xl shadow-black/30 backdrop-blur transition hover:border-white/20 hover:shadow-black/20 ${
                index === 0 ? "md:-translate-y-4" : ""
              }`}
            >
              <div className="text-4xl">{index === 0 ? "🥇" : index === 1 ? "🥈" : "🥉"}</div>
              <p className="mt-3 text-sm uppercase tracking-widest text-white/60">Rank {user.rank || index + 1}</p>
              {user.id ? (
                <Link
                  href={`/profile/${user.id}`}
                  className="mt-1 text-2xl font-semibold text-emerald-200 transition hover:text-emerald-100"
                >
                  {user.username}
                </Link>
              ) : (
                <h2 className="mt-1 text-2xl font-semibold text-white">{user.username}</h2>
              )}
              <div className="mt-4 flex flex-col gap-2 text-sm text-white/70">
                <p className="rounded-full border border-white/15 bg-white/5 px-4 py-1 font-semibold text-white">
                  {user.xp || user.XP} XP
                </p>
                <p className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-1 font-semibold text-emerald-200">
                  🔥 {user.streak} day streak
                </p>
              </div>
            </article>
          ))}
        </section>

        <section className="rounded-3xl border border-white/10 bg-white/5 shadow-2xl shadow-black/30 backdrop-blur">
          <div className="overflow-x-auto rounded-3xl">
            <table className="w-full min-w-[600px]">
              <thead>
                <tr className="bg-white/5 text-left text-xs uppercase tracking-[0.3em] text-white/50">
                  <th className="px-6 py-4">Rank</th>
                  <th className="px-6 py-4">User</th>
                  <th className="px-6 py-4">XP</th>
                  <th className="px-6 py-4">Streak</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {rest.map((user, index) => (
                  <tr key={user.id || index} className="text-sm text-white/80 transition hover:bg-white/5">
                    <td className="px-6 py-4 font-semibold text-white">
                      {user.rank || index + 4}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        {user.id ? (
                          <Link
                            href={`/profile/${user.id}`}
                            className="flex items-center gap-3 transition hover:text-emerald-200"
                          >
                            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-500/30 text-base font-bold text-indigo-100">
                              {user.username?.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <p className="font-medium text-white">{user.username}</p>
                              <p className="text-xs text-white/50">{user.email || "anon"}</p>
                            </div>
                          </Link>
                        ) : (
                          <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-500/30 text-base font-bold text-indigo-100">
                              {user.username?.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <p className="font-medium text-white">{user.username}</p>
                              <p className="text-xs text-white/50">{user.email || "anon"}</p>
                            </div>
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-emerald-300 font-semibold">
                      {user.xp || user.XP}
                    </td>
                    <td className="px-6 py-4 text-amber-300 font-semibold">
                      🔥 {user.streak}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {leaderboardData.length === 0 && (
            <div className="px-6 py-12 text-center text-white/60">
              No leaderboard data yet. Start solving to claim the crown.
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
