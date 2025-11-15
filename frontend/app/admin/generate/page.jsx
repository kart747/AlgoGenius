"use client";

import { useState } from "react";
import api from "@/src/lib/api";

const TOPICS = [
  "arrays",
  "math",
  "strings",
  "dynamic programming",
  "graphs",
  "greedy",
];

const DIFFICULTIES = ["easy", "medium", "hard"];

export default function AdminGeneratePage() {
  const [topic, setTopic] = useState(TOPICS[0]);
  const [difficulty, setDifficulty] = useState("easy");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);
  const [problem, setProblem] = useState(null);
  const [modelUsed, setModelUsed] = useState(null);
  const [activeLanguage, setActiveLanguage] = useState("python");

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const handleGenerate = async () => {
    setLoading(true);
    setSaving(false);
    setError(null);
    setProblem(null);
    setModelUsed(null);

    try {
      const { data } = await api.post("/problems/generate", {
        topic,
        difficulty,
      });
      setProblem(data.problem);
      setModelUsed(data.model_used);
      const languages = Object.keys(data.problem.reference_solution || {});
      if (languages.length > 0) {
        setActiveLanguage(languages[0]);
      }
      showToast("Problem generated successfully.");
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        "Failed to generate problem.";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!problem) {
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const normalizedTestCases = (problem.test_cases || [])
        .map((testCase) => ({
          input_data: testCase.input_data ?? testCase.input ?? "",
          expected_output: testCase.expected_output ?? testCase.output ?? "",
        }))
        .filter((testCase) => testCase.input_data && testCase.expected_output);

      if (normalizedTestCases.length === 0) {
        setError("Generated problem is missing test cases to save.");
        setSaving(false);
        return;
      }

      const normalizedExamples = (problem.examples || [])
        .map((example) => ({
          input: example.input ?? example.input_data ?? "",
          output: example.output ?? example.output_data ?? "",
          explanation: example.explanation ?? "",
        }))
        .filter((example) => example.input && example.output);

      const referenceSolution = Object.fromEntries(
        Object.entries(problem.reference_solution || {}).filter(
          ([, code]) => typeof code === "string" && code.trim().length > 0
        )
      );

      const payload = {
        title: problem.title,
        description: problem.description,
        difficulty: (problem.difficulty || difficulty || "easy").toLowerCase(),
        test_cases: normalizedTestCases,
        examples: normalizedExamples,
        reference_solution: referenceSolution,
      };

      const { data } = await api.post("/problems", payload);
      setProblem(data);
      const languages = Object.keys(data.reference_solution || {});
      if (languages.length > 0) {
        setActiveLanguage(languages[0]);
      }
      showToast("Problem saved to database.");
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        "Failed to save problem.";
      setError(detail);
    } finally {
      setSaving(false);
    }
  };

  const renderDescription = (text) => {
    if (!text) return null;
    return text
      .split("\n")
      .filter(Boolean)
      .map((paragraph, idx) => (
        <p
          key={idx}
          className="text-sm leading-relaxed text-gray-700 dark:text-gray-300 mb-3"
        >
          {paragraph.trim()}
        </p>
      ));
  };

  const renderExamples = (examples) => {
    if (!examples || examples.length === 0)
      return (
        <p className="text-sm text-gray-600 dark:text-gray-400">
          No examples provided.
        </p>
      );
    return (
      <div className="space-y-4">
        {examples.map((example, idx) => (
          <div
            key={idx}
            className="border border-gray-200 dark:border-gray-700 rounded-lg p-3 bg-gray-50 dark:bg-gray-900/30"
          >
            <h4 className="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-2">
              Example {idx + 1}
            </h4>
            <div className="text-xs text-gray-600 dark:text-gray-400">
              <div className="mb-2">
                <span className="font-semibold text-gray-700 dark:text-gray-300">
                  Input:
                </span>
                <pre className="mt-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded p-2 whitespace-pre-wrap">
                  {example.input}
                </pre>
              </div>
              <div className="mb-2">
                <span className="font-semibold text-gray-700 dark:text-gray-300">
                  Output:
                </span>
                <pre className="mt-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded p-2 whitespace-pre-wrap">
                  {example.output}
                </pre>
              </div>
              {example.explanation && (
                <div>
                  <span className="font-semibold text-gray-700 dark:text-gray-300">
                    Explanation:
                  </span>
                  <p className="mt-1">{example.explanation}</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderReferenceSolutions = (reference) => {
    if (!reference || Object.keys(reference).length === 0) {
      return (
        <p className="text-sm text-gray-600 dark:text-gray-400">
          No reference solutions generated.
        </p>
      );
    }

    const languages = Object.keys(reference);

    return (
      <div>
        <div className="flex gap-2 mb-3">
          {languages.map((lang) => (
            <button
              key={lang}
              onClick={() => setActiveLanguage(lang)}
              className={`px-3 py-1 text-sm rounded border transition-colors ${
                activeLanguage === lang
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white dark:bg-gray-900 border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
              }`}
            >
              {lang.toUpperCase()}
            </button>
          ))}
        </div>
        <pre className="bg-gray-900 text-gray-100 text-sm rounded-lg p-4 whitespace-pre-wrap overflow-x-auto border border-gray-800">
          {reference[activeLanguage]}
        </pre>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-950 py-10">
      <div className="max-w-5xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
          AI Problem Generator
        </h1>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-8">
          Generate fresh coding challenges using Gemini and optionally save them
          to the database.
        </p>

        <div className="bg-white dark:bg-gray-900 rounded-lg shadow-md border border-gray-200 dark:border-gray-800 p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Topic
              </label>
              <select
                value={topic}
                onChange={(event) => setTopic(event.target.value)}
                className="w-full px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200"
              >
                {TOPICS.map((option) => (
                  <option key={option} value={option}>
                    {option.charAt(0).toUpperCase() + option.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Difficulty
              </label>
              <select
                value={difficulty}
                onChange={(event) => setDifficulty(event.target.value)}
                className="w-full px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200"
              >
                {DIFFICULTIES.map((level) => (
                  <option key={level} value={level}>
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 mt-6">
            <button
              onClick={handleGenerate}
              disabled={loading}
              className={`px-5 py-2 rounded-md text-white font-medium transition-colors ${
                loading
                  ? "bg-blue-400 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-700"
              }`}
            >
              {loading ? "Generating..." : "Generate Problem"}
            </button>
            <button
              onClick={handleSave}
              disabled={!problem || saving}
              className={`px-5 py-2 rounded-md font-medium transition-colors flex items-center gap-2 ${
                !problem || saving
                  ? "bg-gray-300 dark:bg-gray-700 text-gray-600 dark:text-gray-400 cursor-not-allowed"
                  : "bg-green-600 text-white hover:bg-green-700"
              }`}
            >
              {saving ? "Saving..." : "💾 Save Problem"}
            </button>
            {loading && (
              <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <svg className="animate-spin h-4 w-4 mr-2" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v8z"
                  ></path>
                </svg>
                Calling Gemini...
              </div>
            )}
          </div>

          {error && (
            <div className="mt-4 p-3 rounded border border-red-300 bg-red-50 text-red-700 text-sm">
              {error}
            </div>
          )}

          {toast && (
            <div
              className={`mt-4 p-3 rounded border text-sm ${
                toast.type === "success"
                  ? "border-green-300 bg-green-50 text-green-700"
                  : "border-yellow-300 bg-yellow-50 text-yellow-700"
              }`}
            >
              {toast.message}
            </div>
          )}
        </div>

        {problem && (
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-md border border-gray-200 dark:border-gray-800 p-6 space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {problem.title}
              </h2>
              <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300">
                {problem.difficulty?.toUpperCase()}
              </div>
            </div>

            <section>
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
                Description
              </h3>
              {renderDescription(problem.description)}
            </section>

            <section>
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
                Examples
              </h3>
              {renderExamples(problem.examples)}
            </section>

            <section>
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
                Reference Solutions
              </h3>
              {renderReferenceSolutions(problem.reference_solution)}
            </section>

            <section>
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
                Test Cases
              </h3>
              <div className="space-y-3">
                {(problem.test_cases || []).map((testCase, idx) => (
                  <div
                    key={idx}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-3 bg-gray-50 dark:bg-gray-900/30 text-xs text-gray-700 dark:text-gray-300"
                  >
                    <div className="font-semibold text-gray-800 dark:text-gray-200 mb-2">
                      Test Case {idx + 1}
                    </div>
                    <div className="mb-2">
                      <span className="font-semibold">Input:</span>
                      <pre className="mt-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded p-2 whitespace-pre-wrap">
                        {testCase.input}
                      </pre>
                    </div>
                    <div>
                      <span className="font-semibold">Expected Output:</span>
                      <pre className="mt-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded p-2 whitespace-pre-wrap">
                        {testCase.expected_output}
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {modelUsed && (
              <div className="text-xs text-gray-500 dark:text-gray-400 pt-4 border-t border-gray-200 dark:border-gray-800">
                Generated by Gemini model:{" "}
                <span className="font-semibold">{modelUsed}</span>
                {modelUsed !== "gemini-2.5-flash" && (
                  <span className="ml-2 text-yellow-600 dark:text-yellow-400">
                    (fallback model in use)
                  </span>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
