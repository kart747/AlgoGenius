"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { toast } from "@/lib/toast";
import api from "@/src/lib/api";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center text-sm text-slate-400">
      Loading editor…
    </div>
  ),
});

const LANGUAGE_OPTIONS = [
  {
    id: "python",
    label: "Python 3",
    template: [
      "import sys",
      "",
      "def solve():",
      "    data = sys.stdin.read().strip().split()",
      "    # TODO: implement solution",
      "    print(0)",
      "",
      'if __name__ == "__main__":',
      "    solve()",
      "",
    ].join("\n"),
  },
  {
    id: "cpp",
    label: "C++17",
    template: [
      "#include <bits/stdc++.h>",
      "using namespace std;",
      "",
      "int main() {",
      "    ios::sync_with_stdio(false);",
      "    cin.tie(nullptr);",
      "    // TODO: implement solution",
      "    cout << 0 << '\\n';",
      "    return 0;",
      "}",
      "",
    ].join("\n"),
  },
  {
    id: "java",
    label: "Java 17",
    template: [
      "import java.io.*;",
      "import java.util.*;",
      "",
      "public class Main {",
      "    public static void main(String[] args) throws Exception {",
      "        FastScanner fs = new FastScanner(System.in);",
      "        PrintWriter out = new PrintWriter(System.out);",
      "        // TODO: implement solution",
      "        out.println(0);",
      "        out.flush();",
      "    }",
      "",
      "    static final class FastScanner {",
      "        private final InputStream in;",
      "        private final byte[] buffer = new byte[1 << 16];",
      "        private int ptr = 0, len = 0;",
      "",
      "        FastScanner(InputStream is) { this.in = is; }",
      "",
      "        private int read() throws IOException {",
      "            if (ptr >= len) {",
      "                len = in.read(buffer);",
      "                ptr = 0;",
      "                if (len <= 0) return -1;",
      "            }",
      "            return buffer[ptr++];",
      "        }",
      "",
      "        int nextInt() throws IOException {",
      "            int c;",
      "            while ((c = read()) <= ' ') {",
      "                if (c == -1) return -1;",
      "            }",
      "            int sign = 1;",
      "            if (c == '-') {",
      "                sign = -1;",
      "                c = read();",
      "            }",
      "            int val = 0;",
      "            while (c > ' ') {",
      "                val = val * 10 + (c - '0');",
      "                c = read();",
      "            }",
      "            return val * sign;",
      "        }",
      "    }",
      "}",
      "",
    ].join("\n"),
  },
];

const MIN_EDITOR_HEIGHT = 320;
const MAX_EDITOR_HEIGHT = 880;

function normalizeStatus(status) {
  if (!status) return "PENDING";
  const normalized = status.toString().trim().toUpperCase();
  if (["AC", "WA", "RE", "TLE"].includes(normalized)) {
    return normalized;
  }
  if (normalized.includes("ACCEPT")) return "AC";
  if (normalized.includes("SUCCESS")) return "AC";
  if (normalized.includes("WRONG")) return "WA";
  if (normalized.includes("TIME")) return "TLE";
  if (normalized.includes("LIMIT")) return "TLE";
  if (normalized.includes("RUNTIME")) return "RE";
  if (normalized.includes("ERROR")) return "RE";
  if (normalized.includes("FAIL")) return "RE";
  return normalized || "PENDING";
}

function verdictStyle(status) {
  switch (status) {
    case "AC":
      return "bg-emerald-500/15 text-emerald-200 border border-emerald-400/40";
    case "WA":
      return "bg-amber-500/15 text-amber-200 border border-amber-400/40";
    case "TLE":
      return "bg-sky-500/15 text-sky-200 border border-sky-400/40";
    case "RE":
      return "bg-rose-500/15 text-rose-200 border border-rose-400/40";
    default:
      return "bg-white/10 text-white/70 border border-white/20";
  }
}

function formatMetric(value, suffix) {
  if (value === null || value === undefined) return "—";
  return `${value}${suffix}`;
}

function splitParagraphs(text) {
  if (!text) return [];
  return text
    .split("\n")
    .map((paragraph) => paragraph.trim())
    .filter(Boolean);
}

export default function ProblemSolveShell({ problem }) {
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState("");
  const [testInput, setTestInput] = useState("");
  const [testOutput, setTestOutput] = useState("");
  const [diagnostic, setDiagnostic] = useState("");
  const [verdict, setVerdict] = useState("PENDING");
  const [executionTime, setExecutionTime] = useState(null);
  const [memoryUsage, setMemoryUsage] = useState(null);
  const [theme, setTheme] = useState("vs-dark");
  const [busy, setBusy] = useState(false);
  const [editorHeight, setEditorHeight] = useState(520);
  const resizeState = useRef({ active: false, startY: 0, startHeight: 520 });

  const selectedLanguage = useMemo(
    () =>
      LANGUAGE_OPTIONS.find((option) => option.id === language) ??
      LANGUAGE_OPTIONS[0],
    [language]
  );

  const storageKey = useCallback(
    (lang) => `algogenius:solve:${problem.id}:language:${lang}`,
    [problem.id]
  );

  useEffect(() => {
    const stored =
      typeof window !== "undefined"
        ? localStorage.getItem(storageKey(language))
        : null;
    setCode(stored ?? selectedLanguage.template);
  }, [language, selectedLanguage.template, storageKey]);

  useEffect(() => {
    const handle = setTimeout(() => {
      if (typeof window !== "undefined") {
        localStorage.setItem(storageKey(language), code);
      }
    }, 400);

    return () => clearTimeout(handle);
  }, [code, language, storageKey]);

  useEffect(() => {
    const handleShortcut = (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        event.preventDefault();
        runCode();
      }
    };

    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [code, language, testInput]);

  const beginResize = useCallback(
    (startY) => {
      resizeState.current = {
        active: true,
        startY,
        startHeight: editorHeight,
      };
    },
    [editorHeight]
  );

  const handlePointerDown = useCallback(
    (event) => {
      event.preventDefault();
      const clientY = event.clientY ?? event.touches?.[0]?.clientY;
      if (typeof clientY !== "number") return;
      beginResize(clientY);
    },
    [beginResize]
  );

  useEffect(() => {
    const handleMove = (event) => {
      if (!resizeState.current.active) return;
      const clientY = event.clientY ?? event.touches?.[0]?.clientY;
      if (typeof clientY !== "number") return;
      const delta = clientY - resizeState.current.startY;
      const nextHeight = Math.min(
        MAX_EDITOR_HEIGHT,
        Math.max(MIN_EDITOR_HEIGHT, resizeState.current.startHeight + delta)
      );
      setEditorHeight(nextHeight);
    };

    const stopResize = () => {
      resizeState.current.active = false;
    };

    window.addEventListener("mousemove", handleMove);
    window.addEventListener("touchmove", handleMove);
    window.addEventListener("mouseup", stopResize);
    window.addEventListener("touchend", stopResize);
    window.addEventListener("touchcancel", stopResize);

    return () => {
      window.removeEventListener("mousemove", handleMove);
      window.removeEventListener("touchmove", handleMove);
      window.removeEventListener("mouseup", stopResize);
      window.removeEventListener("touchend", stopResize);
      window.removeEventListener("touchcancel", stopResize);
    };
  }, []);

  const applyExecutionResult = useCallback((data, intent) => {
    const status = normalizeStatus(
      data?.status || (intent === "submit" ? "SUBMITTED" : "COMPLETED")
    );
    setVerdict(status);
    setExecutionTime(
      data?.execution_time ??
        data?.runtime_ms ??
        data?.runtime ??
        data?.time ??
        null
    );
    setMemoryUsage(
      data?.memory_usage ?? data?.memory_kb ?? data?.memory ?? null
    );
    setTestOutput(data?.stdout ?? data?.output ?? "");
    setDiagnostic(data?.stderr ?? data?.error ?? "");

    const message =
      data?.message ||
      (status === "AC"
        ? intent === "submit"
          ? "Accepted! Great job."
          : "Execution completed successfully."
        : intent === "submit"
        ? "Submission processed."
        : "Execution finished.");

    if (status === "AC") {
      toast.success(message);
    } else if (status === "PENDING" || status === "IDLE") {
      toast.info(message);
    } else {
      toast.error(message);
    }
  }, []);

  const runCode = useCallback(async () => {
    if (!code.trim()) {
      toast.error("Write your solution before running.");
      return;
    }

    setBusy(true);
    setVerdict("RUNNING");
    setExecutionTime(null);
    setMemoryUsage(null);
    setTestOutput("");
    setDiagnostic("");

    try {
      const { data } = await api.post("/submissions/run", {
        problem_id: problem.id,
        language,
        code,
        stdin: testInput,
      });
      applyExecutionResult(data, "run");
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        "Failed to execute code.";
      setVerdict("RE");
      setDiagnostic(message);
      toast.error(message);
    } finally {
      setBusy(false);
    }
  }, [applyExecutionResult, code, language, problem.id, testInput]);

  const submitSolution = useCallback(async () => {
    if (!code.trim()) {
      toast.error("Write your solution before submitting.");
      return;
    }

    setBusy(true);
    setVerdict("SUBMITTING");

    try {
      const { data } = await api.post("/submissions/submit", {
        problem_id: problem.id,
        language,
        code,
      });
      applyExecutionResult(data, "submit");
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        "Submission failed.";
      setVerdict("RE");
      setDiagnostic(message);
      toast.error(message);
    } finally {
      setBusy(false);
    }
  }, [applyExecutionResult, code, language, problem.id]);

  const descriptionParagraphs = useMemo(
    () =>
      splitParagraphs(problem.description || problem.problem_statement || ""),
    [problem.description, problem.problem_statement]
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <header className="border-b border-white/10 bg-slate-950/80 px-6 py-6 backdrop-blur">
        <div className="mx-auto flex w-full max-w-6xl flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-white/50">
              Problem
            </p>
            <h1 className="text-2xl font-semibold text-white/90 sm:text-3xl">
              {problem.title}
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <span className="rounded-full border border-emerald-400/30 bg-emerald-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-emerald-200">
              {(problem.difficulty || "easy").toUpperCase()}
            </span>
            <label className="flex items-center gap-2 text-xs text-white/60">
              Theme
              <select
                value={theme}
                onChange={(event) => setTheme(event.target.value)}
                className="rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs text-white focus:border-white/50 focus:outline-none"
              >
                <option value="vs-dark">Dark</option>
                <option value="light">Light</option>
              </select>
            </label>
          </div>
        </div>
      </header>

      <main className="mx-auto grid w-full max-w-6xl gap-6 px-6 pb-16 pt-8 lg:grid-cols-[minmax(320px,0.9fr)_minmax(420px,1.1fr)]">
        <article className="scrollbar-thin scrollbar-track-transparent scrollbar-thumb-white/10 space-y-8 overflow-y-auto rounded-3xl border border-white/10 bg-white/5 p-6">
          <section className="space-y-4 text-sm leading-relaxed text-white/80">
            {descriptionParagraphs.length ? (
              descriptionParagraphs.map((paragraph, idx) => (
                <p key={idx}>{paragraph}</p>
              ))
            ) : (
              <p>No description provided.</p>
            )}
          </section>

          {Array.isArray(problem.examples) && problem.examples.length > 0 && (
            <section className="space-y-4">
              <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-white/50">
                Examples
              </h2>
              <div className="space-y-4">
                {problem.examples.map((example, idx) => (
                  <div
                    key={example.id ?? idx}
                    className="rounded-2xl border border-white/10 bg-black/40 p-4 text-xs text-white/70"
                  >
                    <h3 className="text-xs font-semibold text-white/80">
                      Example {idx + 1}
                    </h3>
                    <div className="mt-3">
                      <span className="font-semibold text-white/70">Input</span>
                      <pre className="mt-1 rounded bg-black/60 p-3 whitespace-pre-wrap">
                        {example.input ?? example.input_data ?? ""}
                      </pre>
                    </div>
                    <div className="mt-3">
                      <span className="font-semibold text-white/70">
                        Output
                      </span>
                      <pre className="mt-1 rounded bg-black/60 p-3 whitespace-pre-wrap">
                        {example.output ?? example.output_data ?? ""}
                      </pre>
                    </div>
                    {example.explanation && (
                      <p className="mt-3 text-white/60">
                        {example.explanation}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {Array.isArray(problem.test_cases) &&
            problem.test_cases.length > 0 && (
              <section className="space-y-3">
                <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-white/50">
                  Hidden Tests
                </h2>
                <p className="text-xs text-white/50">
                  {problem.test_cases.length} hidden cases ensure correctness.
                  Use custom tests before submitting.
                </p>
              </section>
            )}
        </article>

        <section className="flex flex-col gap-5">
          <div className="rounded-3xl border border-white/10 bg-black/40 p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                {LANGUAGE_OPTIONS.map((option) => (
                  <button
                    key={option.id}
                    type="button"
                    onClick={() => setLanguage(option.id)}
                    className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
                      language === option.id
                        ? "bg-white text-slate-900"
                        : "bg-white/10 text-white/80 hover:bg-white/20"
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
              <div className="flex items-center gap-2 text-xs text-white/60">
                <span>Status</span>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${verdictStyle(
                    verdict
                  )}`}
                >
                  {verdict}
                </span>
              </div>
            </div>

            <div className="mt-4 overflow-hidden rounded-2xl border border-white/10">
              <MonacoEditor
                language={language === "cpp" ? "cpp" : language}
                theme={theme}
                value={code}
                onChange={(value) => setCode(value ?? "")}
                height={editorHeight}
                options={{
                  automaticLayout: true,
                  fontSize: 14,
                  minimap: { enabled: false },
                  fontLigatures: true,
                  scrollbar: { useShadows: false, verticalScrollbarSize: 6 },
                }}
              />
              <div
                className="flex cursor-row-resize items-center justify-center border-t border-white/10 bg-black/60 py-1 text-[10px] uppercase tracking-[0.3em] text-white/40"
                onMouseDown={handlePointerDown}
                onTouchStart={handlePointerDown}
              >
                Drag to resize
              </div>
            </div>

            <div className="mt-4 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={runCode}
                disabled={busy}
                className="inline-flex items-center rounded-full bg-indigo-500 px-5 py-2 text-sm font-semibold text-white transition hover:bg-indigo-600 disabled:opacity-60"
              >
                {busy && verdict === "RUNNING"
                  ? "Running…"
                  : "Run (Ctrl+Enter)"}
              </button>
              <button
                type="button"
                onClick={submitSolution}
                disabled={busy}
                className="inline-flex items-center rounded-full border border-white/30 px-5 py-2 text-sm font-semibold text-white transition hover:bg-white/10 disabled:opacity-60"
              >
                {busy && verdict === "SUBMITTING" ? "Submitting…" : "Submit"}
              </button>
            </div>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-white/80">
                  Test Input
                </h3>
                <span className="text-[10px] uppercase tracking-[0.25em] text-white/40">
                  stdin
                </span>
              </div>
              <textarea
                value={testInput}
                onChange={(event) => setTestInput(event.target.value)}
                placeholder="Paste custom input here…"
                className="mt-3 h-40 w-full rounded-2xl border border-white/10 bg-black/30 p-3 text-sm text-white/80 focus:border-white/40 focus:outline-none"
              />
            </div>
            <div className="rounded-3xl border border-white/10 bg-black/40 p-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-white/80">
                  Test Output
                </h3>
                <span className="text-[10px] uppercase tracking-[0.25em] text-white/40">
                  stdout
                </span>
              </div>
              <pre className="mt-3 h-40 overflow-auto rounded-2xl bg-black/60 p-3 text-sm text-white/70 whitespace-pre-wrap">
                {testOutput || "Run code to view output."}
              </pre>
            </div>
          </div>

          <div className="grid gap-5 md:grid-cols-3">
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-center">
              <p className="text-[11px] uppercase tracking-[0.3em] text-white/50">
                Time
              </p>
              <p className="mt-2 text-lg font-semibold text-white/90">
                {formatMetric(executionTime, " ms")}
              </p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-center">
              <p className="text-[11px] uppercase tracking-[0.3em] text-white/50">
                Memory
              </p>
              <p className="mt-2 text-lg font-semibold text-white/90">
                {formatMetric(memoryUsage, " KB")}
              </p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-center">
              <p className="text-[11px] uppercase tracking-[0.3em] text-white/50">
                Hidden Tests
              </p>
              <p className="mt-2 text-lg font-semibold text-white/90">
                {Array.isArray(problem.test_cases)
                  ? problem.test_cases.length
                  : 0}
              </p>
            </div>
          </div>

          {diagnostic && (
            <div className="rounded-3xl border border-rose-400/40 bg-rose-500/10 p-4 text-sm text-rose-100">
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-rose-200/90">
                stderr
              </p>
              <pre className="mt-2 whitespace-pre-wrap text-rose-100">
                {diagnostic}
              </pre>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
