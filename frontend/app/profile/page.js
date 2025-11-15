// Async function to fetch mock user data
async function fetchUserData() {
  // Mock user data for now
  return {
    username: 'JohnDoe',
    currentStreak: 15,
    totalXP: 2450,
    problemsSolved: 42,
    rank: 128,
    joinedDate: 'January 2025',
  };
}

export default async function ProfilePage() {
  const userData = await fetchUserData();

  return (
    <div className="min-h-screen bg-gray-100">
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Profile
        </h1>

        {/* User Info Section */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center text-white text-3xl font-bold">
              {userData.username.charAt(0)}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {userData.username}
              </h2>
              <p className="text-gray-600">
                Member since {userData.joinedDate}
              </p>
            </div>
          </div>
        </div>

        {/* Stats Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Current Streak Card */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-700">
                Current Streak
              </h3>
              <span className="text-2xl">🔥</span>
            </div>
            <p className="text-4xl font-bold text-blue-600">
              {userData.currentStreak}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              days
            </p>
          </div>

          {/* Total XP Card */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-700">
                Total XP
              </h3>
              <span className="text-2xl">⭐</span>
            </div>
            <p className="text-4xl font-bold text-green-600">
              {userData.totalXP}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              experience points
            </p>
          </div>

          {/* Problems Solved Card */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-700">
                Problems Solved
              </h3>
              <span className="text-2xl">✓</span>
            </div>
            <p className="text-4xl font-bold text-purple-600">
              {userData.problemsSolved}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              challenges
            </p>
          </div>

          {/* Rank Card */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-700">
                Global Rank
              </h3>
              <span className="text-2xl">🏆</span>
            </div>
            <p className="text-4xl font-bold text-orange-600">
              #{userData.rank}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              worldwide
            </p>
          </div>
        </div>

        {/* Contribution Heatmap Placeholder */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Contribution Activity
          </h3>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
            <p className="text-gray-500 text-lg mb-2">
              📊 Contribution Heatmap
            </p>
            <p className="text-gray-400 text-sm">
              Heatmap visualization coming soon...
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
