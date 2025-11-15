"use client";

import { useState } from "react";
import api from "@/src/lib/api";

export default function CodeSubmission({ problemId }) {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setResult(null);

    try {
      // POST to /submissions (api baseURL is http://localhost:8000/api)
      const response = await api.post("/submissions", {
        problem_id: problemId,
        code,
        language,
      });

      setResult(response.data);
    } catch (error) {
      setResult({
        status: "Error",
        message:
          error.response?.data?.message ||
          "Submission failed. Please try again.",
        error: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
        Submit Your Solution
      </h2>

      <div className="flex flex-col flex-1">
        {/* Language Selector */}
        <div className="mb-4">
          <label
            htmlFor="language"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >
            Language
          </label>
          <select
            id="language"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full px-3 py-2 border rounded-md bg-white text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 border-gray-300 dark:bg-gray-900 dark:text-gray-100 dark:placeholder-gray-500 dark:border-gray-700"
          >
            <option value="python">Python</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
          </select>
        </div>

        {/* Code Editor (Textarea placeholder) */}
        <div className="mb-4 flex-1">
          <label
            htmlFor="code"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >
            Your Code
          </label>
          <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
            Your code will receive input via stdin and should output to stdout.
          </p>
          <textarea
            id="code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Write your code here... (use stdin for input, stdout for output)"
            className="w-full h-64 px-3 py-2 border rounded-md font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none bg-white text-gray-900 placeholder-gray-500 border-gray-300 dark:bg-gray-900 dark:text-gray-100 dark:placeholder-gray-500 dark:border-gray-700"
          />
        </div>

        {/* Submit Button */}
        <button
          onClick={handleSubmit}
          disabled={loading}
          className={`w-full py-3 px-4 rounded-md font-medium transition-colors ${
            loading
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700 text-white"
          }`}
        >
          {loading ? "Testing Your Code..." : "Run & Submit"}
        </button>

        {/* Result Display */}
        {result && (
          <div
            className={`mt-4 p-4 rounded-md border ${
              result.status === "Accepted"
                ? "bg-green-50 dark:bg-green-900/20 border-green-400 dark:border-green-700"
                : result.status === "Wrong Answer"
                ? "bg-yellow-50 dark:bg-yellow-900/20 border-yellow-400 dark:border-yellow-700"
                : "bg-red-50 dark:bg-red-900/20 border-red-400 dark:border-red-700"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <h3
                className={`font-bold text-lg ${
                  result.status === "Accepted"
                    ? "text-green-800 dark:text-green-300"
                    : result.status === "Wrong Answer"
                    ? "text-yellow-800 dark:text-yellow-300"
                    : "text-red-800 dark:text-red-300"
                }`}
              >
                {result.status === "Accepted" && "✓ Accepted!"}
                {result.status === "Wrong Answer" && "✗ Wrong Answer"}
                {result.status === "Error" && "✗ Error"}
                {!["Accepted", "Wrong Answer", "Error"].includes(
                  result.status
                ) && result.status}
              </h3>
            </div>

            <p
              className={`text-sm mb-3 ${
                result.status === "Accepted"
                  ? "text-green-700 dark:text-green-400"
                  : result.status === "Wrong Answer"
                  ? "text-yellow-700 dark:text-yellow-400"
                  : "text-red-700 dark:text-red-400"
              }`}
            >
              {result.message}
            </p>

            {/* Test Results */}
            {result.test_results && result.test_results.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-semibold text-gray-900 dark:text-gray-100 text-sm">
                  Test Case Results:
                </h4>
                {result.test_results.map((test, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded border ${
                      test.passed
                        ? "bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-800"
                        : "bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-800"
                    }`}
                  >
                    <div className="font-medium mb-2 flex items-center justify-between">
                      <span>
                        {test.passed ? "✓" : "✗"} Test Case {idx + 1}
                      </span>
                      <span
                        className={`text-xs font-semibold ${
                          test.passed
                            ? "text-green-700 dark:text-green-400"
                            : "text-red-700 dark:text-red-400"
                        }`}
                      >
                        {test.passed ? "PASSED" : "FAILED"}
                      </span>
                    </div>

                    {/* Always show input, expected, and actual output */}
                    <div className="space-y-2 text-xs">
                      <div>
                        <span className="font-semibold text-gray-700 dark:text-gray-300">
                          📥 stdin:
                        </span>
                        <pre className="mt-1 bg-white dark:bg-gray-900 p-2 rounded border border-gray-200 dark:border-gray-700 overflow-x-auto">
                          <code className="text-gray-800 dark:text-gray-200">
                            {test.input}
                          </code>
                        </pre>
                      </div>

                      <div>
                        <span className="font-semibold text-green-700 dark:text-green-400">
                          📤 Expected stdout:
                        </span>
                        <pre className="mt-1 bg-white dark:bg-gray-900 p-2 rounded border border-green-200 dark:border-green-800 overflow-x-auto">
                          <code className="text-gray-800 dark:text-gray-200">
                            {test.expected}
                          </code>
                        </pre>
                      </div>

                      <div>
                        <span
                          className={`font-semibold ${
                            test.passed
                              ? "text-green-700 dark:text-green-400"
                              : "text-red-700 dark:text-red-400"
                          }`}
                        >
                          {test.passed ? "✓" : "✗"} Your stdout:
                        </span>
                        <pre
                          className={`mt-1 p-2 rounded border overflow-x-auto ${
                            test.passed
                              ? "bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800"
                              : "bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800"
                          }`}
                        >
                          <code className="text-gray-800 dark:text-gray-200">
                            {test.actual}
                          </code>
                        </pre>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Full result for debugging */}
            {result.error && (
              <details className="mt-3">
                <summary className="cursor-pointer text-xs text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200">
                  Show full error details
                </summary>
                <pre className="mt-2 text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded overflow-x-auto">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </details>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
