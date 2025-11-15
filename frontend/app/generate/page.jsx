"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/src/lib/api";
import { toast } from "@/lib/toast";

const TOPICS = [
  "arrays",
  "dynamic programming",
  "graphs",
  "strings",
  "math",
  "trees",
  "greedy",
  "hash maps",
  "sorting",
];

const DIFFICULTIES = ["easy", "medium", "hard"];

const shimmerBlock = "rounded bg-white/10";

const PLACEHOLDER_MESSAGES = [
  "Generating a fresh challenge…",
  "Asking the algorithm gods…",
  "Crafting a unique problem…",
];

export default function GenerateProblemPage() {
  const router = useRouter();

  const [topic, setTopic] = useState(TOPICS[0]);
  const [difficulty, setDifficulty] = useState("easy");

  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [placeholderIndex, setPlaceholderIndex] = useState(0);

  const [generatedProblem, setGeneratedProblem] = useState(null);
  const [modelUsed, setModelUsed] = useState(null);
  const [fallbackUsed, setFallbackUsed] = useState(false);
  const [activeSolutionLang, setActiveSolutionLang] = useState("python");
  const [savedProblemId, setSavedProblemId] = useState(null);

  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isGenerating) {
      setPlaceholderIndex(0);
      return;
    }

    const interval = setInterval(() => {
      setPlaceholderIndex((prev) => (prev + 1) % PLACEHOLDER_MESSAGES.length);
    }, 2400);

    return () => clearInterval(interval);
  }, [isGenerating]);

  const toDisplayString = (value, fallback = "") => {
    if (typeof value === "string") {
      return value;
    }
    if (Array.isArray(value)) {
      return value
        .map((item) =>
          typeof item === "object" && item !== null
            ? item.msg || item.message || JSON.stringify(item)
            : String(item)
        )
        .join("; ");
    }
    if (value && typeof value === "object") {
      if (typeof value.message === "string") {
        return value.message;
      }
      return JSON.stringify(value);
    }
    if (value == null) {
      return fallback;
    }
    return String(value);
  };

  const referenceLanguages = useMemo(() => {
    if (!generatedProblem?.reference_solution) {
      return [];
    }
    return Object.keys(generatedProblem.reference_solution).filter((lang) => {
      const val = generatedProblem.reference_solution[lang];
      return typeof val === "string" && val.trim().length > 0;
    });
  }, [generatedProblem]);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    setSavedProblemId(null);

    try {
      const { data } = await api.post(
        "/problems/generate",
        {
          topic,
          difficulty,
          force_new: true,
          avoid_duplicates: true,
          min_variation: "high",
          seed: Date.now().toString(),
        },
        {
          timeout: 120000,
        }
      );

      if (!data?.problem) {
        throw new Error("No problem returned by the AI service.");
      }

      const canonicalProblem = {
        ...data.problem,
        reference_solution:
          data.problem.reference_solution ||
          data.problem.reference_solutions ||
          {},
      };

      setGeneratedProblem(canonicalProblem);
      setModelUsed(data.model_used || "gemini-2.5-flash");
      setFallbackUsed(Boolean(data?.fallback_used));
      const languages = Object.keys(canonicalProblem.reference_solution || {});
      setActiveSolutionLang(languages[0] || "python");
    } catch (err) {
      const isTimeout = err?.code === "ECONNABORTED";
      const message = isTimeout
        ? "Problem generation took too long. Please try again in a moment."
        : toDisplayString(
            err?.response?.data?.detail ||
              err?.response?.data?.message ||
              err?.message,
            "Failed to generate problem. Please try again."
          );
      setGeneratedProblem(null);
      setModelUsed(null);
      setFallbackUsed(false);
      setError(message);
      toast.error(message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSave = async () => {
    if (!generatedProblem) {
      return;
    }

    setIsSaving(true);
    setError(null);

    const normalizedTestCases = (generatedProblem.test_cases || [])
      .map((testCase) => ({
        input_data: testCase.input_data ?? testCase.input ?? "",
        expected_output: testCase.expected_output ?? testCase.output ?? "",
      }))
      .filter((testCase) => testCase.input_data && testCase.expected_output);

    if (normalizedTestCases.length === 0) {
      setIsSaving(false);
      setError("Generated problem is missing test cases to save.");
      toast.error("Generated problem is missing test cases to save.");
      return;
    }

    const normalizedExamples = (generatedProblem.examples || [])
      .map((example) => ({
        input: example.input ?? example.input_data ?? "",
        output: example.output ?? example.output_data ?? "",
        explanation: example.explanation ?? "",
      }))
      .filter((example) => example.input && example.output);

    const referenceSolutions = Object.fromEntries(
      Object.entries(
        generatedProblem.reference_solution ||
          generatedProblem.reference_solutions ||
          {}
      ).filter(([, code]) => typeof code === "string" && code.trim().length > 0)
    );

    const payload = {
      title: generatedProblem.title,
      difficulty: (
        generatedProblem.difficulty ||
        difficulty ||
        "easy"
      ).toLowerCase(),
      description: generatedProblem.description,
      examples: normalizedExamples,
      test_cases: normalizedTestCases,
      reference_solution: referenceSolutions,
    };

    try {
      let savedProblem = null;
      try {
        const { data } = await api.post("/problems/generate/save", {
          topic,
          difficulty,
          force_new: true,
          avoid_duplicates: true,
          min_variation: "high",
          seed: Date.now().toString(),
        });
        savedProblem = data?.problem ?? data ?? null;
        setModelUsed((prev) => data?.model_used ?? prev);
        setFallbackUsed(Boolean(data?.fallback_used ?? fallbackUsed));
      } catch (primaryError) {
        const status = primaryError?.response?.status;
        if (!status || ![404, 405, 422].includes(status)) {
          throw primaryError;
        }

        const { data } = await api.post("/problems", payload);
        savedProblem = {
          ...(generatedProblem || {}),
          ...(data || {}),
          id: data?.id ?? generatedProblem?.id ?? null,
        };
        setFallbackUsed(false);
      }

      const newId = savedProblem?.id;
      if (!newId) {
        throw new Error("Problem saved but no identifier was returned.");
      }

      setSavedProblemId(newId);
      setGeneratedProblem((prev) => ({ ...(prev || {}), ...savedProblem }));
      toast.success("Problem saved to AlgoGenius. You can solve it now.");
    } catch (err) {
      const message = toDisplayString(
        err?.response?.data?.detail ||
          err?.response?.data?.message ||
          err?.message,
        "Failed to save the generated problem."
      );
      setError(message);
      toast.error(message);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSolve = () => {
    if (!savedProblemId) {
      toast.error("Save the problem first before solving.");
      return;
    }
    toast.info("Opening Solve Workspace…");
    router.prefetch(`/problems/${savedProblemId}/solve`);
    router.push(`/problems/${savedProblemId}/solve`);
  };

  const renderDescription = () => {
    if (!generatedProblem?.description) {
      return <p className="text-sm text-white/60">No description provided.</p>;
    }
    return generatedProblem.description
      .split("\n")
      .map((paragraph) => paragraph.trim())
      .filter(Boolean)
      .map((paragraph, idx) => (
        <p key={idx} className="text-sm leading-relaxed text-white/75">
          {paragraph}
        </p>
      ));
  };

  const renderExamples = () => {
    if (!generatedProblem?.examples || generatedProblem.examples.length === 0) {
      return <p className="text-sm text-white/60">No examples provided.</p>;
    }
    return generatedProblem.examples.map((example, idx) => (
      <div
        key={idx}
        className="rounded-2xl border border-white/10 bg-white/5 p-4"
      >
        <h4 className="text-sm font-semibold text-white/90">
          Example {idx + 1}
        </h4>
        <div className="mt-3 text-xs text-white/60">
          <div className="font-semibold text-white/80">Input</div>
          <pre className="mt-1 rounded bg-black/40 p-3 text-xs text-white/80 whitespace-pre-wrap">
            {example.input ?? example.input_data ?? ""}
          </pre>
        </div>
        <div className="mt-3 text-xs text-white/60">
          <div className="font-semibold text-white/80">Output</div>
          <pre className="mt-1 rounded bg-black/40 p-3 text-xs text-white/80 whitespace-pre-wrap">
            {example.output ?? example.output_data ?? ""}
          </pre>
        </div>
        {example.explanation && (
          <p className="mt-3 text-xs text-white/70">{example.explanation}</p>
        )}
      </div>
    ));
  };

  const renderTestCases = () => {
    if (
      !generatedProblem?.test_cases ||
      generatedProblem.test_cases.length === 0
    ) {
      return <p className="text-sm text-white/60">No test cases provided.</p>;
    }
    return generatedProblem.test_cases.map((testCase, idx) => (
      <div
        key={idx}
        className="rounded-2xl border border-white/10 bg-black/20 p-4 text-xs text-white/70"
      >
        <div className="mb-2 font-semibold text-white/80">
          Test Case {idx + 1}
        </div>
        <div className="mb-2">
          <div className="font-semibold text-white/70">stdin</div>
          <pre className="mt-1 rounded bg-black/40 p-3 whitespace-pre-wrap">
            {testCase.input ?? testCase.input_data ?? ""}
          </pre>
        </div>
        <div>
          <div className="font-semibold text-white/70">stdout</div>
          <pre className="mt-1 rounded bg-black/40 p-3 whitespace-pre-wrap">
            {testCase.expected_output ?? testCase.output ?? ""}
          </pre>
        </div>
      </div>
    ));
  };

  const renderReferenceSolutions = () => {
    if (!referenceLanguages.length) {
      return (
        <p className="text-sm text-white/60">
          No reference solutions generated.
        </p>
      );
    }

    const activeCode =
      generatedProblem?.reference_solution?.[activeSolutionLang] ?? "";

    return (
      <div className="space-y-3">
        <div className="flex flex-wrap gap-2">
          {referenceLanguages.map((lang) => (
            <button
              key={lang}
              type="button"
              onClick={() => setActiveSolutionLang(lang)}
              className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
                activeSolutionLang === lang
                  ? "bg-white text-slate-900"
                  : "bg-white/10 text-white/80 hover:bg-white/20"
              }`}
            >
              {lang.toUpperCase()}
            </button>
          ))}
        </div>
        <pre className="max-h-96 overflow-auto rounded-2xl border border-white/10 bg-black/50 p-4 text-xs text-white/80 whitespace-pre">
          {activeCode}
        </pre>
      </div>
    );
  };

  const hiddenTestsCount =
    generatedProblem?.hidden_tests_count ??
    (Array.isArray(generatedProblem?.test_cases)
      ? generatedProblem.test_cases.length
      : 0);

  const loadingMessage =
    PLACEHOLDER_MESSAGES[placeholderIndex % PLACEHOLDER_MESSAGES.length];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      <div className="absolute inset-0 overflow-hidden">
        <div className="pointer-events-none absolute -top-24 right-24 h-72 w-72 rounded-full bg-purple-500/20 blur-[120px]" />
        <div className="pointer-events-none absolute bottom-0 left-12 h-80 w-80 rounded-full bg-blue-500/20 blur-[120px]" />
      </div>

      <main className="relative mx-auto flex w-full max-w-6xl flex-col gap-10 px-6 pb-24 pt-16 sm:px-10">
        <header className="space-y-4 text-center sm:text-left">
          <p className="text-sm uppercase tracking-[0.3em] text-white/50">
            AI Problem Studio
          </p>
          <h1 className="text-3xl font-bold sm:text-4xl">
            Generate, review, and solve brand new coding problems
          </h1>
          <p className="text-white/70">
            Choose a topic and difficulty, let Gemini craft the challenge, save
            it to AlgoGenius, and jump straight into solving.
          </p>
        </header>
        <section className="grid gap-8 lg:grid-cols-[1.1fr_1fr]">
          <div className="space-y-6 rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur">
            <div className="grid gap-4 md:grid-cols-2">
              <label className="space-y-2 text-sm text-white/70">
                <span className="font-semibold text-white/80">
                  Select difficulty
                </span>
                <select
                  value={difficulty}
                  onChange={(event) => setDifficulty(event.target.value)}
                  className="w-full rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm text-white focus:border-white/50 focus:outline-none"
                >
                  {DIFFICULTIES.map((value) => (
                    <option
                      key={value}
                      value={value}
                      className="text-slate-900"
                    >
                      {value.charAt(0).toUpperCase() + value.slice(1)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="space-y-2 text-sm text-white/70">
                <span className="font-semibold text-white/80">
                  Select topic
                </span>
                <select
                  value={topic}
                  onChange={(event) => setTopic(event.target.value)}
                  className="w-full rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm text-white focus:border-white/50 focus:outline-none"
                >
                  {TOPICS.map((value) => (
                    <option
                      key={value}
                      value={value}
                      className="text-slate-900"
                    >
                      {value.charAt(0).toUpperCase() + value.slice(1)}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className={`w-full rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 px-8 py-3 text-base font-semibold text-white shadow-lg shadow-indigo-500/30 transition-transform ${
                isGenerating ? "opacity-60" : "hover:scale-[1.02]"
              }`}
            >
              {isGenerating ? "Generating..." : "Generate Problem"}
            </button>

            {isGenerating && (
              <p className="text-sm font-medium text-white/60">
                {loadingMessage}
              </p>
            )}

            {error && (
              <div className="rounded-2xl border border-rose-400/60 bg-rose-500/10 p-4 text-sm text-rose-200">
                {error}
              </div>
            )}

            {isGenerating && (
              <div className="space-y-4">
                <div className={`${shimmerBlock} h-6 w-3/4 animate-pulse`} />
                <div className={`${shimmerBlock} h-4 w-full animate-pulse`} />
                <div className={`${shimmerBlock} h-4 w-5/6 animate-pulse`} />
                <div className={`${shimmerBlock} h-32 w-full animate-pulse`} />
              </div>
            )}

            {generatedProblem && !isGenerating && (
              <article className="space-y-6 rounded-3xl border border-white/10 bg-black/30 p-6">
                <header className="space-y-3">
                  <div className="flex flex-wrap items-center gap-3">
                    <h2 className="text-2xl font-semibold text-white/95">
                      {generatedProblem.title}
                    </h2>
                    <span className="rounded-full border border-emerald-400/40 bg-emerald-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-emerald-200">
                      {generatedProblem.difficulty?.toUpperCase() ??
                        difficulty.toUpperCase()}
                    </span>
                  </div>
                  <span className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-semibold text-white/70">
                    Generated using: {modelUsed || "gemini-2.5-flash"}
                    {fallbackUsed && (
                      <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] font-semibold text-amber-200">
                        fallback
                      </span>
                    )}
                  </span>
                </header>

                <section className="space-y-3">
                  <h3 className="text-lg font-semibold text-white/90">
                    Description
                  </h3>
                  <div className="space-y-3">{renderDescription()}</div>
                </section>

                <section className="space-y-3">
                  <h3 className="text-lg font-semibold text-white/90">
                    Examples
                  </h3>
                  <div className="space-y-4">{renderExamples()}</div>
                </section>

                <section className="space-y-3">
                  <h3 className="text-lg font-semibold text-white/90">
                    Test Cases
                  </h3>
                  <p className="text-xs text-white/50">
                    Hidden tests: {hiddenTestsCount}
                  </p>
                  <div className="space-y-4">{renderTestCases()}</div>
                </section>

                <section className="space-y-3">
                  <h3 className="text-lg font-semibold text-white/90">
                    Reference solutions
                  </h3>
                  {renderReferenceSolutions()}
                </section>

                <section className="space-y-3">
                  <h3 className="text-lg font-semibold text-white/90">
                    Editor preview
                  </h3>
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-sm text-white/70">
                    The full Monaco editor will be available on the solve page.
                    Use the reference solutions above as a starting point if
                    needed.
                  </div>
                </section>
              </article>
            )}
          </div>

          <aside className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-gradient-to-br from-white/10 via-white/5 to-transparent p-6">
            <h3 className="text-lg font-semibold text-white/90">Next steps</h3>
            <p className="text-sm text-white/70">
              Generate a problem, review the prompt, and when you are ready,
              save it to make it part of the AlgoGenius platform. Once saved,
              you can jump straight into solving with the full editor
              experience.
            </p>

            <button
              onClick={handleSave}
              disabled={!generatedProblem || isGenerating || isSaving}
              className={`w-full rounded-full px-6 py-3 text-sm font-semibold text-white transition ${
                !generatedProblem || isGenerating || isSaving
                  ? "bg-white/20 text-white/50"
                  : "bg-emerald-500 hover:bg-emerald-600"
              }`}
            >
              {isSaving ? "Saving..." : "Save to Platform"}
            </button>

            <button
              onClick={handleSolve}
              disabled={!savedProblemId || isSaving}
              className={`w-full rounded-full border px-6 py-3 text-sm font-semibold transition ${
                !savedProblemId || isSaving
                  ? "border-white/20 text-white/40"
                  : "border-white/40 text-white/80 hover:border-white/60 hover:text-white"
              }`}
            >
              Solve This Problem →
            </button>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-xs text-white/60">
              <p>
                Save first to receive a permanent link and enable the in-browser
                Monaco editor with automated judging.
              </p>
            </div>
          </aside>
        </section>
      </main>
    </div>
  );
}
