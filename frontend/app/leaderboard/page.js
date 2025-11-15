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

  return (
    <div className="min-h-screen bg-gray-100">
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          🏆 Leaderboard
        </h1>

        {/* Leaderboard Table */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-900 text-white">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold uppercase tracking-wider">
                    Username
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold uppercase tracking-wider">
                    XP
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold uppercase tracking-wider">
                    Streak
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {leaderboardData.map((user, index) => (
                  <tr
                    key={user.id || index}
                    className={`hover:bg-gray-50 transition-colors ${
                      index < 3 ? "bg-yellow-50" : ""
                    }`}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {index === 0 && (
                          <span className="text-2xl mr-2">🥇</span>
                        )}
                        {index === 1 && (
                          <span className="text-2xl mr-2">🥈</span>
                        )}
                        {index === 2 && (
                          <span className="text-2xl mr-2">🥉</span>
                        )}
                        <span className="text-lg font-semibold text-gray-900">
                          {user.rank || index + 1}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold mr-3">
                          {user.username.charAt(0).toUpperCase()}
                        </div>
                        <span className="text-base font-medium text-gray-900">
                          {user.username}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-base font-semibold text-green-600">
                        {user.xp || user.XP}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className="text-xl mr-1">🔥</span>
                        <span className="text-base font-semibold text-orange-600">
                          {user.streak}
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Empty State */}
          {leaderboardData.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">
                No leaderboard data available yet.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
