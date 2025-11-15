import CodeSubmission from "@/components/CodeSubmission";

// Async function to fetch the daily problem
async function fetchDailyProblem() {
  const base =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";
  const res = await fetch(`${base}/problems/today`, {
    cache: "no-store",
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || "Failed to fetch daily problem");
  }

  return res.json();
}

export default async function DailyQuestionPage() {
  // Fetch the daily problem
  let problem;

  try {
    problem = await fetchDailyProblem();
  } catch (error) {
    console.error("Daily problem fetch failed", error);
    return (
      <div className="min-h-screen grid place-items-center bg-gray-100 dark:bg-gray-950 px-4">
        <div className="max-w-xl w-full bg-white dark:bg-gray-900 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center space-y-4">
          <h1 className="text-2xl font-semibold text-red-600 dark:text-red-400">
            Unable to load today&apos;s problem
          </h1>
          <p className="text-sm text-gray-700 dark:text-gray-300">
            Please verify the backend is running at{" "}
            <code className="text-xs bg-gray-200 dark:bg-gray-800 px-2 py-1 rounded">
              {process.env.NEXT_PUBLIC_API_BASE_URL ||
                "http://localhost:8000/api"}
            </code>{" "}
            and try refreshing this page.
          </p>
        </div>
      </div>
    );
  }

  const testCases = problem?.test_cases ?? [];

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-950">
      <main className="container mx-auto px-4 py-8">
        {/* Two-column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Problem Details */}
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg p-6">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              {problem.title}
            </h1>

            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                Problem Statement
              </h2>
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                {problem.description}
              </p>
            </div>

            {/* Test Cases Section */}
            {testCases.length > 0 && (
              <div>
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                  Example Test Cases
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Your solution will be tested with stdin input and compared
                  against expected stdout.
                </p>
                {testCases.map((testCase, index) => (
                  <div
                    key={testCase.id ?? index}
                    className="mb-6 bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700"
                  >
                    <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">
                      Example {index + 1}
                    </h3>
                    <div className="space-y-3">
                      <div>
                        <div className="text-sm font-semibold text-blue-700 dark:text-blue-400 mb-1">
                          📥 stdin (Input)
                        </div>
                        <pre className="bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded p-3 overflow-x-auto">
                          <code className="text-sm text-gray-800 dark:text-gray-200">
                            {testCase.input_data}
                          </code>
                        </pre>
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-green-700 dark:text-green-400 mb-1">
                          📤 stdout (Expected Output)
                        </div>
                        <pre className="bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded p-3 overflow-x-auto">
                          <code className="text-sm text-gray-800 dark:text-gray-200">
                            {testCase.expected_output}
                          </code>
                        </pre>
                      </div>
                      {testCase.explanation && (
                        <div>
                          <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-1">
                            💡 Explanation
                          </div>
                          <p className="text-gray-700 dark:text-gray-300 text-sm">
                            {testCase.explanation}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Note about testing */}
            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">
                ℹ️ Testing Method
              </h3>
              <p className="text-sm text-blue-800 dark:text-blue-400">
                Your code will receive input through stdin and must write output
                to stdout. The system compares your stdout with the expected
                output for each test case.
              </p>
            </div>
          </div>

          {/* Right Column - Code Submission */}
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg p-6">
            <CodeSubmission problemId={problem.id} />
          </div>
        </div>
      </main>
    </div>
  );
}
