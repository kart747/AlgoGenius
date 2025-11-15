import AdminDeleteProblem from "@/components/AdminDeleteProblem";
import ProblemEditorClient from "./ProblemEditorClient";

export default async function ProblemPage({ params }) {
  const { id } = await params;
  const apiBase =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";
  const endpoint = `${apiBase}/problems/${encodeURIComponent(id)}`;

  let problem = null;
  let fetchError = null;

  try {
    const res = await fetch(endpoint, { cache: "no-store" });
    if (!res.ok) {
      fetchError = `Failed to fetch problem: ${res.status} ${res.statusText}`;
    } else {
      problem = await res.json();
    }
  } catch (err) {
    fetchError = err instanceof Error ? err.message : String(err);
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-950">
      <main className="max-w-7xl mx-auto p-4">
        {fetchError ? (
          <div className="p-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded">
            <h2 className="text-xl font-semibold text-red-800 dark:text-red-200">
              Error
            </h2>
            <p className="mt-2 text-sm text-red-700 dark:text-red-300">
              {fetchError}
            </p>
          </div>
        ) : !problem ? (
          <div className="p-6 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded">
            <p className="text-sm text-yellow-800 dark:text-yellow-300">
              Problem not found or unavailable.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <section className="lg:col-span-7 bg-white dark:bg-gray-900 rounded shadow p-6">
              <header className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div className="flex flex-wrap items-center gap-3">
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    {problem.title}
                  </h1>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      (problem.difficulty || "easy").toLowerCase() === "hard"
                        ? "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300"
                        : (problem.difficulty || "easy").toLowerCase() ===
                          "medium"
                        ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300"
                        : "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300"
                    }`}
                  >
                    {problem.difficulty || "easy"}
                  </span>
                </div>
                <AdminDeleteProblem
                  problemId={Number(id)}
                  problemTitle={problem.title}
                />
              </header>

              <div className="prose dark:prose-invert max-w-none text-sm leading-relaxed">
                <pre className="whitespace-pre-wrap">
                  {problem.problem_statement ||
                    problem.description ||
                    "No description provided."}
                </pre>
              </div>

              {Array.isArray(problem.examples) &&
                problem.examples.length > 0 && (
                  <section className="mt-6">
                    <h2 className="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">
                      Examples
                    </h2>
                    <div className="space-y-4">
                      {problem.examples.map((example, index) => (
                        <article
                          key={index}
                          className="p-4 bg-gray-50 dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700"
                        >
                          <div className="text-sm text-gray-700 dark:text-gray-300 mb-2 font-semibold">
                            Input
                          </div>
                          <pre className="bg-white dark:bg-gray-900 p-2 rounded text-sm whitespace-pre-wrap">
                            {example.input}
                          </pre>
                          <div className="text-sm text-gray-700 dark:text-gray-300 mt-3 mb-2 font-semibold">
                            Output
                          </div>
                          <pre className="bg-white dark:bg-gray-900 p-2 rounded text-sm whitespace-pre-wrap">
                            {example.output}
                          </pre>
                          {example.explanation && (
                            <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">
                              {example.explanation}
                            </p>
                          )}
                        </article>
                      ))}
                    </div>
                  </section>
                )}
            </section>

            <aside className="lg:col-span-5">
              <ProblemEditorClient problemId={Number(id)} />
            </aside>
          </div>
        )}
      </main>
    </div>
  );
}
