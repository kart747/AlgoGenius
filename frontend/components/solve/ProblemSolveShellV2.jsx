"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "@/lib/toast";
import api from "@/src/lib/api";
import ProblemPanel from "./ProblemPanel";
import CodeEditor from "./CodeEditor";
import ConsolePanel from "./ConsolePanel";

const LANGUAGE_OPTIONS = [
  {
    id: "python",
    label: "Python 3",
    template: `import sys

def solve():
    data = sys.stdin.read().strip().split()
    # TODO: implement solution
    print(0)

if __name__ == "__main__":
    solve()
`,
  },
  {
    id: "cpp",
    label: "C++17",
    template: `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    // TODO: implement solution
    cout << 0 << '\\n';
    return 0;
}
`,
  },
  {
    id: "java",
    label: "Java 17",
    template: `import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        PrintWriter out = new PrintWriter(System.out);
        // TODO: implement solution
        out.println(0);
        out.flush();
    }
}
`,
  },
];

function normalizeStatus(status) {
  if (!status) return "PENDING";
  const normalized = status.toString().trim().toUpperCase();
  if (
    ["AC", "WA", "RE", "TLE", "PENDING", "RUNNING", "SUBMITTING"].includes(
      normalized
    )
  ) {
    return normalized;
  }
  if (normalized.includes("ACCEPT") || normalized.includes("SUCCESS"))
    return "AC";
  if (normalized.includes("WRONG")) return "WA";
  if (normalized.includes("TIME") || normalized.includes("LIMIT")) return "TLE";
  if (
    normalized.includes("RUNTIME") ||
    normalized.includes("ERROR") ||
    normalized.includes("FAIL")
  )
    return "RE";
  return normalized || "PENDING";
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

  const selectedLanguage = useMemo(
    () =>
      LANGUAGE_OPTIONS.find((opt) => opt.id === language) ||
      LANGUAGE_OPTIONS[0],
    [language]
  );

  const storageKey = useCallback(
    (lang) => `algogenius:solve:${problem.id}:${lang}`,
    [problem.id]
  );

  // Load saved code or template
  useEffect(() => {
    if (typeof window === "undefined") return;

    const saved = localStorage.getItem(storageKey(language));
    if (saved) {
      setCode(saved);
    } else {
      setCode(selectedLanguage.template);
    }
  }, [language, selectedLanguage.template, storageKey]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleShortcut = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        handleRun();
      }
    };

    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [code, language, testInput]);

  const handleLanguageChange = useCallback((newLang) => {
    setLanguage(newLang);
  }, []);

  const handleCodeChange = useCallback((newCode) => {
    setCode(newCode);
  }, []);

  const handleThemeChange = useCallback((newTheme) => {
    setTheme(newTheme);
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

    // Handle output - check both stdout and output fields
    const outputText = data?.stdout ?? data?.output ?? "";
    const errorText = data?.stderr ?? data?.error ?? "";

    setTestOutput(outputText);
    setDiagnostic(errorText);

    const message =
      data?.message ||
      (status === "AC"
        ? intent === "submit"
          ? "Accepted! Great job."
          : "Execution completed successfully."
        : status === "WA"
        ? "Wrong Answer"
        : status === "RE"
        ? "Runtime Error"
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

  const handleRun = useCallback(async () => {
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

  const handleSubmit = useCallback(async () => {
    if (!code.trim()) {
      toast.error("Write your solution before submitting.");
      return;
    }

    setBusy(true);
    setVerdict("SUBMITTING");

    try {
      const { data } = await api.post("/submissions", {
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

  return (
    <div className="flex h-screen flex-col bg-slate-950 text-slate-100">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-slate-700/60 bg-slate-900/80 px-6 py-4 backdrop-blur">
        <div>
          <div className="text-xs uppercase tracking-wider text-slate-500">
            Problem
          </div>
          <h1 className="text-lg font-semibold text-slate-100">
            {problem.title}
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Problem */}
        <div className="w-full border-r border-slate-700/60 bg-slate-900/40 lg:w-5/12">
          <ProblemPanel problem={problem} />
        </div>

        {/* Right Panel - Editor + Console */}
        <div className="flex w-full flex-col lg:w-7/12">
          <CodeEditor
            problemId={problem.id}
            language={language}
            code={code}
            theme={theme}
            onLanguageChange={handleLanguageChange}
            onCodeChange={handleCodeChange}
            onThemeChange={handleThemeChange}
          />

          <ConsolePanel
            testInput={testInput}
            testOutput={testOutput}
            diagnostic={diagnostic}
            verdict={verdict}
            executionTime={executionTime}
            memoryUsage={memoryUsage}
            busy={busy}
            onTestInputChange={setTestInput}
            onRun={handleRun}
            onSubmit={handleSubmit}
          />
        </div>
      </div>
    </div>
  );
}
