"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/src/lib/api";
import { toast } from "@/lib/toast";
import { useUserContext } from "@/components/UserProvider";

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

const MAX_TOPICS = 4;

const normalizeTopicKey = (value = "") => value.trim().toLowerCase();

const formatTopicLabel = (value = "") =>
  value
    .split(" ")
    .filter(Boolean)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");

export default function GenerateProblemPage() {
  const router = useRouter();
  const { user, loading: userLoading } = useUserContext();

  const [selectedTopics, setSelectedTopics] = useState([TOPICS[0]]);
  const [difficulty, setDifficulty] = useState("easy");
  const [customTopicInput, setCustomTopicInput] = useState("");
  const [customPromptEnabled, setCustomPromptEnabled] = useState(false);
  const [customPrompt, setCustomPrompt] = useState("");

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
    if (!userLoading && !user) {
      router.replace("/login?next=/generate");
    }
  }, [router, user, userLoading]);

  if (userLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <p className="text-sm uppercase tracking-[0.3em] text-white/60">Loading…</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <p className="text-sm uppercase tracking-[0.3em] text-white/60">Redirecting to login…</p>
      </div>
    );
  }


  const primaryTopic = selectedTopics[0] || "";
  const selectedTopicLimitReached = selectedTopics.length >= MAX_TOPICS;

  const handleTopicToggle = (rawValue) => {
    const candidate = rawValue.trim();
    if (!candidate) {
      return;
    }

    setSelectedTopics((prev) => {
      const exists = prev.some(
        (entry) => normalizeTopicKey(entry) === normalizeTopicKey(candidate)
      );
      if (exists) {
        if (prev.length === 1) {
          toast.error("Keep at least one topic selected.");
          return prev;
        }
        return prev.filter(
          (entry) => normalizeTopicKey(entry) !== normalizeTopicKey(candidate)
        );
      }

      if (prev.length >= MAX_TOPICS) {
        toast.error(`Select up to ${MAX_TOPICS} topics.`);
        return prev;
      }

      return [...prev, candidate];
    });
  };

  const handleMakePrimaryTopic = (rawValue) => {
    const targetKey = normalizeTopicKey(rawValue);
    setSelectedTopics((prev) => {
      const target = prev.find(
        (entry) => normalizeTopicKey(entry) === targetKey
      );
      if (!target || prev[0] === target) {
        return prev;
      }
      const others = prev.filter(
        (entry) => normalizeTopicKey(entry) !== targetKey
      );
      return [target, ...others];
    });
  };

  const handleCustomTopicAdd = () => {
    const value = customTopicInput.trim();
    if (!value) {
      toast.error("Type a topic before adding it.");
      return;
    }
    handleTopicToggle(value);
    setCustomTopicInput("");
  };

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
    if (!primaryTopic) {
      toast.error("Select at least one topic before generating a problem.");
      return;
    }

    const customPromptPayload =
      customPromptEnabled && customPrompt.trim().length > 0
        ? customPrompt.trim()
        : null;

    setIsGenerating(true);
    setError(null);
    setSavedProblemId(null);

    try {
      const payload = {
        topic: primaryTopic,
        topics: selectedTopics.slice(1),
        difficulty,
        force_new: true,
        avoid_duplicates: true,
        min_variation: "high",
        seed: Date.now().toString(),
      };

      if (customPromptPayload) {
        payload.custom_prompt = customPromptPayload;
      }

      const { data } = await api.post(
        "/problems/generate",
        payload,
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
        function_templates:
          data.problem.function_templates ||
          data.problem.function_template ||
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
      topics:
        Array.isArray(generatedProblem.topics) && generatedProblem.topics.length
          ? generatedProblem.topics
          : selectedTopics,
    };

    try {
      const { data } = await api.post("/problems", payload, {
        timeout: 30000,
      });

      const savedProblem = {
        ...(generatedProblem || {}),
        ...(data || {}),
        id: data?.id ?? generatedProblem?.id ?? null,
      };

      const newId = savedProblem?.id;
      if (!newId) {
        throw new Error("Problem saved but no identifier was returned.");
      }

      setSavedProblemId(newId);
      setGeneratedProblem(savedProblem);
      toast.success("Problem saved to DevArena. You can solve it now.");
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
        <div className="space-y-2 rounded-2xl border border-white/10 bg-black/20 p-4">
          <p className="text-sm font-semibold text-white/80">
            Reference solutions are disabled.
          </p>
          <p className="text-xs text-white/60">
            We now skip auto-generating answers so you can focus on solving the
            prompt without spoilers. Save and open the challenge in the solve
            workspace when you are ready to code.
          </p>
        </div>
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

  const renderFunctionTemplates = () => {
    const templates = generatedProblem?.function_templates || {};
    const entries = Object.entries(templates);

    if (!entries.length) {
      return (
        <p className="text-sm text-white/60">
          No function templates were generated for this problem.
        </p>
      );
    }

    return (
      <div className="space-y-4">
        {entries.map(([lang, template]) => (
          <div
            key={lang}
            className="rounded-2xl border border-white/10 bg-black/20 p-4"
          >
            <div className="mb-2 flex items-center justify-between">
              <span className="text-sm font-semibold text-white/90">
                {lang.toUpperCase()}
              </span>
              <button
                type="button"
                onClick={async () => {
                  try {
                    await navigator.clipboard.writeText(template);
                    toast.success(`${lang.toUpperCase()} template copied.`);
                  } catch (err) {
                    console.error("Copy failed", err);
                    toast.error("Unable to copy template.");
                  }
                }}
                className="rounded-full border border-white/20 px-3 py-1 text-xs font-semibold text-white/70 transition hover:border-white/40 hover:text-white"
              >
                Copy
              </button>
            </div>
            <pre className="max-h-72 overflow-auto rounded-xl border border-white/5 bg-black/50 p-3 text-xs text-white/80 whitespace-pre-wrap">
              {template}
            </pre>
          </div>
        ))}
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
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
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
            it to DevArena, and jump straight into solving.
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
              <div className="space-y-3 text-sm text-white/70 md:col-span-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold text-white/80">
                    Topic focus
                  </span>
                  <span className="text-xs text-white/50">
                    {selectedTopics.length}/{MAX_TOPICS} selected
                  </span>
                </div>
                <p className="text-xs text-white/60">
                  Pick up to {MAX_TOPICS} topics. Click a pill to add or remove it.
                  The order below controls how the AI blends them.
                </p>
                <div className="flex flex-wrap gap-2">
                  {TOPICS.map((value) => {
                    const isActive = selectedTopics.some(
                      (entry) => normalizeTopicKey(entry) === normalizeTopicKey(value)
                    );
                    return (
                      <button
                        key={value}
                        type="button"
                        onClick={() => handleTopicToggle(value)}
                        className={`rounded-full px-4 py-1.5 text-xs font-semibold transition ${
                          isActive
                            ? "bg-white text-slate-900"
                            : "bg-white/10 text-white/70 hover:bg-white/20"
                        }`}
                      >
                        {formatTopicLabel(value)}
                      </button>
                    );
                  })}
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.3em] text-white/40">
                    Selected order
                  </p>
                  {selectedTopics.length ? (
                    <ul className="mt-3 space-y-2 text-sm text-white/80">
                      {selectedTopics.map((value, index) => (
                        <li
                          key={`${value}-${index}`}
                          className="flex flex-col gap-2 rounded-xl bg-white/5 px-3 py-2 sm:flex-row sm:items-center sm:justify-between"
                        >
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-semibold text-white/60">
                              {index + 1}.
                            </span>
                            <span className="font-medium text-white">
                              {formatTopicLabel(value)}
                            </span>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {index > 0 && (
                              <button
                                type="button"
                                onClick={() => handleMakePrimaryTopic(value)}
                                className="rounded-full border border-white/20 px-3 py-1 text-xs font-semibold text-white/70 transition hover:border-white/40 hover:text-white"
                              >
                                Move up
                              </button>
                            )}
                            <button
                              type="button"
                              onClick={() => handleTopicToggle(value)}
                              className="rounded-full border border-white/20 px-3 py-1 text-xs font-semibold text-white/70 transition hover:border-white/40 hover:text-white"
                            >
                              Remove
                            </button>
                          </div>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="mt-2 text-xs text-white/60">
                      Select at least one topic to continue.
                    </p>
                  )}
                </div>
                <div className="flex flex-col gap-2 sm:flex-row">
                  <input
                    value={customTopicInput}
                    onChange={(event) => setCustomTopicInput(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        event.preventDefault();
                        handleCustomTopicAdd();
                      }
                    }}
                    placeholder="Add a custom topic (e.g., bitmask dp)"
                    className="flex-1 rounded-full border border-white/20 bg-white/5 px-4 py-2 text-sm text-white placeholder:text-white/40 focus:border-white/50 focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={handleCustomTopicAdd}
                    disabled={selectedTopicLimitReached}
                    className={`rounded-full px-5 py-2 text-sm font-semibold transition ${
                      selectedTopicLimitReached
                        ? "bg-white/10 text-white/40"
                        : "bg-white text-slate-900 hover:bg-slate-100"
                    }`}
                  >
                    Add topic
                  </button>
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-white/70">
              <label className="flex items-center gap-3 text-white/80">
                <input
                  type="checkbox"
                  checked={customPromptEnabled}
                  onChange={(event) => {
                    setCustomPromptEnabled(event.target.checked);
                    if (!event.target.checked) {
                      setCustomPrompt("");
                    }
                  }}
                  className="h-4 w-4 rounded border-white/30 bg-transparent accent-emerald-400"
                />
                <span className="font-semibold">
                  Add custom prompt instructions
                </span>
              </label>
              {customPromptEnabled && (
                <textarea
                  value={customPrompt}
                  onChange={(event) => setCustomPrompt(event.target.value)}
                  maxLength={1200}
                  placeholder="Describe constraints, storytelling, or anything Gemini should emphasize."
                  className="mt-3 h-28 w-full rounded-2xl border border-white/20 bg-white/10 p-3 text-sm text-white placeholder:text-white/40 focus:border-white/50 focus:outline-none"
                />
              )}
              <p className="mt-2 text-xs text-white/50">
                Leave blank to let DevArena craft the prompt automatically.
              </p>
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
                    Function templates (parameter-based)
                  </h3>
                  {renderFunctionTemplates()}
                </section>

                <section className="space-y-3">
                  <h3 className="text-lg font-semibold text-white/90">
                    Editor preview
                  </h3>
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-sm text-white/70">
                    The full Monaco editor will be available on the solve page.
                    Craft your own approach—there are no spoiler solutions to
                    lean on.
                  </div>
                </section>
              </article>
            )}
          </div>

          <aside className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-gradient-to-br from-white/10 via-white/5 to-transparent p-6">
            <h3 className="text-lg font-semibold text-white/90">Next steps</h3>
            <p className="text-sm text-white/70">
              Generate a problem, review the prompt, and when you are ready,
              save it to make it part of the DevArena platform. Once saved,
              you can jump straight into solving with the full editor
              experience.
            </p>

            <button
              onClick={handleSave}
              disabled={
                !generatedProblem ||
                isGenerating ||
                isSaving ||
                Boolean(savedProblemId)
              }
              className={`w-full rounded-full px-6 py-3 text-sm font-semibold text-white transition ${
                !generatedProblem || isGenerating || isSaving || savedProblemId
                  ? "bg-white/20 text-white/50"
                  : "bg-emerald-500 hover:bg-emerald-600"
              }`}
            >
              {savedProblemId
                ? "Saved"
                : isSaving
                ? "Saving..."
                : "Save to Platform"}
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
