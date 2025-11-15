"use client";

import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";
import api from "@/src/lib/api";

const LANG_OPTIONS = [
  { id: "python", label: "Python" },
  { id: "cpp", label: "C++" },
  { id: "java", label: "Java" },
];

const DEFAULT_SNIPPETS = {
  python: "# Write your Python solution here\n",
  cpp: [
    "// Write your C++ solution here",
    "#include <bits/stdc++.h>",
    "using namespace std;",
    "int main(){",
    "    ios::sync_with_stdio(false);",
    "    cin.tie(nullptr);",
    "    return 0;",
    "}\n",
  ].join("\n"),
  java: [
    "// Write your Java solution here",
    "import java.io.*;",
    "import java.util.*;",
    "public class Main {",
    "    public static void main(String[] args) throws Exception {",
    "        // TODO",
    "    }",
    "}\n",
  ].join("\n"),
};

export default function ProblemEditorClient({ problemId }) {
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState("");
  const [editorLoading, setEditorLoading] = useState(true);
  const [monacoAvailable, setMonacoAvailable] = useState(false);
  const [MonacoEditor, setMonacoEditor] = useState(null);

  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const editorRef = useRef(null);

  const storageKey = (lang) =>
    `algogenius:problem:${problemId}:language:${lang}`;

  useEffect(() => {
    let isMounted = true;
    setEditorLoading(true);
    import("@monaco-editor/react")
      .then((mod) => {
        if (!isMounted) return;
        setMonacoEditor(() => mod.default);
        setMonacoAvailable(true);
      })
      .catch(() => {
        setMonacoAvailable(false);
      })
      .finally(() => {
        if (isMounted) setEditorLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(storageKey(language));
      if (saved !== null) {
        setCode(saved);
      } else {
        setCode(DEFAULT_SNIPPETS[language] || "");
      }
    } catch (err) {
      setCode(DEFAULT_SNIPPETS[language] || "");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [language, problemId]);

  useEffect(() => {
    const handle = setTimeout(() => {
      try {
        localStorage.setItem(storageKey(language), code || "");
      } catch (err) {
        // ignore storage errors
      }
    }, 400);
    return () => clearTimeout(handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [code, language]);

  const handleRun = async () => {
    setError(null);
    setResult(null);

    if (!code.trim()) {
      setError("Code is empty.");
      return;
    }

    if (new Blob([code]).size > 50 * 1024) {
      setError("Code exceeds 50KB limit.");
      return;
    }

    setRunning(true);
    try {
      const payload = {
        problem_id: Number(problemId),
        language,
        code,
      };
      const response = await api.post("/submissions", payload);
      setResult(response.data || response);
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        "Submission failed";
      setError(message);
    } finally {
      setRunning(false);
    }
  };

  const handleEditorMount = (editor) => {
    editorRef.current = editor;
  };

  const renderEditor = () => {
    if (editorLoading) {
      return (
        <div className="h-full flex items-center justify-center text-sm text-gray-600 dark:text-gray-300">
          <svg
            className="animate-spin h-5 w-5 text-gray-500 mr-2"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
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
          Loading editor...
        </div>
      );
    }

    if (monacoAvailable && MonacoEditor) {
      const languageMap =
        language === "cpp" ? "cpp" : language === "java" ? "java" : "python";
      return (
        <MonacoEditor
          height="500px"
          language={languageMap}
          value={code}
          onChange={(value) => setCode(value || "")}
          onMount={handleEditorMount}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            tabSize: 4,
            automaticLayout: true,
          }}
        />
      );
    }

    return (
      <textarea
        value={code}
        onChange={(event) => setCode(event.target.value)}
        className="w-full h-[500px] p-3 font-mono text-sm bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded resize-none"
        placeholder="Write your solution here..."
      />
    );
  };

  return (
    <div className="bg-white dark:bg-gray-900 rounded shadow p-4 flex flex-col h-full">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Language
          </label>
          <select
            value={language}
            onChange={(event) => setLanguage(event.target.value)}
            className="rounded border px-2 py-1 bg-white dark:bg-gray-800 text-sm"
          >
            {LANG_OPTIONS.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={handleRun}
          disabled={running}
          className={`px-4 py-2 rounded font-medium text-white ${
            running
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          {running ? "Running..." : "Run Code"}
        </button>
      </div>

      <div className="flex-1 border border-gray-200 dark:border-gray-800 rounded overflow-hidden mb-3">
        {renderEditor()}
      </div>

      {error && (
        <div className="mb-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded">
          <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
        </div>
      )}

      {result && (
        <div className="p-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded">
          <div className="flex items-center justify-between mb-2">
            <div>
              <span className="text-sm font-semibold text-gray-800 dark:text-gray-100">
                {result.status}
              </span>
              {typeof result.runtime_ms === "number" && (
                <span className="ml-2 text-xs text-gray-600 dark:text-gray-400">
                  ({result.runtime_ms} ms)
                </span>
              )}
            </div>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {result.message || ""}
            </span>
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
            Output:
          </div>
          <pre className="bg-white dark:bg-gray-900 p-3 rounded max-h-40 overflow-auto text-sm whitespace-pre-wrap">
            {result.output || "(no output)"}
          </pre>
          {result.failed_case !== null && result.failed_case !== undefined && (
            <div className="mt-2 text-xs text-red-600 dark:text-red-400">
              Failed case: #{result.failed_case}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
